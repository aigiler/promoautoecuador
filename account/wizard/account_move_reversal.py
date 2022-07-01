# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _

from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

class AccountMoveReversal(models.TransientModel):
    """
    Account move reversal wizard, it cancel an account move by reversing it.
    """
    _name = 'account.move.reversal'
    _description = 'Account Move Reversal'

    move_id = fields.Many2one('account.move', string='Journal Entry',
        domain=[('state', '=', 'posted'), ('type', 'not in', ('out_refund', 'in_refund'))])
    date = fields.Date(string='Reversal date', default=fields.Date.context_today, required=True)
    reason = fields.Char(string='Reason')
    refund_method = fields.Selection(selection=[
            ('refund', 'Partial Refund'),
            ('cancel', 'Full Refund'),
            ('modify', 'Full refund and new draft invoice')
        ], string='Credit Method', required=True,
        help='Choose how you want to credit this invoice. You cannot "modify" nor "cancel" if the invoice is already reconciled.')
    journal_id = fields.Many2one('account.journal', string='Use Specific Journal', help='If empty, uses the journal of the journal entry to be reversed.')

    # computed fields
    residual = fields.Monetary(compute="_compute_from_moves")
    currency_id = fields.Many2one('res.currency', compute="_compute_from_moves")
    move_type = fields.Char(compute="_compute_from_moves")

    @api.model
    def default_get(self, fields):
        res = super(AccountMoveReversal, self).default_get(fields)
        move_ids = self.env['account.move'].browse(self.env.context['active_ids']) if self.env.context.get('active_model') == 'account.move' else self.env['account.move']
        res['refund_method'] = (len(move_ids) > 1 or move_ids.type == 'entry') and 'cancel' or 'refund'
        res['residual'] = len(move_ids) == 1 and move_ids.amount_residual or 0
        res['currency_id'] = len(move_ids.currency_id) == 1 and move_ids.currency_id.id or False
        res['move_type'] = len(move_ids) == 1 and move_ids.type or False
        res['move_id'] = move_ids[0].id if move_ids else False
        return res

    @api.depends('move_id')
    def _compute_from_moves(self):
        move_ids = self.env['account.move'].browse(self.env.context['active_ids']) if self.env.context.get('active_model') == 'account.move' else self.move_id
        for record in self:
            record.residual = len(move_ids) == 1 and move_ids.amount_residual or 0
            record.currency_id = len(move_ids.currency_id) == 1 and move_ids.currency_id or False
            record.move_type = len(move_ids) == 1 and move_ids.type or False

    def _prepare_default_reversal(self, move):
        return {
            'ref': _('Reversal of: %s, %s') % (move.name, self.reason) if self.reason else _('Reversal of: %s') % (move.name),
            'date': self.date or move.date,
            'invoice_date': move.is_invoice(include_receipts=True) and (self.date or move.date) or False,
            'journal_id': self.journal_id and self.journal_id.id or move.journal_id.id,
            'invoice_payment_term_id': None,
            'auto_post': True if self.date > fields.Date.context_today(self) else False,
            'invoice_user_id': move.invoice_user_id.id,
        }

    def _reverse_moves_post_hook(self, moves):
        # DEPRECATED: TO REMOVE IN MASTER
        return

    def reverse_moves(self):
        moves = self.env['account.move'].browse(self.env.context['active_ids']) if self.env.context.get('active_model') == 'account.move' else self.move_id

        # Create default values.
        default_values_list = []
        for move in moves:
            default_values_list.append(self._prepare_default_reversal(move))

        batches = [
            [self.env['account.move'], [], True],   # Moves to be cancelled by the reverses.
            [self.env['account.move'], [], False],  # Others.
        ]
        for move, default_vals in zip(moves, default_values_list):
            is_auto_post = bool(default_vals.get('auto_post'))
            is_cancel_needed = not is_auto_post and self.refund_method in ('cancel', 'modify')
            batch_index = 0 if is_cancel_needed else 1
            batches[batch_index][0] |= move
            batches[batch_index][1].append(default_vals)

        # Handle reverse method.
        moves_to_redirect = self.env['account.move']
        for moves, default_values_list, is_cancel_needed in batches:
            new_moves = moves._reverse_moves(default_values_list, cancel=is_cancel_needed)

            if self.refund_method == 'modify':
                moves_vals_list = []
                for move in moves.with_context(include_business_fields=True):
                    moves_vals_list.append(move.copy_data({'date': self.date or move.date})[0])
                new_moves = self.env['account.move'].create(moves_vals_list)

            moves_to_redirect |= new_moves

        # Create action.
        action = {
            'name': _('Reverse Moves'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
        }
        if len(moves_to_redirect) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': moves_to_redirect.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', moves_to_redirect.ids)],
            })
        if self.refund_method=='cancel' and self.move_id.contrato_estado_cuenta_ids:

            cuota_capital_obj = self.env['rubros.contratos'].search([('name','=','cuota_capital')])
            seguro_obj = self.env['rubros.contratos'].search([('name','=','seguro')])
            otros_obj = self.env['rubros.contratos'].search([('name','=','otros')])
            rastreo_obj = self.env['rubros.contratos'].search([('name','=','rastreo')])
            lista_diarios=[]
            
            if cuota_capital_obj:
                lista_diarios.append(cuota_capital_obj.journal_id.id)
            if seguro_obj:
                lista_diarios.append(seguro_obj.journal_id.id)
            if otros_obj:
                lista_diarios.append(otros_obj.journal_id.id)
            if rastreo_obj:
                lista_diarios.append(rastreo_obj.journal_id.id)

            movimientos_cuota=self.env['account.move'].search([('ref','=',self.move_id.name),('journal_id','in',lista_diarios)])
            lista_pagos=[]
            for mov in movimientos_cuota:
                for x in mov.line_ids:
                    if x.account_id.id==x.partner_id.property_account_receivable_id.id:
                        for y in x.matched_credit_ids:
                            lista_pagos.append(y.credit_move_id.payment_id.id)
            for linea in self.move_id:
                for ant in linea.anticipos_ids:
                    lista_pagos.append(ant.payment_id.id)
                    for pag in ant.linea_pago_id:
                        pag.saldo_pendiente+=(ant.credit-ant.valor_sobrante)
                        pag.aplicar_anticipo=True
            for cuota_id in self.move_id.contrato_estado_cuenta_ids:
                cuota_id.factura_id=False
                pagos_cuotas=self.env['account.payment.cuotas'].search([('pago_id','in',lista_pagos)])
                pagos_cuotas.unlink()
                monto_sobrante=0
                for det in cuota_id.ids_pagos:
                    if det.pago_id not in lista_pagos:
                        monto_sobrante+=det.valor_asociado
                pagado_capital=cuota_id.cuota_capital-cuota_id.saldo_cuota_capital-monto_sobrante
                pagado_seguro=cuota_id.seguro-cuota_id.saldo_seguro
                pagado_rastreo=cuota_id.rastreo-cuota_id.saldo_rastreo
                pagado_otros=cuota_id.otro-cuota_id.saldo_otros
                pagado_administrativo=cuota_id.cuota_adm-cuota_id.saldo_cuota_administrativa
                pagado_iva=cuota_id.iva_adm-cuota_id.saldo_iva
                if cuota_id.estado_pago=='pagado':
                    transacciones=self.env['transaccion.grupo.adjudicado']
                    dct={
                            'grupo_id':cuota_id.contrato_id.grupo.id,
                            'debe':cuota_id.cuota_capital+cuota_id.seguro+cuota_id.rastreo+cuota_id.otro+cuota_id.cuota_adm+cuota_id.iva_adm,
                            'adjudicado_id':cuota_id.contrato_id.cliente.id,
                            'contrato_id':cuota_id.contrato_id.id,
                            'state':cuota_id.contrato_id.state
                            }
                    transacciones.create(dct)

                cuota_id.saldo_cuota_capital+=pagado_capital
                cuota_id.saldo_seguro+=pagado_seguro
                cuota_id.saldo_rastreo+=pagado_rastreo
                cuota_id.saldo_otros+=pagado_otros
                cuota_id.saldo_cuota_administrativa+=pagado_administrativo
                cuota_id.saldo_iva+=pagado_iva
                if cuota_id.saldo==0 or cuota_id.saldo==0.0 or cuota_id.saldo==0.00:
                    cuota_id.estado_pago='pagado'
                else:
                    cuota_id.estado_pago='pendiente'

            for mov in movimientos_cuota:

                movimiento_reverso_id=self.env['account.move.reversal'].create({'move_id':mov.id,'date':fields.Date.context_today(self),
                                        'journal_id':mov.journal_id.id,'move_type':'entry'})
                                #raise ValidationError("{0}".format(action_rubros))
                movimiento_reverso_id.reverso_diarios(mov)
                
        return action


    def reverso_diarios(self,moves):
        # Create default values.
        default_values_list = []
        for move in moves:
            default_values_list.append(self._prepare_default_reversal(move))

        batches = [
            [self.env['account.move'], [], True],   # Moves to be cancelled by the reverses.
            [self.env['account.move'], [], False],  # Others.
        ]
        for move, default_vals in zip(moves, default_values_list):
            is_auto_post = True
            is_cancel_needed =True
            batch_index = 0 if is_cancel_needed else 1
            batches[batch_index][0] |= move
            batches[batch_index][1].append(default_vals)

        # Handle reverse method.
        moves_to_redirect = self.env['account.move']
        for moves, default_values_list, is_cancel_needed in batches:
            new_moves = moves._reverse_moves(default_values_list, cancel=is_cancel_needed)

            if self.refund_method == 'modify':
                moves_vals_list = []
                for move in moves.with_context(include_business_fields=True):
                    moves_vals_list.append(move.copy_data({'date': self.date or move.date})[0])
                new_moves = self.env['account.move'].create(moves_vals_list)
            #new_moves.action_post()

            moves_to_redirect |= new_moves


        # Create action.
        # action = {
        #     'name': _('Reverse Moves'),
        #     'type': 'ir.actiaccountons.act_window',
        #     'res_model': '.move',
        # }
        # if len(moves_to_redirect) == 1:
        #     action.update({
        #         'view_mode': 'form',
        #         'res_id': moves_to_redirect.id,
        #     })
        # else:
        #     action.update({
        #         'view_mode': 'tree,form',
        #         'domain': [('id', 'in', moves_to_redirect.ids)],
        #     })

        #return action
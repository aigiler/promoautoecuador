# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    contrato_estado_cuenta_payment_ids = fields.One2many('contrato.estado.cuenta.payment', 'payment_pagos_id')

    tipo_valor = fields.Selection([
        ('enviar_credito', 'Enviar a Credito'),
        ('crear_acticipo', 'Crear Anticipo')
    ], string='Tipo')

    @api.onchange('tipo_valor')
    def _onchange_tipo_valor(self):
        if self.tipo_valor == 'enviar_credito':
            obj_am = self.env['account.move'].search([('id','in',self.invoice_ids.ids)])
            list_ids_cuotas = []
            cuotas = {
                'numero_cuota':'',
                'fecha':'',
                'cuota_capital':'',
                'seguro':'',
                'rastreo':'',
                'otro':'',
                'saldo':'',
                'cuota_capital_pagar':'',
                'seguro_pagar':'',
                'rastreo_pagar':'',
                'otro_pagar':'',
                'monto_pagar':'',
            }
            if not self.contrato_estado_cuenta_payment_ids:
                if obj_am:
                    for rec in obj_am:
                        for ric in rec.contrato_estado_cuenta_ids:
                            # list_ids_cuotas.append(ric)
                            cuotas.update({
                                'numero_cuota':ric.numero_cuota,
                                'fecha':ric.fecha,
                                'cuota_capital':ric.cuota_capital,
                                'seguro':ric.seguro,
                                'rastreo':ric.rastreo,
                                'otro':ric.otro,
                                'saldo':ric.saldo,
                                # 'cuota_capital_pagar':ric.cuota_capital_pagar,
                                # 'seguro_pagar':'',
                                # 'rastreo_pagar':'',
                                # 'otro_pagar':'',
                                # 'monto_pagar':'',
                            })
                            
                            self.contrato_estado_cuenta_payment_ids = [(0,0,cuotas)]

            # pass
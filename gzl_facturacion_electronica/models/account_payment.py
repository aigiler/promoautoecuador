# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    contrato_estado_cuenta_payment_ids = fields.One2many('contrato.estado.cuenta.payment', 'payment_pagos_id')
    valor_deuda=fields.Float("Valores Pendiente")
    saldo_pago=fields.Float("Saldo")

    tipo_valor = fields.Selection([
        ('enviar_credito', 'Enviar a Credito'),
        ('crear_acticipo', 'Crear Anticipo')
    ], string='Tipo')

    @api.onchange('partner_id')
    def obtener_deudas(self):
        valor_deuda=0
        for l in self:
            if l.partner_id:
                for x in l.payment_line_ids:
                    valor_deuda+=(x.actual_amount+x.monto_pendiente_pago)
        self.valor_deuda=valor_deuda

    @api.onchange('amount')
    def obtener_deudas(self):
        monto=0
        for l in self:
            valor=0
            if l.amount:
                valor=l.amount    
        monto=valor-self.valor_deuda

    #@api.multi
    def crear_detalles(self):
        self._onchange_tipo_valor()
        viewid = self.env.ref('gzl_facturacion_electronica.pago_cuota_form2').id
        return {   
            'name':'Detalle de Cuotas',
            'view_type':'form',
            'views' : [(viewid,'form')],
            'res_model':'account.payment',
            'res_id':self.id,
            'type':'ir.actions.act_window',
            'target':'new',
            }



    def cerrar_ventana(self):
        return {
        'type':'ir.actions.act_window_close'
        }

    @api.onchange('tipo_valor','payment_line_ids')
    def _onchange_tipo_valor(self):
        lista_cuotas = []
        if self.tipo_valor == 'enviar_credito':
            for rec in self.payment_line_ids:
                for cuota in rec.invoice_id.contrato_estado_cuenta_ids:
                    if cuota.id not in lista_cuotas:
                        lista_cuotas.append(cuota.id)
            # obj_am = self.env['account.move'].search([('id','in',self.invoice_ids.ids)])
            obj_estado_cuenta_ids = self.env['contrato.estado.cuenta'].search([('id','in',lista_cuotas)])
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
                if obj_estado_cuenta_ids:
                    # for rec in obj_am:
                    for ric in obj_estado_cuenta_ids:
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


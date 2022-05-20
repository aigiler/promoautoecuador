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
# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError

import numpy_financial as npf


class WizardPagoCuotaAmortizacion(models.TransientModel):
    _name = 'wizard.pago.cuota.amortizacion.contrato'
    
    tabla_amortizacion_id = fields.Many2one('contrato.estado.cuenta')
    payment_date = fields.Date(required=True, default=fields.Date.context_today)
    journal_id = fields.Many2one('account.journal', required=True, string='Diario', domain=[('type', 'in', ('bank', 'cash'))])
    payment_method_id = fields.Many2one('account.payment.method', string='Método de Pago', required=True)
    
    @api.onchange('journal_id')
    def onchange_payment_method(self):
        if self.journal_id:
            self.env.cr.execute("""select inbound_payment_method from account_journal_inbound_payment_method_rel where journal_id={0}""".format(self.journal_id.id))
            res = self.env.cr.dictfetchall()
            if res:
                list_method=[]
                for l in res:
                    list_method.append(l['inbound_payment_method'])
                return {'domain': {'payment_method_id': [('id', 'in', list_method)]}}

    
    def validar_pago(self):
        factura = self.tabla_amortizacion_id.factura_id
        pago = self.tabla_amortizacion_id.pago_id
        if factura:
            factura.write({
                'journal_id':self.journal_id,
                'invoice_date':self.payment_date,
            })
            
            pago.write({
                'journal_id':self.journal_id,
                'invoice_id':factura,
                'payment_date':self.payment_date,
                'payment_method_id':self.payment_method_id,
                'communication':factura.name
            })
            
        else:
            factura = self.env['account.move'].create({
                        'type': 'out_invoice',
                        'partner_id': self.tabla_amortizacion_id.oportunidad_id.partner_id.id,
                        'invoice_line_ids': [(0, 0, {
                            'quantity': 1,
                            'price_unit': self.tabla_amortizacion_id.cuota,
                            'name': self.tabla_amortizacion_id.oportunidad_id.name+' - Cuota '+self.tabla_amortizacion_id.numero_cuota,
                        })],
                        'journal_id':self.journal_id,
                        'invoice_date':self.payment_date,
                    })
            self.tabla_amortizacion_id.factura_id=factura

            pago = self.env['account.payment'].create({
                    'payment_date': self.payment_date,
                    'communication': l.oportunidad_id.name+' - Cuota '+l.numero_cuota,
                    'invoice_ids': [(6, 0, [factura.id])],
                    'payment_type': 'inbound',
                    'amount': l.cuota,
                    'partner_id': l.oportunidad_id.partner_id.id,
                    'partner_type': 'customer',
                    'payment_method_id': self.payment_method_id,
                    'journal_id': self.journal_id,
                    'invoice_id':factura,
                    'communication':factura.name
                    })
            self.tabla_amortizacion_id.pago_id = pago
            
        factura.action_post()
        pago.post()
        self.tabla_amortizacion_id.estado_pago='pagado'


        hoy=date.today()
        obj_calificador=self.env['calificador.cliente']

        if hoy<self.tabla_amortizacion_id.fecha:
            motivo=self.env.ref('gzl_adjudicacion.calificacion_4')
        else:
            motivo=self.env.ref('gzl_adjudicacion.calificacion_5')

        obj_calificador.create({'partner_id': self.tabla_amortizacion_id.contrato_id.cliente.id,'motivo':motivo.motivo,'calificacion':motivo.calificacion})

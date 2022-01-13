# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError

import numpy_financial as npf


class WizardAdelantarCuotas(models.TransientModel):
    _name = 'wizard.adelantar.cuotas'
    
    contrato_id = fields.Many2one('contrato')
    numero_cuotas = fields.Integer( string='Nro. Cuotas a Pagar',compute='calcular_numero_cuotas_a_cancelar',store=True)
    diferencia=fields.Float( string='Saldo de Pago que se acredita a una cuota',compute='calcular_numero_cuotas_a_cancelar',store=True)
    monto_a_pagar = fields.Float( string='Monto a Pagar')
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

    

    @api.depends('monto_a_pagar')
    def calcular_numero_cuotas_a_cancelar(self):
        for rec in self:
            saldo=rec.contrato_id.tabla_amortizacion.mapped('saldo')
            if len(saldo)>0:
                valor_saldo=max(saldo)
                rec.numero_cuotas=rec.monto_a_pagar/valor_saldo
                diferencia=(valor_saldo*rec.numero_cuotas) - rec.monto_a_pagar

                rec.diferencia=abs(diferencia)



    def validar_pago(self):

        if self.numero_cuotas==0 and self.monto_a_pagar>0:
            raise ValidationError('El número de cuotas debe ser diferente de 0')

        tabla=self.env['contrato.estado.cuenta'].search([('contrato_id','=',self.contrato_id.id),('estado_pago','=','pendiente')],order='fecha desc')





        saldo=self.contrato_id.tabla_amortizacion.mapped('saldo')
        valor_saldo=max(saldo)


        lista_pagos={}
        for i  in range(0,self.numero_cuotas):
            dct={
            i:valor_saldo
            }
            lista_pagos.update(dct)

        diferencia=(valor_saldo*self.numero_cuotas) - self.monto_a_pagar

        #if not (diferencia==0):
        #    cuota_adicional=self.numero_cuotas
        #    lista_pagos.update({cuota_adicional:abs(diferencia)})



        contador=0
       # raise ValidationError(str(lista_pagos))

        if len(lista_pagos.keys())>len(tabla):
            raise ValidationError('Ingrese un monto menor')

        for detalle in tabla[:len(lista_pagos.keys())]:
            dct={

            'tabla_amortizacion_id':detalle.id,
            'payment_date':self.payment_date,
            'journal_id':self.journal_id.id,
            'payment_method_id':self.payment_method_id.id,
            'amount':lista_pagos[contador]

            }
            pago=self.env['wizard.pago.cuota.amortizacion.contrato'].create(dct)
            pago.validar_pago(True)
            contador+=1

        if abs(diferencia)>0:
            tabla=self.env['contrato.estado.cuenta'].search([('contrato_id','=',self.contrato_id.id),('estado_pago','=','pendiente')],order='fecha asc')
            if len(tabla)>1:
                dct={

                'tabla_amortizacion_id':tabla.id,
                'payment_date':self.payment_date,
                'journal_id':self.journal_id.id,
                'payment_method_id':self.payment_method_id.id,
                'amount':diferencia

                }
                pago=self.env['wizard.pago.cuota.amortizacion.contrato'].create(dct)
                pago.validar_pago()

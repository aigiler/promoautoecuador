# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError

import numpy_financial as npf




class WizardContratoAdendum(models.Model):
    _name = 'wizard.contrato.adendum'
    _description = 'Contrato Adendum'


    contrato_id = fields.Many2one('contrato',string="Contrato")
    socio_id = fields.Many2one('res.partner',string="Socio")

    monto_financiamiento = fields.Monetary(
        string='Monto Financiamiento', currency_field='currency_id', track_visibility='onchange')
    plazo_meses = fields.Many2one('numero.meses',default=lambda self: self.env.ref('gzl_adjudicacion.{0}'.format('numero_meses60')).id ,track_visibility='onchange' )

    currency_id = fields.Many2one(
        'res.currency', readonly=True, default=lambda self: self.env.company.currency_id)


    def ejecutar_cambio(self,):
        obj=self.contrato_id

        pagos=self.contrato_id.tabla_amortizacion.filtered(lambda l: l.estado_pago=='pagado')
        pago_capital=sum(pagos.mapped("cuota_capital"))

        nuevoMontoReeestructura=self.monto_financiamiento-pago_capital


        cuotasPagadas=self.contrato_id.tabla_amortizacion.filtered(lambda l: l.estado_pago=='pagado' and l.cuotaAdelantada==False)


        cuotasAdelantadas=self.contrato_id.tabla_amortizacion.filtered(lambda l: l.estado_pago=='pagado' and l.cuotaAdelantada==True)


        numeroCuotasPagadaTotal=len(cuotasAdelantadas) + len(cuotasPagadas)


        diferenciaPlazoAdendum= abs(self.contrato_id.plazo_meses.numero - self.plazo_meses.numero)

        numeroCuotasTotal=diferenciaPlazoAdendum

        intervalo_nuevo=self.plazo_meses.numero - numeroCuotasPagadaTotal
        ####Calcular tus nuevos datos




        tasa_administrativa =  float(self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.tasa_administrativa'))
        obj_contrato=self.env['contrato.estado.cuenta'].search([('contrato_id','=',self.contrato_id.id),('estado_pago','=','pagado')])
        lista_cuotapagadas=[]
        cont =0
        for l in obj_contrato:
            cont+=1
            dct ={}
            dct['numero_cuota'] = cont
            dct['fecha']= l.fecha
            dct['cuota_capital']= l.cuota_capital
            dct['cuota_adm']= l.cuota_adm
            dct['iva_adm']= l.iva_adm
            dct['saldo']= l.saldo
            dct['contrato_id']= self.contrato_id.id
            lista_cuotapagadas.append(dct)
            
        obj_contrato.unlink()
        for a in lista_cuotapagadas:
            self.env['contrato.estado.cuenta'].create({
                                                'numero_cuota':a['numero_cuota'],
                                                'fecha':a['fecha'],
                                                'cuota_capital':a['cuota_capital'],
                                                'cuota_adm':a['cuota_adm'],
                                                'iva_adm':a['iva_adm'],
                                                'saldo':a['saldo'],
                                                'contrato_id':a['contrato_id'],                                                    
                                                    })
        for i in range(cont, int(intervalo_nuevo)):

            cuota_capital = nuevoMontoReeestructura/int(intervalo_nuevo)
            cuota_adm = nuevoMontoReeestructura *tasa_administrativa / 100 / 12
            iva = cuota_adm * 0.12

            cuota_administrativa_neto= cuota_adm + iva
            saldo = cuota_capital+cuota_adm+iva
            self.env['contrato.estado.cuenta'].create({
                                                'numero_cuota':i+1,
                                                'fecha':self.contrato_id.fecha_inicio_pago + relativedelta(months=i),
                                                'cuota_capital':cuota_capital,
                                                'cuota_adm':cuota_adm,
                                                'iva_adm':iva,
                                                'saldo':saldo,
                                                'contrato_id':self.contrato_id.id,                                                    
                                                    })
                                                    
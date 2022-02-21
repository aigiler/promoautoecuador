# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError
import numpy_financial as npf
import math


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
        numcuotas_congeladas=self.contrato_id.tabla_amortizacion.filtered(lambda l:  l.cuota_capital == 0)


        cuotasAdelantadas=self.contrato_id.tabla_amortizacion.filtered(lambda l: l.estado_pago=='pagado' and l.cuotaAdelantada==True)


        numeroCuotasPagadaTotal=len(cuotasAdelantadas) + len(cuotasPagadas)


        diferenciaPlazoAdendum= abs(self.contrato_id.plazo_meses.numero - self.plazo_meses.numero)

        numeroCuotasTotal=diferenciaPlazoAdendum

        intervalo_nuevo=self.plazo_meses.numero - numeroCuotasPagadaTotal + len(numcuotas_congeladas)
        self.contrato_id.plazo_meses.numero =self.plazo_meses.numero
        ####Calcular tus nuevos datos




        tasa_administrativa =  float(self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.tasa_administrativa'))
        #aqui se muestran las cuotas que han sido pagadas ya sean por adelanto o no 
        obj_contrato=self.env['contrato.estado.cuenta'].search([('contrato_id','=',self.contrato_id.id),('estado_pago','=','pagado')])
        lista_cuotapagadas=[]
        cont =0
        monto_finan_contrato= 0.00
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
            dct['estado_pago']= l.estado_pago
            lista_cuotapagadas.append(dct)
            
        #if nuevoMontoReeestructura:
        #    raise ValidationError(str(nuevoMontoReeestructura)+'--'+str(intervalo_nuevo))
        obj_contrato_detalle=self.env['contrato.estado.cuenta'].search([('contrato_id','=',self.contrato_id.id)])
        obj_contrato_detalle.unlink()
        
        for a in lista_cuotapagadas:
            #monto_finan_contrato+= a['cuota_capital']
            self.env['contrato.estado.cuenta'].create({
                                                'numero_cuota':a['numero_cuota'],
                                                'fecha':a['fecha'],
                                                'cuota_capital':a['cuota_capital'],
                                                'cuota_adm':a['cuota_adm'],
                                                'iva_adm':a['iva_adm'],
                                                'saldo':a['saldo'],
                                                'contrato_id':a['contrato_id'],
                                                'estado_pago':a['estado_pago'],                                                
                                                    })
        #cont+=1
        #raise ValidationError(str(monto_finan_contrato)+' monto_finan_contrato')
        contb=0
        for i in range(cont, int(intervalo_nuevo+cont)):
            contb +=1
            cuota_capital = (nuevoMontoReeestructura/int(intervalo_nuevo))
            #raise ValidationError(str(cuota_capital)+'--'+str(round(nuevoMontoReeestructura/int(intervalo_nuevo))))
            cuota_adm = nuevoMontoReeestructura *tasa_administrativa / 100 / 12
            iva = cuota_adm * 0.12
            #monto_finan_contrato+= cuota_capital
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
            
###############################################################################################################3333
        #raise ValidationError(str(sum(self.contrato_id.tabla_amortizacion.mapped('cuota_capital')))+' contb '+ str(contb))
        monto_finan_contrato = sum(self.contrato_id.tabla_amortizacion.mapped('cuota_capital'))
        if  monto_finan_contrato  > self.contrato_id.monto_financiamiento:
            valor_sobrante = monto_finan_contrato - self.contrato_id.monto_financiamiento 
            parte_decimal, parte_entera = math.modf(valor_sobrante)
            valor_a_restar= (valor_sobrante/parte_decimal)*0.1
            
            obj_contrato=self.env['contrato.estado.cuenta'].search([('contrato_id','=',self.contrato_id.id),('estado_pago','=','pendiente')] , order ='numero_cuota desc')
            #raise ValidationError(str(valor_sobrante)+'-kk-'+str(parte_decimal)+'----'+str(valor_a_restar))
            for c in obj_contrato:
                #raise ValidationError(str(valor_sobrante)+'-kk-'+str(parte_decimal)+'----'+str(valor_a_restar)+'==='+str(monto_finan_contrato)+'==0='+str(c.cuota_capital))
                valor_sobrante = valor_sobrante -valor_a_restar
                
                if valor_sobrante != 0.00 or valor_sobrante != 0:
                     c.update({
                        'cuota_capital': c.cuota_capital - valor_a_restar,
                        'contrato_id':self.contrato_id.id,
                    })
                
        if  monto_finan_contrato  < self.contrato_id.monto_financiamiento:
            valor_sobrante = self.contrato_id.monto_financiamiento  - monto_finan_contrato 
            
            parte_decimal, parte_entera = math.modf(valor_sobrante)
            #raise ValidationError(str(valor_sobrante)+'--'+str(parte_decimal)+'----'+str(monto_finan_contrato))
            valor_a_restar= (valor_sobrante/parte_decimal)*0.1
            
            obj_contrato=self.env['contrato.estado.cuenta'].search([('contrato_id','=',self.contrato_id.id),('estado_pago','=','pendiente')] , order ='numero_cuota desc')
            
            for c in obj_contrato:
                valor_sobrante = valor_sobrante -valor_a_restar
                if valor_sobrante != 0.00 or valor_sobrante != 0:
                    #raise ValidationError(str(valor_sobrante)+'--'+str(parte_decimal)+'----'+str(valor_a_restar))
                    c.update({
                        'cuota_capital': c.cuota_capital + valor_a_restar,
                        'contrato_id':self.contrato_id.id,
                    })                     
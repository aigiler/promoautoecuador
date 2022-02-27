# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError

import numpy_financial as npf
import math


class WizardActualizarRubro(models.Model):
    _name = 'wizard.actualizar.rubro'
    
    contrato_id = fields.Many2one('contrato')
    monto = fields.Float(string='Monto')
    mes = fields.Integer(string='Mes',default=1)
    anio = fields.Integer(string='Año',default=2022)
    diferido=fields.Integer(string='Numero de meses diferido',default=12)
    rubro = fields.Selection(selection=[
        ('rastreo', 'Rastreo'),
        ('seguro', 'Seguro'),
        ('otro', 'Otro')
    ], string='Rubro', default='rastreo', track_visibility='onchange')


    def actualizar_contrato(self,):
        if self.diferido==0:
            raise ValidationError('El número de meses a diferir debe ser mayor a 0')

        numero_cuota=self.diferido
        month=self.mes
        year=self.anio
        valor=self.monto/self.diferido

        self.funcion_modificar_contrato_por_rubro_seguro(valor,self.rubro,numero_cuota,month,year,self.diferido)



    def funcion_modificar_contrato_por_rubro_seguro(self,valor,variable,numero_cuota,month,year,diferido):


        month=month
        year=year


        obj_detalle=self.contrato_id.tabla_amortizacion.filtered(lambda l: l.fecha.year==year and l.fecha.month==month,limit=1)

        cuota_inicial=int(obj_detalle.numero_cuota)
        contador=0
        detalle_a_pagar=self.contrato_id.tabla_amortizacion.filtered(lambda l: int(l.numero_cuota)>=int(obj_detalle.numero_cuota))

        for range in (0,diferido):

            obj_detalle=self.contrato_id.tabla_amortizacion.filtered(lambda l: int(l.numero_cuota)==cuota_inicial)
            obj_detalle.write({variable:valor})
            cuota_inicial+=1
            










        vls=[]                                                

        monto_finan_contrato = sum(self.contrato_id.tabla_amortizacion.mapped(variable))
        monto_finan_contrato = round(monto_finan_contrato,2)
        #raise ValidationError(str(monto_finan_contrato))
        if  monto_finan_contrato  > self.monto:
            valor_sobrante = monto_finan_contrato - self.monto 
            valor_sobrante = round(valor_sobrante,2)
            parte_decimal, parte_entera = math.modf(valor_sobrante)
            if parte_decimal >=1:
                valor_a_restar= (valor_sobrante/parte_decimal)*0.1
            else:
                valor_a_restar= (valor_sobrante/parte_decimal)*0.01

            obj_contrato=self.env['contrato.estado.cuenta'].search([('contrato_id','=',self.contrato_id.id),('estado_pago','=','pendiente')] , order ='fecha desc')
            for c in obj_contrato:
                if valor_sobrante != 0.00 or valor_sobrante != 0 or valor_sobrante != 0.0:

                    c.update({
                        variable: c.cuota_capital - valor_a_restar,
                        'contrato_id':self.contrato_id.id,
                    })
                    vls.append(valor_sobrante)
                    valor_sobrante = valor_sobrante -valor_a_restar
                    valor_sobrante = round(valor_sobrante,2)
                            
                            
        if  monto_finan_contrato  < self.monto:
            valor_sobrante = self.monto  - monto_finan_contrato 
            valor_sobrante = round(valor_sobrante,2)
            parte_decimal, parte_entera = math.modf(valor_sobrante)
            if parte_decimal >=1:
                valor_a_restar= (valor_sobrante/parte_decimal)*0.1
            else:
                valor_a_restar= (valor_sobrante/parte_decimal)*0.01

            obj_contrato=self.env['contrato.estado.cuenta'].search([('contrato_id','=',self.contrato_id.id),('estado_pago','=','pendiente')] , order ='fecha desc')

            for c in obj_contrato:

                if valor_sobrante != 0.00 or valor_sobrante != 0 or valor_sobrante != 0.0:
                    #raise ValidationError(str(valor_sobrante)+'--'+str(parte_decimal)+'----'+str(valor_a_restar))
                    c.update({
                        'cuota_capital': c.cuota_capital + valor_a_restar,
                        'contrato_id':self.contrato_id.id,
                    })  
                    vls.append(valor_sobrante)
                    valor_sobrante = valor_sobrante -valor_a_restar
                    valor_sobrante = round(valor_sobrante,2)



# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError

import numpy_financial as npf


class WizardActualizarRubro(models.TransientModel):
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

        self.funcion_modificar_contrato_por_rubro_seguro(valor,self.rubro,numero_cuota,month,year)



    def funcion_modificar_contrato_por_rubro_seguro(self,valor,variable,numero_cuota,month,year):


        month=month
        year=year

        obj_detalle=self.tabla_amortizacion.filtered(lambda l: l.fecha.year==year and l.fecha.month==month)


        contador=0

        for l in self.tabla_amortizacion.filtered(lambda l: l.numero_cuota>=obj_detalle.numero_cuota):
            l.write({variable:valor})

            contador+=1
            if contador==numero_cuota:
                break



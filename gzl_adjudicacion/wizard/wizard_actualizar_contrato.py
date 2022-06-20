# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError
import numpy_financial as npf
import math


class WizardContratoAct(models.Model):
    _name = 'actualizacion.contrato.valores'
    _description = 'Modificar Contrato'


    contrato_id = fields.Many2one('contrato',string="Contrato")
    socio_id = fields.Many2one('res.partner',string="Socio")
    ejecutado = fields.Boolean(string="Ejecutado", default = False)
    monto_financiamiento = fields.Monetary(
        string='Monto Financiamiento', currency_field='currency_id', track_visibility='onchange')

    
    currency_id = fields.Many2one(
        'res.currency', readonly=True, default=lambda self: self.env.company.currency_id)
    ##valores anteriores
    monto_financiamiento_anterior = fields.Monetary(
        string='Monto Financiamiento', currency_field='currency_id', track_visibility='onchange')

    observacion = fields.Char(string='Observacion')
    def ejecutar_cambio(self,):

        #if   self.contrato_id.ejecutado:
        #    raise ValidationError("El contrato ya fue modificado")
        #else:
        monto_excedente=self.monto_financiamiento_anterior-self.monto_financiamiento
        obj=self.contrato_id
        monto_restado=0
        cuota_ultima=self.contrato_id.plazo_meses.numero
        #for x in self.contrato.tabla_amortizacion:
        while(monto_restado<monto_excedente):
            valor_cuota=self.contrato_id.tabla_amortizacion.filtered(lambda l: l.numero_cuota==cuota_ultima)  
            if valor_cuota.cuota_capital:
                if (monto_restado+x.cuota_capital)>monto_excedente:
                    valor_restado=monto_excedente-(monto_restado+valor_cuota.cuota_capital)
                    monto_restado+=(valor_cuota.cuota_capital-valor_restado)
                    valor_cuota.cuota_capital=valor_cuota.cuota_capital-valor_restado
                    valor_cuota.fecha_pagada=date.today()
                else:
                    monto_restado+=valor_cuota.cuota_capital
                    valor_cuota.cuota_capital=0
                    valor_cuota.cuota_adm=0
                    valor_cuota.iva_adm=0
                    valor_cuota.fecha_pagada=date.today()
                cuota_ultima=cuota_ultima-1

        self.ejecutado=True

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

    ##valores anteriores
    monto_financiamiento_anterior = fields.Monetary(
        string='Monto Financiamiento', currency_field='currency_id', track_visibility='onchange')

    observacion = fields.Char(string='Observacion')
    def ejecutar_cambio(self,):

        if   self.contrato_id.ejecutado:
            raise ValidationError("El contrato ya fue modificado")
        else:
            monto_excedente=self.monto_financiamiento_anterior-self.monto_financiamiento
            obj=self.contrato_id
            monto_restado=0
            cuota_ultima=self.contrato_id.plazo_meses.numero
            for x in self.contrato.tabla_amortizacion:
                if x.cuota_capital:
                    if monto_restado<monto_excedente:
                        if (monto_restado+x.cuota_capital)>monto_excedente:
                            valor_restado=monto_excedente-(monto_restado+x.cuota_capital)
                            monto_restado+=(x.cuota_capital-valor_restado)
                            x.cuota_capital=x.cuota_capital-valor_restado
                            x.fecha_pagada=date.today()
                        else:
                            monto_restado+=x.cuota_capital
                            x.cuota_capital=0
                            x.cuota_adm=0
                            x.iva_adm=0
                            x.fecha_pagada=date.today()
                    else:
                        pass
            self.ejecutado=True

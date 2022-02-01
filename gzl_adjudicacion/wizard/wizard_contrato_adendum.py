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

        pagos=self.contrato_id.detalle_tabla_amortizacion.filtered(lambda l: l.state=='pagado')
        pago_capital=sum(pagos.mapped("cuota_capital"))

        nuevoMontoReeestructura=monto_financiamiento-pago_capital


        cuotasPagadas=self.contrato_id.detalle_tabla_amortizacion.filtered(lambda l: l.state=='pagado' and l.adelanto==False)


        cuotasAdelantadas=self.contrato_id.detalle_tabla_amortizacion.filtered(lambda l: l.state=='pagado' and l.cuotaAdelantada==True)


        numeroCuotasPagadaTotal=len(cuotaAdelantada) + len(cuotasPagadas)


        diferenciaPlazoAdendum= abs(self.contrato_id.plazo_meses.numero - self.plazo_mesesplazo_meses.numero)

        numeroCuotasTotal=diferenciaPlazoAdendum
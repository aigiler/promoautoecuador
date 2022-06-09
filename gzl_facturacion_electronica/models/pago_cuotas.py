# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
import datetime
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
from dateutil.parser import parse
import calendar
from dateutil.relativedelta import relativedelta
import math

class ContratoEstadoCuenta(models.Model):
    _inherit = 'contrato.estado.cuenta'

    ids_pagos = fields.One2many(
        'account.payment.cuotas', 'cuotas_id', track_visibility='onchange')

class CuotasPagadas(models.Model):
    _name = 'account.payment.cuotas'
    _description = 'Pagos Asociados'


    cuotas_id = fields.Many2one('contrato.estado.cuenta',string="Estado Cuenta" ,track_visibility='onchange')
    pago_id = fields.Many2one('account.payment',string="Pago" ,track_visibility='onchange')
    monto_pagado = fields.Float(related='pago_id.amount',string="Total Pago" ,track_visibility='onchange')
    valor_asociado = fields.Float(related='pago_id.amount',string="Asignado a la cuota" ,track_visibility='onchange')

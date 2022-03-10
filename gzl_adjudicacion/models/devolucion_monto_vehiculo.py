# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, tools,  _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime,timedelta,date
import re


class DevolucionMonto(models.Model):   
    _name = 'devolucion.monto'   
    _inherit = 'entrega.vehiculo' 
  


    monto = fields.Float(string='Monto')
    contrato_id = fields.Many2one('contrato')
    fsolicitud  = fields.Date(string='Fecha de Solicitud')
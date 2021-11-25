# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, tools,  _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime,timedelta,date
import re


class Partner(models.Model):   
    _inherit = 'res.partner'    
  



    tipo=fields.Char(string='Tipo')
    monto = fields.Float(string='Monto')
    tipo_contrato = fields.Many2one("tipo.contrato.adjudicado", String="Tipo de Contrato")
    codigo_cliente = fields.Char(string='Código Cliente')
    fecha_nacimiento  = fields.Date(string='Fecha de nacimiento')
    estado_civil = fields.Char(string='Estado Civil')
    numero_cargas_familiares = fields.Char(string='Cargas Familiares')
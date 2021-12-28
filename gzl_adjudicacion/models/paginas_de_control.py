# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
import datetime
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
from dateutil.parser import parse


class PaginasRevision(models.Model):
    _name = 'paginas.de.control'
    _description = 'Revisión de paginas de control'
    _rec_name= 'nombre'
    
    nombre = fields.Char('Nombre',  required=True)
    descripcion=fields.Text('Descripcion',  required=True)
  
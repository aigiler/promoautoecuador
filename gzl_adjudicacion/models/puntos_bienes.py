# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
import datetime
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
from dateutil.parser import parse


class PuntosBienes(models.Model):
    _name = 'puntos.bienes'
    _description = 'Bienes'
    _rec_name= 'nombre'
    
    #items bienes
    nombre = fields.Char('Nombre',  required=True)
    valorPuntos = fields.Integer('Valor Puntos',  required=True)
    poseeBien = fields.Char()

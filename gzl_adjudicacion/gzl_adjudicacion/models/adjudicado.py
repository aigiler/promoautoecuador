# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, tools,  _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime,timedelta,date
import re


class Partner(models.Model):   
     
    _inherit = 'res.partner'    
  


    tipo=fields.Char(string='Tipo')



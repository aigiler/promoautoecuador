# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import *

class Comision(models.Model):
    _name = 'comision'

    cargo_id = fields.Many2one('hr.job',string="Cargo")
    valor_max = fields.Float('Máximo')
    valor_min = fields.Float('Mìnimo')

    comision = fields.Float('Comisión')
    bono = fields.Float('Bono')
    logica = fields.Selection(selection=[
        ('asesor', 'Borrador'),
        ('supervisor', 'Activo'),
        ('jefe', 'Inactivo'),
        ('gerente', 'Congelar Contrato'),

    ], string='Logica', default='asesor', track_visibility='onchange')
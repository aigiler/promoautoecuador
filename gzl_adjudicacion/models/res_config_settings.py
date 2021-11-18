# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = 'Ajustes de Adjudicaciones'

    tasa_administrativa = fields.Integer(string='Tasa Administrativa %', default=4)
    dia_corte = fields.Integer(string='Día de Corte', default=5)
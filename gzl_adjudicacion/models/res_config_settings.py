# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = 'Ajustes de Adjudicaciones'
    
    dia_corte = fields.Integer(string='Día de Corte', default=5)
    tasa_administrativa = fields.Float(string='Tasa Administrativa %', default=4)
    requisitosPoliticasCredito = fields.Text(string='Informacion Cobranzas')

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
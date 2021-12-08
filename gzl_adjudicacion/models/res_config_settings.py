# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = 'Ajustes de Adjudicaciones'
    
    dia_corte = fields.Integer(string='Día de Corte', default=5)
    tasa_administrativa = fields.Float(string='Tasa Administrativa %', default=4.00)
    requisitosPoliticasCredito = fields.Text(string='Informacion Cobranzas')


    @api.one
    def set_config_values(self):
        company = self.env.user.company_id
        company.dia_corte = self.dia_corte
        company.tasa_administrativa = self.tasa_administrativa




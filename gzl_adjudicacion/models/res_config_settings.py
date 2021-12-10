# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    dia_corte = fields.Integer(string='Día de Corte', default=5)
    tasa_administrativa = fields.Float(string='Tasa Administrativa %', default=4.00)
    requisitosPoliticasCredito = fields.Text(string='Informacion Cobranzas')






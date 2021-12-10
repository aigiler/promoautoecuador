# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    dia_corte = fields.Integer(string='Día de Corte', config_parameter="gzl_adjudicacion.dia_corte")
    tasa_administrativa = fields.Float(string='Tasa Administrativa %' , config_parameter="gzl_adjudicacion.tasa_administrativa")
    configuracion_adicional=fields.Many2one('configuracion.adicional.template',string="Configuracion Adicional",default=lambda self:self.env.ref('gzl_adjudicacion.configuracion_adicional1'))






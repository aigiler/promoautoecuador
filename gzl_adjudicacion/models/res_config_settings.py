# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = 'Ajustes de Adjudicaciones'
    
    dia_corte = fields.Integer(string='Día de Corte', default=5)
    tasa_administrativa = fields.Float(string='Tasa Administrativa %', default=4.00)
    requisitosPoliticasCredito = fields.Text(string='Informacion Cobranzas')


    @api.onchange('dia_corte')
    def _onchange_dia_corte(self):
        if not self.dia_corte:
            self.dia_corte = 0.0

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            dia_corte=self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.dia_corte')
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('gzl_adjudicacion.dia_corte', self.dia_corte)





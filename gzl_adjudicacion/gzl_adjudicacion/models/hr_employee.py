# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrEmployee(models.Model):
    
    _inherit = 'hr.employee'

    asamblea_id = fields.Many2one('asamblea', string='Asamblea')
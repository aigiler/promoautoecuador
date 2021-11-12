# -*- coding: utf-8 -*-
from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    signature = fields.Image(string='Firma', copy=False, attachment=True, max_width=624, max_height=354)


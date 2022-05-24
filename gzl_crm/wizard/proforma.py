# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class Proforma(models.TransientModel):
    _name = 'proforma'
    _description = 'Proforma de cuota exacta'

    monto_fijo = fields.Monetary(string='Monto Fijo')
    porcentaje_ce = fields.Float(string='Porcentaje de C.E')


    def print_proforma(self):
        return self.env.ref('glz_crm.report_proforma').report_action(self)
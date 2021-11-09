# -*- coding: utf-8 -*-

from odoo import api, fields, models

class CrmLead(models.Model):
    
    _inherit = 'crm.lead'

    @api.constrains('stage_id')
    def crear_adjudicado(self):
        if self.stage_id.is_won:
            self.env['res.partner'].create({
                                        'tipo':'adjudicado',
                                    
            })
# -*- coding: utf-8 -*-

from odoo import api, fields, models

class CrmLead(models.Model):
    
    _inherit = 'crm.lead'


    def crear_adjudicado(self):
        if self.stage_id.is_won:
            monto=0
            for l in self.quotation_count:
                monto=+l.amount_total
            self.env['res.partner'].create({
                                        'tipo':'adjudicado',
                                        'monto':monto,
                                        'function':self.partner_id.function or '',
                                        'email':self.partner_id.email or '',
                                        'phone':self.partner_id.phone or '',
                                        'mobile':self.partner_id.mobile or '',
            })
            
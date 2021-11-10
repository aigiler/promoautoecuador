# -*- coding: utf-8 -*-

from odoo import api, fields, models

class CrmLead(models.Model):
    
    _inherit = 'crm.lead'

    is_won = fields.Boolean(related='stage_id.is_won')
    
    def crear_adjudicado(self):
        if self.stage_id.is_won:
            monto=0
            for l in self.order_ids:
                if l.state=='draft':
                    monto+=l.amount_total
            self.env['res.partner'].create({
                                        'name':self.partner_id.name,
                                        'type':'contact',
                                        'tipo':'adjudicado',
                                        'monto':monto,
                                        'function':self.partner_id.function or None,
                                        'email':self.partner_id.email or None,
                                        'phone':self.partner_id.phone or None,
                                        'mobile':self.partner_id.mobile or None,
            })
            
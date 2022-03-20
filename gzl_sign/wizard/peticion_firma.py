# -*- coding: utf-8 -*-
from odoo import fields, models

class SignSendRequest(models.TransientModel):
    _inherit = 'sign.send.request'

    contrato = fields.Many2one('contrato', string='Contrato')
    grupo = fields.Many2one('grupo.adjudicado', string='Grupo')

    def sign_directly_without_mail(self):
        self.sign_directly_without_mail()
        self.env.cr.execute("""update res_partner set contrato={0},grupo={1} where id={2} """.format(self.contrato.id,self.grupo.id,self.signer_ids.partner_id.id))
        self.env.cr.commit()
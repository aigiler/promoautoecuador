# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError


class Team(models.Model):
    _inherit = 'crm.team'
    _description = 'Sales Team'


    correos = fields.Char( string='Correos' )
    member_ids = fields.Many2many('res.users', string='Miembros del Equipo' )

    @api.onchange("member_ids")
    def actualizar_correos_team(self,):
        correos=self.member_ids.mapped('email')
        correo=""
        for correo in correos:
            correos=correos+corr


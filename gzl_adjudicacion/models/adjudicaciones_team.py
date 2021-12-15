# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError


class AdjudicacionTeam(models.Model):
    _name = 'adjudicaciones.team'
    _inherit = ['mail.alias.mixin', 'crm.team']
    _description = 'Roles'



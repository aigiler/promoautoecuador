# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError


class Team(models.Model):
    _name = 'Roles'
    _inherit = ['mail.alias.mixin', 'crm.team']
    _description = 'Sales Team'

    use_leads = fields.Boolean('Leads', help="Check this box to filter and qualify incoming requests as leads before converting them into opportunities and assigning them to a salesperson.")
    use_opportunities = fields.Boolean('Pipeline', default=True, help="Check this box to manage a presales process with opportunities.")
    alias_id = fields.Many2one('mail.alias', string='Alias', ondelete="restrict", required=True, help="The email address associated with this channel. New emails received will automatically create new leads assigned to the channel.")

    unassigned_leads_count = fields.Integer(
        compute='_compute_unassigned_leads_count',
        string='Unassigned Leads')
    opportunities_count = fields.Integer(
        compute='_compute_opportunities',
        string='Number of open opportunities')
    overdue_opportunities_count = fields.Integer(
        compute='_compute_overdue_opportunities',
        string='Number of overdue opportunities')
    opportunities_amount = fields.Integer(
        compute='_compute_opportunities',
        string='Opportunities Revenues')
    overdue_opportunities_amount = fields.Integer(
        compute='_compute_overdue_opportunities',
        string='Overdue Opportunities Revenues')

    # Since we are in a _inherits case, this is not an override
    # but a plain definition of a field
    # So we need to reset the property related of that field
    alias_user_id = fields.Many2one('res.users', related='alias_id.alias_user_id', inherited=True, domain=lambda self: [
        ('groups_id', 'in', self.env.ref('sales_team.group_sale_salesman_all_leads').id)])


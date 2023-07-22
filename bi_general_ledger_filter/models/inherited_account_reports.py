# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _

class AccountReports(models.AbstractModel):
    _inherit = 'account.report'


    filter_custom_account = None
    filter_custom_account_type = None

    @api.model
    def _init_filter_custom_account(self, options, previous_options=None):
        if not self.filter_custom_account:
            return

        options['custom_account'] = True
        options['custom_account_ids'] = previous_options and previous_options.get('custom_account_ids') or []
        selected_custom_account_ids = [int(account) for account in options['custom_account_ids']]
        selected_custom_accountes = selected_custom_account_ids and self.env['account.account'].browse(selected_custom_account_ids) or self.env['account.account']
        options['selected_custom_account_ids'] = selected_custom_accountes.mapped('name')


    @api.model
    def _init_filter_custom_account_type(self, options, previous_options=None):
        if not self.filter_custom_account_type:
            return

        options['custom_account_type'] = True
        options['custom_account_type_ids'] = previous_options and previous_options.get('custom_account_type_ids') or []
        selected_custom_account_type_ids = [int(account_type) for account_type in options['custom_account_type_ids']]
        selected_custom_account_typees = selected_custom_account_type_ids and self.env['account.account.type'].browse(selected_custom_account_type_ids) or self.env['account.account.type']
        options['selected_custom_account_type_ids'] = selected_custom_account_typees.mapped('name')


    @api.model
    def _get_options(self, previous_options=None):
        # Create default options.
        options = {
            'unfolded_lines': previous_options and previous_options.get('unfolded_lines') or [],
        }

        # Multi-company is there for security purpose and can't be disabled by a filter.
        self._init_filter_multi_company(options, previous_options=previous_options)

        # Call _init_filter_date/_init_filter_comparison because the second one must be called after the first one.
        if self.filter_date:
            self._init_filter_date(options, previous_options=previous_options)
        if self.filter_comparison:
            self._init_filter_comparison(options, previous_options=previous_options)

        # if self.filter_branch:
        #     self._init_filter_branch(options, previous_options=previous_options)

        filter_list = [attr for attr in dir(self)
                       if (attr.startswith('filter_') or attr.startswith('order_')) and attr not in ('filter_date', 'filter_comparison') and len(attr) > 7 and not callable(getattr(self, attr))]
        for filter_key in filter_list:
            options_key = filter_key[7:]
            init_func = getattr(self, '_init_%s' % filter_key, None)
            if init_func:
                init_func(options, previous_options=previous_options)
            else:
                filter_opt = getattr(self, filter_key, None)
                if filter_opt is not None:
                    if previous_options and options_key in previous_options:
                        options[options_key] = previous_options[options_key]
                    else:
                        options[filter_key[7:]] = filter_opt                
        return options


    def _set_context(self, options):
        ctx = self.env.context.copy()
        if options.get('date') and options['date'].get('date_from'):
            ctx['date_from'] = options['date']['date_from']
        if options.get('date'):
            ctx['date_to'] = options['date'].get('date_to') or options['date'].get('date')
        if options.get('all_entries') is not None:
            ctx['state'] = options.get('all_entries') and 'all' or 'posted'
        if options.get('journals'):
            ctx['journal_ids'] = [j.get('id') for j in options.get('journals') if j.get('selected')]
        company_ids = []
        if options.get('multi_company'):
            company_ids = [c.get('id') for c in options['multi_company'] if c.get('selected')]
            company_ids = company_ids if len(company_ids) > 0 else [c.get('id') for c in options['multi_company']]
        ctx['company_ids'] = len(company_ids) > 0 and company_ids or [self.env.company.id]

        if options.get('analytic_accounts'):
            ctx['analytic_account_ids'] = self.env['account.analytic.account'].browse([int(acc) for acc in options['analytic_accounts']])

        if options.get('analytic_tags'):
            ctx['analytic_tag_ids'] = self.env['account.analytic.tag'].browse([int(t) for t in options['analytic_tags']])

        if options.get('partner_ids'):
            ctx['partner_ids'] = self.env['res.partner'].browse([int(partner) for partner in options['partner_ids']])

        if options.get('custom_account_ids'):
            ctx['custom_account_ids'] = self.env['account.account'].browse([int(custom_account) for custom_account in options['custom_account_ids']])

        if options.get('custom_account_type_ids'):
            ctx['custom_account_type_ids'] = self.env['account.account.type'].browse([int(custom_account_type) for custom_account_type in options['custom_account_type_ids']])

        if options.get('partner_categories'):
            ctx['partner_categories'] = self.env['res.partner.category'].browse([int(category) for category in options['partner_categories']])
        return ctx

    def get_report_informations(self, options):
        '''
        return a dictionary of informations that will be needed by the js widget, manager_id, footnotes, html of report and searchview, ...
        '''
        options = self._get_options(options)

        searchview_dict = {'options': options, 'context': self.env.context}

        if options.get('analytic_accounts') is not None:
            options['selected_analytic_account_names'] = [self.env['account.analytic.account'].browse(int(account)).name for account in options['analytic_accounts']]

        if options.get('analytic_tags') is not None:
            options['selected_analytic_tag_names'] = [self.env['account.analytic.tag'].browse(int(tag)).name for tag in options['analytic_tags']]

        if options.get('partner'):
            options['selected_partner_ids'] = [self.env['res.partner'].browse(int(partner)).name for partner in options['partner_ids']]
            options['selected_partner_categories'] = [self.env['res.partner.category'].browse(int(category)).name for category in options['partner_categories']]

        if options.get('custom_account_type'):
            options['selected_custom_account_type_ids'] = [self.env['account.account.type'].browse(int(account_type)).name for account_type in options['custom_account_type_ids']]

        if options.get('custom_account'):
            options['selected_custom_account_ids'] = [self.env['account.account'].browse(int(account)).name for account in options['custom_account_ids']]


        # Check whether there are unposted entries for the selected period or not (if the report allows it)
        if options.get('date') and options.get('all_entries') is not None:
            date_to = options['date'].get('date_to') or options['date'].get('date') or fields.Date.today()
            period_domain = [('state', '=', 'draft'), ('date', '<=', date_to)]
            options['unposted_in_period'] = bool(self.env['account.move'].search_count(period_domain))

        if options.get('journals'):
            journals_selected = set(journal['id'] for journal in options['journals'] if journal.get('selected'))
            for journal_group in self.env['account.journal.group'].search([('company_id', '=', self.env.company.id)]):
                if journals_selected and journals_selected == set(self._get_filter_journals().ids) - set(journal_group.excluded_journal_ids.ids):
                    options['name_journal_group'] = journal_group.name
                    break

        report_manager = self._get_report_manager(options)
        if self._context.get('model') == 'bi.account.general.ledger':
            options.update({'flag':True})
        info = {'options': options,
                'context': self.env.context,
                'report_manager_id': report_manager.id,
                'footnotes': [{'id': f.id, 'line': f.line, 'text': f.text} for f in report_manager.footnotes_ids],
                'buttons': self._get_reports_buttons_in_sequence(),
                'main_html': self.get_html(options),
                'searchview_html': self.env['ir.ui.view'].render_template(self._get_templates().get('search_template', 'account_report.search_template'), values=searchview_dict),
                }
        return info
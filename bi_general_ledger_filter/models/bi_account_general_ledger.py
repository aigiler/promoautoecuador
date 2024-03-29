# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
##################################################################################

from datetime import datetime, timedelta,date

from odoo import models, api, fields, _
from odoo.tools import float_is_zero
from odoo.tools.misc import format_date

from odoo.exceptions import AccessError, UserError, ValidationError

import calendar

from .funciones import *



class report_account_general_ledger_bi(models.AbstractModel):
    _name = "bi.account.general.ledger"
    _description = "Detailed General Ledger"
    _inherit = "account.report"

    filter_date = {'date_from': '', 'date_to': '', 'filter': 'this_month'}
    filter_cash_basis = False
    filter_all_entries = False
    filter_journals = True
    filter_analytic = True
    filter_unfold_all = False
    filter_custom_account = True
    filter_custom_account_type = True

    def _get_templates(self):
        templates = super(report_account_general_ledger_bi, self)._get_templates()
        # templates['main_template'] = 'account_reports.template_general_ledger_report'
        templates['line_template'] = 'account_reports.line_template_general_ledger_report'
        return templates

    def _get_columns_name(self, options):
        return [
            {'name':''},
            {'name': _("Date"), 'class': 'date'},
            {'name': _("Display Name")},
            {'name': _("Communication")},
            {'name': _("Partner")},
            {'name': _("Currency"), 'class': 'number'},
            {'name': _("Debit"), 'class': 'number'},
            {'name': _("Credit"), 'class': 'number'},
            {'name': _("Balance"), 'class': 'number'}]

    @api.model
    def _get_report_name(self):
        return _("Detailed General Ledger")

    def _get_with_statement(self, user_types, domain=None):
        """ This function allow to define a WITH statement as prologue to the usual queries returned by query_get().
            It is useful if you need to shadow a table entirely and let the query_get work normally although you're
            fetching rows from your temporary table (built in the WITH statement) instead of the regular tables.

            @returns: the WITH statement to prepend to the sql query and the parameters used in that WITH statement
            @rtype: tuple(char, list)
        """
        sql = ''
        params = []

        #Cash basis option
        #-----------------
        #In cash basis, we need to show amount on income/expense accounts, but only when they're paid AND under the payment date in the reporting, so
        #we have to make a complex query to join aml from the invoice (for the account), aml from the payments (for the date) and partial reconciliation
        #(for the reconciled amount).
        if self.env.context.get('cash_basis'):
            if not user_types:
                return sql, params
            #we use query_get() to filter out unrelevant journal items to have a shadowed table as small as possible
            tables, where_clause, where_params = self.env['account.move.line']._query_get(domain=domain)
            sql = """WITH account_move_line AS (
              SELECT \"account_move_line\".id, \"account_move_line\".date, \"account_move_line\".name, \"account_move_line\".debit_cash_basis, \"account_move_line\".credit_cash_basis, \"account_move_line\".move_id, \"account_move_line\".account_id, \"account_move_line\".journal_id, \"account_move_line\".balance_cash_basis, \"account_move_line\".amount_residual, \"account_move_line\".partner_id, \"account_move_line\".reconciled, \"account_move_line\".company_id, \"account_move_line\".company_currency_id, \"account_move_line\".amount_currency, \"account_move_line\".balance, \"account_move_line\".user_type_id, \"account_move_line\".analytic_account_id
               FROM """ + tables + """
               WHERE (\"account_move_line\".journal_id IN (SELECT id FROM account_journal WHERE type in ('cash', 'bank'))
                 OR \"account_move_line\".move_id NOT IN (SELECT DISTINCT move_id FROM account_move_line WHERE user_type_id IN %s))
                 AND """ + where_clause + """
              UNION ALL
              (
               WITH payment_table AS (
                 SELECT aml.move_id, \"account_move_line\".date,
                        CASE WHEN (aml.balance = 0 OR sub_aml.total_per_account = 0)
                            THEN 0
                            ELSE part.amount / ABS(sub_aml.total_per_account)
                        END as matched_percentage
                   FROM account_partial_reconcile part
                   LEFT JOIN account_move_line aml ON aml.id = part.debit_move_id
                   LEFT JOIN (SELECT move_id, account_id, ABS(SUM(balance)) AS total_per_account
                                FROM account_move_line
                                GROUP BY move_id, account_id) sub_aml
                            ON (aml.account_id = sub_aml.account_id AND sub_aml.move_id=aml.move_id)
                   LEFT JOIN account_move am ON aml.move_id = am.id,""" + tables + """
                   WHERE part.credit_move_id = "account_move_line".id
                    AND "account_move_line".user_type_id IN %s
                    AND """ + where_clause + """
                 UNION ALL
                 SELECT aml.move_id, \"account_move_line\".date,
                        CASE WHEN (aml.balance = 0 OR sub_aml.total_per_account = 0)
                            THEN 0
                            ELSE part.amount / ABS(sub_aml.total_per_account)
                        END as matched_percentage
                   FROM account_partial_reconcile part
                   LEFT JOIN account_move_line aml ON aml.id = part.credit_move_id
                   LEFT JOIN (SELECT move_id, account_id, ABS(SUM(balance)) AS total_per_account
                                FROM account_move_line
                                GROUP BY move_id, account_id) sub_aml
                            ON (aml.account_id = sub_aml.account_id AND sub_aml.move_id=aml.move_id)
                   LEFT JOIN account_move am ON aml.move_id = am.id,""" + tables + """
                   WHERE part.debit_move_id = "account_move_line".id
                    AND "account_move_line".user_type_id IN %s
                    AND """ + where_clause + """
               )
               SELECT aml.id, ref.date, aml.name,
                 CASE WHEN aml.debit > 0 THEN ref.matched_percentage * aml.debit ELSE 0 END AS debit_cash_basis,
                 CASE WHEN aml.credit > 0 THEN ref.matched_percentage * aml.credit ELSE 0 END AS credit_cash_basis,
                 aml.move_id, aml.account_id, aml.journal_id,
                 ref.matched_percentage * aml.balance AS balance_cash_basis,
                 aml.amount_residual, aml.partner_id, aml.reconciled, aml.company_id, aml.company_currency_id, aml.amount_currency, aml.balance, aml.user_type_id, aml.analytic_account_id
                FROM account_move_line aml
                RIGHT JOIN payment_table ref ON aml.move_id = ref.move_id
                WHERE journal_id NOT IN (SELECT id FROM account_journal WHERE type in ('cash', 'bank'))
                  AND aml.move_id IN (SELECT DISTINCT move_id FROM account_move_line WHERE user_type_id IN %s)
              )
            ) """
            params = [tuple(user_types.ids)] + where_params + [tuple(user_types.ids)] + where_params + [tuple(user_types.ids)] + where_params + [tuple(user_types.ids)]
        return sql, params

    def _do_query_unaffected_earnings(self, options, line_id, company=None):
        ''' Compute the sum of ending balances for all accounts that are of a type that does not bring forward the balance in new fiscal years.
            This is needed to balance the trial balance and the general ledger reports (to have total credit = total debit)
        '''

        select = '''
        SELECT COALESCE(SUM("account_move_line".balance), 0),
               COALESCE(SUM("account_move_line".amount_currency), 0),
               COALESCE(SUM("account_move_line".debit), 0),
               COALESCE(SUM("account_move_line".credit), 0)'''
        if options.get('cash_basis'):
            select = select.replace('debit', 'debit_cash_basis').replace('credit', 'credit_cash_basis')
        select += " FROM %s WHERE %s"
        user_types = self.env['account.account.type'].search([('type', 'in', ('receivable', 'payable'))])
        with_sql, with_params = self._get_with_statement(user_types, domain=[('account_id.user_type_id.include_initial_balance', '=', False)])
        aml_domain = [('account_id.user_type_id.include_initial_balance', '=', False)]
        if company:
            aml_domain += [('company_id', '=', company.id)]
        tables, where_clause, where_params = self.env['account.move.line']._query_get(domain=aml_domain)
        query = select % (tables, where_clause)
        self.env.cr.execute(with_sql + query, with_params + where_params)
        res = self.env.cr.fetchone()
        date = self._context.get('date_to') or fields.Date.today()
        currency_convert = lambda x: company and company.currency_id._convert(x, self.env.user.company_id.currency_id, company, date) or x
        return {'balance': currency_convert(res[0]), 'amount_currency': res[1], 'debit': currency_convert(res[2]), 'credit': currency_convert(res[3])}

    def _do_query(self, options, line_id, group_by_account=True, limit=False):
        if group_by_account:
            select = "SELECT \"account_move_line\".account_id"
            select += ',COALESCE(SUM(\"account_move_line\".debit-\"account_move_line\".credit), 0),SUM(\"account_move_line\".amount_currency),SUM(\"account_move_line\".debit),SUM(\"account_move_line\".credit)'
            if options.get('cash_basis'):
                select = select.replace('debit', 'debit_cash_basis').replace('credit', 'credit_cash_basis')
        else:
            select = "SELECT \"account_move_line\".id"
        sql = "%s FROM %s WHERE %s%s"
        if group_by_account:
            sql +=  "GROUP BY \"account_move_line\".account_id"
        else:
            sql += " GROUP BY \"account_move_line\".id"
            sql += " ORDER BY MAX(\"account_move_line\".date),\"account_move_line\".id"
            if limit and isinstance(limit, int):
                sql += " LIMIT " + str(limit)
        user_types = self.env['account.account.type'].search([('type', 'in', ('receivable', 'payable'))])
        with_sql, with_params = self._get_with_statement(user_types)
        tables, where_clause, where_params = self.env['account.move.line']._query_get()
        custom_accounts = []
        custom_accounts_type = []
        print(options.get('custom_account_type_ids'),'============================options \n\n')
        if options.get('custom_account_ids'):
            custom_accounts = [int(a) for a in options.get('custom_account_ids')]
        if options.get('custom_account_type_ids'):
                user_type_id = [int(a) for a in options.get('custom_account_type_ids')]
                acc_ids = self.env['account.account'].search([('user_type_id','in',user_type_id)])
                custom_accounts_type = [a.id for a in acc_ids]
        final_list = list(set(custom_accounts + custom_accounts_type))
        if not final_list:
            line_clause = line_id and ' AND \"account_move_line\".account_id = ' + str(line_id) or ''
        if final_list:
            line_clause = 'and "account_move_line"."account_id" in ('
            for a in range(len(final_list)):
                line_clause += '%s,'
            line_clause = line_clause[:-1]
            line_clause += ')'
            for a in final_list:
                where_params.append(int(a))
        query = sql % (select, tables, where_clause, line_clause)
        self.env.cr.execute(with_sql + query, with_params + where_params)
        results = self.env.cr.fetchall()
        return results

    def _do_query_group_by_account(self, options, line_id):
        results = self._do_query(options, line_id, group_by_account=True, limit=False)
        used_currency = self.env.user.company_id.currency_id
        company = self.env['res.company'].browse(self._context.get('company_id')) or self.env.user.company_id
        date = datetime.strptime(options['date']['date_to'],'%Y-%m-%d') or fields.Date.today()
        def build_converter(currency):
            def convert(amount):
                return currency._convert(amount, used_currency, company, date)
            return convert

        compute_table = {
            a.id: build_converter(a.company_id.currency_id)
            for a in self.env['account.account'].browse([k[0] for k in results])
        }
        results = dict([(
            k[0], {
                'balance': compute_table[k[0]](k[1]) if k[0] in compute_table else k[1],
                'amount_currency': k[2],
                'debit': compute_table[k[0]](k[3]) if k[0] in compute_table else k[3],
                'credit': compute_table[k[0]](k[4]) if k[0] in compute_table else k[4],
            }
        ) for k in results])
        return results

    def _group_by_account_id(self, options, line_id):
        accounts = {}
        results = self._do_query_group_by_account(options, line_id)
        initial_bal_date_to = fields.Date.from_string(datetime.strptime(options['date']['date_from'],'%Y-%m-%d') + timedelta(days=-1))
        initial_bal_results = self._do_query_group_by_account(options, line_id)

        context = self.env.context
        
      #  raise ValidationError(str(options['date']['date_from']))

        last_day_previous_fy = datetime.strptime(options['date']['date_from'],'%Y-%m-%d')   + timedelta(days=-1)
        unaffected_earnings_per_company = {}
        for cid in context.get('company_ids', []):
            company = self.env['res.company'].browse(cid)
            unaffected_earnings_per_company[company] = self.with_context(date_to=last_day_previous_fy.strftime('%Y-%m-%d'), date_from=False)._do_query_unaffected_earnings(options, line_id, company)

        unaff_earnings_treated_companies = set()
        unaffected_earnings_type = self.env.ref('account.data_unaffected_earnings')
        for account_id, result in results.items():
            account = self.env['account.account'].browse(account_id)
            accounts[account] = result
            accounts[account]['initial_bal'] = initial_bal_results.get(account.id, {'balance': 0, 'amount_currency': 0, 'debit': 0, 'credit': 0})
            if account.user_type_id == unaffected_earnings_type and account.company_id not in unaff_earnings_treated_companies:
                #add the benefit/loss of previous fiscal year to unaffected earnings accounts
                unaffected_earnings_results = unaffected_earnings_per_company[account.company_id]
                for field in ['balance', 'debit', 'credit']:
                    accounts[account]['initial_bal'][field] += unaffected_earnings_results[field]
                    accounts[account][field] += unaffected_earnings_results[field]
                unaff_earnings_treated_companies.add(account.company_id)
            #use query_get + with statement instead of a search in order to work in cash basis too
            aml_ctx = {}
            if  options['date']['date_from']:
                if options.get('groupByMonth',False):
                    aml_ctx = {
                        'strict_range': True,
                        'date_from':  options['date']['date_from'],
                        'date_to':options['date']['date_to'] if options['groupByMonth'] else self.env.context['date_to']
                    }
                else:
                    aml_ctx = {
                        'strict_range': True,
                        'date_from':  options['date']['date_from'],
                    }
            aml_ids = self.with_context(**aml_ctx)._do_query(options, account_id, group_by_account=False)
            aml_ids = [x[0] for x in aml_ids]

            accounts[account]['total_lines'] = len(aml_ids)
            offset = int(options.get('lines_offset', 0))
            if self.MAX_LINES:
                stop = offset + self.MAX_LINES
            else:
                stop = None
            aml_ids = aml_ids[offset:stop]

            accounts[account]['lines'] = self.env['account.move.line'].browse(aml_ids)

        # For each company, if the unaffected earnings account wasn't in the selection yet: add it manually
        user_currency = self.env.user.company_id.currency_id
        for cid in context.get('company_ids', []):
            company = self.env['res.company'].browse(cid)
            if company not in unaff_earnings_treated_companies and not float_is_zero(unaffected_earnings_per_company[company]['balance'], precision_digits=user_currency.decimal_places):
                unaffected_earnings_account = self.env['account.account'].search([
                    ('user_type_id', '=', unaffected_earnings_type.id), ('company_id', '=', company.id)
                ], limit=1)
                if unaffected_earnings_account and (not line_id or unaffected_earnings_account.id == line_id):
                    accounts[unaffected_earnings_account[0]] = unaffected_earnings_per_company[company]
                    accounts[unaffected_earnings_account[0]]['initial_bal'] = unaffected_earnings_per_company[company]
                    accounts[unaffected_earnings_account[0]]['lines'] = []
        return accounts

    def _get_taxes(self, journal):
        tables, where_clause, where_params = self.env['account.move.line']._query_get()
        query = """
            SELECT rel.account_tax_id, SUM("account_move_line".balance) AS base_amount
            FROM account_move_line_account_tax_rel rel, """ + tables + """
            WHERE "account_move_line".id = rel.account_move_line_id
                AND """ + where_clause + """
           GROUP BY rel.account_tax_id"""
        self.env.cr.execute(query, where_params)
        ids = []
        base_amounts = {}
        for row in self.env.cr.fetchall():
            ids.append(row[0])
            base_amounts[row[0]] = row[1]

        res = {}
        for tax in self.env['account.tax'].browse(ids):
            self.env.cr.execute('SELECT sum(debit - credit) FROM ' + tables + ' '
                ' WHERE ' + where_clause + ' AND tax_line_id = %s', where_params + [tax.id])
            res[tax] = {
                'base_amount': base_amounts[tax.id],
                'tax_amount': self.env.cr.fetchone()[0] or 0.0,
            }
            if journal.get('type') == 'sale':
                #sales operation are credits
                res[tax]['base_amount'] = res[tax]['base_amount'] * -1
                res[tax]['tax_amount'] = res[tax]['tax_amount'] * -1
        return res











    @api.model
    def _get_lines(self, options, line_id=None):
        offset = int(options.get('lines_offset', 0))
        remaining = int(options.get('lines_remaining', 0))
        balance_progress = float(options.get('lines_progress', 0))
        group = int(options.get('groupByMonth', False))

        if offset > 0:
            # Case a line is expanded using the load more.
            return self._load_more_lines(options, line_id, offset, remaining, balance_progress)
        else:
            # Case the whole report is loaded or a line is expanded for the first time.
            if not group:
                return self._get_general_ledger_lines(options, line_id=line_id)
            else:

                fechaDesde=datetime.strptime(options['date']['date_from'], '%Y-%m-%d')
                fechaHasta=datetime.strptime(options['date']['date_to'], '%Y-%m-%d')
                optionsEditado=options.copy()
                listaMesesEntreFecha=self.obtenerListaMesesEntreFecha(fechaDesde,fechaHasta)
                lines=[]
                
              #  raise ValidationError(str(listaMesesEntreFecha))
                for mes in listaMesesEntreFecha:
                    optionsEditado['date']['date_from']=mes['fechaDesde']
                    optionsEditado['date']['date_to']=mes['fechaHasta']

                    lines=lines+self._get_general_ledger_lines(optionsEditado, line_id=line_id)

                return lines



    @api.model
    def obtenerListaMesesEntreFecha(self,fechaDesde, fechaHasta):
        date_from_formulario=fechaDesde
        date_to_formulario=fechaHasta

        date_from=date(date_from_formulario.year, date_from_formulario.month, 1)
        date_to=date(date_to_formulario.year, date_to_formulario.month,(calendar.monthrange(date_to_formulario.year, date_to_formulario.month)[1]))

        start_date = datetime(date_from.year, date_from.month, date_from.day)

        end_date = datetime(date_to.year, date_to.month, date_to.day)
        num_months = [i-12 if i>12 else i for i in range(start_date.month, monthdelta(start_date, end_date)+start_date.month+1)]


        monthly_daterange = [datetime(start_date.year,i, start_date.day) for i in num_months]

        lista_mes=[]
        dct_nombre_mes={
            1:'Enero',
            2:'Febrero',
            3:'Marzo',
            4:'Abril',
            5:'Mayo',
            6:'Junio',
            7:'Julio',
            8:'Agosto',
            9:'Septiembre',
            10:'Octubre',
            11:'Noviembre',
            12:'Diciembre',



        }
        cont=0
        for mes in monthly_daterange:
            dct_mes={}


            dct_mes['nombre']=dct_nombre_mes[mes.month]
 
 
            fecha_actual="%s-%s-01" % (mes.year, str(mes.month).zfill(2))
            fecha_fin="%s-%s-%s" %(mes.year, str(mes.month).zfill(2),str((calendar.monthrange(mes.year, mes.month)[1])).zfill(2))


            dct_mes['fechaDesde']=fecha_actual
            dct_mes['fechaHasta']=fecha_fin
            dct_mes['anio']=str(mes.year)
            if cont==0 and date_from_formulario.day!=1:
                dct_mes['fechaDesde']="%s-%s-%s" %(date_from_formulario.year, date_from_formulario.month,date_from_formulario.day)
            if cont==(len(monthly_daterange)-1) and (date_to_formulario.day not in [30,31]):
                dct_mes['fechaHasta']="%s-%s-%s" %(mes.year, mes.month,date_to_formulario.day)

            cont+=1

            lista_mes.append(dct_mes)
        lista_descendente = sorted(lista_mes, key=lambda k: k['fechaHasta'],reverse=True) 
        return lista_descendente







    @api.model
    def _get_general_ledger_lines(self, options, line_id=None):

        offset = int(options.get('lines_offset', 0))
        lines = []
        context = self.env.context
        company_id = self.env.user.company_id
        used_currency = company_id.currency_id
        dt_from = options['date'].get('date_from')
        line_id = line_id and int(line_id.split('_')[1]) or None
        aml_lines = []
        # Aml go back to the beginning of the user chosen range but the amount on the account line should go back to either the beginning of the fy or the beginning of times depending on the account
      #  raise ValidationError(str(context))

        
        
        grouped_accounts = self._group_by_account_id(options, line_id)
        sorted_accounts = sorted(grouped_accounts, key=lambda a: a.code)
        unfold_all = context.get('print_mode') and len(options.get('unfolded_lines')) == 0
        sum_debit = sum_credit = sum_balance = 0
        
        
       # raise ValidationError(str(sorted_accounts))
        for account in sorted_accounts:
            display_name = account.code + " " + account.name
            if options.get('filter_accounts'):
                #skip all accounts where both the code and the name don't start with the given filtering string
                if not any([display_name_part.startswith(options.get('filter_accounts')) for display_name_part in display_name.split(' ')]):
                    continue
            debit = grouped_accounts[account]['debit']
            credit = grouped_accounts[account]['credit']
            balance = grouped_accounts[account]['balance']
            sum_debit += debit
            sum_credit += credit
            sum_balance += balance
            amount_currency = '' if not account.currency_id else self.with_context(no_format=False).format_value(grouped_accounts[account]['amount_currency'], currency=account.currency_id)
            # don't add header for `load more`
            if offset == 0:
                lines.append({
                    'id': 'account_%s' % (account.id,),
                    'name': display_name,
                    'columns':[{'name' : ''}] + [{'name': v} for v in [amount_currency, self.format_value(debit), self.format_value(credit), self.format_value(balance)]],
                    'level': 2,
                    'unfoldable': True,
                    'unfolded': 'account_%s' % (account.id,) in options.get('unfolded_lines') or unfold_all,
                    'colspan': 4,
                })

            unfold_all =True
            if unfold_all:
                initial_debit = grouped_accounts[account]['initial_bal']['debit']
                initial_credit = grouped_accounts[account]['initial_bal']['credit']
                initial_balance = grouped_accounts[account]['initial_bal']['balance']
                initial_currency = '' if not account.currency_id else self.with_context(no_format=False).format_value(grouped_accounts[account]['initial_bal']['amount_currency'], currency=account.currency_id)

                domain_lines = []
                if offset == 0:
                    domain_lines.append({
                        'id': 'initial_%s' % (account.id,),
                        'class': 'o_account_reports_initial_balance',
                        'name': _('Initial Balance'),
                        'parent_id': 'account_%s' % (account.id,),
                        'columns': [{'name': v} for v in ['', '', '', '', initial_currency, self.format_value(initial_debit), self.format_value(initial_credit), self.format_value(initial_balance)]],
                    })

                    progress = initial_balance
                else:
                    # for load more:
                    progress = float(options.get('lines_progress', initial_balance))

                amls = grouped_accounts[account]['lines']


                for line in amls:
                    if options.get('cash_basis'):
                        line_debit = line.debit_cash_basis
                        line_credit = line.credit_cash_basis
                    else:
                        line_debit = line.debit
                        line_credit = line.credit
                    date = amls.env.context.get('date') or fields.Date.today()
                    line_debit = line.company_id.currency_id._convert(line_debit, used_currency, company_id, date)
                    line_credit = line.company_id.currency_id._convert(line_credit, used_currency, company_id, date)
                    progress = progress + line_debit - line_credit
                    currency = "" if not line.currency_id else self.with_context(no_format=False).format_value(line.amount_currency, currency=line.currency_id)

                    name = line.name and line.name or ''
                    if line.ref:
                        name = name and name + ' - ' + line.ref or line.ref
                    name_title = name
                    # Don't split the name when printing
                    if len(name) > 35 and not self.env.context.get('no_format') and not self.env.context.get('print_mode'):
                        name = name[:32] + "..."
                    partner_name = line.partner_id.name
                    partner_name_title = partner_name
                    if partner_name and len(partner_name) > 35  and not self.env.context.get('no_format') and not self.env.context.get('print_mode'):
                        partner_name = partner_name[:32] + "..."
                    caret_type = 'account.move'
                    communication = ''

                    if line.move_id.is_purchase_document():
                        caret_type = 'account.invoice.in'
                    elif line.move_id.is_sale_document():
                        caret_type = 'account.invoice.out'
                    elif line.payment_id:
                        caret_type = 'account.payment'
                    else:
                        caret_type = 'account.move'

                    if line.payment_id:
                        communication = line.payment_id.communication

                    columns = [{'name': v} for v in [
                        format_date(self.env, line.date), 
                        name,
                        communication,
                        partner_name, 
                        currency,
                        line_debit != 0 and self.format_value(line_debit) or '',
                        line_credit != 0 and self.format_value(line_credit) or '',
                        self.format_value(progress)
                    ]]
                    columns[1]['class'] = 'whitespace_print'
                    columns[2]['class'] = 'whitespace_print'
                    columns[1]['title'] = name_title
                    columns[2]['title'] = partner_name_title
                    line_value = {
                        'id': line.id,
                        'caret_options': caret_type,
                        'class': 'top-vertical-align',
                        'parent_id': 'account_%s' % (account.id,),
                        'name': line.move_id.name if line.move_id.name else '/',
                        'columns': columns,
                        'level': 4,
                    }
                    aml_lines.append(line.id)
                    domain_lines.append(line_value)

                # load more
                # if remaining_lines > 0:
                #     domain_lines.append({
                #         'id': 'loadmore_%s' % account.id,
                #         # if MAX_LINES is None, there will be no remaining lines
                #         # so this should not cause a problem
                #         'offset': offset + self.MAX_LINES,
                #         'progress': progress,
                #         'class': 'o_account_reports_load_more text-center',
                #         'parent_id': 'account_%s' % (account.id,),
                #         'name': _('Load more... (%s remaining)') % remaining_lines,
                #         'colspan': 7,
                #         'columns': [{}],
                #     })
                # don't add total line for `load more`
                if offset == 0:
                    domain_lines.append({
                        'id': 'total_' + str(account.id),
                        'class': 'o_account_reports_domain_total',
                        'parent_id': 'account_%s' % (account.id,),
                        'name': _('Total '),
                        'columns': [{'name': v} for v in ['', '', '', '', amount_currency, self.format_value(debit), self.format_value(credit), self.format_value(balance)]],
                    })

                lines += domain_lines
                # print(lines,'================3============lines \n\n')
        if not line_id:



            dct_nombre_mes={
                1:'Enero',
                2:'Febrero',
                3:'Marzo',
                4:'Abril',
                5:'Mayo',
                6:'Junio',
                7:'Julio',
                8:'Agosto',
                9:'Septiembre',
                10:'Octubre',
                11:'Noviembre',
                12:'Diciembre',



            }
            fechaDesde=datetime.strptime(options['date']['date_from'], '%Y-%m-%d')










            lines.append({
                'id': 'general_ledger_total_%s' % company_id.id,
                'name': _('Total %s %s' %(dct_nombre_mes[fechaDesde.month],fechaDesde.year)),
                'class': 'total',
                'level': 1,
                'columns': [{'name': v} for v in ['', '', '', '', '', self.format_value(sum_debit), self.format_value(sum_credit), self.format_value(sum_balance)]],
            })

            # print(lines,'===================4=========lines \n\n')

        journals = [j for j in options.get('journals') if j.get('selected')]
        if len(journals) == 1 and journals[0].get('type') in ['sale', 'purchase'] and not line_id:
            lines.append({
                'id': 0,
                'name': _('Tax Declaration'),
                'columns': [{'name': v} for v in ['', '', '', '', '', '', '', '']],
                'level': 1,
                'unfoldable': False,
                'unfolded': False,
            })
            lines.append({
                'id': 0,
                'name': _('Name'),
                'columns': [{'name': v} for v in ['', '', '', '', '', _('Base Amount'), _('Tax Amount'), '']],
                'level': 2,
                'unfoldable': False,
                'unfolded': False,
            })
            # print(lines,'================5============lines \n\n')
            for tax, values in self._get_taxes(journals[0]).items():
                lines.append({
                    'id': '%s_tax' % (tax.id,),
                    'name': tax.name + ' (' + str(tax.amount) + ')',
                    'caret_options': 'account.tax',
                    'unfoldable': False,
                    'columns': [{'name': v} for v in ['', '', '', '', '', values['base_amount'], values['tax_amount'], '']],
                    'level': 4,
                })
            # print(lines,'=================6===========lines \n\n')

        if self.env.context.get('aml_only', False):
            return aml_lines
        # print ("==================7=======base lines",lines)
        return lines

    def view_all_journal_items(self, options, params):
        if params.get('id'):
            params['id'] = int(params.get('id').split('_')[1])
        return self.env['account.report'].open_journal_items(options, params)

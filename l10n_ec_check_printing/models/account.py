# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from . import amount_to_text_es
from datetime import datetime, timedelta

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'out_receipt': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
    'in_receipt': 'supplier',
    }

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    check_report_id = fields.Many2one(
        'ir.actions.report',
        'Formato de Cheque'
    )


class AccountPayment(models.Model):

    _inherit = 'account.payment'

    third_party_name = fields.Char('A nombre de Tercero',readonly=True,states={'draft': [('readonly', False)]})
    to_third_party = fields.Boolean('A nombre de terceros ?',readonly=True,states={'draft': [('readonly', False)]})
    date_to = fields.Date('Fecha Pago')
    number = fields.Integer('Numero de Cheque')
    bank = fields.Many2one('res.bank','Banco del Cheque', related="journal_id.bank_id")
    check_type = fields.Selection([('posfechado','Posfechado'),
                                    ('dia','Al dia')], string="Tipo" , default='dia')
    payment_line_ids = fields.One2many('account.payment.line', 'payment_id')
    invoice_id = fields.Many2one('account.move','Factura')
    has_payment_line = fields.Boolean(string="Tiene lineas de pagos", store=True)
    selected_inv_total = fields.Float(compute='_compute_amounts', store=True, string='Monto Asignado')
    account_check_id = fields.Many2one('account.cheque', string="Cheque")
    
    ############################################################ Pay multiple bills ############################################################
    @api.onchange('partner_id','payment_type')
    def onchange_partner_id(self):
        if not self.partner_id:
            self.payment_line_ids.unlink()
            return
        Invoice = self.env['account.move']
        PaymentLine = self.env['account.payment.line']
        type = self.payment_type == 'outbound' \
                and ('in_invoice', 'in_debit', 'liq_purchase', 'in_receipt') \
                or ('out_invoice', 'out_debit')
        invoices = Invoice.search([
            ('partner_id', 'in', self.partner_id.child_ids.ids + self.partner_id.ids),
            ('state', '=', 'posted'), ('type', 'in', type),('invoice_payment_state','!=','paid')
        ], order="invoice_date asc")
        list_ids =[]
        for invoice in invoices:
            payment_term_line = self.env['account.payment.term.line'].search([('payment_id','=',invoice.invoice_payment_term_id.id)])
            amount_balance = 0        
            for l in payment_term_line:
                if l.value_amount>0:
                    amount = round(invoice.amount_total*(l.value_amount/100),2)
                    amount_balance += amount
                else:
                    if len(payment_term_line)==1:
                        amount = invoice.amount_total
                    else:
                        amount = invoice.amount_total-amount_balance 
                line_id = PaymentLine.create([{
                    'invoice_id': invoice.id,
                    'amount_total': invoice.amount_total,
                    'actual_amount':invoice.amount_residual,
                    'residual': amount,
                    'amount': 0.0,
                    'date_due': invoice.invoice_date+timedelta(days=l.days),
                    'document_number':invoice.l10n_latam_document_number
                }])
                list_ids.append(line_id.id)
        self.payment_line_ids = [(6, 0, list_ids)]
        
    @api.onchange('payment_line_ids')
    def _onchange_residual(self):
        total=0
        for line in self.payment_line_ids:
            total += line.amount
        self.amount = total
    
    
    
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one
        default = dict(default or {})
        default.update(payment_line_ids=[], invoice_total=0.0)
        return super(AccountPayment, self).copy(default)
        
        
    @api.depends('payment_line_ids.actual_amount', 'payment_line_ids.amount', 'amount')
    def _compute_amounts(self):
        for payment in self:
            payment.selected_inv_total = sum(payment.payment_line_ids.mapped('actual_amount'))
            payment.balance = payment.currency_id.with_context(
                date=payment.payment_date
            ).compute(payment.amount - payment.selected_inv_total, self.currency_id)
    
    ############################################################ Pay multiple bills ############################################################

    @api.onchange('payment_method_code','third_name','is_third_name')
    def onchange_third_name(self):
        if self.is_third_name and self.third_name and self.payment_method_code=='check_printing':
            self.to_third_party=self.is_third_name
            self.third_party_name= self.third_name
        else:
            self.to_third_party=False
            self.third_party_name=False
    
    # @api.onchange('payment_method_id')
#     def onchange_payment_line(self):
#         if self.payment_method_code=='check_printing' and self.has_payment_line!=True:
#             payment_term_line = self.env['account.payment.term.line'].search([('payment_id','=',self.invoice_id.invoice_payment_term_id.id)])
#             amount_balance = 0
#             if payment_term_line:
#                 for l in payment_term_line:
#                     if l.value_amount>0:
#                         amount = round(self.invoice_id.amount_total*(l.value_amount/100),2)
#                         amount_balance += amount
#                     else:
#                         if len(payment_term_line)==1:
#                             amount = self.invoice_id.amount_total
#                         else:
#                             amount = self.invoice_id.amount_total-amount_balance
#                     self.env['account.payment.line'].create({
#                         'payment_id':self.id,
#                         'partner_id':self.partner_id,
#                         'date_due':self.invoice_id.invoice_date+timedelta(days=l.days),
#                         'amount':amount
#                     })                
#                 self.has_payment_line =True


    @api.onchange('payment_date')
    def onchange_payment_date(self):
        if self.payment_date:
            self.date_to = self.payment_date

    @api.onchange('date_to')
    def onchange_date_to(self):
        if self.date_to and self.date_to > self.payment_date:
            self.check_type = 'posfechado'

    @api.onchange('check_number')
    def onchange_check_number(self):
        if self.check_number:
            self.number = self.check_number

    @api.onchange('amount')
    def _onchange_amount(self):
        if hasattr(super(AccountPayment, self), '_onchange_amount'):
            super(AccountPayment, self)._onchange_amount()
        check_amount_in_words = amount_to_text_es.amount_to_text(self.amount)# noqa
        self.check_amount_in_words = check_amount_in_words

    def do_print_checks(self):
        """
        Validate numbering
        Print from journal check template
        """
        for payment in self:
            report = payment.journal_id.check_report_id
            if payment.env.context.get('active_model') == 'account.cheque':
                modelo = 'account.payment'
            else:
                modelo = payment._name
            report.write({'model': modelo})
            payment.write({'state':'sent'})
            return report.report_action(payment)
    
    def post(self):
        for rec in self:
            invoice_id=[l.invoice_id.id for l in rec.payment_line_ids if l.amount>0]
            if invoice_id:
                self.invoice_ids = invoice_id
            account_check = rec.env['account.cheque']
            if rec.payment_method_id.code in ['check_printing','batch_payment'] and not rec.payment_type == 'transfer':
                #types = 'outgoing'
                date = 'cheque_given_date'
                name = rec.partner_id.name
                if rec.to_third_party:
                    name = rec.third_party_name
                last_printed_check = rec.search([
                    ('journal_id', '=', rec[0].journal_id.id),
                    ('check_number', '!=', 0)], order="check_number desc", limit=1)
                debit = rec.destination_account_id.id
                credit = rec.journal_id.default_debit_account_id.id
                date_check = rec.payment_date
                bank_account = rec.journal_id.default_debit_account_id.id
                if not rec.check_number:
                    next_check_number = last_printed_check and int(last_printed_check.check_number) + 1 or 1     
                else:
                    next_check_number = rec.check_number
                
                check_id = account_check.create({
                    'name':'*',
                    'company_id':rec.company_id.id,
                    'bank_account_id':bank_account,
                    'amount':rec.amount,
                    'payee_user_id':rec.partner_id.id or False,
                    'cheque_date':date_check,
                    'cheque_receive_date':rec.payment_date,
                    'cheque_given_date':rec.date_to,
                    'credit_account_id':credit,
                    'debit_account_id':debit,
                    'journal_id':rec.journal_id.id,
                    #'account_cheque_type': types,
                    'status':'registered',
                    'status1':'registered',
                    'cheque_number':next_check_number,
                    'third_party_name':name,
                    'payment_id': rec.id,
                    # 'date' : rec.date_to,
                    #'invoice_ids': rec.invoice_ids,
                })
                rec.account_check_id = check_id.id
                for move in rec.move_line_ids:
                    move.move_id.account_cheque_id = check_id.id
            return super(AccountPayment, self.with_context({'multi_payment': invoice_id and True or False})).post()

    @api.onchange('name')
    @api.constrains('name')
    def name_check(self):
        for l in self:
            if l.account_check_id.name=='*':
                l.account_check_id.update({'name':l.name})
        
    @api.model
    def default_get(self, default_fields):
        rec = super(AccountPayment, self).default_get(default_fields)
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')

        # Check for selected invoices ids
        if not active_ids or active_model != 'account.move':
            return rec

        invoices = self.env['account.move'].browse(active_ids).filtered(lambda move: move.is_invoice(include_receipts=True))

        # Check all invoices are open
        if not invoices or any(invoice.state != 'posted' for invoice in invoices):
            raise UserError(_("You can only register payments for open invoices"))
        # Check if, in batch payments, there are not negative invoices and positive invoices
        dtype = invoices[0].type
        for inv in invoices[1:]:
            if inv.type != dtype:
                if ((dtype == 'in_refund' and inv.type == 'in_invoice') or
                        (dtype == 'in_invoice' and inv.type == 'in_refund')):
                    raise UserError(_("You cannot register payments for vendor bills and supplier refunds at the same time."))
                if ((dtype == 'out_refund' and inv.type == 'out_invoice') or
                        (dtype == 'out_invoice' and inv.type == 'out_refund')):
                    raise UserError(_("You cannot register payments for customer invoices and credit notes at the same time."))

        amount = self._compute_payment_amount(invoices, invoices[0].currency_id, invoices[0].journal_id, rec.get('payment_date') or fields.Date.today())
        rec.update({
            'currency_id': invoices[0].currency_id.id,
            'amount': abs(amount),
            'payment_type': 'inbound' if amount > 0 else 'outbound',
            'partner_id': invoices[0].commercial_partner_id.id,
            'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
            'communication': invoices[0].invoice_payment_ref or invoices[0].ref or invoices[0].name,
            'invoice_ids': [(6, 0, invoices.ids)],
            'invoice_id':invoices[0].id
        })  
        return rec

class AccountPaymentLine(models.Model):
    _name = 'account.payment.line'
    _descripcion = 'Lineas de Pago'
    
    payment_id = fields.Many2one('account.payment', 'Pago')
    #partner_id = fields.Many2one(related='payment_id.partner_id', string='Proveedor')
    date_due = fields.Date(string='Fecha de Vencimiento')
    amount = fields.Monetary('Monto a Pagar')
    currency_id = fields.Many2one(related='invoice_id.currency_id', string="Moneda")
    invoice_id = fields.Many2one('account.move', 'Factura')
    actual_amount = fields.Float(string='Monto actual adeudado')
    amount_total = fields.Monetary('Monto Total')
    residual = fields.Monetary('Cuotas')
    document_number = fields.Char(string="Número de Documento")

    @api.onchange('amount')
    def _onchange_amount(self):
        if self.amount>self.residual:
            raise ValidationError("El monto a pagar no puede ser mayor al valor de la cuota")

            
class AccountMove (models.Model):
    _inherit = 'account.move.line'

    
    def _reconcile_lines(self, debit_moves, credit_moves, field):
        """ This function loops on the 2 recordsets given as parameter as long as it
            can find a debit and a credit to reconcile together. It returns the recordset of the
            account move lines that were not reconciled during the process.
        """
        if not self.env.context.get('multi_payment'):
            return super(AccountMove, self)._reconcile_lines(debit_moves, credit_moves, field)
        to_create = []
        cash_basis = debit_moves and debit_moves[0].account_id.internal_type in ('receivable', 'payable') or False
        cash_basis_percentage_before_rec = {}
        dc_vals ={}
        while (debit_moves and credit_moves):
            debit_move = debit_moves[0]
            credit_move = credit_moves[0]
            company_currency = debit_move.company_id.currency_id
            balance = (credit_move + debit_move)
            payment_line_id = balance.mapped('payment_id.payment_line_ids').filtered(lambda x: x.invoice_id.id in balance.move_id.ids and x.amount>0)
            if len(payment_line_id)>1:
                raise UserError("Por factura solo debe ingresar un valor")
            temp_amount_residual = payment_line_id.amount
            temp_amount_residual_currency = payment_line_id.amount
            dc_vals[(debit_move.id, credit_move.id)] = (debit_move, credit_move, temp_amount_residual_currency)
            amount_reconcile = payment_line_id.amount
            if payment_line_id.invoice_id == debit_move.move_id:
                debit_move.amount_residual -= temp_amount_residual
                debit_move.amount_residual_currency -= temp_amount_residual_currency
                debit_moves -= debit_move
            if payment_line_id.invoice_id == credit_move.move_id:
                credit_move.amount_residual += temp_amount_residual
                credit_move.amount_residual_currency += temp_amount_residual_currency
                credit_moves -= credit_move
            currency = False
            amount_reconcile_currency = 0
            if field == 'amount_residual_currency':
                currency = credit_move.currency_id.id
                amount_reconcile_currency = temp_amount_residual_currency
                amount_reconcile = temp_amount_residual
            elif bool(debit_move.currency_id) != bool(credit_move.currency_id):
                currency = debit_move.currency_id or credit_move.currency_id
                currency_date = debit_move.currency_id and credit_move.date or debit_move.date
                amount_reconcile_currency = company_currency._convert(amount_reconcile, currency, debit_move.company_id, currency_date)
                currency = currency.id
            if cash_basis:
                tmp_set = debit_move | credit_move
                cash_basis_percentage_before_rec.update(tmp_set._get_matched_percentage())
            if not self.company_id.currency_id.is_zero(amount_reconcile) \
                    or not self.company_id.currency_id.is_zero(amount_reconcile_currency):
                to_create.append({
                    'debit_move_id': debit_move.id,
                    'credit_move_id': credit_move.id,
                    'amount': amount_reconcile,
                    'amount_currency': amount_reconcile_currency,
                    'currency_id': currency,
                })
        cash_basis_subjected = []
        part_rec = self.env['account.partial.reconcile']
        for partial_rec_dict in to_create:
            debit_move, credit_move, amount_residual_currency = dc_vals[partial_rec_dict['debit_move_id'], partial_rec_dict['credit_move_id']]
            if not amount_residual_currency and debit_move.currency_id and credit_move.currency_id:
                part_rec.create(partial_rec_dict)
            else:
                cash_basis_subjected.append(partial_rec_dict)
        for after_rec_dict in cash_basis_subjected:
            new_rec = part_rec.create(after_rec_dict)
            if cash_basis and not (
                    new_rec.debit_move_id.move_id == new_rec.credit_move_id.move_id.reversed_entry_id
                    or
                    new_rec.credit_move_id.move_id == new_rec.debit_move_id.move_id.reversed_entry_id
            ):
                new_rec.create_tax_cash_basis_entry(cash_basis_percentage_before_rec)
        return debit_moves+credit_moves

    def remove_move_reconcile(self):
        """ Undo a reconciliation """
        move_id = self.env.context.get('move_id')
        if not move_id:
            return super().remove_move_reconcile()
        (
            self.mapped('matched_debit_ids').filtered(
                lambda x: x.debit_move_id.move_id.id == move_id
            ) +
            self.mapped('matched_credit_ids').filtered(
                lambda x: x.credit_move_id.move_id.id == move_id
            )
        ).unlink()


class AccountCheque(models.Model):
    _inherit = "account.cheque"
 
    payee_user_id = fields.Many2one('res.partner',string="Payee", required=False)

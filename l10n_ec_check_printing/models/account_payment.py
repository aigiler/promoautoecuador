# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from . import amount_to_text_es
from datetime import datetime, timedelta

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'out_receipt': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
    'in_receipt': 'supplier',
    'out_debit': 'customer',
    }


class AccountPayment(models.Model):

    _inherit = 'account.payment'
    _order = "id desc"


    @api.model
    def _get_default_invoice_date(self):
        return fields.Date.today()

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
    
    amount_residual = fields.Float( string='Saldo Anticipo',readonly="1",compute="_calculate_amount_residual",store=True)
    fecha_aplicacion_anticipo = fields.Date('Fecha de Aplicación de Anticipo',default=_get_default_invoice_date)


    es_nota_credito = fields.Boolean('Es N/C')


    def actualizar_nc(self):
        pagos=self.env['account.payment'].search([])
        for l in pagos:
            if l.communication:
                if 'N/C' in l.communication:
                    l.es_nota_credito=True

    @api.onchange('communication')
    def actualizar_check_nc(self):
        if self.communication:
            if 'N/C' in self.communication:
                self.es_nota_credito=True



    parent_id = fields.Many2one('account.payment' ,string='Anticipo')

    pagos_relacionadas = fields.One2many(
        'account.payment', 'parent_id',
        'Pagos relacionados anticipo')


    estado_anticipo = fields.Selection([('draft','Borrador'),('anticipo', 'Anticipo Pendiente'),('posted', 'Validado')],default="draft")

    anticipo_ids = fields.One2many(
        'account.payment.anticipo', 'payment_id',
        'Anticipos', readonly=True)

    aplicacion_anticipo_ids = fields.One2many(
        'account.payment.anticipo.valor', 'payment_id',
        'Anticipos')

    account_payment_account_ids = fields.One2many('account.payment.line.account','payment_id', string="Cuentas Contables")




    def asientos_contables(self):


        movimientos=self.env['account.move.line'].search([('payment_id', '=',self.id)])
        lista_obj=[]
        for asiento in movimientos:

            lista_obj.append(asiento)
        return lista_obj


    #@api.constrains('account_payment_account_ids' )
    def calcular_monto(self):
        total=0


        if self.payment_type=='outbound':
            for line in self.account_payment_account_ids:
                total += line.debit
        elif  self.payment_type=='inbound':
            for line in self.account_payment_account_ids:
                total += line.credit

        if total!=self.amount and self.tipo_transaccion=='movimiento':
            raise ValidationError('El valor ingresado en el detalle de cuentas contables la suma debe ser igual al monto a pagar.')















    @api.depends('anticipo_ids','amount')
    def _calculate_amount_residual(self):
        total=0
        for l in self:
            for line in l.anticipo_ids:
                total += line.amount
            l.amount_residual = l.amount - total
            total=0



    def job_actualizar_pagos_facturas_pendientes(self):
        obj=self.env['account.payment'].search([('estado_anticipo','=','anticipo')])
        for l in obj:
            l.onchange_partner_id()






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
            if len(payment_term_line) >0:
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
            else:

                line_id = PaymentLine.create([{
                    'invoice_id': invoice.id,
                    'amount_total': invoice.amount_total,
                    'actual_amount':invoice.amount_residual,
                    'residual': invoice.amount_residual,
                    'amount': 0.0,
                    'date_due': invoice.invoice_date_due,
                    'document_number':invoice.l10n_latam_document_number
                }])
                list_ids.append(line_id.id)

        self.payment_line_ids = [(6, 0, list_ids)]
        


    @api.onchange('payment_line_ids')
    def _onchange_residual(self):

        total=0
        for line in self.payment_line_ids:
            total += line.amount
        
        if self.tipo_valor:
            self.amount=self.amount
        elif self.tipo_transaccion=='Pago':
            self.amount = total
        elif self.tipo_transaccion=='Anticipo':
            if total>self.amount_residual:
                raise ValidationError('El Anticipo no puede ser mayor al valor a pagar de todas las facturas.')

    
    
    
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one
        default = dict(default or {})
        default.update(payment_line_ids=[], amount=0.0)
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

    def button_journal_entries(self):
        lista=self.ids
        pagos_asociados=self.pagos_relacionadas.mapped("id")

        lista=pagos_asociados+lista
        lista.sort()


        return {
            'name': _('Journal Items'),
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('payment_id', 'in',lista)],
        }





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
    

    @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id','tipo_transaccion')
    def _compute_destination_account_id(self):
        self.destination_account_id = False
        for payment in self:
            if payment.invoice_ids:
                payment.destination_account_id = payment.invoice_ids[0].mapped(
                    'line_ids.account_id').filtered(
                        lambda account: account.user_type_id.type in ('receivable', 'payable'))[0]
            elif payment.payment_type == 'transfer':
                if not payment.company_id.transfer_account_id.id:
                    raise UserError(_('There is no Transfer Account defined in the accounting settings. Please define one to be able to confirm this transfer.'))
                payment.destination_account_id = payment.company_id.transfer_account_id.id
            elif payment.partner_id:
                partner = payment.partner_id.with_context(force_company=payment.company_id.id)
                if payment.partner_type == 'customer':
                    payment.destination_account_id = partner.property_account_receivable_id.id
                else:
                    payment.destination_account_id = partner.property_account_payable_id.id
            elif payment.partner_type == 'customer':
                default_account = self.env['ir.property'].with_context(force_company=payment.company_id.id).get('property_account_receivable_id', 'res.partner')

                payment.destination_account_id = default_account.id
            elif payment.partner_type == 'supplier':
                default_account = self.env['ir.property'].with_context(force_company=payment.company_id.id).get('property_account_payable_id', 'res.partner')
                payment.destination_account_id = default_account.id

            if payment.tipo_transaccion=='Anticipo':
                if payment.payment_type=='inbound':
                    default_account = payment.partner_id.property_account_payable_id.id
                else:
                    default_account = payment.partner_id.property_account_receivable_id.id
                payment.destination_account_id = default_account




    def aplicar_anticipo_pagos(self):

        PaymentLine = self.env['account.payment.line']
        PaymentLineValor = self.env['account.payment.anticipo.valor']


        for rec in self:
            if sum(rec.payment_line_ids.mapped('amount'))>0:
                PaymentLineValor.create({'fechaAplicacion':self.fecha_aplicacion_anticipo,'payment_id':rec.id,'aplicacion_anticipo':sum(rec.payment_line_ids.mapped('amount'))})

            invoices=[{'invoice':l.invoice_id,'invoice_id':l.invoice_id.id,'amount':l.amount} for l in rec.payment_line_ids if l.amount>0]

            list_ids =[]

            for invoice in invoices:
                copia_pago=self.copy()
                payment_term_line = self.env['account.payment.term.line'].search([('payment_id','=',invoice['invoice'].invoice_payment_term_id.id)])
                amount_balance = 0
                amount=0 
                if len(payment_term_line)>0:       
                    for l in payment_term_line:
                        if l.value_amount>0:
                            amount = round(invoice['invoice'].amount_total*(l.value_amount/100),2)
                            amount_balance += amount
                        else:
                            if len(payment_term_line)==1:
                                amount = invoice['invoice'].amount_total
                            else:
                                amount = invoice['invoice'].amount_total-amount_balance 

                    line_id = PaymentLine.create([{
                        'invoice_id': invoice['invoice'].id,
                        'amount_total': invoice['invoice'].amount_total,
                        'actual_amount':invoice['invoice'].amount_residual,
                        'residual': amount,
                        'amount': invoice['amount'],
                        'date_due': invoice['invoice'].invoice_date+timedelta(days=l.days),
                        'document_number':invoice['invoice'].l10n_latam_document_number,
                        'payment_id':copia_pago.id
                    }])
                else:

                    line_id = PaymentLine.create([{
                        'invoice_id': invoice['invoice'].id,
                        'amount_total': invoice['invoice'].amount_total,
                        'actual_amount':invoice['invoice'].amount_residual,
                        'residual': invoice['invoice'].amount_residual,
                        'amount': invoice['amount'],
                        'date_due': invoice['invoice'].invoice_date_due,
                        'document_number':invoice['invoice'].l10n_latam_document_number,
                        'payment_id':copia_pago.id


                    }])


                copia_pago.parent_id=rec.id
                copia_pago.tipo_transaccion='Pago'
                copia_pago.payment_date=self.fecha_aplicacion_anticipo
                copia_pago.amount=invoice['amount']


                copia_pago.payment_method_id=self.env['account.payment.method'].search([('payment_type','=',copia_pago.payment_type),('code','=','transfer')])
                copia_pago.post()
                copia_pago.payment_type='transfer'
                copia_pago.amount_residual=self.amount_residual-invoice['amount']
                copia_pago.destination_journal_id=copia_pago.journal_id.id



            anticipos=[(0,0,{'invoice_id':l.invoice_id.id,'amount':l.amount}) for l in rec.payment_line_ids if l.amount>0 ]

            rec.write({'anticipo_ids': anticipos})
            rec.onchange_partner_id()

        for pago in self.payment_line_ids:
            pago.amount=0

        if self.estado_anticipo=='posted' and self.amount_residual==0:
            self.estado_anticipo='posted'
        else:
            self.estado_anticipo='anticipo'

        if self.estado_anticipo=='anticipo' and  self.amount_residual==0 :
            self.estado_anticipo='posted'



    def post(self):
        for rec in self:

            #for l in rec.payment_line_ids:
                #if l.amount>l.actual_amount:
                    #raise ValidationError("El monto a pagar no puede ser al monto adeudado en la factura {0}".format(l.invoice_id.l10n_latam_document_number))
            lista_invoice=[]
            if rec.tipo_valor:
                if rec.tipo_valor=='enviar_credito':
                    for y in self.contrato_estado_cuenta_payment_ids:
                        cuota_id=self.env['contrato.estado.cuenta'].search([('contrato_id','=',rec.contrato_id.id),
                                                                  ('numero_cuota','=',y.numero_cuota)])[0]     
                        if cuota_id:
                            for act in cuota_id:
                                cuota_id.monto_pagado=y.monto_pagar
                                cuota_id.saldo=cuota_id.saldo-y.monto_pagar
                else:
                    for pago in rec.payment_line_ids:
                        if pago.pagar:
                            lista_invoice.append(pago.invoice_id.id)
                            movimientos_occ=self.env['account.move'].search([('journal_id','=',21),('ref','=',pago.invoice_id.name)])
                            for mov in movimientos_occ:
                                lista_invoice.append(mov.id)
  

                        for contrato in pago.invoice_id.contrato_estado_cuenta_ids:
                            contrato.monto_pagado=pago.amount
                            contrato.saldo=contrato.saldo-pago.amount  
                rec.update({'invoice_ids': [(6, 0, lista_invoice)]})
            if rec.amount==0:
                raise ValidationError("Ingrese el valor del monto")
            invoice_id=list(set([l.invoice_id.id for l in rec.payment_line_ids if l.amount>0]))
            lista_respaldo=[]
            for factura in invoice_id:
                payment_lines= rec.payment_line_ids.filtered(lambda l: l.invoice_id.id==factura)
                monto_total=sum(payment_lines.mapped("amount"))

                for pago in payment_lines:
                    dct={
                        'invoice_id':pago.invoice_id.id, 
                        'amount':pago.amount  ,
                        'amount_total': pago.amount_total,
                        'residual': pago.residual,
                        'amount': pago.amount,
                        'date_due': pago.date_due,
                        'document_number':pago.document_number,
                        'payment_id':pago.payment_id.id
                        }
                    lista_respaldo.append(dct)
                payment_lines.unlink()
                PaymentLine = self.env['account.payment.line']
                obj_factura=self.env['account.move'].browse(factura)
                line_id = PaymentLine.create([{
                    'invoice_id': obj_factura.id,
                    'amount_total': obj_factura.amount_total,
                    'actual_amount':obj_factura.amount_residual,
                    'residual':obj_factura.amount_residual,
                    'amount': monto_total,
                    'date_due':obj_factura.invoice_date_due,
                    'document_number':obj_factura.l10n_latam_document_number,
                    'payment_id':rec.id

                }])
            
            
            invoice_id=[l.invoice_id.id for l in rec.payment_line_ids if l.amount>0]
         #   raise ValidationError(invoice_id)

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
                    
                if  rec.account_check_id.id==False :
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
                else:
                    rec.account_check_id.update({
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



            super(AccountPayment, self.with_context({'multi_payment': invoice_id and True or False})).post()
    
            full_reconcile_id=''
            for inv in rec.invoice_ids:
                for lin in inv.line_ids:
                    if lin.account_id==rec.partner_id.property_account_receivable_id.id:
                        full_reconcile_id=lin.full_reconcile_id.id
            for pagos in rec.payment_line_ids:
                if pagos.pagar:
                    movimientos_occ=self.env['account.move'].search([('journal_id','=',21),('ref','=',pagos.invoice_id.name)])
                    for mov in movimientos_occ:
                        for line_ext in mov.line_ids:
                            if line_ext.account_id==rec.partner_id.property_account_receivable_id.id:
                                if full_reconcile_id:
                                    line_ext.full_reconcile_id=full_reconcile_id

            rec.payment_line_ids.unlink()

            
            for factura in lista_respaldo:

                PaymentLine = self.env['account.payment.line']
                line_id = PaymentLine.create(factura)
                #for y in factura.invoice_id.contrato_estado_cuenta_ids:

            
            
            if self.tipo_transaccion=='Anticipo':
                self.estado_anticipo='posted'
                self.aplicar_anticipo_pagos()


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





    def _prepare_payment_moves(self):
        ''' Prepare the creation of journal entries (account.move) by creating a list of python dictionary to be passed
        to the 'create' method.

        Example 1: outbound with write-off:

        Account             | Debit     | Credit
        ---------------------------------------------------------
        BANK                |   900.0   |
        RECEIVABLE          |           |   1000.0
        WRITE-OFF ACCOUNT   |   100.0   |

        Example 2: internal transfer from BANK to CASH:

        Account             | Debit     | Credit
        ---------------------------------------------------------
        BANK                |           |   1000.0
        TRANSFER            |   1000.0  |
        CASH                |   1000.0  |
        TRANSFER            |           |   1000.0

        :return: A list of Python dictionary to be passed to env['account.move'].create.
        '''
        all_move_vals = []

        for payment in self:
            company_currency = payment.company_id.currency_id
            move_names = payment.move_name.split(payment._get_move_name_transfer_separator()) if payment.move_name else None

            # Compute amounts.
            
            write_off_amount = payment.payment_difference_handling == 'reconcile' and -payment.payment_difference or 0.0
            print("este es essdfghgfds de write oggffzxcfvf dfgllf ")
            if payment.payment_type in ('outbound', 'transfer'):
                counterpart_amount = payment.amount
                if payment.parent_id.id:
                    if payment.payment_type=='inbound':
                        liquidity_line_account = payment.partner_id.property_account_payable_id
                    else:
                        liquidity_line_account = payment.partner_id.property_account_receivable_id

                else:
                    liquidity_line_account = payment.journal_id.default_debit_account_id
            else:
                counterpart_amount = -payment.amount
                if payment.parent_id.id:
                    if payment.payment_type=='inbound':
                        liquidity_line_account = payment.partner_id.property_account_payable_id
                    else:
                        liquidity_line_account = payment.partner_id.property_account_receivable_id
                else:
                    liquidity_line_account = payment.journal_id.default_credit_account_id






            # Manage currency.
            if payment.currency_id == company_currency:
                # Single-currency.
                balance = counterpart_amount
                write_off_balance = write_off_amount
                counterpart_amount = write_off_amount = 0.0
                currency_id = False
            else:
                # Multi-currencies.
                balance = payment.currency_id._convert(counterpart_amount, company_currency, payment.company_id, payment.payment_date)
                write_off_balance = payment.currency_id._convert(write_off_amount, company_currency, payment.company_id, payment.payment_date)
                currency_id = payment.currency_id.id

            # Manage custom currency on journal for liquidity line.
            if payment.journal_id.currency_id and payment.currency_id != payment.journal_id.currency_id:
                # Custom currency on journal.
                if payment.journal_id.currency_id == company_currency:
                    # Single-currency
                    liquidity_line_currency_id = False
                else:
                    liquidity_line_currency_id = payment.journal_id.currency_id.id
                liquidity_amount = company_currency._convert(
                    balance, payment.journal_id.currency_id, payment.company_id, payment.payment_date)
            else:
                # Use the payment currency.
                liquidity_line_currency_id = currency_id
                liquidity_amount = counterpart_amount

            # Compute 'name' to be used in receivable/payable line.
            rec_pay_line_name = ''
            if payment.payment_type == 'transfer':
                rec_pay_line_name = payment.name
            else:
                if payment.partner_type == 'customer':
                    if payment.payment_type == 'inbound':
                        rec_pay_line_name += _("Customer Payment")
                    elif payment.payment_type == 'outbound':
                        rec_pay_line_name += _("Customer Credit Note")
                elif payment.partner_type == 'supplier':
                    if payment.payment_type == 'inbound':
                        rec_pay_line_name += _("Vendor Credit Note")
                    elif payment.payment_type == 'outbound':
                        rec_pay_line_name += _("Vendor Payment")
                if payment.invoice_ids:
                    rec_pay_line_name += ': %s' % ', '.join(payment.invoice_ids.mapped('name'))

            # Compute 'name' to be used in liquidity line.
        
            if payment.payment_type == 'transfer':
                liquidity_line_name = _('Transfer to %s') % payment.destination_journal_id.name
            else:
                liquidity_line_name = payment.name

            # ==== 'inbound' / 'outbound' ====



            
            move_vals = {
                'date': payment.payment_date,
                'ref': payment.communication,
                'journal_id': payment.journal_id.id,
                'currency_id': payment.journal_id.currency_id.id or payment.company_id.currency_id.id,
                'partner_id': payment.partner_id.id,
                'line_ids': [
                    # Receivable / Payable / Transfer line.
                    (0, 0, {
                        'name': rec_pay_line_name,
                        'amount_currency': counterpart_amount + write_off_amount if currency_id else 0.0,
                        'currency_id': currency_id,
                        'debit': balance + write_off_balance > 0.0 and balance + write_off_balance or 0.0,
                        'credit': balance + write_off_balance < 0.0 and -balance - write_off_balance or 0.0,
                        'date_maturity': payment.payment_date,
                        'partner_id': payment.partner_id.commercial_partner_id.id,
                        'account_id': payment.destination_account_id.id ,
                        'payment_id': payment.id,
                        'analytic_account_id':payment.analytic_account_id.id or False,
                    }),
                    # Liquidity line.
                    (0, 0, {
                        'name': liquidity_line_name,
                        'amount_currency': -liquidity_amount if liquidity_line_currency_id else 0.0,
                        'currency_id': liquidity_line_currency_id,
                        'debit': balance < 0.0 and -balance or 0.0,
                        'credit': balance > 0.0 and balance or 0.0,
                        'date_maturity': payment.payment_date,
                        'partner_id': payment.partner_id.commercial_partner_id.id,
                        'account_id': liquidity_line_account.id,
                        'payment_id': payment.id,
                        'analytic_account_id': False,
                    }),
                ]}

            if write_off_balance:
                # Write-off line.
                move_vals['line_ids'].append((0, 0, {
                    'name': payment.writeoff_label,
                    'amount_currency': -write_off_amount,
                    'currency_id': currency_id,
                    'debit': write_off_balance < 0.0 and -write_off_balance or 0.0,
                    'credit': write_off_balance > 0.0 and write_off_balance or 0.0,
                    'date_maturity': payment.payment_date,
                    'partner_id': payment.partner_id.commercial_partner_id.id,
                    'account_id': payment.writeoff_account_id.id,
                    'payment_id': payment.id,
                }))

            if move_names:
                move_vals['name'] = move_names[0]

            all_move_vals.append(move_vals)

            # ==== 'transfer' ====
            if payment.payment_type == 'transfer':
                journal = payment.destination_journal_id

                # Manage custom currency on journal for liquidity line.
                if journal.currency_id and payment.currency_id != journal.currency_id:
                    # Custom currency on journal.
                    liquidity_line_currency_id = journal.currency_id.id
                    transfer_amount = company_currency._convert(balance, journal.currency_id, payment.company_id, payment.payment_date)
                else:
                    # Use the payment currency.
                    liquidity_line_currency_id = currency_id
                    transfer_amount = counterpart_amount

                transfer_move_vals = {
                    'date': payment.payment_date,
                    'ref': payment.communication,
                    'partner_id': payment.partner_id.id,
                    'journal_id': payment.destination_journal_id.id,
                    'line_ids': [
                        # Transfer debit line.
                        (0, 0, {
                            'name': payment.name,
                            'amount_currency': -counterpart_amount if currency_id else 0.0,
                            'currency_id': currency_id,
                            'debit': balance < 0.0 and -balance or 0.0,
                            'credit': balance > 0.0 and balance or 0.0,
                            'date_maturity': payment.payment_date,
                            'partner_id': payment.partner_id.commercial_partner_id.id,
                            'account_id': payment.company_id.transfer_account_id.id,
                            'payment_id': payment.id,
                        }),
                        # Liquidity credit line.
                        (0, 0, {
                            'name': _('Transfer from %s') % payment.journal_id.name,
                            'amount_currency': transfer_amount if liquidity_line_currency_id else 0.0,
                            'currency_id': liquidity_line_currency_id,
                            'debit': balance > 0.0 and balance or 0.0,
                            'credit': balance < 0.0 and -balance or 0.0,
                            'date_maturity': payment.payment_date,
                            'partner_id': payment.partner_id.commercial_partner_id.id,
                            'account_id': payment.destination_journal_id.default_credit_account_id.id,
                            'payment_id': payment.id,
                        }),
                    ],
                }

                if move_names and len(move_names) == 2:
                    transfer_move_vals['name'] = move_names[1]

                all_move_vals.append(transfer_move_vals)

            if payment.tipo_valor=='enviar_credito':
                if payment.saldo_pago:
                    if not self.account_payment_account_ids:
                        raise ValidationError("El saldo Pendiente debe ser asignado a un apunte contable. Favor crear un registro en la sección Cuentas Contables.")
                    listaMovimientos=[

                            #  Este se envía al banco 
                            (0, 0, {
                                'name': payment.name,
                                'amount_currency': -liquidity_amount if liquidity_line_currency_id else 0.0,
                                'currency_id': liquidity_line_currency_id,
                                'debit': payment.amount,
                                'credit': 0,
                                'date_maturity': payment.payment_date,
                                'partner_id': payment.partner_id.commercial_partner_id.id,
                                'account_id': liquidity_line_account.id,
                                'payment_id': payment.id,
                            })
                        ]


                    saldo_debito=0
                    saldo_credito=0
                    total_credito=0
                    for linea in self.account_payment_account_ids:
                            if linea.debit:
                                saldo_debito=linea.debit
                            else:
                                saldo_credito=linea.credit
                                total_credito+=saldo_credito

                                # Receivable / Payable / Transfer line. Este se envia al proveedor
                            tupla=(0, 0, {
                                'name': linea.name,
                                'amount_currency':  0.0,
                                'currency_id': currency_id,
                                'debit': linea.debit,
                                'credit':  linea.credit,
                                'date_maturity': payment.payment_date,
                                'partner_id': False,
                                'account_id': linea.cuenta.id,
                                'payment_id': payment.id,
                                'account_id': linea.cuenta.id,
                                'analytic_account_id':linea.cuenta_analitica.id or False,



                            })
                            listaMovimientos.append(tupla)
                    if total_credito!=payment.saldo_pago:
                        raise ValidationError("Las lineas ubicadas en la sección Cuentas Contables debe ser igual al saldo.")
                    credito_asignado=0
                    debito_asignado=0
                    if total_credito:
                        credito_asignado=balance+total_credito
                    elif saldo_debito:
                        debito_asignado=balance-saldo_debito

                    listaMovimientos.append(#  Este se envía al banco 
                            (0, 0, {
                                'name': "Pago de Cliente",
                                'amount_currency': counterpart_amount + write_off_amount if currency_id else 0.0,
                                'currency_id': liquidity_line_currency_id,
                                'debit': debito_asignado,
                                'credit': -credito_asignado,
                                'date_maturity': payment.payment_date,
                                'partner_id': payment.partner_id.commercial_partner_id.id,
                                'account_id': payment.partner_id.property_account_receivable_id.id,
                                'payment_id': payment.id,
                            }))                        
                    move_vals = {
                        'date': payment.payment_date,
                        'ref': payment.communication,
                        'journal_id': payment.journal_id.id,
                        'currency_id': payment.journal_id.currency_id.id or payment.company_id.currency_id.id,
                        'partner_id': payment.partner_id.id,
                        'line_ids': listaMovimientos,
                    }
                    all_move_vals=[]
                    all_move_vals.append(move_vals)
                for y in self.contrato_estado_cuenta_payment_ids:
                    cuota_id=self.env['contrato.estado.cuenta'].search([('contrato_id','=',payment.contrato_id.id),
                                                                ('numero_cuota','=',y.numero_cuota)])[0]     
                    if cuota_id:
                        for act in cuota_id:
                            cuota_id.monto_pagado=y.monto_pagar
                            cuota_id.saldo=cuota_id.saldo-y.monto_pagar










            if payment.tipo_valor=='crear_acticipo':
                if not payment.payment_line_ids:
                    raise ValidationError("Debe seleccionar facturas Pagar")

                if payment.amount<=payment.saldo_pago:
                    raise ValidationError("En caso de anticipos el monto a pagar debe ser mayor que los valores a pagar.")
                else:
                    listaMovimientos=[

                            #  Este se envía al banco 
                            (0, 0, {
                                'name': payment.name,
                                'amount_currency': -liquidity_amount if liquidity_line_currency_id else 0.0,
                                'currency_id': liquidity_line_currency_id,
                                'debit': payment.amount,
                                'credit': 0,
                                'date_maturity': payment.payment_date,
                                'partner_id': payment.partner_id.commercial_partner_id.id,
                                'account_id': liquidity_line_account.id,
                                'payment_id': payment.id,
                            }),

                            (0, 0, {
                                'name': "Pago de Cuentas Adminitrativa y Capital",
                                'amount_currency': counterpart_amount + write_off_amount if currency_id else 0.0,
                                'currency_id': liquidity_line_currency_id,
                                'debit': 0,
                                'credit': payment.valor_deuda+payment.valor_deuda_admin,
                                'date_maturity': payment.payment_date,
                                'partner_id': payment.partner_id.commercial_partner_id.id,
                                'account_id': payment.partner_id.property_account_receivable_id.id,
                                'payment_id': payment.id,
                            }),
                            (0, 0, {
                                'name': "Pago de Cliente",
                                'amount_currency': counterpart_amount + write_off_amount if currency_id else 0.0,
                                'currency_id': liquidity_line_currency_id,
                                'debit': 0,
                                'credit': payment.saldo_pago,
                                'date_maturity': payment.payment_date,
                                'partner_id': payment.partner_id.commercial_partner_id.id,
                                'account_id': payment.partner_id.property_account_receivable_id.id,
                                'payment_id': payment.id,
                            }),
                           
                        ]

                  
                    move_vals = {
                        'date': payment.payment_date,
                        'ref': payment.communication,
                        'journal_id': payment.journal_id.id,
                        'currency_id': payment.journal_id.currency_id.id or payment.company_id.currency_id.id,
                        'partner_id': payment.partner_id.id,
                        'line_ids': listaMovimientos,

                    }
                    all_move_vals=[]
                    all_move_vals.append(move_vals)





            if self.is_third_name:

        # ==== 'inbound' / 'outbound' ==== para múltiples cuentas

                listaMovimientos=[

                        #  Este se envía al banco 
                        (0, 0, {
                            'name': liquidity_line_name,
                            'amount_currency': -liquidity_amount if liquidity_line_currency_id else 0.0,
                            'currency_id': liquidity_line_currency_id,
                            'debit': balance < 0.0 and -balance or 0.0,
                            'credit': balance > 0.0 and balance or 0.0,
                            'date_maturity': payment.payment_date,
                            'partner_id': payment.partner_id.commercial_partner_id.id,
                            'account_id': liquidity_line_account.id,
                            'payment_id': payment.id,
                        })
                    ]


                for linea in self.account_payment_account_ids:

                        # Receivable / Payable / Transfer line. Este se envia al proveedor
                    tupla=(0, 0, {
                        'name': rec_pay_line_name,
                        'amount_currency':  0.0,
                        'currency_id': currency_id,
                        'debit': linea.debit ,
                        'credit':  linea.credit,
                        'date_maturity': payment.payment_date,
                        'partner_id': False,
                        'account_id': linea.cuenta.id,
                        'payment_id': payment.id,
                        'account_id': linea.cuenta.id,
                        'analytic_account_id':linea.cuenta_analitica.id or False,



                    })

                    listaMovimientos.append(tupla)
                #raise ValidationError(str(listaMovimientos))
                
                move_vals = {
                    'date': payment.payment_date,
                    'ref': payment.communication,
                    'journal_id': payment.journal_id.id,
                    'currency_id': payment.journal_id.currency_id.id or payment.company_id.currency_id.id,
                    'partner_id': payment.partner_id.id,
                    'line_ids': listaMovimientos,
                }
                all_move_vals=[]
                all_move_vals.append(move_vals)

       # raise ValidationError(str(all_move_vals))

        return all_move_vals































class AccountPaymentLine(models.Model):
    _name = 'account.payment.line'
    _descripcion = 'Lineas de Pago'
    
    payment_id = fields.Many2one('account.payment', 'Pago')
    #partner_id = fields.Many2one(related='payment_id.partner_id', string='Proveedor')
    pagar=fields.Boolean(string="Seleccione para Pagar")
    date_due = fields.Date(string='Fecha de Vencimiento')
    amount = fields.Monetary('Monto a Pagar')
    currency_id = fields.Many2one(related='invoice_id.currency_id', string="Moneda")
    invoice_id = fields.Many2one('account.move', 'Factura')
    actual_amount = fields.Float(string='Monto actual adeudado')
    amount_total = fields.Monetary('Monto Total')
    residual = fields.Monetary('Cuotas')
    document_number = fields.Char(string="Número de Documento")
    monto_pendiente_pago = fields.Float(string='Monto de la cuota de Pago')

    @api.constrains('invoice_id')
    def obtener_monto(self):
        for l in self:
            if l.invoice_id:
                monto_pendiente_pago=0
                for x in l.invoice_id.contrato_estado_cuenta_ids:
                    monto_pendiente_pago+=(x.saldo-x.cuota_adm)
                l.monto_pendiente_pago=monto_pendiente_pago

    @api.onchange('pagar')
    def actualizar_totales(self):
        for l in self:
            monto_inicial=l.payment_id.amount
            
            if l.pagar:
                l.amount=l.actual_amount
                l.payment_id._saldo_pagar()
            else:
                l.amount=0
                l.payment_id._saldo_pagar()
            l.payment_id.amount=monto_inicial 

    @api.onchange('amount')
    def actualizar_saldo(self):
        for l in self:
            l.payment_id._saldo_pagar()

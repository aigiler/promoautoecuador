# -*- coding: utf-8 -*-
 

import time
from datetime import datetime, date
from odoo import api, fields, models

class AccountPaymentLine(models.Model):
    _inherit = 'account.payment.line'

    monto_pendiente_pago = fields.Float(string='Monto de la cuota de Pago')

    @api.constrains('invoice_id')
    def obtener_monto(self):
    	for l in self:
    		if l.invoice_id:
   			for x in l.invoice_id.contrato_estado_cuenta_ids:
   				l.monto_pendiente_pago=x.saldo-x.cuota_adm+x.iva_adm



class AccountPayment(models.Model):

    _inherit = 'account.payment'





    def post(self):
        for rec in self:

            for l in rec.payment_line_ids:
                if l.amount>l.actual_amount:
                    raise ValidationError("El monto a pagar no puede ser al monto adeudado en la factura {0}".format(l.invoice_id.l10n_latam_document_number))



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
            

            rec.payment_line_ids.unlink()

            for factura in lista_respaldo:

                PaymentLine = self.env['account.payment.line']
                line_id = PaymentLine.create(factura)

            
            
            if self.tipo_transaccion=='Anticipo':
                self.estado_anticipo='posted'
                self.aplicar_anticipo_pagos()


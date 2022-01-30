# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons.web.controllers.main import clean_action

class PaymentLineAccount(models.Model):
    _name = 'account.payment.line.account'


    payment_id = fields.Many2one('account.paymentt',string='Pago' )

    cuenta = fields.Many2one('account.account',string='Cuentas' )
    name = fields.Char(string='Descripcion' )
    cuenta_analitica = fields.Many2one('account.analytic.account',string='Cuenta Analitica' )
    analytic_tag_ids = fields.Many2many('account.analytic.tag',string='Etiqueta Analitica' )
    debit = fields.Float(string='Debito' )
    credit = fields.Float(string='Credito' )

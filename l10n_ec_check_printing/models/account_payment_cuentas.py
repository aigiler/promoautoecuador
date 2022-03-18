# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons.web.controllers.main import clean_action

class PaymentLineAccount(models.Model):
    _name = 'account.payment.line.account'


    payment_id = fields.Many2one('account.payment',string='Pago' )

    cuenta = fields.Many2one('account.account',string='Cuentas' )
    name = fields.Char(string='Descripcion' )
    cuenta_analitica = fields.Many2one('account.analytic.account',string='Cuenta Analítica' )
    analytic_tag_ids = fields.Many2many('account.analytic.tag',string='Etiquetas Analíticas' )
    debit = fields.Float(string='Débito' )
    credit = fields.Float(string='Crédito' )

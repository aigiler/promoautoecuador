# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons.web.controllers.main import clean_action

class PaymentLineAccount(models.Model):
    _name = 'account.payment.line.account'


    payment_id = fields.Many2one('account.payment',string='Pago' )

    partner_id=fields.Many2one('res.partner', related="payment_id.partner_id")
    cuenta = fields.Many2one('account.account',string='Cuentas' )
    name = fields.Char(string='Descripcion' )
    cuenta_analitica = fields.Many2one('account.analytic.account',string='Cuenta Analítica' )
    analytic_tag_ids = fields.Many2many('account.analytic.tag',string='Etiquetas Analíticas' )
    debit = fields.Float(string='Débito' )
    credit = fields.Float(string='Crédito' )
    aplicar_anticipo=fields.Boolean("Anticipo")


class AccountMove(models.Model):
    _inherit = 'account.move'
    anticipos_ids=fields.One2many('anticipos.pendientes','factura_id',string='Anticipos Pendientes')


class AnticiposPendientes(models.Model):
    _name = 'anticipos.pendientes'

    linea_pago_id=fields.Many2one('account.payment.line.account',string='Anticipo Pendiente' )
    payment_id = fields.Many2one('account.payment',related='linea_pago_id.payment_id',string='Pago' )
    credit=fields.Float(related='linea_pago_id.credit',string="Monto")
    aplicar_anticipo=fields.Boolean(string="Aplicar")
    factura_id = fields.Many2one('account.move',string='Factura' )

    @api.onchange('aplicar_anticipo')
    def aplicar_anticipo(self):
        for l in self:
            if l.aplicar_anticipo:
                l.linea_pago_id.aplicar_anticipo=False
            else:
                l.linea_pago_id.aplicar_anticipo=True
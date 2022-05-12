# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, tools,  _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime,timedelta,date

class AccountMove(models.Model):   
    _inherit = 'account.move'    

    contrato_id = fields.Many2one('contrato', string='Contrato')

    contrato_estado_cuenta_ids = fields.Many2many('contrato.estado.cuenta', string='Estado de Cuenta de Aportes')
    
    @api.onchange('contrato_estado_cuenta_ids')
    def _onchange_contrato_estado_cuenta_ids(self):
        obj_product = self.env['product.template'].search([('default_code','=','CA1')])
        obj_account = self.env['account.account'].search([('code','=','4010101002')])
        obj_tax = self.env['account.tax'].search([('name','=','VENTAS DE ACTIVOS FIJOS GRAVADAS TARIFA 12%')])
        list_pagos_diferentes = {}
        valor = 0
        values = {
                    'product_id':obj_product.id,
                    'name': 'Pago de cuotas ',
                    'account_id':obj_account.id,
                    'tax_ids': [(6,0,[obj_tax.id])],
                    'quantity': 0,
                    'price_unit':0,
                }
        if self.contrato_estado_cuenta_ids:
            obj_contrato_estado_cuenta = self.env['contrato.estado.cuenta'].search([('id','in',self.contrato_estado_cuenta_ids.ids)])
            for rec in obj_contrato_estado_cuenta:
                values['quantity'] = values.get('quantity') + 1
                valor += rec.cuota_adm
                values['price_unit'] = valor/values.get('quantity')
                values['name'] = values.get('name')+rec.numero_cuota+','
                list_pagos_diferentes.update({
                    str(rec.cuota_adm):values
                })
                    
            for rec in list_pagos_diferentes.values():
                if not self.invoice_line_ids:
                    self.invoice_line_ids = [(0,0,rec)]
                    if not self.campos_adicionales_facturacion:
                        dic_caf = {
                            'nombre': 'Descripcion',
                            'valor':rec.get('name')
                        }
                        self.update({'campos_adicionales_facturacion':[(0,0,dic_caf)]})
                    self._move_autocomplete_invoice_lines_values()
                else:
                    for ric in self.invoice_line_ids:
                        ric.name = rec.get('name')
                        ric.quantity = rec.get('quantity')
                        ric.price_unit = rec.get('price_unit')
                    
                    
                    for roc in self.campos_adicionales_facturacion:
                        roc.valor = rec.get('name')
                    self._move_autocomplete_invoice_lines_values()


  
    @api.onchange("manual_establishment","manual_referral_guide")
    def obtener_diario_por_establecimiento(self,):
        diario_de_ventas=self.env['account.journal'].search([('type','=?',self.invoice_filter_type_domain),('auth_out_invoice_id.serie_establecimiento','=',self.manual_establishment),('auth_out_invoice_id.serie_emision','=',self.manual_referral_guide),('auth_out_invoice_id.active','=',True)],limit=1)
        if len(diario_de_ventas)>0:
            self.journal_id=diario_de_ventas.id
            self.auth_number=diario_de_ventas.auth_out_invoice_id.authorization_number


class AccountMoveLine(models.Model):   
    _inherit = 'account.move.line'    
  
    @api.constrains('account_id')
    def constrains_analytic_account_id(self):
        for l in self:
            if l.move_id.type=='entry' and l.account_id.analytic_account==True and not l.analytic_account_id:
                raise ValidationError('Seleccione una Cuenta analítica para la cta: '+l.account_id.code+' '+l.account_id.name.strip())


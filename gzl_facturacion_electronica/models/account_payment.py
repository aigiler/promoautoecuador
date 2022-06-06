# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    contrato_estado_cuenta_payment_ids = fields.One2many('contrato.estado.cuenta.payment', 'payment_pagos_id')
    deuda_total=fields.Float("Deuda Total", compute='obtener_deudas_facturas', store=True)
    valor_deuda=fields.Float("Valor a Pagar",compute='_saldo_pagar', store=True)
    saldo_pago=fields.Float("Saldo", compute='_saldo_pagar', store=True)
    total_asignado=fields.Float("Total asignado", compute="total_asignar")
    contrato_id = fields.Many2one('contrato', string='Contrato')
    valor_deuda_admin=fields.Float("Cuota Administrativa a Pagar",compute='_saldo_pagar', store=True)

    tipo_valor = fields.Selection([
        ('enviar_credito', 'Enviar a Credito'),
        ('crear_acticipo', 'Crear Anticipo')
    ], string='Tipo')

    @api.onchange('partner_id','payment_line_ids')
    def obtener_deudas_facturas(self):
        total_deuda=0
        for l in self:
            for y in l.payment_line_ids:
                if l.invoice_id:
                    for x in l.invoice_id.contrato_estado_cuenta_ids:
                        total_deuda+=(x.cuota_capital+x.seguro+x.rastreo+x.otro+y.actual_amount)
            l.deuda_total=total_deuda



    @api.onchange('partner_id')
    def obtener_deudas(self):
        valor_deuda=0
        for l in self:
            if l.partner_id:
                for x in l.payment_line_ids:
                    valor_deuda+=(x.actual_amount+x.monto_pendiente_pago)
        self.valor_deuda=valor_deuda

    @api.onchange('amount')
    def obtener_deudas(self):
        monto=0
        for l in self:
            valor=0
            if l.amount:
                valor=l.amount    
        monto=valor-self.valor_deuda

    #@api.multi
    def crear_detalles(self):
        for l in self:
            if l.amount==0 or not l.amount:
                raise ValidationError("Debe Asignar un monto a Pagar")
        
        self._onchange_tipo_valor()
        viewid = self.env.ref('gzl_facturacion_electronica.pago_cuota_form2').id
        return {   
            'name':'Detalle de Cuotas',
            'view_type':'form',
            'views' : [(viewid,'form')],
            'res_model':'account.payment',
            'res_id':self.id,
            'type':'ir.actions.act_window',
            'target':'new',
            }



    def cerrar_ventana(self):
        return {
        'type':'ir.actions.act_window_close'
        }


    @api.onchange('amount')
    def _onchange_amount(self):
        self.saldo_pago=self._saldo_pagar()

    @api.onchange('tipo_valor','contrato_id','contrato_estado_cuenta_payment_ids')
    def _onchange_tipo_valor(self):
        if self.tipo_valor=='crear_acticipo':
            self._saldo_pagar()
        lista_cuotas = []
        if self.tipo_valor == 'enviar_credito':
            self.saldo_pago=self._saldo_pagar()
            if not self.contrato_id:
                for rec in self.payment_line_ids:
                    for cuota in rec.invoice_id.contrato_estado_cuenta_ids:
                        if cuota.id not in lista_cuotas:
                            lista_cuotas.append(cuota.id)

            if self.contrato_id:
                if self.contrato_estado_cuenta_payment_ids:
                    for l in self.contrato_estado_cuenta_payment_ids:
                        if l.contrato_id==self.contrato_id:
                            pass
                        else:
                            self.update({'contrato_estado_cuenta_payment_ids':[(6,0,[])]}) 
                for cuota in self.contrato_id.estado_de_cuenta_ids:
                    if cuota.factura_id.amount_residual!=0 and cuota.saldo!=0:
                        lista_cuotas.append(cuota.id)
            obj_estado_cuenta_ids = self.env['contrato.estado.cuenta'].search([('id','in',lista_cuotas)])
            list_ids_cuotas = []
            cuotas = {
                'numero_cuota':'',
                'fecha':'',
                'cuota_capital':'',
                'seguro':'',
                'rastreo':'',
                'otro':'',
                'saldo':'',
                'cuota_capital_pagar':'',
                'seguro_pagar':'',
                'rastreo_pagar':'',
                'otro_pagar':'',
                'monto_pagar':'',
                'contrato_id':'',
            }
            if not self.contrato_estado_cuenta_payment_ids:
                if obj_estado_cuenta_ids:
                    # for rec in obj_am:
                    for ric in obj_estado_cuenta_ids:
                        # list_ids_cuotas.append(ric)
                        if ric.saldo!=0:
                            saldo=ric.seguro+ric.rastreo+ric.cuota_capital+ric.otro
                            cuotas.update({
                                'numero_cuota':ric.numero_cuota,
                                'fecha':ric.fecha,
                                'cuota_capital':ric.cuota_capital,
                                'seguro':ric.seguro,
                                'rastreo':ric.rastreo,
                                'otro':ric.otro,
                                'saldo':saldo,
                                'contrato_id':ric.contrato_id.id,
                                # 'cuota_capital_pagar':ric.cuota_capital_pagar,
                                # 'seguro_pagar':'',
                                # 'rastreo_pagar':'',
                                # 'otro_pagar':'',
                                # 'monto_pagar':'',
                            })
                            
                            self.contrato_estado_cuenta_payment_ids = [(0,0,cuotas)]

    @api.depends('contrato_estado_cuenta_payment_ids')
    def total_asignado(self):
        for l in self:
            for x in l.contrato_estado_cuenta_payment_ids:
                l.total_asignado+=x.monto_pagar

    @api.onchange('tipo_valor','l.amount')
    @api.depends('tipo_valor','l.amount')
    def _saldo_pagar(self):
        for l in self:
            self.obtener_deudas_facturas()
            if l.tipo_valor=='enviar_credito':
                valor_asignado=0
                for x in l.contrato_estado_cuenta_payment_ids:
                    if x.monto_pagar:
                        valor_asignado+=x.monto_pagar
                if (l.amount-valor_asignado)<0:
                    raise ValidationError("Los valores a pagar exceden los ${0} especificados.".format(l.amount))
                l.valor_deuda=valor_asignado
                l.saldo_pago=l.amount-l.valor_deuda
            if l.tipo_valor=='crear_acticipo':
                    valor_asignado=0
                    valor_facturas=0
                    for x in l.payment_line_ids:
                        if x.amount:
                            #x.amount=x.actual_amount
                            valor_asignado+=(x.amount+x.monto_pendiente_pago)
                    l.valor_deuda=valor_asignado
                    l.saldo_pago=l.amount-l.valor_deuda

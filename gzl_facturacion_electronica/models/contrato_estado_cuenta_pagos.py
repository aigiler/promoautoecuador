from odoo import models,api,fields

class ContratoEstadoCuentaPagos(models.Model):
    _name = 'contrato.estado.cuenta.payment'
    _description = 'Contrato - Tabla Relacional de pagos y contratos'
    # _rec_name = 'numero_cuota'



    payment_pagos_id = fields.Many2one('account.payment')
    idContrato = fields.Char("ID de Contrato en base")
    contrato_id = fields.Many2one('contrato')
    numero_cuota = fields.Char(String='Número de Cuota', readonly=True)
    fecha = fields.Date(String='Fecha Pago', readonly=True)
    currency_id = fields.Many2one(
        'res.currency', readonly=True, default=lambda self: self.env.company.currency_id)
    cuota_capital = fields.Monetary(
        string='Cuota Capital', currency_field='currency_id', readonly=True)
    # pago_ids = fields.Many2many('account.payment','contrato_estado_cuenta_payment_rel', 'estado_cuenta_id','payment_id', string='Pagos')
    seguro = fields.Monetary(string='Seguro', currency_field='currency_id', readonly=True)
    rastreo = fields.Monetary(string='Rastreo', currency_field='currency_id', readonly=True)
    otro = fields.Monetary(string='Otro', currency_field='currency_id', readonly=True)
    saldo = fields.Monetary(string='Saldo', currency_field='currency_id' , readonly=True)
    cuota_capital_pagar = fields.Monetary('Cuota Capital a Pagar')
    seguro_pagar = fields.Monetary('Seguro a Pagar')
    rastreo_pagar = fields.Monetary('Rastreo a Pagar')
    otro_pagar = fields.Monetary('Otro a Pagar')
    monto_pagar = fields.Monetary('Monto a Pagar')
    # certificado = fields.Binary(string='Certificado')
    # cuotaAdelantada = fields.Boolean(string='Cuota Adelantada')
    # estado_pago = fields.Selection([('pendiente', 'Pendiente'),
    #                                 ('pagado', 'Pagado'),
    #                                 ('congelado', 'Congelado')
    #                                 ], string='Estado de Pago', default='pendiente')

    # pago_ids = fields.One2many(
    #     'account.payment', 'pago_id', track_visibility='onchange')
    

    # fondo_reserva = fields.Monetary(
    #     string='Fondo Reserva', currency_field='currency_id')

    # iva = fields.Monetary(
    #     string='Iva ', currency_field='currency_id')
    
    # referencia = fields.Char(String='Referencia')

    # saldo_cuota_capital = fields.Monetary(
    #     string='Saldo cuota capital', currency_field='currency_id')
    # saldo_cuota_administrativa = fields.Monetary(
    #     string='Saldo cuota adm ', currency_field='currency_id')
    # saldo_fondo_reserva = fields.Monetary(
    #     string='Saldo fondo de reserva ', currency_field='currency_id')
    
    # saldo_iva = fields.Monetary(
    #     string='Saldo Iva ', currency_field='currency_id')
    
    # saldo_programado = fields.Monetary(
    #     string='Saldo Programado ', currency_field='currency_id')
    
    # saldo_seguro = fields.Monetary(
    #     string='Saldo Seguro ', currency_field='currency_id')
    
    # saldo_rastreo = fields.Monetary(
    #     string='Saldo rastreo ', currency_field='currency_id')
    
    # saldo_otros = fields.Monetary(
    #     string='Saldo Otros ', currency_field='currency_id')
    
    # saldo_tabla = fields.Monetary(
    #     string='Saldo Tabla ', currency_field='currency_id')

    # @api.depends("seguro","rastreo","otro","pago_ids")
    # def calcular_monto_pagado(self):

    #     for l in self:
    #         monto=sum(l.pago_ids.mapped("amount"))
    #         l.monto_pagado=monto

    #         l.saldo=l.cuota_capital+ l.seguro+ l.rastreo + l.otro


        @api.multi
    def crear_detalles(self):
        viewid = self.env.ref('gzl_facturacion_electronica.estado_contrato_form').id
        return {   
            'name':'Valores a Pagar',
            'view_type':'form',
            'views' : [(viewid,'form')],
            'res_model':'contrato.estado.cuenta.payment',
            'res_id':self.id,
            'type':'ir.actions.act_window',
            'target':'new',
            }

# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class EntegaVehiculo(models.Model):
    _name = 'entrega.vehiculo'
    _description = 'Enrega Vehiculo'
    _rec_name = 'secuencia'


    secuencia = fields.Char(index=True)
    requisitosPoliticasCredito = fields.Text(string='Informacion Cobranzas')

    archivo = fields.Binary(string='Archivo')
    
    active = fields.Boolean(string='Activo', default=True)
    estado = fields.Selection(selection=[
        ('borrador', 'Borrador'),
        ('revision_documentos', 'Revisión documentos'),
        ('informe_credito_cobranza', 'Informe de Crédito y Cobranza'),
        ('calificador_compra', 'Calificador para compra del bien'),
        ('liquidacion_orden_compra', 'Liquidación de compra y orden de compra'),
        ('entrega_vehiculo', 'Entrega de Vehiculo'),
        ], string='Estado', default='borrador')

    documentos  = fields.Binary(string='Carga Documentos')
    rh_cargas_ids = fields.One2many('l.cargas', 'employee_id', string='Cargas')
    nombreSocioAdjudicado = fields.Many2one('res.partner',string="Nombre del Socio Adj.")
    documentoIdentidad = fields.One2many('res.partner', 'nombreSocioAdjudicado', string='Cédula de ciudad')

    @api.model
    def create(self, vals):
        vals['secuencia'] = self.env['ir.sequence'].next_by_code('entrega.vehiculo')
        res = self.env['res.config.settings'].sudo(1).search([], limit=1, order="id desc")
        vals['requisitosPoliticasCredito'] = res.requisitosPoliticasCredito
        return super(EntegaVehiculo, self).create(vals)

    
    @api.constrains('cliente', 'secuencia')
    def constrains_valor_por_defecto(self): 
        res = self.env['res.config.settings'].sudo(1).search([], limit=1, order="id desc")
        self.requisitosPoliticasCredito= res.requisitosPoliticasCredito


""" class ContratoEstadoCuenta(models.Model):
    _name = 'contrato.estado.cuenta'
    _description = 'Contrato - Tabla de estado de cuenta de Aporte'

    contrato_id = fields.Many2one('contrato')
    numero_cuota = fields.Char(String='Número de Cuota')
    fecha = fields.Date(String='Fecha Pago')
    fecha_pagada = fields.Date(String='Fecha Pagada')
    currency_id = fields.Many2one('res.currency', readonly=True, default=lambda self: self.env.company.currency_id)
    cuota_capital = fields.Monetary(string='Cuota Capital', currency_field='currency_id')
    cuota_adm = fields.Monetary(string='Cuota Adm', currency_field='currency_id')
    factura_id = fields.Many2one('account.move', string='Factura')
    # pago_ids = fields.Many2many('account.payment','contrato_estado_cuenta_payment_rel', 'estado_cuenta_id','payment_id', string='Pagos')
    seguro = fields.Monetary(string='Seguro', currency_field='currency_id')
    rastreo = fields.Monetary(string='Rastreo', currency_field='currency_id')
    otro = fields.Monetary(string='Otro', currency_field='currency_id')
    monto_pagado = fields.Monetary(string='Monto Pagado', currency_field='currency_id')
    saldo = fields.Monetary(string='Saldo', currency_field='currency_id')
    certificado = fields.Binary(string='Certificado')
    estado_pago = fields.Selection([('pendiente', 'Pendiente'), 
                                      ('pagado', 'Pagado')
                                    ],string='Estado de Pago', default='pendiente') 
     """
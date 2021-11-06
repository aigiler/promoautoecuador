# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, datetime

from odoo.exceptions import (
    Warning as UserError,
    ValidationError
)

class AccountGuiaRemision(models.Model):
    _name = 'account.guia.remision'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name =  fields.Char('Número', default="*")
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('valid', 'Validado'),
        ('sent', 'Enviado'),
        ('cancel', 'Anulado')
    ], string="Estado", default="draft", track_visibility="onchange")
    company_id = fields.Many2one('res.company', string="Compania", default=lambda self: self.env.company.id)
    transporter_id = fields.Many2one('res.partner', string="Transportista", domain=[('is_transporter', '=', True)] )
    auth_id = fields.Many2one('establecimiento', 'Establecimiento')
    date = fields.Date("Fecha", default=date.today())
    guia_remision_line_ids = fields.One2many('account.guia.remision.line', inverse_name = 'guia_id')
    placa = fields.Char('Placa')
    partner_id = fields.Many2one('res.partner', string="Empresa")
    date_start = fields.Date('Fecha inicio')
    date_end = fields.Date('Fecha fin')
    transportation_company = fields.Char('Empresa Transportadora')
    commentary = fields.Text(string='Comentario')
    is_electronic = fields.Boolean('Es Electrónico?')
    ######## TRIBUTACION
    respuesta_sri = fields.Char('Respuesta SRI')
    clave_acceso_sri = fields.Char('Clave de Acceso')
    numero_autorizacion_sri = fields.Char('Número de Autorización SRI')
    fecha_autorizacion_sri = fields.Char('Fecha de Autorización')
    estado_autorizacion_sri = fields.Selection([('PPR', 'En procesamiento'), 
                                                ('AUT', 'Autorizado'),
                                                ('NAT', 'No Autorizado'),],
                                    string='Estado de Autorización del Sri')

    def validate(self):
            self.name="%s%s%09s"%(self.auth_id.serie_establecimiento,self.auth_id.serie_emision,self.auth_id.sequence_id.next_by_id())
            for line in self.guia_remision_line_ids:
                if line.invoice_id:
                    line.invoice_id.guia_ids = [(4,self.id)]
            return self.write({ 'state': 'valid'})
    

    def cancel(self):
        return self.write({ 'state': 'cancel'})


class AccountGuiaRemisionLine(models.Model):
    _name = 'account.guia.remision.line'

    guia_id = fields.Many2one('account.guia.remision', string = 'Guia de Remisión')
    picking_id = fields.Many2one('stock.picking', 'Despacho')
    partner_id = fields.Many2one('res.partner', related='picking_id.partner_id', readonly=True)
    invoice_id = fields.Many2one('account.move', string="Factura")
    exit_route = fields.Char('Ruta de Salida')
    arrival_route = fields.Char('Ruta de Llegada')
    motivo_id = fields.Many2one('reason.guia.remision', string="Motivo")
    origin = fields.Char('Documento Origen', related='picking_id.origin')
    documento_aduanero = fields.Char('Documento Aduanero')
    cod_establecimiento_destino = fields.Char('Codigo Establecimiento Destino')

    guia_remision_line_quantity_ids = fields.One2many('detalle.productos.guia.remision', inverse_name = 'linea_guia_id')




    @api.onchange('picking_id')
    def find_rel_invoice(self):
        invoice_obj = self.env['account.move']
        for s in self:
            if s.picking_id and s.picking_id.sale_id:
                ref = s.picking_id.sale_id.name   
                invoice_ids = invoice_obj.search([('invoice_origin','=', ref)])  
                for line in invoice_ids:
                    if line.journal_id and line.journal_id.auth_out_invoice_id and line.journal_id.auth_out_invoice_id.is_electronic and line.numero_autorizacion:
                        s.invoice_id = line[0]
                        break
                    elif line.journal_id and line.journal_id.auth_out_invoice_id and not line.journal_id.auth_out_invoice_id.is_electronic and line.auth_number:
                        s.invoice_id = line[0]
                        break





class DetalleProductosGuiaRemision(models.Model):
    _name = 'detalle.productos.guia.remision'
    _description = 'detalle de cantidad por linea'
    

    linea_guia_id = fields.Many2one('account.guia.remision.line', string = 'linea')
    product_id= fields.Many2one('product.product', string="Producto")
    cantidad = fields.Float('Cantidad')




class ReasonGuiaRemision(models.Model):
    _name = 'reason.guia.remision'
    _description = 'Motivos de la Guia de Remisión'
    _rec_name = 'name'
    
    name = fields.Char(string='Motivo')
    active = fields.Boolean(string="Activo", default=True)
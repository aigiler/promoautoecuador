# -*- coding: utf-8 -*-
from datetime import date
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class EntegaVehiculo(models.Model):
    _name = 'entrega.vehiculo'
    _description = 'Enrega Vehiculo'
    _rec_name = 'secuencia'


    secuencia = fields.Char(index=True)
    requisitosPoliticasCredito = fields.Text(string='Informacion Cobranzas')

    documentos = fields.Many2many('ir.attachment', string='Carga Documentos')
    
    active = fields.Boolean(string='Activo', default=True)
    state = fields.Selection(selection=[
        ('borrador', 'Borrador'),
        ('revision_documentos', 'Revisión documentos'),
        ('informe_credito_cobranza', 'Informe de Crédito y Cobranza'),
        ('calificador_compra', 'Calificador para compra del bien'),
        ('liquidacion_orden_compra', 'Liquidación de compra y orden de compra'),
        ('entrega_vehiculo', 'Entrega de Vehiculo'),
        ], string='Estado', default='borrador')

    nombreSocioAdjudicado = fields.Many2one('res.partner',string="Nombre del Socio Adj.")
    codigoAdjudicado = fields.Char(related="nombreSocioAdjudicado.codigo_cliente", string='Código')
    fechaNacimientoAdj  = fields.Date(related="nombreSocioAdjudicado.fecha_nacimiento", string='Fecha de Nacimiento')
    vatAdjudicado = fields.Char(related="nombreSocioAdjudicado.vat", string='Cedula de Ciudadanía')
    estadoCivilAdj  = fields.Char(related="nombreSocioAdjudicado.estado_civil")
    edadAdjudicado  = fields.Integer(string="Edad")
    #cargasFamAdj  = fields.Integer(related="nombreSocioAdjudicado.num_cargas_familiares")

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


    def calcular_edad(fechaNacimientoAdj):
        today = date.today()
        return today.year - fechaNacimientoAdj.year - ((today.month, today.day) < (fechaNacimientoAdj.month, fechaNacimientoAdj.day))

    
    def cambio_estado_boton_borrador(self):
        return self.write({"state": "revision_documentos"})

    def cambio_estado_boton_revision(self):
        return self.write({"state": "informe_credito_cobranza"})
    
    def cambio_estado_boton_informe(self):
        return self.write({"state": "calificador_compra"})
    
    def cambio_estado_boton_caificador(self):
        return self.write({"state": "liquidacion_orden_compra"})
    
    def cambio_estado_boton_liquidacion(self):
        return self.write({"state": "entrega_vehiculo"})
    
    def cambio_estado_boton_entrega(self):
        return self.write({"state": "entrega_vehiculo"})





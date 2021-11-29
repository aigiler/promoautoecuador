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
    # datos del socio adjudicado
    nombreSocioAdjudicado = fields.Many2one('res.partner',string="Nombre del Socio Adj.")
    codigoAdjudicado = fields.Char(related="nombreSocioAdjudicado.codigo_cliente", string='Código')
    fechaNacimientoAdj  = fields.Date(related="nombreSocioAdjudicado.fecha_nacimiento", string='Fecha de Nacimiento', default=date.today())
    vatAdjudicado = fields.Char(related="nombreSocioAdjudicado.vat", string='Cedula de Ciudadanía')
    estadoCivilAdj  = fields.Selection(related="nombreSocioAdjudicado.estado_civil")
    edadAdjudicado  = fields.Integer(compute='calcular_edad', string="Edad")
    cargasFamiliares = fields.Integer( string="Cargas Fam.")
    # datos del conyuge
    nombreConyuge = fields.Char(string="Nombre del Conyuge")
    fechaNacimientoConyuge = fields.Date(string='Fecha de Nacimiento')
    vatConyuge = fields.Char(related="nombreSocioAdjudicado.vat", string='Cedula de Ciudadanía')
    estadoCivilConyuge = fields.Selection(related="nombreSocioAdjudicado.estado_civil")
    edadConyuge  = fields.Integer(compute='calcular_edad_conyuge', string="Edad")

    #datos domiciliarios
    referenciaDomiciliaria = fields.Text(string='Referencias indican:')

    #datos laborales
    referenciaLaborales = fields.Text(string='Referencias indican:')

    #datos del patrimonio del socio
    montoAhorroInversiones =  fields.Float(string='Ahorro o Inversiones')
    casaValor  = fields.Float(string='Casa Valor',digits=(6, 2), default=0.00)
    terrenoValor  = fields.Float(string='Terreno Valor',digits=(6, 2), default=0.00)
    montoMueblesEnseres = fields.Float(string='Muebles y Enseres',digits=(6, 2), default=0.00)
    vehiculoValor = fields.Float(string='Vehiculo Valor', digits=(6, 2), default=0.00)
    inventarios  = fields.Float(string='Inventarios', digits=(6, 2), default=0.00)
    institucionFinanciera = fields.Char(string='Institución')
    direccion = fields.Char(string='Direccion')
    direccion1 = fields.Char(string='Direccion')
    placa  = fields.Char(string='Placa')

    totalActivosAdj = fields.Float(compute='calcular_total_activos', string='TOTAL ACTIVOS', digits=(6, 2))

    def calcular_total_activos(self):
        totalActivos = 0
        for rec in self:
            totalActivos = rec.montoAhorroInversiones + rec.casaValor + rec.terrenoValor + rec.vehiculoValor + rec.montoMueblesEnseres + rec.inventarios
            rec.totalActivosAdj = totalActivos
        
        
    def calcular_edad(self):
        edad = 0  
        for rec in self:
            today = date.today()
            
            if rec.fechaNacimientoConyuge != False:
                edad = today.year - rec.fechaNacimientoAdj.year - ((today.month, today.day) < (rec.fechaNacimientoAdj.month, rec.fechaNacimientoAdj.day))
                rec.edadAdjudicado =edad
            else:
                rec.edadAdjudicado = 0
            rec.edadAdjudicado =edad
   
    @api.onchange(fechaNacimientoConyuge)
    def calcular_edad_conyuge(self): 
        edad = 0 
        for rec in self:
            today = date.today()
            if rec.fechaNacimientoConyuge != False:
                edad = today.year - rec.fechaNacimientoConyuge.year - ((today.month, today.day) < (rec.fechaNacimientoConyuge.month, rec.fechaNacimientoConyuge.day))
                rec.edadAdjudicado =edad
            else:
                rec.edadAdjudicado = 0
        rec.edadAdjudicado =edad

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





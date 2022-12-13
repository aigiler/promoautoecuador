# -*- coding: utf-8 -*-
import datetime

from datetime import datetime, timedelta
from datetime import date, timedelta
from email.policy import default
from logging import StringTemplateStyle
import logging
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

from dateutil.parser import parse


class Partner(models.Model):   
    _inherit = 'res.partner'    

    tipo=fields.Selection(selection=[
                    ('concesionrio', 'Concesionario'),
                    ('patio', 'Patio'),
                    ('tercero', 'Tercero'),
                    ('preAdjudicado', 'preAdjudicado'),
                    ], string='Tipo de Proveedor')

    monto = fields.Float(string='Monto')
    direccion = fields.Text(string='Dirección')
    streetConyuge = fields.Text(string='DirecciónConyuge')

    id_cliente = fields.Char(string='ID Cliente')
    tipo_contrato = fields.Many2one("tipo.contrato.adjudicado", String="Tipo de Contrato")
    codigo_cliente = fields.Char(string='Código Cliente')
    mobileConyuge = fields.Char(string='Celular Conyuge')
    ciudadConyuge = fields.Char(string='Ciudad Conyuge')

    fecha_nacimiento  = fields.Date(string='Fecha de nacimiento')
    state_conyuge_id=fields.Many2one("res.country.state", string="Provincia del Conyuge")
    estado_civil = fields.Selection(selection=[
                    ('soltero', 'Soltero/a'),
                    ('union_libre', 'Unión libre'),
                    ('casado', 'Casado/a'),
                    ('divorciado', 'Divorciado/a'),
                    ('viudo', 'Viudo/a')                    
                    ], string='Estado Civil', default='soltero')
    num_cargas_familiares = fields.Integer(string='Cargas Familiares')
    emailConyuge = fields.Integer(string='Email Conyuge')
    comisionFacturaConcesionario = fields.Float(string="COMISION FACTURA A NOMBRE CONCESIONARIO")

    conyuge=fields.Char(string='Nombre del Conyuge')
    dependiente=fields.Char(string='Dependiente')
    dependienteConyuge=fields.Char(string='Dependiente Conyuge')
    phoneConyuge=fields.Char(string='Telefono Conyuge')

    fechaNacimientoConyuge = fields.Date(string='Fecha de Nacimiento Conyuge')
    vatConyuge = fields.Char(string='Cedula de Ciudadanía Conyuge')
    direccion_trabajo=fields.Char(string='Dirección Laboral')
    nombre_compania=fields.Char(string='Compañia')
    telefono_trabajo=fields.Char(string='Telefono')
    emailContabilidad=fields.Char(string='Email Contabilidad')
    emailFinanciero=fields.Char(string='Email Financiero')
    emailComercial=fields.Char(string='Email Comercial')
    cargo=fields.Char(string='Cargo')
    cargoConyuge=fields.Char(string='Cargo Conyuge')

    property_account_payable_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Payable",
        domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]",
        required=False)
    property_account_receivable_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Receivable",
        domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]",
        required=False)

class EntegaVehiculo(models.Model):
    _name = 'entrega.vehiculo'
    _description = 'Entrega Vehiculo'
    _rec_name = 'secuencia'
    _inherit = ['mail.thread', 'mail.activity.mixin']



    nombreSocioAdjudicado = fields.Many2one('res.partner', string="Nombre del Socio Adj.", track_visibility='onchange')

    correoAdj = fields.Char(string='Correo Adjudicado',store=True, default='')

    @api.constrains("correoAdj")
    @api.onchange("correoAdj")
    def actualizar_correo_adj(self):
        for l in self:
            if l.correoAdj:
                l.nombreSocioAdjudicado.email=l.correoAdj

    telefonoAdj = fields.Char(string='Telefono Adjudicado',store=True, default='')

    @api.constrains("telefonoAdj")
    @api.onchange("telefonoAdj")
    def actualizar_telefono_adj(self):
        for l in self:
            if l.telefonoAdj:
                l.nombreSocioAdjudicado.phone=l.telefonoAdj

    provinciaAdjudicado = fields.Many2one("res.country.state", string='State')

    @api.constrains("provinciaAdjudicado")
    @api.onchange("provinciaAdjudicado")
    def actualizar_provincia_adj(self):
        for l in self:
            if l.provinciaAdjudicado:
                l.nombreSocioAdjudicado.state_id=l.provinciaAdjudicado.id

    direccionAdjudicado = fields.Char('Direccion')

    @api.constrains("direccionAdjudicado")
    @api.onchange("direccionAdjudicado")
    def actualizar_direccion_adj(self):
        for l in self:
            if l.direccionAdjudicado:
                l.nombreSocioAdjudicado.street=l.direccionAdjudicado

    dependienteAdj = fields.Char(string='Dependiente Adjudicado',store=True, default='')

    @api.constrains("dependienteAdj")
    @api.onchange("dependienteAdj")
    def actualizar_dependiente_adj(self):
        for l in self:
            if l.dependienteAdj:
                l.nombreSocioAdjudicado.dependiente=l.dependienteAdj

    cargoAdj=fields.Char(string='Cargo')

    @api.constrains("cargoAdj")
    @api.onchange("cargoAdj")
    def actualizar_car_adj(self):
        for l in self:
            if l.cargoAdj:
                l.nombreSocioAdjudicado.cargo=l.cargoAdj

    ingresosFamiliares = fields.Monetary(string='Ingresos familiares')

    edadAdjudicado = fields.Integer(compute='calcular_edad', string="Edad", readonly=True, store=True, default = 0)

    vatAdjudicado = fields.Char(string='Cedula de Ciudadanía',store=True, default='')

    @api.constrains("vatAdjudicado")
    @api.onchange("vatAdjudicado")
    def actualizar_cedula_adj(self):
        for l in self:
            if l.vatAdjudicado:
                l.nombreSocioAdjudicado.vat=l.vatAdjudicado

    fechaNacimientoAdj = fields.Date(string='Fecha de Nacimiento', store=True)

    @api.constrains("fechaNacimientoAdj")
    @api.onchange("fechaNacimientoAdj")
    def actualizar_fecha_nac_adj(self):
        for l in self:
            if l.fechaNacimientoAdj:
                l.nombreSocioAdjudicado.fecha_nacimiento=l.fechaNacimientoAdj

    @api.constrains("estadoCivilAdj")
    @api.onchange("estadoCivilAdj")
    def actualizar_estado_civ_adj(self):
        for l in self:
            if l.estadoCivilAdj:
                l.nombreSocioAdjudicado.estado_civil=l.estadoCivilAdj
                l.estadoCivilConyuge=l.estadoCivilAdj

    celularAdj = fields.Char(string='Telefono Adjudicado',store=True, default='')

    @api.constrains("celularAdj")
    @api.onchange("celularAdj")
    def actualizar_telefono_adj(self):
        for l in self:
            if l.celularAdj:
                l.nombreSocioAdjudicado.mobile=l.celularAdj


    ciudadAdjudicado = fields.Char('Ciudad')
    @api.constrains("ciudadAdjudicado")
    @api.onchange("ciudadAdjudicado")
    def actualizar_ciudad_adj(self):
        for l in self:
            if l.ciudadAdjudicado:
                l.nombreSocioAdjudicado.city=l.ciudadAdjudicado

    nombreConyuge = fields.Char(string="Nombre del Conyuge", store=True)

    @api.constrains("nombreConyuge")
    @api.onchange("nombreConyuge")
    def actualizar_conyuge_adj(self):
        for l in self:
            if l.nombreConyuge:
                l.nombreSocioAdjudicado.conyuge=l.nombreConyuge

    fechaNacimientoConyuge = fields.Date(string='Fecha de Nacimiento',store=True)

    @api.constrains("fechaNacimientoConyuge")
    @api.onchange("fechaNacimientoConyuge")
    def actualizar_nac_conyuge_adj(self):
        for l in self:
            if l.fechaNacimientoConyuge:
                l.nombreSocioAdjudicado.fechaNacimientoConyuge=l.fechaNacimientoConyuge

    correoConyuge = fields.Char(string='Correo Conyuge',store=True, default='')

    @api.constrains("correoConyuge")
    @api.onchange("correoConyuge")
    def actualizar_correo_conyuge_adj(self):
        for l in self:
            if l.correoConyuge:
                l.nombreSocioAdjudicado.emailConyuge=l.correoConyuge

    telefonoConyuge = fields.Char(string='Telefono Conyuge',store=True, default='')

    @api.constrains("telefonoConyuge")
    @api.onchange("telefonoConyuge")
    def actualizar_telefono_conyuge_adj(self):
        for l in self:
            if l.telefonoConyuge:
                l.nombreSocioAdjudicado.phoneConyuge=l.telefonoConyuge

    provinciaConyuge = fields.Many2one("res.country.state", string='State')

    @api.constrains("provinciaConyuge")
    @api.onchange("provinciaConyuge")
    def actualizar_provincia_conyuge_adj(self):
        for l in self:
            if l.provinciaConyuge:
                l.nombreSocioAdjudicado.state_conyuge_id=l.provinciaConyuge.id

    direccionConyuge = fields.Char('Direccion')
    @api.constrains("direccionConyuge")
    @api.onchange("direccionConyuge")
    def actualizar_direccion_conyuge_adj(self):
        for l in self:
            if l.direccionConyuge:
                l.nombreSocioAdjudicado.streetConyuge=l.direccionConyuge

    dependienteConyuge = fields.Char(string='Dependiente Conyuge',store=True, default='')

    @api.constrains("dependienteConyuge")
    @api.onchange("dependienteConyuge")
    def actualizar_dependiente_conyuge_adj(self):
        for l in self:
            if l.dependienteConyuge:
                l.nombreSocioAdjudicado.dependienteConyuge=l.dependienteConyuge

    cargoConyuge=fields.Char(string='Cargo')

    @api.constrains("cargoConyuge")
    @api.onchange("cargoConyuge")
    def actualizar_car_conyuge_adj(self):
        for l in self:
            if l.cargoConyuge:
                l.nombreSocioAdjudicado.cargoConyuge=l.cargoConyuge

    ingresosFamiliaresConyuge = fields.Monetary(string='Ingresos familiares')

    edadConyuge = fields.Integer(compute='calcular_edad_conyuge', string="Edad", default = 0)

    vatConyuge = fields.Char(string='Cedula de Ciudadanía', store=True)

    @api.constrains("vatConyuge")
    @api.onchange("vatConyuge")
    def actualizar_vat_conyuge_adj(self):
        for l in self:
            if l.vatConyuge:
                l.nombreSocioAdjudicado.vatConyuge=l.vatConyuge

    estadoCivilConyuge = fields.Selection(selection=[
                    ('soltero', 'Soltero/a'),
                    ('union_libre', 'Unión libre'),
                    ('casado', 'Casado/a'),
                    ('divorciado', 'Divorciado/a'),
                    ('viudo', 'Viudo/a')                    
                    ], string='Estado Civil', default='soltero')

    celularConyuge = fields.Char(string='Celular', store=True)
    @api.constrains("celularConyuge")
    @api.onchange("celularConyuge")
    def actualizar_celular_conyuge_adj(self):
        for l in self:
            if l.celularConyuge:
                l.nombreSocioAdjudicado.mobileConyuge=l.celularConyuge

    ciudadConyuge = fields.Char('Ciudad')
    @api.constrains("ciudadConyuge")
    @api.onchange("ciudadConyuge")
    def actualizar_ciudad_conyuge_adj(self):
        for l in self:
            if l.ciudadConyuge:
                l.nombreSocioAdjudicado.cityConyuge=l.ciudadConyuge

    montoAhorroInversiones = fields.One2many('items.patrimonio.entrega.vehiculo','entrega_id',domain=[('garante','=',False)] ,track_visibility='onchange')

    ingresosIds = fields.One2many('ingresos.financiero.entrega.vehiculo','entrega_id',domain=[('garante','=',False)] ,track_visibility='onchange')

    egresosIds = fields.One2many('egresos.financiero.entrega.vehiculo','entrega_id',domain=[('garante','=',False)] ,track_visibility='onchange')

    total_ingresos_familiares = fields.Monetary(string='Total Ingresos Familiares')

    total_egresos_familiares = fields.Monetary(string='Total Egresos Familiares')

    disponibilidad_dinero= fields.Monetary(string='Total Dispinible')

    referencias_familiares_ids=fields.One2many('referencias.familiares','entrega_id',domain=[('garante','=',False)] ,track_visibility='onchange')
    referencias_bancarias_ids=fields.One2many('referencias.bancarias','entrega_id',domain=[('garante','=',False)] ,track_visibility='onchange')



    necesidadIds = fields.One2many('necesidad.adjudicado','entrega_id',domain=[('garante','=',False)] ,track_visibility='onchange')

    estadoVehiculo = fields.Selection(selection=[
                    ('USADO', 'USADO'),
                    ('NUEVO', 'NUEVO'),
                    ], string='Estado Vehiculo', default='')

    publico=fields.Boolean(string="Público")

    particular=fields.Boolean(string="Particular")
    detalleVehiculoIds = fields.One2many('detalle.necesidad.adjudicado','entrega_id',domain=[('garante','=',False)] ,track_visibility='onchange')

    @api.onchange("nombreSocioAdjudicado")
    @api.constrains("nombreSocioAdjudicado")
    def obtener_datos(self):
        for l in self:
            if l.nombreSocioAdjudicado:
                l.vatAdjudicado=l.nombreSocioAdjudicado.vat
                l.fechaNacimientoAdj=l.nombreSocioAdjudicado.fecha_nacimiento
                l.estadoCivilAdj=l.nombreSocioAdjudicado.estado_civil
                l.estadoCivilConyuge=l.nombreSocioAdjudicado.estado_civil
                l.codigoAdjudicado=l.nombreSocioAdjudicado.codigo_cliente
                l.cargasFamiliares=l.nombreSocioAdjudicado.num_cargas_familiares
                l.nombreConyuge=l.nombreSocioAdjudicado.conyuge
                l.fechaNacimientoConyuge=l.nombreSocioAdjudicado.fechaNacimientoConyuge
                l.vatConyuge=l.nombreSocioAdjudicado.vatConyuge
                l.ciudadAdjudicado=l.nombreSocioAdjudicado.city
                l.provinciaAdjudicado=l.nombreSocioAdjudicado.state_id.id
                l.direccionAdjudicado=l.nombreSocioAdjudicado.street
                l.direccion_trabajoAdj=l.nombreSocioAdjudicado.direccion_trabajo
                l.telefono_trabajoAdj=l.nombreSocioAdjudicado.telefono_trabajo
                l.cargoAdj=l.nombreSocioAdjudicado.cargo
                l.nombre_companiaAdj=l.nombreSocioAdjudicado.nombre_compania








    nombreGarante = fields.Many2one('res.partner', string="Nombre del Garante", track_visibility='onchange')

    fechaNacimientoGarante = fields.Date(string='Fecha de Nacimiento', store=True)

    correoGarante = fields.Char(string='Correo Garante',store=True, default='')

    @api.constrains("correoGarante")
    @api.onchange("correoGarante")
    def actualizar_correo_gar(self):
        for l in self:
            if l.correoGarante:
                l.nombreGarante.email=l.correoGarante

    telefonoGar = fields.Char(string='Telefono Garante',store=True, default='')

    @api.constrains("telefonoGar")
    @api.onchange("telefonoGar")
    def actualizar_telefono_gar(self):
        for l in self:
            if l.telefonoGar:
                l.nombreGarante.phone=l.telefonoGar


    provinciaGarante = fields.Many2one("res.country.state", string='State')

    @api.constrains("provinciaGarante")
    @api.onchange("provinciaGarante")
    def actualizar_provincia_conyuge_gar(self):
        for l in self:
            if l.provinciaGarante:
                l.nombreGarante.state_id=l.provinciaGarante.id

    direccionGarante = fields.Char('Direccion')
    @api.constrains("direccionGarante")
    @api.onchange("direccionGarante")
    def actualizar_direccion_gar(self):
        for l in self:
            if l.direccionGarante:
                l.nombreGarante.street=l.direccionGarante

    dependienteGar = fields.Char(string='Dependiente Garante',store=True, default='')

    @api.constrains("dependienteGar")
    @api.onchange("dependienteGar")
    def actualizar_dependiente_gar(self):
        for l in self:
            if l.dependienteGar:
                l.nombreGarante.dependiente=l.dependienteGar

    cargoGar=fields.Char(string='Cargo')

    @api.constrains("cargoGar")
    @api.onchange("cargoGar")
    def actualizar_car_gar(self):
        for l in self:
            if l.cargoGar:
                l.nombreGarante.cargo=l.cargoGar

    ingresosFamiliaresGarante = fields.Monetary(string='Ingresos familiares')

    edadGarante = fields.Integer(compute='calcular_edad_Garante', string="Edad", readonly=True, store=True, default = 0)

    vatGarante = fields.Char(string='Cedula de Ciudadanía',store=True, default='')

    estadoCivilGarante = fields.Selection(selection=[
                    ('soltero', 'Soltero/a'),
                    ('union_libre', 'Unión libre'),
                    ('casado', 'Casado/a'),
                    ('divorciado', 'Divorciado/a'),
                    ('viudo', 'Viudo/a')                    
                    ], string='Estado Civil', default='soltero')

    celularGar = fields.Char(string='Telefono Garante',store=True, default='')

    @api.constrains("celularGar")
    @api.onchange("celularGar")
    def actualizar_celular_gar(self):
        for l in self:
            if l.celularGar:
                l.nombreGarante.mobile=l.celularGar


    ciudadGarante = fields.Char('Ciudad')
    @api.constrains("ciudadGarante")
    @api.onchange("ciudadGarante")
    def actualizar_ciudad_gar(self):
        for l in self:
            if l.ciudadGarante:
                l.nombreGarante.city=l.ciudadGarante

    fechaNacimientoConyugeGarante = fields.Date(string='Fecha de Nacimiento',store=True)

    @api.constrains("fechaNacimientoConyugeGarante")
    @api.onchange("fechaNacimientoConyugeGarante")
    def actualizar_nac_conyuge_gar(self):
        for l in self:
            if l.fechaNacimientoConyugeGarante:
                l.nombreGarante.fechaNacimientoConyuge=l.fechaNacimientoConyugeGarante


    correoConyugeGarante = fields.Char(string='Correo Conyuge',store=True, default='')

    @api.constrains("correoConyugeGarante")
    @api.onchange("correoConyugeGarante")
    def actualizar_correo_conyuge_gar(self):
        for l in self:
            if l.correoConyugeGarante:
                l.nombreGarante.emailConyuge=l.correoConyugeGarante

    nombreConyugeGarante = fields.Char(string="Nombre del Conyuge", store=True)

    direccionConyugeGarante = fields.Char('Direccion')
    @api.constrains("direccionConyugeGarante")
    @api.onchange("direccionConyugeGarante")
    def actualizar_direccion_conyuge_gar(self):
        for l in self:
            if l.direccionConyugeGarante:
                l.nombreGarante.streetConyuge=l.direccionConyugeGarante


    telefonoConyugeGarante = fields.Char(string='Telefono Conyuge',store=True, default='')

    @api.constrains("telefonoConyugeGarante")
    @api.onchange("telefonoConyugeGarante")
    def actualizar_telefono_conyuge_gar(self):
        for l in self:
            if l.telefonoConyugeGarante:
                l.nombreGarante.phoneConyuge=l.telefonoConyugeGarante


    provinciaConyugeGarante = fields.Many2one("res.country.state", string='State')

    @api.constrains("provinciaConyugeGarante")
    @api.onchange("provinciaConyugeGarante")
    def actualizar_provincia_conyuge_gar(self):
        for l in self:
            if l.provinciaConyugeGarante:
                l.nombreGarante.state_conyuge_id=l.provinciaConyugeGarante.id


    dependienteConyugeGarante = fields.Char(string='Dependiente Conyuge',store=True, default='')

    @api.constrains("dependienteConyugeGarante")
    @api.onchange("dependienteConyugeGarante")
    def actualizar_dependiente_conyuge_gar(self):
        for l in self:
            if l.dependienteConyugeGarante:
                l.nombreGarante.dependienteConyuge=l.dependienteConyugeGarante


    cargoConyugeGarante=fields.Char(string='Cargo')

    @api.constrains("cargoConyugeGarante")
    @api.onchange("cargoConyugeGarante")
    def actualizar_car_conyuge_gar(self):
        for l in self:
            if l.cargoConyugeGarante:
                l.nombreGarante.cargoConyuge=l.cargoConyugeGarante

    ingresosFamiliaresConyugeGarante = fields.Monetary(string='Ingresos familiares')

    edadConyugeGarante = fields.Integer(compute='calcular_edad_conyuge', string="Edad", default = 0)

    vatConyugeGarante = fields.Char(string='Cedula de Ciudadanía', store=True)

    @api.constrains("vatConyugeGarante")
    @api.onchange("vatConyugeGarante")
    def actualizar_vat_conyuge_gar(self):
        for l in self:
            if l.vatConyugeGarante:
                l.nombreGarante.vatConyuge=l.vatConyugeGarante

    estadoCivilConyugeGarante = fields.Selection(selection=[
                    ('soltero', 'Soltero/a'),
                    ('union_libre', 'Unión libre'),
                    ('casado', 'Casado/a'),
                    ('divorciado', 'Divorciado/a'),
                    ('viudo', 'Viudo/a')                    
                    ], string='Estado Civil', default='soltero')

    celularConyugeGarante = fields.Char(string='Celular', store=True)
    @api.constrains("celularConyugeGarante")
    @api.onchange("celularConyugeGarante")
    def actualizar_celular_conyuge_gar(self):
        for l in self:
            if l.celularConyugeGarante:
                l.nombreGarante.mobileConyuge=l.celularConyugeGarante

    ciudadConyugeGarante = fields.Char('Ciudad')
    @api.constrains("ciudadConyugeGarante")
    @api.onchange("ciudadConyugeGarante")
    def actualizar_ciudad_conyuge_adj(self):
        for l in self:
            if l.ciudadConyugeGarante:
                l.nombreGarante.cityConyuge=l.ciudadConyugeGarante

    montoAhorroInversionesGarante = fields.One2many('items.patrimonio.entrega.vehiculo','entrega_id',domain=[('garante','=',True)], track_visibility='onchange')

    ingresosIdsGarante = fields.One2many('ingresos.financiero.entrega.vehiculo','entrega_id',domain=[('garante','=',True)], track_visibility='onchange')

    egresosIdsGarante = fields.One2many('egresos.financiero.entrega.vehiculo','entrega_id',domain=[('garante','=',True)], track_visibility='onchange')


    total_ingresos_familiares_garante = fields.Monetary(string='Total Ingresos Familiares')
    total_egresos_familiares_garante = fields.Monetary(string='Total Egresos Familiares')
    disponibilidad_dinero_garante= fields.Monetary(string='Total Dispinible')


    referencias_familiares_ids_garante=fields.One2many('referencias.familiares','entrega_id',domain=[('garante','=',True)] ,track_visibility='onchange')
    referencias_bancarias_ids_garante=fields.One2many('referencias.bancarias','entrega_id',domain=[('garante','=',True)] ,track_visibility='onchange')

    @api.onchange('fechaNacimientoConyuge','fechaNacimientoConyugeGarante')
    def calcular_edad_conyuge(self):
        edad = 0
        self.edadConyugeGarante = 0
        self.edadConyuge=0
        for rec in self:
            today = date.today()
            if rec.fechaNacimientoConyuge:
                edad = today.year - rec.fechaNacimientoConyuge.year - \
                    ((today.month, today.day) < (
                        rec.fechaNacimientoConyuge.month, rec.fechaNacimientoConyuge.day))
                rec.edadConyuge = edad
            else:
                rec.edadConyuge = 0
            if rec.fechaNacimientoConyugeGarante:
                edadGarante = today.year - rec.fechaNacimientoConyugeGarante.year - \
                    ((today.month, today.day) < (
                        rec.fechaNacimientoConyugeGarante.month, rec.fechaNacimientoConyugeGarante.day))
                rec.edadConyugeGarante = edadGarante
            else:
                rec.edadConyugeGarante = 0









    rolAsignado = fields.Many2one('adjudicaciones.team', string="Rol Asignado", track_visibility='onchange')
    rolCredito = fields.Many2one('adjudicaciones.team', string="Rol Credito", track_visibility='onchange',default=lambda self:self.env.ref('gzl_adjudicacion.tipo_rol3'))
    rolGerenciaAdmin = fields.Many2one('adjudicaciones.team', string="Rol Gerencia Admin", track_visibility='onchange',default=lambda self:self.env.ref('gzl_adjudicacion.tipo_rol1'))
    rolGerenciaFin = fields.Many2one('adjudicaciones.team', string="Rol Gerencia Financiera", track_visibility='onchange',default=lambda self:self.env.ref('gzl_adjudicacion.tipo_rol4'))
    rolAdjudicacion = fields.Many2one('adjudicaciones.team', string="Rol Adjudicacion", track_visibility='onchange',default=lambda self:self.env.ref('gzl_adjudicacion.tipo_rol2'))
    asamblea = fields.Many2one('asamblea','Asamblea del Adjudicado')

    rolcontab = fields.Many2one('adjudicaciones.team', string="Rol contabilidad Financiera", track_visibility='onchange',default=lambda self:self.env.ref('gzl_adjudicacion.tipo_rol7'))

    fecha_reserva = fields.Date(string='Fecha de Reserva')
    fecha_inscripcion = fields.Date(string='Fecha de Inscripción')
    num_inscripcion = fields.Date(string='Numero de Inscripción')
    num_repertorio = fields.Date(string='Número de Repertorio')
    secuencia = fields.Char(index=True)
    requisitosPoliticasCredito = fields.Html(string='Informacion Cobranzas', default=lambda self: self._capturar_valores_por_defecto())
    
    def _capturar_valores_por_defecto(self):
        referencia=self.env.ref('gzl_adjudicacion.configuracion_adicional1')
        return referencia.requisitosPoliticasCredito

    documentos = fields.Many2many('ir.attachment', string='Carga Documentos', track_visibility='onchange')
    active = fields.Boolean(string='Activo', default=True)
    cuv = fields.Boolean(string='CUV', default=False)
    documento_cuv=fields.Binary(string="Adjuntar CUV")
    chequeo_mecanico = fields.Boolean(string='Chequeo Mecánico', default=False)
    documento_chequeo=fields.Binary(string="Adjuntar Chequeo Mecánico")
    record_policial = fields.Boolean(string='Récord Policial', default=False)
    documento_record=fields.Binary(string="Adjuntar Record Policial")
    estado = fields.Selection(selection=[
        ('borrador', 'Borrador'),
        ('revision_documentos', 'Revisión documentos'),
        ('informe_de_créditos_y_cobranzas', 'Informe de Crédito y Cobranza'),
        ('calificador_compra', 'Calificador para compra del bien'),
        ('liquidacion_orden_compra', 'Liquidación de compra y orden de compra'),
        ('orden_compra', 'Orden de compra'),
        ('factura', 'Factura de Vehículo'),
        ('firma', 'Firma de Contrato'),
        ('legalizar', 'Legalización de Contrato'),
        ('matriculacion', 'Matriculacion, Seguro y Rastreo'),

        ('orden_salida', 'Orden de Salida'),
        ('rechazado', 'Rechazado'),

        ('entrega_vehiculo', 'Entrega de Vehículo'),
        ('finalizado', 'Finalizado'),


    ], string='Estado', default='borrador', track_visibility='onchange')
    # datos del socio adjudicado
    factura_id = fields.Many2one('account.move', string='Factura')
    archivo = fields.Binary(string='Adjuntar Documentos Adjudicado')
    archivo_garante = fields.Binary(string='Adjuntar Documento Garante')
    archivo_habilitantes = fields.Binary(string='Adjuntar Documento Habilitantes')

    compras_terceros=fields.Boolean(string="Compra a terceros")

    documentos_pagos = fields.Binary(string='Adjuntar Documento')

    pago_seguro_id=fields.Many2one("account.payment", string="Pago de Seguro")
    pago_rastreo_id=fields.Many2one("account.payment", string="Pago de Rastreo")
    pago_factura=fields.Many2one("account.payment", string="Pago de Factura")
    pago_matriculacion_id=fields.Many2one("account.payment", string="Pago de Matriculación")

    orden_compra=fields.Binary()
    orden_salida=fields.Binary()
    liquidacion_compra=fields.Binary()
    correo_id=fields.Many2one("ir.attachment")
    reserva_id=fields.Many2one("ir.attachment",string="Contrato de Reserva")
    pagare_id=fields.Many2one("ir.attachment",string="Pagaré a la Orden")

    salida_id=fields.Many2one("ir.attachment")





















    estadoCivilAdj = fields.Selection(selection=[
                    ('soltero', 'Soltero/a'),
                    ('union_libre', 'Unión libre'),
                    ('casado', 'Casado/a'),
                    ('divorciado', 'Divorciado/a'),
                    ('viudo', 'Viudo/a')                    
                    ], string='Estado Civil', default='soltero')







    codigoAdjudicado = fields.Char(string='Código', track_visibility='onchange',store=True, default=' ') 

    @api.constrains("codigoAdjudicado")
    @api.onchange("codigoAdjudicado")
    def actualizar_codigo_adj(self):
        for l in self:
            if l.codigoAdjudicado:
                l.nombreSocioAdjudicado.codigo_cliente=l.codigoAdjudicado


    cargasFamiliares = fields.Integer(string="Cargas Fam.", store=True, default = 0)

    @api.constrains("cargasFamiliares")
    @api.onchange("cargasFamiliares")
    def actualizar_cargas_adj(self):
        for l in self:
            if l.cargasFamiliares:
                l.nombreSocioAdjudicado.num_cargas_familiares=l.cargasFamiliares






















    direccion_trabajoAdj=fields.Char(string='Dirección Laboral')

    @api.constrains("direccion_trabajoAdj")
    @api.onchange("direccion_trabajoAdj")
    def actualizar_direccion_trab_adj(self):
        for l in self:
            if l.direccion_trabajoAdj:
                l.nombreSocioAdjudicado.direccion_trabajo=l.direccion_trabajoAdj

    nombre_companiaAdj=fields.Char(string='Compañia')
    
    @api.constrains("nombre_companiaAdj")
    @api.onchange("nombre_companiaAdj")
    def actualizar_compania_adj(self):
        for l in self:
            if l.nombre_companiaAdj:
                l.nombreSocioAdjudicado.nombre_compania=l.nombre_companiaAdj

    telefono_trabajoAdj=fields.Char(string='Telefono')

    @api.constrains("telefono_trabajoAdj")
    @api.onchange("telefono_trabajoAdj")
    def actualizar_telefono_adj(self):
        for l in self:
            if l.telefono_trabajoAdj:
                l.nombreSocioAdjudicado.telefono_trabajo=l.telefono_trabajoAdj


















    @api.onchange("nombreGarante")
    @api.constrains("nombreGarante")
    def obtener_datos_garante(self):
        for l in self:
            if l.nombreGarante:

                l.vatGarante=l.nombreGarante.vat
                l.fechaNacimientoGarante=l.nombreGarante.fecha_nacimiento
                l.estadoCivilGarante=l.nombreGarante.estado_civil
                l.estadoCivilConyugeGarante=l.nombreGarante.estado_civil
                l.codigoGarante=l.nombreGarante.codigo_cliente
                l.cargasFamiliaresGarante=l.nombreGarante.num_cargas_familiares
                l.nombreConyugeGarante=l.nombreGarante.conyuge
                l.fechaNacimientoConyugeGarante=l.nombreGarante.fechaNacimientoConyuge
                l.vatConyugeGarante=l.nombreGarante.vatConyuge
                l.ciudadGarante=l.nombreGarante.city
                l.provinciaGarante=l.nombreGarante.state_id.id
                l.direccionGarante=l.nombreGarante.street
                l.direccion_trabajoGar=l.nombreGarante.direccion_trabajo
                l.telefono_trabajoGar=l.nombreGarante.telefono_trabajo
                l.cargoGar=l.nombreGarante.cargo
                l.nombre_companiaGar=l.nombreGarante.nombre_compania














    @api.constrains("vatGarante")
    @api.onchange("vatGarante")
    def actualizar_cedula_gar(self):
        for l in self:
            if l.vatGarante:
                l.nombreGarante.vat=l.vatGarante



    @api.constrains("fechaNacimientoGarante")
    @api.onchange("fechaNacimientoGarante")
    def actualizar_fecha_nac_gar(self):
        for l in self:
            if l.fechaNacimientoGarante:
                l.nombreGarante.fecha_nacimiento=l.fechaNacimientoGarante




    @api.constrains("estadoCivilGarante")
    @api.onchange("estadoCivilGarante")
    def actualizar_estado_civ_gar(self):
        for l in self:
            if l.estadoCivilGarante:
                l.nombreGarante.estado_civil=l.estadoCivilGarante
                l.estadoCivilConyugeGarante=l.estadoCivilGarante

    codigoGarante = fields.Char(string='Código', track_visibility='onchange',store=True, default=' ') 

    @api.constrains("codigoGarante")
    @api.onchange("codigoGarante")
    def actualizar_codigo_gar(self):
        for l in self:
            if l.codigoGarante:
                l.nombreGarante.codigo_cliente=l.codigoGarante


    cargasFamiliaresGarante = fields.Integer(string="Cargas Fam.",  store=True, default = 0)

    @api.constrains("cargasFamiliaresGarante")
    @api.onchange("cargasFamiliaresGarante")
    def actualizar_cargas_gar(self):
        for l in self:
            if l.cargasFamiliaresGarante:
                l.nombreGarante.num_cargas_familiares=l.cargasFamiliaresGarante








    @api.constrains("nombreConyugeGarante")
    @api.onchange("nombreConyugeGarante")
    def actualizar_conyuge_gar(self):
        for l in self:
            if l.nombreConyugeGarante:
                l.nombreGarante.conyuge=l.nombreConyugeGarante






    direccion_trabajoGar=fields.Char(string='Dirección Laboral')

    @api.constrains("direccion_trabajoGar")
    @api.onchange("direccion_trabajoGar")
    def actualizar_direccion_trab_gar(self):
        for l in self:
            if l.direccion_trabajoGar:
                l.nombreGarante.direccion_trabajo=l.direccion_trabajoGar

    nombre_companiaGar=fields.Char(string='Compañia')
    
    @api.constrains("nombre_companiaGar")
    @api.onchange("nombre_companiaGar")
    def actualizar_compania_gar(self):
        for l in self:
            if l.nombre_companiaGar:
                l.nombreGarante.nombre_compania=l.nombre_companiaGar

    telefono_trabajoGar=fields.Char(string='Telefono')

    @api.constrains("telefono_trabajoGar")
    @api.onchange("telefono_trabajoGar")
    def actualizar_telefono_adj(self):
        for l in self:
            if l.telefono_trabajoGar:
                l.nombreGarante.telefono_trabajo=l.telefono_trabajoGar

    cargoGar=fields.Char(string='Cargo')

    @api.constrains("cargoGar")
    @api.onchange("cargoGar")
    def actualizar_cargo_adj(self):
        for l in self:
            if l.cargoGar:
                l.nombreGarante.cargo=l.cargoGar



    
    
    



    referencias_ids_garante=fields.One2many('referencias.familiares','entrega_id',domain=[('garante','=',True)] ,track_visibility='onchange')



    telefonosAdj = fields.Char(string='Celular')



    # datos domiciliarios
    referenciaDomiciliaria = fields.Text( string='Referencias indican:', default=' ',store=True)
    referenciaDomiciliariaGarante = fields.Text( string='Referencias indican:', default=' ',store=True)

    # datos laborales
    referenciasLaborales = fields.Text(string='Referencias indican:', default=' ',store=True)
    referenciasLaboralesGarante = fields.Text(string='Referencias indican:', default=' ',store=True)

    institucionFinanciera = fields.Many2one('res.bank',string='Institución')
    institucionFinancieraGarante = fields.Many2one('res.bank',string='Institución')
    
    direccion = fields.Char(string='Direccion de Casa' , default='')
    direccionGarante = fields.Char(string='Direccion de Casa' , default='')
    
    scoreBuroCredito = fields.Integer(string='Buró de Crédito')
    scoreBuroCreditoGarante = fields.Integer(string='Buró de Crédito')
    
    direccion1 = fields.Char(string='Direccion de Terreno', default=' ')
    direccion1Garante = fields.Char(string='Direccion de Terreno', default=' ')
    
    placa = fields.Char(string='Placa de Vehículo', default=' ')
    placaGarante = fields.Char(string='Placa de Vehículo', default=' ')
    
    totalActivosAdj = fields.Float(compute="calculo_total_activos_adj",store=True,string='TOTAL ACTIVOS', digits=(6, 2))
    purchase_order = fields.Many2one('purchase.order', string="Purchase order", track_visibility='onchange')
    facturas = fields.Many2one('account.move', string="Liquidacion de Compra", track_visibility='onchange')
    products_id = fields.Many2one('product.product', track_visibility='onchange')
    asamblea_id = fields.Many2one('asamblea', string="Asamblea", track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', readonly=True, default=lambda self: self.env.company.currency_id)
    ahorro_garante=fields.Boolean(default=False)




    @api.onchange("ingresosIds")
    def obtener_ingresos(self):
        total_ingresos_familiares=0
        for l in self.ingresosIds:
            total_ingresos_familiares+=l.titular+l.conyuge
        self.total_ingresos_familiares=total_ingresos_familiares


    @api.onchange("egresosIds")
    def obtener_egresos(self):
        total_egresos_familiares=0
        for l in self.egresosIds:
            total_egresos_familiares+=l.titular+l.conyuge
        self.total_egresos_familiares=total_egresos_familiares

    @api.onchange("ingresosIds","egresosIds")
    def obtener_disponibilidad(self):
        for l in self:
            self.disponibilidad_dinero=l.total_ingresos_familiares-l.total_egresos_familiares

    @api.onchange("ingresosIdsGarante")
    def obtener_ingresos_garante(self):
        total_ingresos_familiares=0
        for l in self.ingresosIdsGarante:
            total_ingresos_familiares+=l.titular+l.conyuge
        self.total_ingresos_familiares_garante=total_ingresos_familiares


    @api.onchange("egresosIdsGarante")
    def obtener_egresos_garante(self):
        total_egresos_familiares=0
        for l in self.egresosIdsGarante:
            total_egresos_familiares+=l.titular+l.conyuge
        self.total_egresos_familiares_garante=total_egresos_familiares


    @api.onchange("ingresosIdsGarante","egresosIdsGarante")
    def obtener_disponibilidad_garante(self):
        for l in self:
            self.disponibilidad_dinero_garante=l.total_ingresos_familiares_garante-l.total_egresos_familiares_garante

    proceso_finalizado=fields.Boolean(default=False)
    actividad_id = fields.Many2one('mail.activity',string="Actividades")


    def crear_activity(self,rol):
        if self.actividad_id:
            self.actividad_id.action_done()
        if not self.proceso_finalizado:
            self.contrato_id.state='ADJUDICADO'
            self.contrato_id.state_simplificado='NO ENTREGADO'
            actividad_id=self.env['mail.activity'].create({
                    'res_id': self.id,
                    'res_model_id': self.env['ir.model']._get('entrega.vehiculo').id,
                    'activity_type_id': 4,
                    'summary': "Ha sido asignado al proceso de Entrega de Vehículo para su revisón/Aprobación",
                    'user_id': rol.user_id.id,
                    'date_deadline':datetime.now()+ relativedelta(days=1)
                })
            self.actividad_id=actividad_id.id
        else:
            if self.estado=="finalizado":
                self.contrato_id.state_simplificado='ENTREGADO'
                self.contrato_id.fecha_adjudicado=datetime.now()

    def llenar_tabla(self):
        obj_patrimonio=self.env['items.patrimonio'].search([])  
        
        if not self.montoAhorroInversiones:
            lista_ids=[]
            for patrimonio in obj_patrimonio:
                id_registro=self.env['items.patrimonio.entrega.vehiculo'].create({'patrimonio_id':patrimonio.id,'garante':False})
                lista_ids.append(int(id_registro))
            self.update({'montoAhorroInversiones':[(6,0,lista_ids)]})

    def llenar_tabla_garante(self):
        obj_patrimonio=self.env['items.patrimonio'].search([])  
        lista_ids=[]
        for patrimonio in obj_patrimonio:
            id_registro=self.env['items.patrimonio.entrega.vehiculo'].create({'patrimonio_id':patrimonio.id,'garante':True})
            lista_ids.append(int(id_registro))
        self.update({'montoAhorroInversionesGarante':[(6,0,lista_ids)]})


    def llenar_tabla_ingresos(self):
        obj_ingreso=self.env['ingresos.financiero'].search([])  
        obj_egreso=self.env['egresos.financiero'].search([])  
        
        if not self.ingresosIds:
            lista_ids=[]
            for ingreso in obj_ingreso:
                id_registro=self.env['ingresos.financiero.entrega.vehiculo'].create({'ingresos_id':ingreso.id,'garante':False})
                lista_ids.append(int(id_registro))
            self.update({'ingresosIds':[(6,0,lista_ids)]})

        if not self.egresosIds:
            lista_ids=[]
            for egreso in obj_egreso:
                id_registro=self.env['egresos.financiero.entrega.vehiculo'].create({'egresos_id':egreso.id,'garante':False})
                lista_ids.append(int(id_registro))
            self.update({'egresosIds':[(6,0,lista_ids)]})

    def obtener_vehiculos(self):
        obj_vehiculos=self.env['necesidad.vehiculos'].search([])  
        
        if not self.necesidadIds:
            lista_ids=[]
            for vehiculo in obj_vehiculos:
                id_registro=self.env['necesidad.adjudicado'].create({'necesidad_id':vehiculo.id,'garante':False})
                lista_ids.append(int(id_registro))
            self.update({'necesidadIds':[(6,0,lista_ids)]})

    def llenar_tabla_ingresos_garante(self):
        obj_ingreso=self.env['ingresos.financiero'].search([])  
        obj_egreso=self.env['egresos.financiero'].search([])  
        
        if not self.ingresosIdsGarante:
            lista_ids=[]
            for ingreso in obj_ingreso:
                id_registro=self.env['ingresos.financiero.entrega.vehiculo'].create({'ingresos_id':ingreso.id,'garante':True})
                lista_ids.append(int(id_registro))
            self.update({'ingresosIdsGarante':[(6,0,lista_ids)]})

        if not self.egresosIdsGarante:
            lista_ids=[]
            for egreso in obj_egreso:
                id_registro=self.env['egresos.financiero.entrega.vehiculo'].create({'egresos_id':egreso.id,'garante':True})
                lista_ids.append(int(id_registro))
            self.update({'egresosIdsGarante':[(6,0,lista_ids)]})



    paginasDeControl = fields.One2many('paginas.de.control.entrega.vehiculo','entrega_id',domain=[('garante','=',False)],  track_visibility='onchange')
    paginasDeControlGarante = fields.One2many('paginas.de.control.entrega.vehiculo','entrega_id', domain=[('garante','=',True)], track_visibility='onchange')
    pagcontrol_garante=fields.Boolean(default=False)
    
    def llenar_tabla_paginas(self):
        obj_paginas_de_control=self.env['paginas.de.control'].search([])
        if not self.paginasDeControl:
            lista_ids=[]
            for paginas in obj_paginas_de_control:
                id_registro=self.env['paginas.de.control.entrega.vehiculo'].create({'pagina_id':paginas.id,'garante':False})
                lista_ids.append(int(id_registro))
            self.update({'paginasDeControl':[(6,0,lista_ids)]})

    def llenar_tabla_paginas_garante(self):
        obj_paginas_de_control=self.env['paginas.de.control'].search([])
        lista_ids=[]
        for paginas in obj_paginas_de_control:
            id_registro=self.env['paginas.de.control.entrega.vehiculo'].create({'pagina_id':paginas.id,'garante':True})
            lista_ids.append(int(id_registro))
        self.update({'paginasDeControlGarante':[(6,0,lista_ids)]})
        self.pagcontrol_garante=True


    tablaPuntosBienes = fields.One2many('puntos.bienes.entrega.vehiculo','entrega_id', domain=[('garante','=',False)],track_visibility='onchange')
    puentes_bienes=fields.Boolean(default=False)

    def llenar_tabla_puntos_bienes(self):
        obj_puntos_bienes=self.env['puntos.bienes'].search([])
        if not self.tablaPuntosBienes:
            lista_ids=[]
            for bienes in obj_puntos_bienes:
                id_registro=self.env['puntos.bienes.entrega.vehiculo'].create({'bien_id':bienes.id,'entrega_id':self.id,'garante':False})
                lista_ids.append(int(id_registro))
            self.update({'tablaPuntosBienes':[(6,0,lista_ids)]})
 
    


    @api.onchange('nombreConsesionario')
    def actualizar_porcentaje_comision(self):
        porcentaje=0
        for l in self:
            if l.nombreConsesionario:
                porcentaje=l.nombreConsesionario.comisionFacturaConcesionario
                if l.nombreConsesionario.tipo=='tercero':
                    l.compras_terceros=True
                else:
                    l.compras_terceros=False
        l.comisionFacturaConcesionario=porcentaje


    def create_liquidacion_compra(self):
        plantilla_id=self.env['informe.credito.cobranza'].create({'clave':"liquidacion_compra",
                                                    'entrega_vehiculo_id':self.id})
        dct=plantilla_id.print_report_xls()
        self.liquidacion_compra=dct["archivo_xls1"]
        return dct





    def create_orden_Salida(self):
        plantilla_id=self.env['informe.credito.cobranza'].create({'clave':"orden_salida",
                                                    'entrega_vehiculo_id':self.id})
        dct=plantilla_id.print_report_xls()
        self.orden_salida=dct["archivo_xls1"]
        return dct




    def create_purchase_order(self):
        plantilla_id=self.env['informe.credito.cobranza'].create({'clave':"orden_compra",
                                                    'entrega_vehiculo_id':self.id})
        dct=plantilla_id.print_report_xls()
        self.orden_compra=dct["archivo_xls1"]
        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url += "/web/content/%s?download=true" %(dct["documento"]["id"])
        self.url_doc=url
        self.correo_id=dct["documento"]["id"]
        return dct





#####Funcion para crear purchase order
    def enviar_correo(self):
        ir_model_data = self.env['ir.model.data']
        template_id =  template_id = ir_model_data.get_object_reference('gzl_adjudicacion', "email_orden_compra")[1]
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_template(template.lang, 'entrega.vehiculo', self.ids[0])
        ctx = {
            'default_model': 'entrega.vehiculo',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_attachment_ids':[(4,self.correo_id.id)],
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "",
            'proforma':False,
            'force_email': True,
            'model_description': "ORDEN DE COMPRA",
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }


    def create_liq_compra(self):  
        account=self.env['account.account'].search([('code','=','1010202')] , limit=1) 
        #product=self.env['product.product'].search([('default_code','=','GE')] , limit=1) 1010201
        factura = self.env['account.move'].create({
                    'type': 'liq_purchase',
                    'partner_id': self.nombreSocioAdjudicado.id,
                    
                    'journal_id':2,
                    'l10n_latam_document_type_id':5,
                    'purchase_id':self.purchase_order.id,
                    'invoice_date': datetime.datetime.now(),
                })  
        factura.write({'invoice_line_ids': [(0, 0, {
                        
                        'product_id':self.products_id.id,
                        'name': self.products_id.name,
                        'account_id': factura.journal_id.default_debit_account_id.id,
                        'quantity': 1,
                        'price_unit': self.montoVehiculo,
                    })]})
        self.facturas= factura
    

    @api.depends("montoAhorroInversiones")
    def calculo_total_activos_adj(self):
        for rec in self:
            rec.totalActivosAdj=sum(rec.montoAhorroInversiones.mapped('valor'))
    
    totalPuntosBienesAdj = fields.Integer(compute='calcular_puntos_bienes',store=True)

    @api.depends('tablaPuntosBienes')
    def calcular_puntos_bienes(self):
        for rec in self:
            rec.totalPuntosBienesAdj = sum(rec.tablaPuntosBienes.mapped('puntosBien'))

    # observaciones
    observaciones = fields.Text(string='Observaciones', default=' ')
    observacionesGarante = fields.Text(string='Observaciones', default=' ')
    # calificador compras
    cedulaContrato = fields.Char()
    codClienteContrado = fields.Char()
    contratoCliente = fields.Char()
    montoAdjudicado = fields.Monetary(compute='buscar_contrato_partner', currency_field='currency_id', string='Monto Adjudicado')
    montoEnviadoAsamblea = fields.Monetary( currency_field='currency_id', string='Monto Enviado Asamblea')
    garante  = fields.Boolean(string='Garante')
    plazoMeses = fields.Integer(string='Plazo')
    tipoAdj = fields.Char(string='Tipo Adj.')
    valorCuota = fields.Monetary(string='Valor de Cuota')
    fechaAdj = fields.Date(string='Fecha de Adj.')
    valorTotalPlan = fields.Monetary(compute='calcular_valor_total_plan', string='Valor Total del Plan')
    porcentajeTotal = fields.Float(default=100.00)
    montoCuotasCanceladas = fields.Monetary(string='Cuotas Canceladas', compute='calcular_valor_cuotas_canceladas')
    cuotasCanceladas = fields.Integer()
    porcentajeCancelado = fields.Float(digits=(6, 2), compute='calcular_porcentaj_cuotas_canc')
    

    @api.depends('montoCuotasCanceladas', 'valorTotalPlan')
    def calcular_porcentaj_cuotas_canc(self):
        for rec in self:
            if rec.valorTotalPlan:
                rec.porcentajeCancelado = (
                    rec.montoCuotasCanceladas / rec.valorTotalPlan) * 100
            else:
                rec.porcentajeCancelado = 0.00

    montoCuotasPendientes = fields.Monetary(string='Cuotas Pendientes', compute='calcular_valor_cuotas_pendientes')

    @api.depends('valorTotalPlan', 'montoCuotasCanceladas')
    def calcular_valor_cuotas_pendientes(self):
        for rec in self:
            rec.montoCuotasPendientes = rec.valorTotalPlan - rec.montoCuotasCanceladas

    cuotasPendientes = fields.Integer(compute='calcular_cuotas_pendientes')

    @api.depends('plazoMeses', 'cuotasCanceladas')
    def calcular_cuotas_pendientes(self):
        for rec in self:
            rec.cuotasPendientes = rec.plazoMeses - rec.cuotasCanceladas

    porcentajePendiente = fields.Float(digits=(6, 2), compute='calcular_porcentaj_pendiente')
    
    @api.depends('valorTotalPlan', 'montoCuotasPendientes')
    def calcular_porcentaj_pendiente(self):
        for rec in self:
            if rec.valorTotalPlan:
                rec.porcentajePendiente = (
                    rec.montoCuotasPendientes/rec.valorTotalPlan)*100
            else:
                rec.porcentajePendiente = 0.00
    

    #puntos valor cancelado del plan
    puntosPorcentajeCancelado = fields.Integer(string = 'puntos', compute='calcular_puntos_porcentaje_cancelado')


    @api.depends('porcentajeCancelado')
    def calcular_puntos_porcentaje_cancelado(self):
        for rec in self:
            if rec.porcentajeCancelado >= 0.00 and rec.porcentajeCancelado <= 25.00:
                rec.puntosPorcentajeCancelado = 0
            elif rec.porcentajeCancelado >= 26.00 and rec.porcentajeCancelado <= 30.00:
                rec.puntosPorcentajeCancelado = 100
            elif rec.porcentajeCancelado >= 31.00:
                rec.puntosPorcentajeCancelado = 200
            else:
                rec.puntosPorcentajeCancelado = 0



    #saldosBien
    valorDelBien = fields.Monetary(string='Valor del Bien', compute='set_valor_del_bien')
    @api.depends('montoAdjudicado')
    def set_valor_del_bien(self):
        for rec in self:
            if rec.montoAdjudicado:
                rec.valorDelBien = rec.montoAdjudicado
            else:
                rec.valorDelBien = 0.00
 
    saldoPlan = fields.Monetary(string='Saldo del Plan', compute='set_valor_saldo_plan')

    @api.depends('montoCuotasPendientes')
    def set_valor_saldo_plan(self):
        for rec in self:
            if rec.montoCuotasPendientes:
                rec.saldoPlan = rec.montoCuotasPendientes
            else:
                rec.saldoPlan = 0.00

    porcentajeSaldoPlan = fields.Float(digits=(3, 2), compute='calcular_porcentaj_saldo_plan', default=0.00)
    
    @api.depends('saldoPlan', 'valorDelBien')
    def calcular_porcentaj_saldo_plan(self):
        for rec in self:
            if rec.saldoPlan:
                rec.porcentajeSaldoPlan = round(
                    (rec.valorDelBien/rec.saldoPlan) * 100)
            else:
                rec.porcentajeSaldoPlan = 0.00

    #puntos saldos
    puntosPorcentajSaldos = fields.Integer(compute='calcular_puntos_porcentaje_saldos')
    @api.depends('porcentajeSaldoPlan')
    def calcular_puntos_porcentaje_saldos(self):
        for rec in self:
            if rec.porcentajeSaldoPlan >= 0.00 and rec.porcentajeSaldoPlan <= 99.00:
                rec.puntosPorcentajSaldos = 0
            elif rec.porcentajeSaldoPlan >= 100.00 and rec.porcentajeSaldoPlan <= 139.00:
                rec.puntosPorcentajSaldos = 100
            elif rec.porcentajeSaldoPlan >= 140.00:
                rec.puntosPorcentajSaldos = 200
            else:
                rec.puntosPorcentajSaldos = 0



    #porcentajeIngresos = fields.Float(default=100.00)

    #gastosFamiliares = fields.Monetary(string='Gastos familiares', compute='calcular_valor_gastos_familiares')

    # @api.depends('ingresosFamiliares')
    # def calcular_valor_gastos_familiares(self):
    #     for rec in self:
    #         rec.porcentajeIngresos = 100.00
    #         rec.gastosFamiliares = rec.ingresosFamiliares * 0.7


    #porcentajeGastos = fields.Float( digits=(6, 2), compute='calcular_porcentaje_gastos_familiares')

    # @api.depends('gastosFamiliares', 'ingresosFamiliares')
    # def calcular_porcentaje_gastos_familiares(self):
    #     for rec in self:
    #         rec.porcentajeGastos = (
    #             rec.gastosFamiliares / rec.ingresosFamiliares) * 100

    # @api.depends('ingresosFamiliares', 'gastosFamiliares')
    # def calcular_porcentaje_gastos_familiares(self):
    #     for rec in self:
    #         if rec.gastosFamiliares:
    #             rec.porcentajeGastos = (
    #                 rec.gastosFamiliares / rec.ingresosFamiliares) * 100
    #         else:
    #             rec.porcentajeGastos = 0


    # porcentajeCuotaPlan = fields.Float(digits=(6, 2), default=0.0, compute='calcular_porcentaje_cuota_plan')


    # @api.depends('valorCuota', 'ingresosFamiliares')
    # def calcular_porcentaje_cuota_plan(self):
    #     for rec in self:
    #         if rec.ingresosFamiliares:
    #             rec.porcentajeCuotaPlan = round(((rec.valorCuota/rec.ingresosFamiliares) * 100), 0) 
    #         else:
    #             rec.porcentajeCuotaPlan = 0.0

    # puntosCuotaIngresos = fields.Integer(compute='calcular_puntos_ingresos')
 
    # @api.depends('porcentajeCuotaPlan')
    # def calcular_puntos_ingresos(self):
    #     for rec in self:
    #         if rec.porcentajeCuotaPlan >= 0.00 and rec.porcentajeCuotaPlan <= 30.00:
    #             rec.puntosCuotaIngresos = 200
    #         elif rec.porcentajeCuotaPlan >= 31.00 and rec.porcentajeCuotaPlan <= 40.00:
    #             rec.puntosCuotaIngresos = 100
    #         elif rec.porcentajeCuotaPlan >= 41.00:
    #             rec.puntosCuotaIngresos = 0
    #         else:
    #             rec.puntosPorcentajeCancelado = 0



    # puntosSaldosPlan = fields.Float(digits=(6, 2), compute='calcular_puntos_saldos_plan')

    # @api.depends('porcentajeCuotaPlan')
    # def calcular_puntos_saldos_plan(self):
    #     for rec in self:
    #         if rec.porcentajeCuotaPlan >= 0.00 and rec.porcentajeCuotaPlan <= 25.00:
    #             rec.puntosPorcentajeCancelado = 0
    #         elif rec.porcentajeCuotaPlan >= 26.00 and rec.porcentajeCuotaPlan <= 30.00:
    #             rec.puntosPorcentajeCancelado = 100
    #         elif rec.porcentajeCuotaPlan >= 31.00:
    #             rec.puntosPorcentajeCancelado = 200
    #         else:
    #             rec.puntosPorcentajeCancelado = 0


    # porcentajeDisponibilidad = fields.Float(digits=(6, 2), compute='calcular_porcentaje_disponibilidad')

    # @api.depends('porcentajeGastos', 'porcentajeIngresos')
    # def calcular_porcentaje_disponibilidad(self):
    #     for rec in self:
    #         rec.porcentajeDisponibilidad = rec.porcentajeIngresos - rec.porcentajeGastos


    # disponibilidad = fields.Monetary(string='Disponibilidad', compute='calcular_valor_disponibilidad')

    # @api.depends('ingresosFamiliares', 'gastosFamiliares')
    # def calcular_valor_disponibilidad(self):
    #     for rec in self:
    #         rec.disponibilidad = rec.ingresosFamiliares - rec.gastosFamiliares


    # scoreCredito = fields.Integer(string="Score de Credito Mayor a 800 puntos")


    # @api.onchange('scoreBuroCredito')
    # def calculo_scoreCredito(self):
    #     self.scoreCredito= self.scoreBuroCredito 

    # puntosScoreCredito = fields.Integer(compute='calcular_punto_score_credito')

    # @api.depends('scoreCredito')
    # def calcular_punto_score_credito(self):
    #     for rec in self:
    #         if rec.scoreCredito >= 500 and rec.scoreCredito <= 799:
    #             rec.puntosScoreCredito = 100
    #         elif rec.scoreCredito >= 800:
    #             rec.puntosScoreCredito = 200
    #         else:
    #             rec.puntosScoreCredito = 0


    # antiguedadLaboral = fields.Integer(string="Antigüedad Laboral o Comercial Mayor a 2 años")
    
    # puntosAntiguedadLaboral = fields.Integer(compute='calcular_puntos_antiguedad_laboral')


    # @api.depends('antiguedadLaboral')
    # def calcular_puntos_antiguedad_laboral(self):
    #     for rec in self:
    #         if rec.antiguedadLaboral >= 2:
    #             rec.puntosAntiguedadLaboral = 200
    #         elif rec.antiguedadLaboral >= 1:
    #             rec.puntosAntiguedadLaboral = 100
    #         else:
    #             rec.puntosAntiguedadLaboral = 0



    # totalPuntosCalificador = fields.Integer(compute='calcular_total_puntos')

    # @api.depends('puntosPorcentajeCancelado', 'puntosPorcentajSaldos', 'puntosCuotaIngresos', 'puntosScoreCredito', 'puntosAntiguedadLaboral', 'totalPuntosBienesAdj')
    # def calcular_total_puntos(self):
    #     for rec in self:
    #         rec.totalPuntosCalificador = rec.puntosPorcentajeCancelado + rec.puntosPorcentajSaldos +  rec.puntosCuotaIngresos + rec.puntosScoreCredito +  rec.puntosAntiguedadLaboral + rec.totalPuntosBienesAdj


    # observacionesCalificador = fields.Text(string="Observaciones", default=' ')

    titularConyugePuntos = fields.Char(
        string="Titular, Conyugue y Depositario")
    titularConyugeGarantePuntos = fields.Char(
        string="Titular, Conyugue y Garante Solidario")

    montoVehiculo = fields.Monetary(string="valor del vehiculo")
    montoAFavor = fields.Monetary(compute='calcular_monto_a_favor')

    valorAdjParaCompra = fields.Monetary(
        compute='calcular_valor_adj_para_compra')
    montoAnticipoConsesionaria = fields.Monetary()
    comisionFacturaConcesionario = fields.Float()
    valorComisionFactura = fields.Monetary(
        compute='calcular_valor_comision_fact')
    comisionDispositivoRastreo = fields.Monetary()
    retencion_pagar = fields.Monetary()
    montoChequeConsesionario = fields.Monetary(compute='calcular_valor_cheque')
    nombreConsesionario = fields.Many2one(
        'res.partner', string="NOMBRE DEL CONCESIONARIO:")
    observacionesLiquidacion = fields.Text(string="Observaciones", default=' ')
    
    liquidacionCompra = fields.Many2one('account.move', string="LIquidación de Compra")
    ordenCompra  = fields.Many2one('account.move', string="Orden de Compra")
    dia = fields.Char()
    mes = fields.Char(string='')
    anio = fields.Char()
    
    nombreInforme = fields.Char(compute='setea_informe_garante')
    
    aplicaGarante = fields.Selection(selection=[
        ('NO', 'Titular, Conyugue y Depositario'),
        ('SI', 'Titular, Conyugue y Garante Solidario')
    ], compute='set_aplica_garante')
    
    montoPagoConsesionario = fields.Selection(selection=[
        ('saldo_a_favor', 'SALDO A FAVOR APLICA A CUOTAS FINALES DEL PLAN'),
        ('diferencia', 'DIFERENCIA PAGA AL CONCESIONARIO')
    ], default = 'saldo_a_favor', compute='calcular_monto_a_favor')


    nombresInforme = fields.Char(compute='setea_datos_informe')
    vatInforme = fields.Char()
    estadoCivilInforme = fields.Char()
    edadInforme = fields.Integer()

    matriculacion = fields.Boolean(string="Matriculación", track_visibility="onchange")
    plazo_matriculacion = fields.Integer(string="Plazo", track_visibility="onchange")
    fecha_vencimiento_matriculacion = fields.Date(string="Fecha Vencimiento", track_visibility="onchange")

    rastreo = fields.Boolean(string="Rastreo",track_visibility="onchange")
    certificado_rastreo=fields.Binary(string="Certificado")
    plazo_rastreo = fields.Integer(string="Plazo", track_visibility="onchange")
    fecha_inicio_rastreo = fields.Date(string="Fecha Inicio", track_visibility="onchange")
    fecha_vencimiento_rastreo = fields.Date(string="Fecha Vencimiento", track_visibility="onchange")
    proveedor_rastreo=fields.Many2one("res.partner")
    seguro = fields.Boolean(string="Seguro",track_visibility="onchange")
    plazo_seguro = fields.Integer(string="Plazo", track_visibility="onchange")
    certificado_seguro=fields.Binary(string="Certificado")
    fecha_inicio_seguro = fields.Date(string="Fecha Inicio", track_visibility="onchange")
    fecha_vencimiento_seguro = fields.Date(string="Fecha Vencimiento", track_visibility="onchange")
    proveedor_seguro=fields.Many2one("res.partner")
    revisiones_generales=fields.Boolean(string="Revisiones estéticas y demás",default=False)
    contrato_id=fields.Many2one("contrato", string="Contrato")


                

    def job_notificar_vencimientos_rastreo(self):

        hoy=date.today()

        fin_busqueda= hoy+relativedelta(days=+30)

        entregas_vehiculos=self.env['entrega.vehiculo'].search([('fecha_vencimiento_seguro','>=',hoy),('fecha_vencimiento_seguro','<',fin_busqueda)])
        entregas_vehiculos_rastreo=self.env['entrega.vehiculo'].search([('fecha_vencimiento_rastreo','<',hoy),('fecha_vencimiento_rastreo','>=',fin_busqueda)])

        for entregas in entregas_vehiculos:
            self.envio_correos_plantilla('email_vencimiento_seguro',entregas.id)
        for entregas in entregas_vehiculos_rastreo:
            self.envio_correos_plantilla('email_vencimiento_rastreo',entregas.id)

    def envio_correos_plantilla(self, plantilla,id_envio):

        try:
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('gzl_adjudicacion', plantilla)[1]
        except ValueError:
            template_id = False
        if template_id:
            obj_template=self.env['mail.template'].browse(template_id)

            email_id=obj_template.send_mail(id_envio)



    @api.constrains("matriculacion")
    def validar_plazo_matriculacion(self):
        for l in self:
            if l.matriculacion:
                if l.plazo_matriculacion==0:
                    raise ValidationError("El plazo de Matriculación debe ser mayor a cero.")
    

    @api.constrains("seguro")
    def validar_plazo_seguro(self):
        for l in self:
            if l.seguro:
                if l.plazo_seguro==0:
                    raise ValidationError("El plazo de Seguro debe ser mayor a cero.")

    @api.constrains("rastreo")
    def validar_plazo_rastreo(self):
        for l in self:
            if l.rastreo:
                if l.plazo_rastreo==0:
                    raise ValidationError("El plazo de Rastreo debe ser mayor a cero.")

    estado_anterior_requisitos = fields.Boolean(string="Estado Anterior",compute="consultar_estado_anterior_requisitos")
    estado_anterior_informe_credito = fields.Boolean(string="Estado Anterior",compute="consultar_estado_anterior_requisitos")
    estado_anterior_liquidacion = fields.Boolean(string="Estado Anterior",compute="consultar_estado_anterior_requisitos")
    estado_anterior_calificador = fields.Boolean(string="Estado Anterior",compute="consultar_estado_anterior_requisitos")
    estado_anterior_factura = fields.Boolean(string="Estado Anterior",compute="consultar_estado_anterior_requisitos")
    estado_anterior_matriculacion = fields.Boolean(string="Estado Anterior",compute="consultar_estado_anterior_requisitos")
    estado_anterior_requisitos = fields.Boolean(string="Estado Anterior",compute="consultar_estado_anterior_requisitos")
    estado_anterior_orden_compra = fields.Boolean(string="Estado Anterior",compute="consultar_estado_anterior_requisitos")

    url_doc = fields.Char('Url doc') 


    def generar_contrato_reserva(self):
        
        reserva_id=[]
        pagare_id=[]
        cuota_id=self.contrato_id.estado_de_cuenta_ids.filtered(lambda l: l.numero_cuota==str(self.contrato_id.plazo_meses.numero))
        if cuota_id:
            fecha=cuota_id.fecha
        else:
            fecha=datetime.now().date()
        if self.aplicaGarante in ["si","SI"]:
            if self.nombreSocioAdjudicado.estado_civil=="casado":
                clave_reserva="reserva_casado_garante"
                clave_pagare="pagare_casado_garante"
            else:
                clave_reserva="reserva_demas_garante"
                clave_pagare="pagare_demas_garante"
        else:
            if self.nombreSocioAdjudicado.estado_civil=="casado":
                clave_reserva="reserva_casado_sin_garante"
                clave_pagare="pagare_casado_sin_garante"
            else:
                clave_reserva="reserva_demas_sin_garante"
                clave_pagare="pagare_demas_sin_garante"

        reserva_id=self.env['contrato.reserva'].create({'contrato_id':self.contrato_id.id,'partner_id':self.nombreSocioAdjudicado.id,
                                        'vehiculo_id':self.id,"clave":clave_reserva})
        pagare_id=self.env['pagare.report'].create({'contrato_id':self.contrato_id.id,'partner_id':self.nombreSocioAdjudicado.id,
                                       "clave":clave,"fecha_vencimiento":fecha})

        if reserva_id:
            dct_reserva=reserva_id.print_report_xls()
            self.reserva_id=dct_reserva["documento"]["id"]

        if pagare_id:
            dct_pagare=pagare_id.print_report_xls()
            self.pagare_id=dct_pagare["documento"]["id"]

    
    @api.model
    def year_selection(self):
        year = 2000 # año de inicio
        year_list = []
        while year != ((date.today().year) +1) : # año de fin
            year_list.append((str(year), str(year)))
            year += 1
        return year_list

    tipoVehiculo = fields.Selection(selection=
                    [('MOTO', 'MOTO'), 
                    ('AUTO', 'AUTO'),
                    ('JEEP', 'JEEP'),
                    ('CAMIONETA', 'CAMIONETA'),
                    ('MICROBUS', 'MICROBUS'),
                    ('MICROBUS', 'MICROBUS'),
                    ('BUS', 'BUS'),
                    ('LIVIANO DE CARGA', 'LIVIANO DE CARGA'),
                    ('CAMION DE CARGA', 'CAMIÓN DE CARGA'),
                    ('CAMION DE CARGA PESADA', 'CAMIÓN DE CARGA PESADA')
                    ], string='Tipo:', default ='AUTO')

    claseVehiculo = fields.Selection(string='Clase:',
        selection=[('TRICIMOTO', 'TRICI MOTO'), 
                    ('MOTOCICLETA', 'MOTOCICLETA'),
                    ('TRICAR', 'TRICAR'),
                    ('CUATRIMOTO', 'CUATRIMOTO'),
                    ('SEDAN', 'SEDAN'),
                    ('COUPE', 'COUPE'),
                    ('CONVERTIBLE', 'CONVERTIBLE'),
                    ('HATCHBACK', 'HATCHBACK'),
                    ('MINIVAN', 'MINIVAN'),
                    ('VEHICULO UTILITARIO', 'VEHICULO UTILITARIO'),
                    ('LIMOSINA', 'LIMOSINA'),
                    ('FUNERARIO', 'FUNERARIO'),
                    ('CAMIONETA', 'CAMIONETA'),
                    ('FURGONETA DE PASAJEROS', 'FURGONETA DE PASAJEROS'),
                    ('FURGONETA DE CARGA', 'FURGONETA DE CARGA'),
                    ('AMBULANCIA', 'AMBULANCIA'),
                    ('MICROBUS', 'MICROBUS'),
                    ('MINIBUS', 'MINIBUS'),
                    ('BUS', 'BUS'),
                    ('BUS COSTA', 'BUS COSTA'),
                    ('ARTICULADO', 'ARTICULADO'),
                    ('CAMION LIGERO', 'CAMIÓN LIGERO'),
                    ('CAMION MEDIANO', 'CAMIÓN MEDIANO'),
                    ('CAMION PESADO', 'CAMIÓN PESADO'),
                    ('TRACTO CAMION', 'TRACTO CAMIÓN'),
                    ('SEMIRREMOLQUE', 'SEMIRREMOLQUE'),
                    ('REMOLQUE', 'REMOLQUE'),
                    ('VEHICULO UTILITARIO ESPECIAL', 'VEHICULO UTILITARIO ESPECIAL'),
                    ('COMPETENCIA', 'COMPETENCIA'),
                    ('MULTIFUNCION', 'MULTIFUNCIÓN'),
                    ('CASA RODANTE', 'CASA RODANTE'),
                    ('CHASIS MOTORIZADO', 'CHASIS MOTORIZADO'),
                    ('CHASIS CABINADO', 'CHASIS CABINADO'),
                    ('OTROS USOS ESPECIALES', 'OTROS USOS ESPECIALES')
                    ], default = 'VEHICULO UTILITARIO')
    
    marcaVehiculo = fields.Char(string='Marca:', default=' ')
    modeloVehiculoSRI = fields.Char(string='Modelo registrado SRI:', default=' ')
    modeloHomologado  = fields.Char(string='Modelo homologado ANT:', default=' ')
    serieVehiculo = fields.Char(string='Serie:', default=' ')
    motorVehiculo = fields.Char(string='Motor:', default=' ')
    valorCpn = fields.Char(string='valorCpn:', default=' ')
    colorVehiculo = fields.Char(string='Color:', default=' ')
    anioVehiculo = fields.Selection(year_selection, string="Año:", default="2019")
    paisOrigenVehiculo = fields.Many2one('res.country', string='País origen:')
    conbustibleVehiculo = fields.Selection(selection=
        [('DIESEL', 'DIESEL'), 
            ('GASOLINA', 'GASOLINA'),
            ('HIBRIDO', 'HÍBRIDO'),
            ('ELECTRICO', 'ELÉCTRICO'),
            ('GAS LICUADO DE PETROLEO', 'GAS LICUADO DE PETROLEO'),
            ('OTRO', 'OTRO')
        ], default = 'GASOLINA', string = 'Combustible:')
    numPasajeros = fields.Integer(string='Pasajeros:', default = 4)
    tonelajeVehiculo = fields.Char(string='Tonelaje:', default=' ')
    numEjesVehiculo = fields.Integer(string='Número de eje:', default = 2)


    @api.depends('garante')
    def setea_valores_informe(self):
        for rec in self:
            if rec.garante == False:
                rec.fechaNacimientoAdj = rec.nombreSocioAdjudicado.fecha_nacimiento
            else:
                rec.fechaNacimientoGarante = rec.nombreGarante.fecha_nacimiento
            

    def validarrol(self):
        roles=self.env['adjudicaciones.team'].search([('id','=',self.rolAsignado.id)])
        for x in roles:
          if self.env.user.id == x.user_id.id:
            return True
          else:
            raise ValidationError("Debe estar asignado al rol %s"% self.rolAsignado.name)
        return False


    @api.depends('garante')
    def setea_informe_garante(self):
        for rec in self:
            if rec.garante == False:
                rec.nombreInforme = 'Nombre del Socio Adj.: '
            else:
                rec.nombreInforme = 'Nombre del Garante.:'


    @api.depends('garante', 'nombreSocioAdjudicado', 'nombreGarante')
    def setea_datos_informe(self):
        for rec in self:
            if rec.garante == False:
                rec.nombresInforme = rec.nombreSocioAdjudicado.name
                rec.vatInforme = rec.vatAdjudicado
                rec.estadoCivilInforme = rec.estadoCivilAdj
                #rec.edadInforme 
                
            else:
                rec.nombresInforme = rec.nombreGarante.name
                rec.vatInforme = rec.vatGarante
                rec.estadoCivilInforme = rec.estadoCivilGarante


    def consultar_estado_anterior_requisitos(self):
        for l in self:

            self.env.cr.execute("""select mtv.new_value_char 
                                            from 
                                                mail_tracking_value mtv, 
                                                mail_message mm 
                                            where 
                                                mtv.mail_message_id=mm.id and 
                                                mm.model='entrega.vehiculo' and
                                                mm.res_id={0}""".format(l.id))



            estados = self.env.cr.dictfetchall()
            result = map(lambda x: x['new_value_char'], estados)

            if 'Revisión documentos' in result:
                l.estado_anterior_requisitos=True
            if 'Informe de Crédito y Cobranza' in result:
                l.estado_anterior_informe_credito=True
            if 'Calificador para compra del bien' in result:
                l.estado_anterior_calificador=True

            if 'Liquidación de compra y orden de compra' in result:
                l.estado_anterior_liquidacion=True

            if 'Orden de compra' in result:
                l.estado_anterior_orden_compra=True
                l.estado_anterior_factura=True
                l.estado_anterior_matriculacion=True


    @api.depends('montoVehiculo', 'montoAdjudicado')
    def calcular_monto_a_favor(self):
        for rec in self:
            rec.montoAFavor = rec.montoVehiculo - rec.montoAdjudicado
            if rec.montoVehiculo < rec.montoAdjudicado:
                rec.montoPagoConsesionario = 'saldo_a_favor'
            else:
                rec.montoPagoConsesionario = 'diferencia'    
    
    
    # @api.depends('totalPuntosCalificador')
    # def set_aplica_garante(self):
    #     for rec in self:
    #         if rec.totalPuntosCalificador  >= 700:
    #             rec.aplicaGarante = 'NO'
    #         else:
    #             rec.aplicaGarante = 'SI'

    @api.depends('montoAdjudicado', 'valorComisionFactura', 'retencion_pagar', 'montoAnticipoConsesionaria')
    def calcular_valor_cheque(self):
        for rec in self:
            if rec.montoAdjudicado<rec.montoVehiculo:
                monto_final=rec.montoAdjudicado
            else:
                monto_final=rec.montoVehiculo
            rec.montoChequeConsesionario = monto_final - rec.valorComisionFactura + rec.retencion_pagar - rec.montoAnticipoConsesionaria

    @api.depends('montoVehiculo', 'comisionFacturaConcesionario')
    def calcular_valor_comision_fact(self):
        for rec in self:
            decimalPorcentaje = (rec.comisionFacturaConcesionario/100)
            rec.valorComisionFactura = rec.montoVehiculo * decimalPorcentaje
            fuente=(rec.valorComisionFactura/1.12)
            iva=fuente*0.12
            retencion_fuente=(fuente*(rec.nombreConsesionario.retencion_fuente/100))
            retencion_iva=(iva*(rec.nombreConsesionario.retencion_iva/100))
            rec.retencion_pagar=retencion_fuente+retencion_iva

    @api.depends('montoVehiculo', 'montoAdjudicado')
    def calcular_valor_adj_para_compra(self):
        for rec in self:
            # si el valor del plan adj. es menor al valor del vehiculo
            if rec.montoAdjudicado < rec.montoVehiculo:
                rec.valorAdjParaCompra = rec.montoAdjudicado
            else:
                rec.valorAdjParaCompra = rec.montoVehiculo



    @api.depends('montoAdjudicado', 'montoPendiente')
    def setear_montos_bien(self):
        for rec in self:
            if rec.ingresosFamiliares:
                rec.porcentajeCuotaPlan = (
                    rec.valorCuota / rec.ingresosFamiliares) * 100
            else:
                rec.porcentajeCuotaPlan = 0


    @api.depends('valorCuota', 'cuotasCanceladas')
    def calcular_valor_cuotas_canceladas(self):
        for rec in self:
            rec.porcentajeTotal = 100.00
            rec.montoCuotasCanceladas = rec.valorCuota * rec.cuotasCanceladas

    @api.depends('valorCuota', 'plazoMeses')
    def calcular_valor_total_plan(self):
        for rec in self:
            rec.valorTotalPlan = rec.valorCuota * rec.plazoMeses


    def setear_fecha_adjudicado(self):
        contrato = self.env['contrato'].search(
            [('cliente', '=', self.nombreSocioAdjudicado.id),('id','=',self.contrato_id.id)], limit=1)
        now=date.today()
        contrato.fecha_adjudicado=now
        contrato.estado='ADJUDICADO'



    def rechazo_setear_fecha_adjudicado(self):
        contrato = self.env['contrato'].search(
            [('cliente', '=', self.nombreSocioAdjudicado.id)], limit=1)
        contrato.fecha_adjudicado=False
        contrato.estado='ACTIVADO'
        contrato.entrega_vehiculo=False

        dct={
        'grupo_id':contrato.grupo.id,
        'haber':self.montoEnviadoAsamblea ,
        'adjudicado_id':contrato.cliente.id,
        'contrato_id':contrato.id,
        'state':contrato.state
        }


        transacciones.create(dct)


    @api.onchange("nombreGarante")
    @api.constrains("nombreGarante")
    @api.depends("nombreGarante")
    def llenar_datos(self):
        self.llenar_tabla_garante()
        self.llenar_tabla_ingresos_garante()
        self.llenar_tabla_paginas_garante()



    @api.onchange('nombreSocioAdjudicado')
    @api.depends('nombreSocioAdjudicado')
    @api.constrains('nombreSocioAdjudicado')
    def buscar_contrato_partner(self):
        self.llenar_tabla()
        self.llenar_tabla_ingresos()
        self.obtener_vehiculos()
        self.llenar_tabla_paginas()
        self.llenar_tabla_puntos_bienes()
        for rec in self:
            
            contrato = self.env['contrato'].search(
                [('cliente', '=', rec.nombreSocioAdjudicado.id)], limit=1)
            rec.montoAdjudicado = contrato.monto_financiamiento
            rec.valorCuota = contrato.cuota_capital
            rec.tipoAdj = contrato.tipo_de_contrato.name
            rec.fechaAdj = contrato.fecha_adjudicado
            rec.cuotasCanceladas = contrato.numero_cuotas_pagadas
            rec.plazoMeses = contrato.plazo_meses.numero
            rec.garante = contrato.aplicaGarante
            rec.telefonosAdj = str(contrato.cliente.phone) +' - '+ str(contrato.cliente.mobile)
            if rec.garante == True:
                rec.nombreGarante = contrato.garante
            


    @api.depends('fechaNacimientoAdj')
    def calcular_edad(self):
        edad = 0
        for rec in self:
            today = date.today()
            if rec.fechaNacimientoAdj:
                edad = today.year - rec.fechaNacimientoAdj.year - \
                    ((today.month, today.day) < (
                        rec.fechaNacimientoAdj.month, rec.fechaNacimientoAdj.day))
                rec.edadAdjudicado = edad
            else:
                rec.edadAdjudicado = 0
    
    @api.depends('fechaNacimientoGarante')
    def calcular_edad_Garante(self):
        edad = 0
        for rec in self:
            today = date.today()
            if rec.fechaNacimientoGarante:
                edad = today.year - rec.fechaNacimientoGarante.year - \
                    ((today.month, today.day) < (
                        rec.fechaNacimientoGarante.month, rec.fechaNacimientoGarante.day))
                rec.edadGarante = edad
            else:
                rec.edadGarante = 0
    



    


    @api.model
    def create(self, vals):
        vals['secuencia'] = self.env['ir.sequence'].next_by_code(
            'entrega.vehiculo')

        return super(EntegaVehiculo, self).create(vals)


 
class IngresosFinanciero(models.Model):
    _name = 'ingresos.financiero.entrega.vehiculo'
    _description = 'Ingresos Financieros '

    currency_id = fields.Many2one(
        'res.currency', readonly=True, default=lambda self: self.env.company.currency_id)
 
    entrega_id = fields.Many2one('entrega.vehiculo')
    tipo=fields.Char(default="Ingresos")
    ingresos_id = fields.Many2one('ingresos.financiero')
    titular  = fields.Monetary(string="Titular($)",digits=(6, 2))
    conyuge  = fields.Monetary(string="Conyuge($)",digits=(6, 2))

    garante= fields.Boolean(default=False)


class NecesidadAdjudicado(models.Model):
    _name = 'necesidad.adjudicado'
    _description = ''


    adquirirBien=fields.Boolean(string="-")
    necesidad_id = fields.Many2one('necesidad.vehiculos')
    entrega_id = fields.Many2one('entrega.vehiculo')

    garante= fields.Boolean(default=False)


class DetalleNecesidadAdjudicado(models.Model):
    _name = 'detalle.necesidad.adjudicado'
    _description = ''


    marca=fields.Char(string="Marca")
    modelo=fields.Char(string="Modelo")
    anio=fields.Char(string="Año")
    colores=fields.Char(string="Colores")
    entrega_id = fields.Many2one('entrega.vehiculo')

    garante= fields.Boolean(default=False)



class ReferenciasBancarias(models.Model):
    _name = 'referencias.bancarias'
    _description = ''


    banco=fields.Char(string="Banco")
    tipo_cuenta=fields.Char(string="Tipo de Cuenta")
    numero_cuenta=fields.Char(string="# de Cuenta")
    entrega_id = fields.Many2one('entrega.vehiculo')

    garante= fields.Boolean(default=False)

class ReferenciasFamiliares(models.Model):
    _name = 'referencias.familiares'
    _description = ''


    nombre=fields.Char(string="Nombre")
    cedula=fields.Char(string="C.C")
    parentezco=fields.Char(string="Parentezco")
    direccion=fields.Char(string="Dirección")
    telefono=fields.Char(string="Teléfono")
    entrega_id = fields.Many2one('entrega.vehiculo')

    garante= fields.Boolean(default=False)



class EgresosFinanciero(models.Model):
    _name = 'egresos.financiero.entrega.vehiculo'
    _description = 'Egresos Financieros '

    currency_id = fields.Many2one(
        'res.currency', readonly=True, default=lambda self: self.env.company.currency_id)
 
    entrega_id = fields.Many2one('entrega.vehiculo')
    tipo=fields.Char(default="Egresos")
    egresos_id = fields.Many2one('egresos.financiero')
    titular  = fields.Monetary(string="Titular($)",digits=(6, 2))
    conyuge  = fields.Monetary(string="Conyuge($)",digits=(6, 2))

    garante= fields.Boolean(default=False)


class ItemPatrimonioEntregaVehiculo(models.Model):
    _name = 'items.patrimonio.entrega.vehiculo'
    _description = 'Items de Patrimonio '

    currency_id = fields.Many2one(
        'res.currency', readonly=True, default=lambda self: self.env.company.currency_id)
    entrega_id = fields.Many2one('entrega.vehiculo')
    patrimonio_id = fields.Many2one('items.patrimonio')
    poseeBien = fields.Selection(selection=[ ('SI', 'SI'),('NO', 'NO')], string='SI/NO', default='NO')
    descripcion = fields.Char()
    valor  = fields.Monetary(string="Monto($)",digits=(6, 2))
    garante= fields.Boolean(default=False)

class PaginasDeControlEntregaVehiculo(models.Model):
    _name = 'paginas.de.control.entrega.vehiculo'
    _description = 'Revisión de páginas de control en Entrega de vehiculo'
    
    entrega_id = fields.Many2one('entrega.vehiculo')
    pagina_id = fields.Many2one('paginas.de.control')
    descripcion  = fields.Char(related='pagina_id.descripcion')
    pagina = fields.Selection(selection=[ ('SI', 'SI'),('NO', 'NO')], default='SI')
    garante= fields.Boolean(default=False)

class PuntosBienesEntregaVehiculo(models.Model):
    _name = 'puntos.bienes.entrega.vehiculo'
    _description = 'Tabla de puntos Bienes'
    
    entrega_id = fields.Many2one('entrega.vehiculo')
    bien_id = fields.Many2one('puntos.bienes')
    garante= fields.Boolean(default=False)
    valorBien  = fields.Integer(related='bien_id.valorPuntos')
    puntosBien = fields.Integer(string='Ptos.', compute = 'set_puntos_bienes', store = True) 
    poseeBien = fields.Selection(selection=[ ('SI', 'SI'),('NO', 'NO')], string='SI/NO', default='NO')
    

    @api.depends('poseeBien')
    def set_puntos_bienes(self):
        valorDefault = 0
        for rec in self:
            if rec.poseeBien == 'NO':
                rec.puntosBien = valorDefault
            else:
                rec.puntosBien = rec.valorBien 



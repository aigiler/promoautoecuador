# -*- coding: utf-8 -*-
from datetime import date, timedelta
from logging import StringTemplateStyle
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
    fechaNacimientoAdj  = fields.Date(related="nombreSocioAdjudicado.fecha_nacimiento", string='Fecha de Nacimiento')
    vatAdjudicado = fields.Char(related="nombreSocioAdjudicado.vat", string='Cedula de Ciudadanía')
    estadoCivilAdj  = fields.Selection(related="nombreSocioAdjudicado.estado_civil")
    edadAdjudicado  = fields.Integer(compute='calcular_edad', string="Edad")
    cargasFamiliares = fields.Integer( string="Cargas Fam.")
    # datos del conyuge
    nombreConyuge = fields.Char(string="Nombre del Conyuge")
    fechaNacimientoConyuge = fields.Date(string='Fecha de Nacimiento')
    vatConyuge = fields.Char(string='Cedula de Ciudadanía')
    estadoCivilConyuge = fields.Selection(selection=[
                    ('soltero', 'Soltero/a'),
                    ('union_libre', 'Unión libre'),
                    ('casado', 'Casado/a'),
                    ('divorciado', 'Divorciado/a'),
                    ('viudo', 'Viudo/a')                    
                    ], string='Estado Civil', default='soltero')
    edadConyuge  = fields.Integer(compute='calcular_edad_conyuge', string="Edad")

    #datos domiciliarios
    referenciaDomiciliaria = fields.Text(string='Referencias indican:')

    #datos laborales
    referenciasLaborales = fields.Text(string='Referencias indican:')

    #datos del patrimonio del socio
    currency_id = fields.Many2one('res.currency', readonly=True, default=lambda self: self.env.company.currency_id)
    montoAhorroInversiones =  fields.Monetary(string='Ahorro o Inversiones')
    casaValor  = fields.Monetary(string='Casa Valor', default=0.00)
    terrenoValor  = fields.Monetary(string='Terreno Valor', default=0.00)
    montoMueblesEnseres = fields.Monetary(string='Muebles y Enseres', default=0.00)
    vehiculoValor = fields.Monetary(string='Vehiculo Valor',  default=0.00)
    inventarios  = fields.Monetary(string='Inventarios',  default=0.00)
    
    institucionFinanciera = fields.Char(string='Institución')
    direccion = fields.Char(string='Direccion')
    direccion1 = fields.Char(string='Direccion')
    placa  = fields.Char(string='Placa')

    totalActivosAdj = fields.Float(compute='calcular_total_activos', string='TOTAL ACTIVOS', digits=(6, 2))

    # REVISION EN PAGINAS DE CONTROL
    scoreBuroCredito = fields.Integer(string='Score')
    posee = fields.Char(string='Posee')
    score = fields.Char(string='Posee')
    poseeAntecedentesPenales  = fields.Selection(selection=[
                    ('si', 'SI'),
                    ('no', 'NO')                  
                    ], string='Policía Nacional antecedentes', default='no')

    estadoTributario = fields.Selection(selection=[
                    ('atrasado', 'ATRASADO'),
                    ('no_activo', 'NO ACTIVO'),
                    ('al_dia', 'AL DIA')                  
                    ], string='SRI, deudas firmes y estado Tributario', default='al_dia')
    
    funcionJudicial = fields.Selection(selection=[
                    ('si', 'SI'),
                    ('no', 'NO')                  
                    ], string='Función Judicial', default='no')
    
    fiscaliaGeneral = fields.Selection(selection=[
                    ('si', 'SI'),
                    ('no', 'NO')                  
                    ], string='Fiscalia General del Estado', default='no')
    
    #observaciones
    observaciones = fields.Text(string='Observaciones')
    

    #calificador compras
    clienteContrato  = fields.Char(compute = 'set_campos_cliente_informe_credito',string="Nombre del Socio Adj.")
    cedulaContrato = fields.Char()
    codClienteContrado = fields.Char()
    contratoCliente =_id = fields.Many2one('contrato',string='')
    montoAdjudicado  = fields.Integer(related="contrato.monto_financiamiento", currency_field='currency_id', string='Monto Adjudicado')
    plazoMeses = fields.Integer(related="contrato.plazo_meses", string='Plazo')
    tipoAdj = fields.Selection(related="contrato.tipo_de_contrato")
    
    valorCuota = fields.Monetary(string='Valor de Cuota')
    # #    #
    fechaAdj = fields.Date(string='Fecha de Adj.')

    valorTotalPlan = fields.Monetary(string='Valor Total del Plan')
    porcentajeTotal = fields.Float(digits=(6, 2))
    montoCancelado = fields.Monetary(string='Cuotas Canceladas')
    cuotasCanceladas  = fields.Integer()
    montoPendiente = fields.Float()
    porcentajeCancelado = fields.Float(digits=(6, 2))
    porcentajePendiente = fields.Float(digits=(6, 2))
    cuotasPendientes  = fields.Integer()

    valorDelBien = fields.Monetary(string='Valor del Bien')
    saldoPlan = fields.Monetary(string='Saldo del Plan')

    ingresosFamiliares = fields.Monetary(string='Saldo del Plan')
    porcentajeIngresos = fields.Float(digits=(6, 2))
    gastosFamiliares = fields.Monetary(string='Saldo del Plan')
    porcentajeGastos = fields.Float(digits=(6, 2))
    disponibilidad = fields.Monetary(string='Saldo del Plan')
    
    scoreCredito  = fields.Integer(string="Score de Credito Mayor a 800 puntos")
    puntosScoreCredito = fields.Integer()
    antiguedadLaboral  = fields.Integer(string="Antigüedad Laboral o Comercial Mayor a 2 años")
    puntosAntiguedadLaboral = fields.Integer()
    
    totalPuntosBienesAdj = fields.Integer()

    poseeCasa = fields.Selection(selection=[
                    ('si', 'SI'),
                    ('no', 'NO')                  
                    ], string='Fiscalia General del Estado', default='no')
    
    puntosCasa = fields.Integer()

    poseeTerreno = fields.Selection(selection=[
                    ('si', 'SI'),
                    ('no', 'NO')                  
                    ], string='Fiscalia General del Estado', default='no')

    puntosTerreno = fields.Integer()

    poseeVehiculo = fields.Selection(selection=[
                    ('si', 'SI'),
                    ('no', 'NO')                  
                    ], string='Fiscalia General del Estado', default='no')
    puntosVehiculo = fields.Integer()
    poseeMotos = fields.Selection(selection=[
                    ('si', 'SI'),
                    ('no', 'NO')                  
                    ], string='Fiscalia General del Estado', default='no')
    puntosMotos = fields.Integer()
    poseeMueblesEnseres = fields.Selection(selection=[
                    ('si', 'SI'),
                    ('no', 'NO')                  
                    ], string='Fiscalia General del Estado', default='no')
    puntosMueblesEnseres = fields.Integer()

    totalPuntosCalificador = fields.Integer()

    observacionesCalificador  = fields.Text(string="Observaciones")




    @api.depends('nombreSocioAdjudicado')
    def set_campos_cliente_informe_credito(self):
        clienteContrato = ''  
        for rec in self:
            if rec.nombreSocioAdjudicado :
               
                rec.clienteContrato = rec.nombreSocioAdjudicado
            else:
                rec.clienteContrato = '' 

    @api.depends('montoAhorroInversiones', 'casaValor','terrenoValor', 'montoMueblesEnseres','vehiculoValor','inventarios')
    def calcular_total_activos(self):
        totalActivos = 0
        for rec in self:
            totalActivos = rec.montoAhorroInversiones + rec.casaValor + rec.terrenoValor + rec.vehiculoValor + rec.montoMueblesEnseres + rec.inventarios
            rec.totalActivosAdj = totalActivos

    @api.depends('fechaNacimientoAdj')
    def calcular_edad(self):
        edad = 0  
        for rec in self:
            today = date.today()
            if rec.fechaNacimientoAdj :
                edad = today.year - rec.fechaNacimientoAdj.year - ((today.month, today.day) < (rec.fechaNacimientoAdj.month, rec.fechaNacimientoAdj.day))
                rec.edadAdjudicado =edad
            else:
                rec.edadAdjudicado = 0
   
    @api.onchange('fechaNacimientoConyuge')
    def calcular_edad_conyuge(self): 
        edad = 0 
        for rec in self:
            today = date.today()
            if rec.fechaNacimientoConyuge:
                edad = today.year - rec.fechaNacimientoConyuge.year - ((today.month, today.day) < (rec.fechaNacimientoConyuge.month, rec.fechaNacimientoConyuge.day))
                rec.edadConyuge =edad
            else:
                rec.edadConyuge = 0

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





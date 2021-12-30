# -*- coding: utf-8 -*-
from datetime import date, timedelta
import datetime
from logging import StringTemplateStyle
import logging
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class EntegaVehiculo(models.Model):
    _name = 'entrega.vehiculo'
    _description = 'Entrega Vehiculo'
    _rec_name = 'secuencia'
    _inherit = ['mail.thread', 'mail.activity.mixin']



    rolAsignado = fields.Many2one('adjudicaciones.team', string="Rol Asignado", track_visibility='onchange')

    rolCredito = fields.Many2one('adjudicaciones.team', string="Rol Credito", track_visibility='onchange',default=lambda self:self.env.ref('gzl_adjudicacion.tipo_rol3'))
    rolGerenciaAdmin = fields.Many2one('adjudicaciones.team', string="Rol Gerencia Admin", track_visibility='onchange',default=lambda self:self.env.ref('gzl_adjudicacion.tipo_rol1'))
    rolGerenciaFin = fields.Many2one('adjudicaciones.team', string="Rol Gerencia Financiera", track_visibility='onchange',default=lambda self:self.env.ref('gzl_adjudicacion.tipo_rol4'))
    rolAdjudicacion = fields.Many2one('adjudicaciones.team', string="Rol Adjudicacion", track_visibility='onchange',default=lambda self:self.env.ref('gzl_adjudicacion.tipo_rol2'))



    secuencia = fields.Char(index=True)
    requisitosPoliticasCredito = fields.Html(string='Informacion Cobranzas', default=lambda self: self._capturar_valores_por_defecto())
    
    def _capturar_valores_por_defecto(self):
        referencia=self.env.ref('gzl_adjudicacion.configuracion_adicional1')
        return referencia.requisitosPoliticasCredito

        
    documentos = fields.Many2many('ir.attachment', string='Carga Documentos', track_visibility='onchange')
    active = fields.Boolean(string='Activo', default=True)
    state = fields.Selection(selection=[
        ('borrador', 'Borrador'),
        ('revision_documentos', 'Revisión documentos'),
        ('informe_de_créditos_y_cobranzas', 'Informe de Crédito y Cobranza'),
        ('calificador_compra', 'Calificador para compra del bien'),
        ('liquidacion_orden_compra', 'Liquidación de compra y orden de compra'),
        ('orden_compra', 'Orden de compra'),
        ('entrega_vehiculo', 'Entrega de Vehiculo'),
    ], string='Estado', default='borrador', track_visibility='onchange')
    # datos del socio adjudicado
    nombreSocioAdjudicado = fields.Many2one('res.partner', string="Nombre del Socio Adj.", track_visibility='onchange')
    codigoAdjudicado = fields.Char(related="nombreSocioAdjudicado.codigo_cliente", string='Código', track_visibility='onchange')
    fechaNacimientoAdj = fields.Date(related="nombreSocioAdjudicado.fecha_nacimiento", string='Fecha de Nacimiento')
    vatAdjudicado = fields.Char(related="nombreSocioAdjudicado.vat", string='Cedula de Ciudadanía')
    estadoCivilAdj = fields.Selection(related="nombreSocioAdjudicado.estado_civil")
    edadAdjudicado = fields.Integer(compute='calcular_edad', string="Edad")
    cargasFamiliares = fields.Integer(string="Cargas Fam.")
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
    edadConyuge = fields.Integer(compute='calcular_edad_conyuge', string="Edad")

    # datos domiciliarios
    referenciaDomiciliaria = fields.Text(string='Referencias indican:')

    # datos laborales
    referenciasLaborales = fields.Text(string='Referencias indican:')

    # datos del patrimonio del socio
    currency_id = fields.Many2one('res.currency', readonly=True, default=lambda self: self.env.company.currency_id)
    #    junta = fields.One2many('junta.grupo.asamblea', 'asamblea_id',track_visibility='onchange')

    montoAhorroInversiones = fields.One2many('items.patrimonio.entrega.vehiculo','entrega_id',track_visibility='onchange')
    
    def llenar_tabla(self):
        obj_patrimonio=self.env['items.patrimonio'].search([])  
        for patrimonio in obj_patrimonio:
            self.env['items.patrimonio.entrega.vehiculo'].create({'patrimonio_id':patrimonio.id,'entrega_id':self.id})
        

    institucionFinanciera = fields.Char(string='Institución')
    direccion = fields.Char(string='Direccion')
    direccion1 = fields.Char(string='Direccion')
    placa = fields.Char(string='Placa')
    totalActivosAdj = fields.Float(string='TOTAL ACTIVOS', digits=(6, 2))

    # REVISION EN PAGINAS DE CONTROL
    paginasDeControl = fields.One2many('paginas.de.control.entrega.vehiculo','entrega_id',track_visibility='onchange')
    
    def llenar_tabla_paginas(self):
        obj_paginas_de_control=self.env['paginas.de.control'].search([])
        for paginas in obj_paginas_de_control:
            self.env['paginas.de.control.entrega.vehiculo'].create({'pagina_id':paginas.id,'entrega_id':self.id})
    
    
    
    
    scoreBuroCredito = fields.Integer(string='Buró de Crédito')
    posee = fields.Char(string='Posee')
    score = fields.Char(string='Posee')
    poseeAntecedentesPenales = fields.Selection(selection=[
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

    # observaciones
    observaciones = fields.Text(string='Observaciones')

    # calificador compras
    clienteContrato = fields.Char(compute='set_campos_cliente_informe_credito', string="Nombre del Socio Adj.")
    cedulaContrato = fields.Char()
    codClienteContrado = fields.Char()
    contratoCliente = fields.Char()
    montoAdjudicado = fields.Monetary(compute='buscar_parner', currency_field='currency_id', string='Monto Adjudicado')
    plazoMeses = fields.Integer(string='Plazo')
    tipoAdj = fields.Char(string='Tipo Adj.')
    valorCuota = fields.Monetary(string='Valor de Cuota')
    fechaAdj = fields.Date(string='Fecha de Adj.')
    # valores del plan
    valorTotalPlan = fields.Monetary(compute='calcular_valor_total_plan', string='Valor Total del Plan')
    porcentajeTotal = fields.Float(default=100.00)
    
    montoCuotasCanceladas = fields.Monetary(string='Cuotas Canceladas', compute='calcular_valor_cuotas_canceladas')
    cuotasCanceladas = fields.Integer()
    porcentajeCancelado = fields.Float(digits=(6, 2), compute='calcular_porcentaj_cuotas_canc')

    montoCuotasPendientes = fields.Monetary(string='Cuotas Pendientes', compute='calcular_valor_cuotas_pendientes')
    cuotasPendientes = fields.Integer(compute='calcular_cuotas_pendientes')
    porcentajePendiente = fields.Float(digits=(6, 2), compute='calcular_porcentaj_pendiente')
    
    #puntos valor cancelado del plan
    puntosPorcentajeCancelado = fields.Integer(string = 'puntos', compute='calcular_puntos_porcentaje_cancelado')

    #saldosBien
    valorDelBien = fields.Monetary(string='Valor del Bien', compute='set_valor_del_bien')
    saldoPlan = fields.Monetary(string='Saldo del Plan', compute='set_valor_saldo_plan')
    porcentajeSaldoPlan = fields.Float(digits=(6, 2), compute='calcular_porcentaj_saldo_plan', default=0.00)
    #puntos saldos
    puntosPorcentajSaldos = fields.Integer(compute='calcular_puntos_porcentaje_saldos')
    
    #ingresos y gastos
    puntosCuotaIngresos = fields.Integer(compute='calcular_puntos_ingresos')

    puntosSaldosPlan = fields.Float(digits=(6, 2), compute='calcular_puntos_saldos_plan')
    ingresosFamiliares = fields.Monetary(string='Ingresos familiares')
    gastosFamiliares = fields.Monetary(string='Gastos familiares', compute='calcular_valor_gastos_familiares')
    porcentajeIngresos = fields.Float(default=100.00)

    porcentajeGastos = fields.Float( digits=(6, 2), compute='calcular_porcentaje_gastos_familiares')
    porcentajeDisponibilidad = fields.Float(digits=(6, 2), compute='calcular_porcentaje_disponibilidad')
    disponibilidad = fields.Monetary(string='Disponibilidad', compute='calcular_valor_disponibilidad')
    porcentajeCuotaPlan = fields.Float(digits=(6, 2), default=0.0, compute='calcular_porcentaje_cuota_plan')

    scoreCredito = fields.Integer(string="Score de Credito Mayor a 800 puntos")
    puntosScoreCredito = fields.Integer(compute='calcular_punto_score_credito')
    antiguedadLaboral = fields.Integer(string="Antigüedad Laboral o Comercial Mayor a 2 años")
    puntosAntiguedadLaboral = fields.Integer(
        compute='calcular_puntos_antiguedad_laboral')

    totalPuntosBienesAdj = fields.Integer(compute='calcular_puntos_bienes')

    poseeCasa = fields.Selection(selection=[
        ('si', 'SI'),
        ('no', 'NO')
    ], string='Fiscalia General del Estado', default='no')

    puntosCasa = fields.Integer(compute='set_puntos_casa')

    poseeTerreno = fields.Selection(selection=[
        ('si', 'SI'),
        ('no', 'NO')
    ], string='Fiscalia General del Estado', default='no')

    puntosTerreno = fields.Integer(compute='set_puntos_terreno')

    poseeVehiculo = fields.Selection(selection=[
        ('si', 'SI'),
        ('no', 'NO')
    ], string='Fiscalia General del Estado', default='no')
    puntosVehiculo = fields.Integer(compute='set_puntos_vehiculo')
    poseeMotos = fields.Selection(selection=[
        ('si', 'SI'),
        ('no', 'NO')
    ], string='Fiscalia General del Estado', default='no')
    puntosMotos = fields.Integer(compute='set_puntos_motos')
    poseeMueblesEnseres = fields.Selection(selection=[
        ('si', 'SI'),
        ('no', 'NO')
    ], string='Fiscalia General del Estado', default='no')
    puntosMueblesEnseres = fields.Integer(compute='set_puntos_muebles')

    totalPuntosCalificador = fields.Integer(compute='calcular_total_puntos')

    observacionesCalificador = fields.Text(string="Observaciones")

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
    montoChequeConsesionario = fields.Monetary(compute='calcular_valor_cheque')
    nombreConsesionario = fields.Many2one(
        'res.partner', string="NOMBRE DEL CONCESIONARIO:")
    observacionesLiquidacion = fields.Text(string="Observaciones")
    
    liquidacionCompra = fields.Many2one('account.move', string="LIquidación de Compra")
    ordenCompra  = fields.Many2one('account.move', string="Orden de Compra")
    dia = fields.Char()
    mes = fields.Char(string='')
    anio = fields.Char()
    
    aplicaGarante = fields.Selection(selection=[
        ('no', 'Titular, Conyugue y Depositario'),
        ('si', 'Titular, Conyugue y Garante Solidario')
    ], compute='set_aplica_garante')
    
    montoPagoConsesionario = fields.Selection(selection=[
        ('saldo_a_favor', 'SALDO A FAVOR APLICA A CUOTAS FINALES DEL PLAN'),
        ('diferencia', 'DIFERENCIA PAGA AL CONCESIONARIO')
    ], default = 'saldo_a_favor', compute='calcular_monto_a_favor')
    
    
    @api.depends('montoVehiculo', 'montoAdjudicado')
    def calcular_monto_a_favor(self):
        for rec in self:
            rec.montoAFavor = rec.montoVehiculo - rec.montoAdjudicado
            if rec.montoVehiculo < rec.montoAdjudicado:
                rec.montoPagoConsesionario = 'saldo_a_favor'
            else:
                rec.montoPagoConsesionario = 'diferencia'    
    
    
    @api.depends('totalPuntosCalificador')
    def set_aplica_garante(self):
        for rec in self:
            if rec.totalPuntosCalificador  >= 700:
                rec.aplicaGarante = 'no'
            else:
                rec.aplicaGarante = 'si'
    

    @api.depends('valorAdjParaCompra', 'valorComisionFactura', 'comisionDispositivoRastreo', 'montoAnticipoConsesionaria')
    def calcular_valor_cheque(self):
        for rec in self:
            rec.montoChequeConsesionario = rec.valorAdjParaCompra - rec.valorComisionFactura - \
                rec.comisionDispositivoRastreo - rec.montoAnticipoConsesionaria

    @api.depends('montoVehiculo', 'comisionFacturaConcesionario')
    def calcular_valor_comision_fact(self):
        for rec in self:
            decimalPorcentaje = (rec.comisionFacturaConcesionario/100)
            rec.valorComisionFactura = rec.montoVehiculo * decimalPorcentaje

    @api.depends('montoVehiculo', 'montoAdjudicado')
    def calcular_valor_adj_para_compra(self):
        for rec in self:
            # si el valor del plan adj. es menor al valor del vehiculo
            if rec.montoAdjudicado < rec.montoVehiculo:
                rec.valorAdjParaCompra = rec.montoAdjudicado
            else:
                rec.valorAdjParaCompra = rec.montoVehiculo

    
    @api.depends('puntosPorcentajeCancelado', 'puntosPorcentajSaldos', 'puntosCuotaIngresos', 'puntosScoreCredito', 'puntosAntiguedadLaboral', 'totalPuntosBienesAdj')
    def calcular_total_puntos(self):
        for rec in self:
            rec.totalPuntosCalificador = rec.puntosPorcentajeCancelado + rec.puntosPorcentajSaldos +  rec.puntosCuotaIngresos + rec.puntosScoreCredito +  rec.puntosAntiguedadLaboral + rec.totalPuntosBienesAdj

    @api.depends('poseeCasa')
    def set_puntos_casa(self):
        for rec in self:
            if rec.poseeCasa == 'si':
                rec.puntosCasa = 200
            else:
                rec.puntosCasa = 0

    @api.depends('poseeTerreno')
    def set_puntos_terreno(self):
        for rec in self:
            if rec.poseeTerreno == 'si':
                rec.puntosTerreno = 150
            else:
                rec.puntosTerreno = 0

    @api.depends('poseeMotos')
    def set_puntos_motos(self):
        for rec in self:
            if rec.poseeMotos == 'si':
                rec.puntosMotos = 50
            else:
                rec.puntosMotos = 0

    @api.depends('poseeVehiculo')
    def set_puntos_vehiculo(self):
        for rec in self:
            if rec.poseeVehiculo == 'si':
                rec.puntosVehiculo = 100
            else:
                rec.puntosVehiculo = 0

    @api.depends('poseeMueblesEnseres')
    def set_puntos_muebles(self):
        for rec in self:
            if rec.poseeMueblesEnseres == 'si':
                rec.puntosMueblesEnseres = 25
            else:
                rec.puntosMueblesEnseres = 0

    @api.depends('puntosMueblesEnseres', 'puntosVehiculo', 'puntosMotos', 'puntosTerreno', 'puntosCasa')
    def calcular_puntos_bienes(self):
        for rec in self:
            rec.totalPuntosBienesAdj = rec.puntosCasa + rec.puntosTerreno + \
                rec.puntosVehiculo + rec.puntosMotos + rec.puntosMueblesEnseres

    @api.depends('antiguedadLaboral')
    def calcular_puntos_antiguedad_laboral(self):
        for rec in self:
            if rec.antiguedadLaboral >= 2:
                rec.puntosAntiguedadLaboral = 200
            elif rec.antiguedadLaboral >= 1:
                rec.puntosAntiguedadLaboral = 100
            else:
                rec.puntosAntiguedadLaboral = 0

    @api.depends('scoreCredito')
    def calcular_punto_score_credito(self):
        for rec in self:
            if rec.scoreCredito >= 500 and rec.scoreCredito <= 799:
                rec.puntosScoreCredito = 100
            elif rec.scoreCredito >= 800:
                rec.puntosScoreCredito = 200
            else:
                rec.puntosScoreCredito = 0

    @api.depends('saldoPlan', 'valorDelBien')
    def calcular_porcentaj_saldo_plan(self):
        for rec in self:
            if rec.saldoPlan:
                rec.porcentajeSaldoPlan = round(
                    (rec.valorDelBien/rec.saldoPlan) * 100)
            else:
                rec.porcentajeSaldoPlan = 0.00

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

    @api.depends('montoAdjudicado')
    def set_valor_del_bien(self):
        for rec in self:
            if rec.montoAdjudicado:
                rec.valorDelBien = rec.montoAdjudicado
            else:
                rec.valorDelBien = 0.00

    @api.depends('montoCuotasCanceladas')
    def set_valor_saldo_plan(self):
        for rec in self:
            if rec.montoCuotasCanceladas:
                rec.saldoPlan = rec.montoCuotasCanceladas
            else:
                rec.saldoPlan = 0.00

    @api.depends('montoAdjudicado', 'montoPendiente')
    def setear_montos_bien(self):
        for rec in self:
            if rec.ingresosFamiliares:
                rec.porcentajeCuotaPlan = (
                    rec.valorCuota / rec.ingresosFamiliares) * 100
            else:
                rec.porcentajeCuotaPlan = 0

    @api.depends('porcentajeCuotaPlan')
    def calcular_puntos_saldos_plan(self):
        for rec in self:
            if rec.porcentajeCuotaPlan >= 0.00 and rec.porcentajeCuotaPlan <= 25.00:
                rec.puntosPorcentajeCancelado = 0
            elif rec.porcentajeCuotaPlan >= 26.00 and rec.porcentajeCuotaPlan <= 30.00:
                rec.puntosPorcentajeCancelado = 100
            elif rec.porcentajeCuotaPlan >= 31.00:
                rec.puntosPorcentajeCancelado = 200
            else:
                rec.puntosPorcentajeCancelado = 0

    @api.depends('porcentajeCuotaPlan')
    def calcular_puntos_ingresos(self):
        for rec in self:
            if rec.porcentajeCuotaPlan >= 0.00 and rec.porcentajeCuotaPlan <= 30.00:
                rec.puntosCuotaIngresos = 200
            elif rec.porcentajeCuotaPlan >= 31.00 and rec.porcentajeCuotaPlan <= 40.00:
                rec.puntosCuotaIngresos = 100
            elif rec.porcentajeCuotaPlan >= 41.00:
                rec.puntosCuotaIngresos = 0
            else:
                rec.puntosPorcentajeCancelado = 0

    @api.depends('valorCuota', 'ingresosFamiliares')
    def calcular_porcentaje_cuota_plan(self):
        for rec in self:
            if rec.ingresosFamiliares:
                rec.porcentajeCuotaPlan = (rec.valorCuota/rec.ingresosFamiliares) * 100
            else:
                rec.porcentajeCuotaPlan = 0.0

    @api.depends('porcentajeGastos', 'porcentajeIngresos')
    def calcular_porcentaje_disponibilidad(self):
        for rec in self:
            rec.porcentajeDisponibilidad = rec.porcentajeIngresos - rec.porcentajeGastos

    @api.depends('ingresosFamiliares', 'gastosFamiliares')
    def calcular_valor_disponibilidad(self):
        for rec in self:
            rec.disponibilidad = rec.ingresosFamiliares - rec.gastosFamiliares

    @api.depends('ingresosFamiliares')
    def calcular_valor_gastos_familiares(self):
        for rec in self:
            rec.porcentajeIngresos = 100.00
            rec.gastosFamiliares = rec.ingresosFamiliares * 0.7

    @api.depends('gastosFamiliares', 'ingresosFamiliares')
    def calcular_porcentaje_gastos_familiares(self):
        for rec in self:
            rec.porcentajeGastos = (
                rec.gastosFamiliares / rec.ingresosFamiliares) * 100

    @api.depends('ingresosFamiliares', 'gastosFamiliares')
    def calcular_porcentaje_gastos_familiares(self):
        for rec in self:
            if rec.gastosFamiliares:
                rec.porcentajeGastos = (
                    rec.gastosFamiliares / rec.ingresosFamiliares) * 100
            else:
                rec.porcentajeGastos = 0

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

    @api.depends('montoCuotasCanceladas', 'valorTotalPlan')
    def calcular_porcentaj_cuotas_canc(self):
        for rec in self:
            if rec.valorTotalPlan:
                rec.porcentajeCancelado = (
                    rec.montoCuotasCanceladas / rec.valorTotalPlan) * 100
            else:
                rec.porcentajeCancelado = 0.00

    @api.depends('valorTotalPlan', 'montoCuotasCanceladas')
    def calcular_valor_cuotas_pendientes(self):
        for rec in self:
            rec.montoCuotasPendientes = rec.valorTotalPlan - rec.montoCuotasCanceladas

    @api.depends('plazoMeses', 'cuotasCanceladas')
    def calcular_cuotas_pendientes(self):
        for rec in self:
            rec.cuotasPendientes = rec.plazoMeses - rec.cuotasCanceladas

    @api.depends('valorTotalPlan', 'montoCuotasPendientes')
    def calcular_porcentaj_pendiente(self):
        for rec in self:
            if rec.valorTotalPlan:
                rec.porcentajePendiente = (
                    rec.montoCuotasPendientes/rec.valorTotalPlan)*100
            else:
                rec.porcentajePendiente = 0.00

    @api.depends('valorCuota', 'cuotasCanceladas')
    def calcular_valor_cuotas_canceladas(self):
        for rec in self:
            rec.porcentajeTotal = 100.00
            rec.cuotasCanceladas = 31
            rec.montoCuotasCanceladas = rec.valorCuota * rec.cuotasCanceladas

    @api.depends('valorCuota', 'plazoMeses')
    def calcular_valor_total_plan(self):
        for rec in self:
            rec.valorTotalPlan = rec.valorCuota * rec.plazoMeses

    @api.depends('nombreSocioAdjudicado')
    def buscar_parner(self):
        for rec in self:
            contrato = self.env['contrato'].search(
                [('cliente', '=', rec.nombreSocioAdjudicado.id)], limit=1)
            rec.montoAdjudicado = contrato.monto_financiamiento
            rec.valorCuota = contrato.cuota_capital
            rec.tipoAdj = contrato.tipo_de_contrato.name
            rec.fechaAdj = contrato.fecha_adjudicado

            rec.plazoMeses = contrato.plazo_meses.numero


    @api.depends('nombreSocioAdjudicado')
    def set_campos_cliente_informe_credito(self):
        for rec in self:
            if rec.nombreSocioAdjudicado:
                contrato = self.env['contrato'].search(
                [('cliente', '=', rec.nombreSocioAdjudicado.id)], limit=1)
                rec.clienteContrato = contrato
                rec.cedulaContrato = rec.vatAdjudicado
                rec.codClienteContrado = rec.codigoAdjudicado
            else:
                rec.clienteContrato = ''
                rec.cedulaContrato = ''
                rec.codClienteContrado = ''

    # @api.depends('montoAhorroInversiones', 'casaValor', 'terrenoValor', 'montoMueblesEnseres', 'vehiculoValor', 'inventarios')
    # def calcular_total_activos(self):
    #     totalActivos = 0
    #     for rec in self:
    #         totalActivos = rec.montoAhorroInversiones + rec.casaValor + rec.terrenoValor + \
    #             rec.vehiculoValor + rec.montoMueblesEnseres + rec.inventarios
    #         rec.totalActivosAdj = totalActivos

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

    @api.onchange('fechaNacimientoConyuge')
    def calcular_edad_conyuge(self):
        edad = 0
        for rec in self:
            today = date.today()
            if rec.fechaNacimientoConyuge:
                edad = today.year - rec.fechaNacimientoConyuge.year - \
                    ((today.month, today.day) < (
                        rec.fechaNacimientoConyuge.month, rec.fechaNacimientoConyuge.day))
                rec.edadConyuge = edad
            else:
                rec.edadConyuge = 0

    @api.model
    def create(self, vals):
        vals['secuencia'] = self.env['ir.sequence'].next_by_code(
            'entrega.vehiculo')
        return super(EntegaVehiculo, self).create(vals)


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

class ItemPatrimonioEntregaVehiculo(models.Model):
    _name = 'items.patrimonio.entrega.vehiculo'
    _description = 'Items de Patrimonio '

    currency_id = fields.Many2one(
        'res.currency', readonly=True, default=lambda self: self.env.company.currency_id)
    entrega_id = fields.Many2one('entrega.vehiculo')
    patrimonio_id = fields.Many2one('items.patrimonio')
    valor  = fields.Monetary(digits=(6, 2))
    
class PaginasDeControlEntregaVehiculo(models.Model):
    _name = 'paginas.de.control.entrega.vehiculo'
    _description = 'Revisión de páginas de control en Entrega de vehiculo'
    
    entrega_id = fields.Many2one('entrega.vehiculo')
    pagina_id = fields.Many2one('paginas.de.control')
    descripcion  = fields.Char(related='pagina_id.descripcion')
    pagina = fields.Selection(selection=[ ('si', 'SI'),('no', 'NO')], default='no')
    
    




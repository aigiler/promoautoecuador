# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from datetime import date, timedelta
from email.policy import default
from logging import StringTemplateStyle
import logging
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


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
    asamblea = fields.Many2one('asamblea','Asamblea del Adjudicado')

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

        ('entrega_vehiculo', 'Entrega de Vehículo'),


    ], string='Estado', default='borrador', track_visibility='onchange')
    # datos del socio adjudicado
    nombreSocioAdjudicado = fields.Many2one('res.partner', string="Nombre del Socio Adj.", track_visibility='onchange')
    nombreGarante = fields.Many2one('res.partner', string="Nombre del Garante", track_visibility='onchange')
    factura_id = fields.Many2one('account.move', string='Factura')
    archivo = fields.Binary(string='Adjuntar Documento')

    documentos_pagos = fields.Binary(string='Adjuntar Documento')

    pago_seguro_id=fields.Many2one("account.payment", string="Pago de Seguro")
    pago_rastreo_id=fields.Many2one("account.payment", string="Pago de Rastreo")
    pago_factura=fields.Many2one("account.payment", string="Pago de Factura")
    pago_matriculacion_id=fields.Many2one("account.payment", string="Pago de Matriculación")

    vatAdjudicado = fields.Char(related="nombreSocioAdjudicado.vat", string='Cedula de Ciudadanía',store=True, default=' ')
    vatGarante = fields.Char(related="nombreGarante.vat", string='Cedula de Ciudadanía',store=True)    
    
    fechaNacimientoGarante = fields.Date(related="nombreGarante.fecha_nacimiento",String='Fecha de Nacimiento')
    fechaNacimientoAdj = fields.Date(related="nombreSocioAdjudicado.fecha_nacimiento", string='Fecha de Nacimiento',compute = 'setea_valores_informe', store=True)
    
    estadoCivilGarante = fields.Selection(related="nombreGarante.estado_civil" ,store=True)    
    estadoCivilAdj = fields.Selection(related="nombreSocioAdjudicado.estado_civil" ,store=True)
    
    codigoAdjudicado = fields.Char(related="nombreSocioAdjudicado.codigo_cliente", string='Código', track_visibility='onchange',store=True, default=' ') 
    codigoGarante = fields.Char(related="nombreGarante.codigo_cliente", string='Código', track_visibility='onchange',store=True, default=' ') 

    edadAdjudicado = fields.Integer(compute='calcular_edad', string="Edad", readonly=True, store=True, default = 0)
    edadGarante = fields.Integer(compute='calcular_edad_Garante', string="Edad", readonly=True, store=True, default = 0)

    cargasFamiliares = fields.Integer(string="Cargas Fam." , related="nombreSocioAdjudicado.num_cargas_familiares", store=True, default = 0)
    cargasFamiliaresGarante = fields.Integer(string="Cargas Fam." , related="nombreGarante.num_cargas_familiares", store=True,default = 0)

    #nombreConyuge = fields.Char(related="nombreSocioAdjudicado.conyuge", string="Nombre del Conyuge", store=True)
    #nombreConyugeGarante = fields.Char(related="nombreGarante.conyuge", string="Nombre del Conyuge", store=True)

    #fechaNacimientoConyuge = fields.Date(related="nombreSocioAdjudicado.fechaNacimientoConyuge", string='Fecha de Nacimiento',store=True)
    #fechaNacimientoConyugeGarante = fields.Date(related="nombreGarante.fechaNacimientoConyuge", string='Fecha de Nacimiento',store=True)

    #vatConyuge = fields.Char(related="nombreSocioAdjudicado.vatConyuge", string='Cedula de Ciudadanía', store=True)
    #vatConyugeGarante = fields.Char(related="nombreGarante.vatConyuge", string='Cedula de Ciudadanía', store=True)

    telefonosAdj = fields.Char(string='Celular')

    estadoCivilConyuge = fields.Selection(selection=[
        ('soltero', 'Soltero/a'),
        ('union_libre', 'Unión libre'),
        ('casado', 'Casado/a'),
        ('divorciado', 'Divorciado/a'),
        ('viudo', 'Viudo/a')
    ], string='Estado Civil', default='soltero',related="nombreSocioAdjudicado.estado_civil",store=True)

    estadoCivilConyugeGarante = fields.Selection(selection=[
        ('soltero', 'Soltero/a'),
        ('union_libre', 'Unión libre'),
        ('casado', 'Casado/a'),
        ('divorciado', 'Divorciado/a'),
        ('viudo', 'Viudo/a')
    ], string='Estado Civil', default='soltero',related="nombreGarante.estado_civil" )
    
    edadConyugeGarante = fields.Integer(compute='calcular_edad_conyuge', string="Edad", default = 0)
    edadConyuge = fields.Integer(compute='calcular_edad_conyuge', string="Edad", default = 0)

    # datos domiciliarios
    referenciaDomiciliaria = fields.Text( string='Referencias indican:', default=' ',store=True)
    referenciaDomiciliariaGarante = fields.Text( string='Referencias indican:', default=' ',store=True)

    # datos laborales
    referenciasLaborales = fields.Text(string='Referencias indican:', default=' ',store=True)
    referenciasLaboralesGarante = fields.Text(string='Referencias indican:', default=' ',store=True)

    institucionFinanciera = fields.Many2one('res.bank',string='Institución')
    institucionFinancieraGarante = fields.Many2one('res.bank',string='Institución')
    
    direccion = fields.Char(string='Direccion de Casa' , default=' ',related="nombreSocioAdjudicado.street")
    direccionGarante = fields.Char(string='Direccion de Casa' , default=' ',related="nombreGarante.street")
    
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
    montoAhorroInversiones = fields.One2many('items.patrimonio.entrega.vehiculo','entrega_id',domain=[('garante','=',False)] ,track_visibility='onchange')
    montoAhorroInversionesGarante = fields.One2many('items.patrimonio.entrega.vehiculo','entrega_id',domain=[('garante','=',True)], track_visibility='onchange')
    ahorro_garante=fields.Boolean(default=False)


    proceso_finalizado=fields.Boolean(default=False)
    actividad_id = fields.Many2one('mail.activity',string="Actividades")


    def crear_activity(self,rol):
        if self.actividad_id:
            self.actividad_id.action_done()
        if not self.proceso_finalizado:

            actividad_id=self.env['mail.activity'].create({
                    'res_id': self.id,
                    'res_model_id': self.env['ir.model']._get('entrega.vehiculo').id,
                    'activity_type_id': 4,
                    'summary': "Ha sido asignado al proceso de Entrega de Vehículo para su revisón/Aprobación",
                    'user_id': rol.user_id.id,
                    'date_deadline':datetime.now()+ relativedelta(days=1)
                })
            self.actividad_id=actividad_id.id

    def llenar_tabla(self):
        obj_patrimonio=self.env['items.patrimonio'].search([])  
        
        if not self.montoAhorroInversiones:
            lista_ids=[]
            for patrimonio in obj_patrimonio:
                id_registro=self.env['items.patrimonio.entrega.vehiculo'].create({'patrimonio_id':patrimonio.id,'garante':False})
                lista_ids.append(int(id_registro))
            self.update({'montoAhorroInversiones':[(6,0,lista_ids)]})
        if self.garante and not self.ahorro_garante:
            lista_ids=[]
            for patrimonio in obj_patrimonio:
                id_registro=self.env['items.patrimonio.entrega.vehiculo'].create({'patrimonio_id':patrimonio.id,'garante':True})
                lista_ids.append(int(id_registro))
            self.update({'montoAhorroInversionesGarante':[(6,0,lista_ids)]})
            self.ahorro_garante=True

    # REVISION EN PAGINAS DE CONTROL
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
        if not self.pagcontrol_garante and self.garante:
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
        l.comisionFacturaConcesionario=porcentaje




#####Funcion para crear purchase order
    def create_purchase_order(self):
        view_id = self.env.ref('gzl_reporte.informe_credito_cobranza_form').id
        return {'type': 'ir.actions.act_window',
                'name': 'ORDEN DE COMPRA',
                'res_model': 'informe.credito.cobranza',
                'target': 'new',
                'view_mode': 'form',
                'views': [[view_id, 'form']],
                'context': {
                    'default_entrega_vehiculo_id': self.id,
                }
        }

        # for l in self:
        #     if not l.nombreConsesionario:
        #         raise ValidationError("Ingrese el Concesionario..")
        #     if l.marcaVehiculo and l.modeloVehiculoSRI and l.colorVehiculo and l.anioVehiculo:
        #         producto_creado=self.env['product.product'].create({'uom_id':1,
        #                                                             'name':str(l.marcaVehiculo)+' '+str(l.modeloVehiculoSRI)+' '+str(l.anioVehiculo)+' '+str(l.colorVehiculo)})
        #         self.products_id=producto_creado
        #     else:
        #         raise ValidationError("Verifique que los datos del vehiculo esten ingresados.")
        #     purchase_creado= self.env['purchase.order'].create({
        #     'partner_id': self.nombreConsesionario.id,
        #     'date_order': datetime.datetime.now(),
        #     #'currency_id': eur_currency.id,
        #     'order_line': [
        #         (0, 0, {
        #             'name': self.products_id.name,
        #             'product_id': self.products_id.id,
        #             'product_qty': 1.0,
        #             'product_uom': self.products_id.uom_id.id,
        #             'price_unit': self.montoVehiculo,
        #             'date_planned': datetime.datetime.now(),
        #         }),
        #     ],
        #     })
        #     self.purchase_order = purchase_creado
    
#####Funcion para crear liquidacion de compra
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


    ingresosFamiliares = fields.Monetary(string='Ingresos familiares')

    porcentajeIngresos = fields.Float(default=100.00)

    gastosFamiliares = fields.Monetary(string='Gastos familiares', compute='calcular_valor_gastos_familiares')

    @api.depends('ingresosFamiliares')
    def calcular_valor_gastos_familiares(self):
        for rec in self:
            rec.porcentajeIngresos = 100.00
            rec.gastosFamiliares = rec.ingresosFamiliares * 0.7


    porcentajeGastos = fields.Float( digits=(6, 2), compute='calcular_porcentaje_gastos_familiares')

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


    porcentajeCuotaPlan = fields.Float(digits=(6, 2), default=0.0, compute='calcular_porcentaje_cuota_plan')


    @api.depends('valorCuota', 'ingresosFamiliares')
    def calcular_porcentaje_cuota_plan(self):
        for rec in self:
            if rec.ingresosFamiliares:
                rec.porcentajeCuotaPlan = round(((rec.valorCuota/rec.ingresosFamiliares) * 100), 0) 
            else:
                rec.porcentajeCuotaPlan = 0.0

    puntosCuotaIngresos = fields.Integer(compute='calcular_puntos_ingresos')
 
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



    puntosSaldosPlan = fields.Float(digits=(6, 2), compute='calcular_puntos_saldos_plan')

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


    porcentajeDisponibilidad = fields.Float(digits=(6, 2), compute='calcular_porcentaje_disponibilidad')

    @api.depends('porcentajeGastos', 'porcentajeIngresos')
    def calcular_porcentaje_disponibilidad(self):
        for rec in self:
            rec.porcentajeDisponibilidad = rec.porcentajeIngresos - rec.porcentajeGastos


    disponibilidad = fields.Monetary(string='Disponibilidad', compute='calcular_valor_disponibilidad')

    @api.depends('ingresosFamiliares', 'gastosFamiliares')
    def calcular_valor_disponibilidad(self):
        for rec in self:
            rec.disponibilidad = rec.ingresosFamiliares - rec.gastosFamiliares


    scoreCredito = fields.Integer(string="Score de Credito Mayor a 800 puntos")


    @api.onchange('scoreBuroCredito')
    def calculo_scoreCredito(self):
        self.scoreCredito= self.scoreBuroCredito 

    puntosScoreCredito = fields.Integer(compute='calcular_punto_score_credito')

    @api.depends('scoreCredito')
    def calcular_punto_score_credito(self):
        for rec in self:
            if rec.scoreCredito >= 500 and rec.scoreCredito <= 799:
                rec.puntosScoreCredito = 100
            elif rec.scoreCredito >= 800:
                rec.puntosScoreCredito = 200
            else:
                rec.puntosScoreCredito = 0


    antiguedadLaboral = fields.Integer(string="Antigüedad Laboral o Comercial Mayor a 2 años")
    
    puntosAntiguedadLaboral = fields.Integer(compute='calcular_puntos_antiguedad_laboral')


    @api.depends('antiguedadLaboral')
    def calcular_puntos_antiguedad_laboral(self):
        for rec in self:
            if rec.antiguedadLaboral >= 2:
                rec.puntosAntiguedadLaboral = 200
            elif rec.antiguedadLaboral >= 1:
                rec.puntosAntiguedadLaboral = 100
            else:
                rec.puntosAntiguedadLaboral = 0



    totalPuntosCalificador = fields.Integer(compute='calcular_total_puntos')

    @api.depends('puntosPorcentajeCancelado', 'puntosPorcentajSaldos', 'puntosCuotaIngresos', 'puntosScoreCredito', 'puntosAntiguedadLaboral', 'totalPuntosBienesAdj')
    def calcular_total_puntos(self):
        for rec in self:
            rec.totalPuntosCalificador = rec.puntosPorcentajeCancelado + rec.puntosPorcentajSaldos +  rec.puntosCuotaIngresos + rec.puntosScoreCredito +  rec.puntosAntiguedadLaboral + rec.totalPuntosBienesAdj


    observacionesCalificador = fields.Text(string="Observaciones", default=' ')

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
    plazo_rastreo = fields.Integer(string="Plazo", track_visibility="onchange")
    fecha_inicio_rastreo = fields.Date(string="Fecha Inicio", track_visibility="onchange")
    fecha_vencimiento_rastreo = fields.Date(string="Fecha Vencimiento", track_visibility="onchange")

    seguro = fields.Boolean(string="Seguro",track_visibility="onchange")
    plazo_seguro = fields.Integer(string="Plazo", track_visibility="onchange")
    fecha_inicio_seguro = fields.Date(string="Fecha Inicio", track_visibility="onchange")
    fecha_vencimiento_seguro = fields.Date(string="Fecha Vencimiento", track_visibility="onchange")

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

    def generar_contrato_reserva(self):
        view_id = self.env.ref('gzl_reporte.contrato_reserva_form').id
        return {'type': 'ir.actions.act_window',
                'name': 'Contrato de Reserva',
                'res_model': 'contrato.reserva',
                'target': 'new',
                'view_mode': 'form',
                'views': [[view_id, 'form']],
                'context': {
                    'default_contrato_id': self.contrato_id.id,
                    'default_partner_id':self.nombreSocioAdjudicado.id,
                    'default_entrega_id':self.id,
                }
        }

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
    
    
    @api.depends('totalPuntosCalificador')
    def set_aplica_garante(self):
        for rec in self:
            if rec.totalPuntosCalificador  >= 700:
                rec.aplicaGarante = 'NO'
            else:
                rec.aplicaGarante = 'SI'
    

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
        contrato.estado='adjudicar'



    def rechazo_setear_fecha_adjudicado(self):
        contrato = self.env['contrato'].search(
            [('cliente', '=', self.nombreSocioAdjudicado.id)], limit=1)
        contrato.fecha_adjudicado=False
        contrato.estado='activo'
        contrato.entrega_vehiculo=False

        dct={
        'grupo_id':contrato.grupo.id,
        'haber':self.montoEnviadoAsamblea ,
        'adjudicado_id':contrato.cliente.id,
        'contrato_id':contrato.id,
        'state':contrato.state
        }


        transacciones.create(dct)




    @api.onchange('nombreSocioAdjudicado')
    @api.depends('nombreSocioAdjudicado')
    @api.constrains('nombreSocioAdjudicado')
    def buscar_contrato_partner(self):
        self.llenar_tabla()
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
                rec.edadConyuge = edadGarante
            else:
                rec.edadConyugeGarante = 0
    


    @api.model
    def create(self, vals):
        vals['secuencia'] = self.env['ir.sequence'].next_by_code(
            'entrega.vehiculo')

        return super(EntegaVehiculo, self).create(vals)


 

class ItemPatrimonioEntregaVehiculo(models.Model):
    _name = 'items.patrimonio.entrega.vehiculo'
    _description = 'Items de Patrimonio '

    currency_id = fields.Many2one(
        'res.currency', readonly=True, default=lambda self: self.env.company.currency_id)
    entrega_id = fields.Many2one('entrega.vehiculo')
    patrimonio_id = fields.Many2one('items.patrimonio')
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



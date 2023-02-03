# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
import datetime
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
from dateutil.parser import parse
import calendar
from dateutil.relativedelta import relativedelta
import math

class Contrato(models.Model):
    _name = 'contrato'
    _description = 'Contrato'
    _rec_name = 'secuencia'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    en_mora = fields.Boolean(stirng="Contrato en Mora")

    entrega_vehiculo_id = fields.Many2one('entrega.vehiculo',string="Solicitud de entrega vehículo" ,track_visibility='onchange')

    supervisor = fields.Many2one('res.users',string="Supervisor",track_visibility='onchange' )

    asesor = fields.Many2one('res.partner',string="Asesor")

    cesion_id=fields.Many2one("wizard.cesion.derecho", string="Cesion de Derecho")

    porcentaje_programado = fields.Float(
        string='Porcentaje Programado')
    monto_programado = fields.Monetary(
        string='Saldo Programado ', currency_field='currency_id')

    cuota_pago = fields.Integer(
        string='Cuota de Pago Programado', track_visibility='onchange')
    idEstadoContrato = fields.Char("ID Estado Contrato")
    idTipoContrato = fields.Char("ID Tipo Contrato")
    idContrato = fields.Char("ID de Contrato en base")
    idClienteContrato= fields.Char("ID de Cliente en Cotnrato")
    idGrupo = fields.Char("ID de Grupo en Cotnrato")
    numeroContratoOriginal = fields.Char("Numero de Contrato Original")
    fechaInicioPago = fields.Date("Fecha de inicio de Pago")
    numeroCuotasPagadas = fields.Char("Numero de Contrato Original")

    tipo_documento = fields.Char()
    prefijo = fields.Char()
    secuencia = fields.Char(index=True)
    currency_id = fields.Many2one(
        'res.currency', readonly=True, default=lambda self: self.env.company.currency_id)
    cliente = fields.Many2one(
        'res.partner', string="Cliente", track_visibility='onchange')
    grupo = fields.Many2one(
        'grupo.adjudicado', string="Grupo", track_visibility='onchange')
    dia_corte = fields.Char(string='Día de Corte', default=lambda self: self.capturar_valores_por_defecto_dia())
    saldo_a_favor_de_capital_por_adendum = fields.Monetary(
        string='Saldo a Favor de Capital por Adendum', currency_field='currency_id', track_visibility='onchange')
    pago = fields.Selection(selection=[
        ('mes_actual', 'Mes Actual'),
        ('siguiente_mes', 'Siguiente Mes'),
        ('personalizado', 'Personalizado')
    ], string='Pago', default='personalizado', track_visibility='onchange')
    monto_financiamiento = fields.Monetary(
        string='Monto Financiamiento', currency_field='currency_id', track_visibility='onchange')
    tasa_administrativa = fields.Float(
        string='Tasa Administrativa(%)', track_visibility='onchange',default=lambda self: self.capturar_valores_por_defecto_tasa_administrativa())
    valor_inscripcion = fields.Monetary(
        string='Valor Inscripción', currency_field='currency_id', track_visibility='onchange')
    tipo_de_contrato = fields.Many2one(
        'tipo.contrato.adjudicado', string='Tipo de Contrato', track_visibility='onchange')
    codigo_grupo = fields.Char(compute='setear_codigo_grupo', string='Código de Grupo', track_visibility='onchange')
    provincias = fields.Many2one(
        'res.country.state', string='Provincia', track_visibility='onchange')
    archivo = fields.Binary(string='Archivo')
    fecha_contrato = fields.Date(
        string='Fecha Contrato', track_visibility='onchange')

    plazo_meses = fields.Many2one('numero.meses',default=lambda self: self.env.ref('gzl_adjudicacion.{0}'.format('numero_meses60')).id ,track_visibility='onchange' )

    plazo_meses_numero=fields.Integer("Plazo de Contrato")
    tiene_cuota = fields.Boolean(String='Cuota de Entrada',default=False)
    cuota_adm = fields.Monetary(
        string='Cuota Administrativa',store=True, compute='calcular_valores_contrato', currency_field='currency_id', track_visibility='onchange')
    factura_inscripcion = fields.Many2one(
        'account.move', string='Factura Incripción', track_visibility='onchange')
    active = fields.Boolean(string='Activo', default=True)
    state = fields.Selection(selection=[
        ('ACTIVADO', 'ACTIVADO'),
        ('NO ACTIVADO', 'NO ACTIVADO'),
        ('ADJUDICADO', 'ADJUDICADO'),
        ('FINALIZADO', 'FINALIZADO'),
    ], string='Estado', default='NO ACTIVADO', track_visibility='onchange')


    state_simplificado=fields.Selection(selection=[
        ('DESACTIVADO', 'DESACTIVADO'),
        ('INSCRITO', 'INSCRITO'),
        ('ENTREGADO', 'ENTREGADO'),
        ('NO ENTREGADO', 'NO ENTREGADO'),
        ('ADJUDICADO', 'ADJUDICADO'),
        ('LIQUIDADO', 'LIQUIDADO'),
        ('SINIESTRADO', 'SINIESTRADO'),
        ('DESISTIDO', 'DESISTIDO'),
        ('RESUELTO', 'RESUELTO'),
    ], string='Detalle de estado', default='DESACTIVADO', track_visibility='onchange')

    es_cesion=fields.Boolean(default=False)

# A  Activo        activo    
# C  Congelado     congelar_contrtato
# F  Finalizado    finalizado
# I  Desistido     desistido
# J  Adjudicado    adjudicar
# P  Pendiente     pendiente


    desistido = fields.Boolean(string='Desistido')



    is_group_cobranza = fields.Boolean(string='Es Cobranza',compute="_compute_is_group_cobranza")

    @api.depends("cliente")
    def _compute_is_group_cobranza(self):
        self.is_group_cobranza = self.env['res.users'].has_group('gzl_facturacion_electronica.grupo_cobranza')

    direccion = fields.Char(string='Dirección',
                              track_visibility='onchange')
    descripcion_adjudicaciones = fields.Char(string='Jefe de Zona',
                              track_visibility='onchange')
    nota = fields.Char(string='Cesión de Derecho')

    observacion = fields.Char(string='Observación',
                              track_visibility='onchange')
    ciudad = fields.Many2one(
        'res.country.city', string='Ciudad', domain="[('provincia_id','=',provincias)]", track_visibility='onchange')
    archivo_adicional = fields.Binary(
        string='Archivo Adicional', track_visibility='onchange')
    fecha_inicio_pago = fields.Date(
        string='Fecha Inicio de Pago', compute='calcular_fecha_pago', track_visibility='onchange',store=True)
    cuota_capital = fields.Monetary(
        string='Cuota Capital', currency_field='currency_id', compute='calcular_valores_contrato', track_visibility='onchange',store=True)
    iva_administrativo = fields.Monetary(
        string='Iva Administrativo',  compute='calcular_valores_contrato',currency_field='currency_id', track_visibility='onchange',store=True)
    estado_de_cuenta_ids = fields.One2many(
        'contrato.estado.cuenta', 'contrato_id', track_visibility='onchange')
    fecha_adjudicado = fields.Date(
        string='Fecha Adj.', track_visibility='onchange')
    fecha_entrega = fields.Date(
        string='Fecha Adj.', track_visibility='onchange')

    monto_pagado = fields.Float(
        string='Monto Pagado', compute="calcular_monto_pagado", store=True, track_visibility='onchange')

    tabla_amortizacion = fields.One2many(
        'contrato.estado.cuenta', 'contrato_id', track_visibility='onchange')

    congelar_contrato_ids = fields.One2many(
        'contrato.congelamiento', 'contrato_id', track_visibility='onchange')

    adendums_contrato_ids = fields.One2many(
        'contrato.adendum', 'contrato_id', track_visibility='onchange')


    actualizacion_ids=fields.One2many('actualizacion.contrato.valores','contrato_id',track_visibility='onchange')





    numero_cuotas_pagadas = fields.Integer(
        string='Cuotas Pagadas', compute="calcular_cuotas_pagadas", store=True, track_visibility='onchange')

    aplicaGarante  = fields.Boolean(string='Garante',default = False, track_visibility='onchange')
    
    garante =  fields.Many2one('res.partner', string="Garante", track_visibility='onchange')

    ejecutado = fields.Boolean(string="Ejecutado", default = False)

    @api.depends('grupo')
    def setear_codigo_grupo(self):
        for rec in self:
            if rec.grupo.codigo and rec.grupo.name:
                rec.codigo_grupo = "["+rec.grupo.codigo+"] "+ rec.grupo.name or ' '
            else:
                rec.codigo_grupo =' '

    @api.onchange('tipo_de_contrato')
    @api.constrains('tipo_de_contrato')
    def validar_entrada(self):
        for l in self:
            if l.tipo_de_contrato.code in ['exacto','programo']:
                l.tiene_cuota=True
            else:
                l.tiene_cuota=False

    @api.onchange('porcentaje_programado','monto_financiamiento','plazo_meses','tipo_de_contrato')
    def obtener_monto_programo(self):
        for l in self:
            if l.porcentaje_programado:
                l.monto_programado=l.monto_financiamiento*(l.porcentaje_programado/100)
            if l.tipo_de_contrato.code=='programo' and l.plazo_meses:
                l.cuota_pago=self.plazo_meses.numero
            else:
                l.cuota_pago=0
            




    @api.depends('tabla_amortizacion.saldo')
    def calcular_cuotas_pagadas(self):
        for rec in self:
            cuotas=rec.tabla_amortizacion.filtered(lambda l: l.saldo==0)
            rec.numero_cuotas_pagadas=len(cuotas)

    def actualizar_calcular_cuotas_pagadas(self):
        for rec in self:
            rec.calcular_cuotas_pagadas()




    def capturar_valores_por_defecto_tasa_administrativa(self):
        tasa_administrativa =  float(self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.tasa_administrativa'))

        return tasa_administrativa


    def capturar_valores_por_defecto_dia(self):
        dia_corte =  self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.dia_corte')

        return dia_corte


    @api.depends('pago')
    def calcular_fecha_pago(self):
        for rec in self:
            if rec.dia_corte:
                if rec.pago == 'mes_actual':
                    anio = str(datetime.today().year)
                    mes = str(datetime.today().month)
                    fechaPago =  anio+"-"+mes+"-{0}".format(rec.dia_corte.zfill(2)) 
                    rec.fecha_inicio_pago = parse(fechaPago).date().strftime('%Y-%m-%d')
                elif rec.pago == 'siguiente_mes':
                    fechaMesSeguiente = datetime.today() + relativedelta(months=1)
                    mesSgte=str(fechaMesSeguiente.month)
                    anioSgte=str(fechaMesSeguiente.year)
                    fechaPago = anioSgte+"-"+mesSgte+"-{0}".format(rec.dia_corte.zfill(2)) 
                    rec.fecha_inicio_pago = parse(fechaPago).date().strftime('%Y-%m-%d')
                else:
                    rec.fecha_inicio_pago =False
    
    @api.depends('plazo_meses', 'monto_financiamiento','monto_programado')
    def calcular_valores_contrato(self):
        for rec in self:

            if int(rec.plazo_meses.numero):
                rec.cuota_capital = rec.monto_financiamiento/int(rec.plazo_meses.numero)
                if rec.tiene_cuota:
                    rec.cuota_capital=(rec.monto_financiamiento-rec.monto_programado)/int(rec.plazo_meses.numero)
                cuotaAdministrativa= rec.monto_financiamiento*((rec.tasa_administrativa/100)/12)
                rec.iva_administrativo = cuotaAdministrativa * 0.12
                rec.cuota_adm = cuotaAdministrativa

    def detalle_tabla_amortizacion(self):
        dia_corte =  self.dia_corte
        tasa_administrativa = self.tasa_administrativa

        self.tabla_amortizacion=()

        for rec in self:
            for i in range(0, int(rec.plazo_meses.numero)):
                
                cuota_capital = rec.monto_financiamiento/int(rec.plazo_meses.numero)
                if self.tiene_cuota:
                    cuota_capital=(rec.monto_financiamiento-rec.monto_programado)/int(rec.plazo_meses.numero)
                cuota_adm = rec.monto_financiamiento *tasa_administrativa / 100 / 12
                iva = cuota_adm * 0.12

                cuota_administrativa_neto= cuota_adm + iva
                saldo = cuota_capital+cuota_adm+iva
                cuota_asignada=i+1
                self.env['contrato.estado.cuenta'].create({
                                                    'numero_cuota':i+1,
                                                    'fecha':rec.fecha_inicio_pago + relativedelta(months=i),
                                                    'cuota_capital':cuota_capital,
                                                    'cuota_adm':cuota_adm,
                                                    'iva_adm':iva,
                                                    'saldo':saldo,
                                                    'saldo_cuota_capital':cuota_capital,
                                                    'saldo_cuota_administrativa':cuota_adm,
                                                    'saldo_iva':iva,
                                                    'contrato_id':self.id,
                                                        })
                if rec.cuota_pago and rec.tiene_cuota:
                    if cuota_asignada==rec.cuota_pago:
                        self.env['contrato.estado.cuenta'].create({'numero_cuota':rec.cuota_pago,
                                                                                'contrato_id':self.id,
                                                                                'cuota_capital':0,
                                                                                'cuota_adm':0,
                                                                                'iva_adm':0,
                                                                                'saldo':rec.monto_programado,
                                                                                'saldo_cuota_capital':0,
                                                                                'saldo_cuota_administrativa':0,
                                                                                'saldo_iva':0,
                                                                                'fecha':rec.fecha_inicio_pago + relativedelta(months=i),
                                                                                'saldo_programado':rec.monto_programado,'programado':rec.monto_programado})



        vls=[]                                                
        monto_finan_contrato = sum(self.tabla_amortizacion.mapped('cuota_capital'))
        monto_finan_contrato = round(monto_finan_contrato,2)
        #raise ValidationError(str(monto_finan_contrato))
        monto_financiamiento_contrato=self.monto_financiamiento
        if self.tiene_cuota:
            monto_financiamiento_contrato=self.monto_financiamiento-self.monto_programado
        if  monto_finan_contrato  > monto_financiamiento_contrato:
            valor_sobrante = monto_finan_contrato - monto_financiamiento_contrato 
            valor_sobrante = round(valor_sobrante,2)
            parte_decimal, parte_entera = math.modf(valor_sobrante)
            if parte_decimal==0:
                valor_a_restar=0
            elif parte_decimal >=1:
                valor_a_restar= (valor_sobrante/parte_decimal)*0.1
            else:
                valor_a_restar= (valor_sobrante/parte_decimal)*0.01

            obj_contrato=self.env['contrato.estado.cuenta'].search([('contrato_id','=',self.id),('estado_pago','=','pendiente')] , order ='fecha desc')
            for c in obj_contrato:
                if valor_sobrante != 0.00 or valor_sobrante != 0 or valor_sobrante != 0.0:
                    if c.programado == 0.00 or c.programado == 0 or c.programado == 0.0:
                        c.update({
                            'cuota_capital': c.cuota_capital - valor_a_restar,
                            'contrato_id':self.id,
                            'saldo_cuota_capital': c.cuota_capital - valor_a_restar,
                        })
                        vls.append(valor_sobrante)
                        valor_sobrante = valor_sobrante -valor_a_restar
                        valor_sobrante = round(valor_sobrante,2)
                            
                            
        if  monto_finan_contrato  < monto_financiamiento_contrato:
            valor_sobrante = monto_financiamiento_contrato  - monto_finan_contrato 
            valor_sobrante = round(valor_sobrante,2)
            parte_decimal, parte_entera = math.modf(valor_sobrante)
            if parte_decimal==0:
                valor_a_restar=0
            elif parte_decimal >=1:
                valor_a_restar= (valor_sobrante/parte_decimal)*0.1
            else:
                valor_a_restar= (valor_sobrante/parte_decimal)*0.01

            obj_contrato=self.env['contrato.estado.cuenta'].search([('contrato_id','=',self.id),('estado_pago','=','pendiente')] , order ='fecha desc')

            for c in obj_contrato:

                if valor_sobrante != 0.00 or valor_sobrante != 0 or valor_sobrante != 0.0:
                    if c.programado == 0.00 or c.programado == 0 or c.programado == 0.0:
                    #raise ValidationError(str(valor_sobrante)+'--'+str(parte_decimal)+'----'+str(valor_a_restar))
                        c.update({
                            'cuota_capital': c.cuota_capital + valor_a_restar,
                            'saldo_cuota_capital': c.cuota_capital + valor_a_restar,
                            'contrato_id':self.id,
                        })  
                        vls.append(valor_sobrante)
                        valor_sobrante = valor_sobrante -valor_a_restar
                        valor_sobrante = round(valor_sobrante,2)
        #raise ValidationError(str(vls)+'--')
    @api.depends("estado_de_cuenta_ids.monto_pagado")
    def calcular_monto_pagado(self,):
        for l in self:
            monto=round(sum(l.estado_de_cuenta_ids.mapped("monto_pagado"),2))
            l.monto_pagado=monto




    @api.model
    def create(self, vals):
        ####Comentar luego de la Migración
        #vals['secuencia']=vals["tipo_documento"]+vals["prefijo"].zfill(3)+vals['secuencia'].zfill(8)
        #return super(Contrato, self).create(vals)


        ####Desomentar luego de la Migración
        grupo=self.env['grupo.adjudicado'].browse(vals['grupo'])
        obj_secuencia= grupo.secuencia_id

        if not vals.get('es_cesion'):
            vals['secuencia'] = obj_secuencia.next_by_code(obj_secuencia.code)
        dia_corte =  self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.dia_corte')
        tasa_administrativa =  self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.tasa_administrativa')

        vals['tasa_administrativa'] = float(tasa_administrativa)
        vals['dia_corte'] = dia_corte
        return super(Contrato, self).create(vals)
        #self.validar_cliente_en_otro_contrato()


    @api.onchange('cliente')
    def onchange_provincia(self):
        self.env.cr.execute("""select id from res_country_state where country_id={0}""".format(
            self.env.ref('base.ec').id))
        res = self.env.cr.dictfetchall()
        if res:
            list_res = []
            for l in res:
                list_res.append(l['id'])
            return {'domain': {'provincias': [('id', 'in', list_res)]}}



    def cambio_estado_boton_borrador(self):
        self.detalle_tabla_amortizacion()
        self.write({"state": "NO ACTIVADO","state_simplificado":"INSCRITO"})

    def cambio_estado_boton_inactivar(self):
        return self.write({"state": "NO ACTIVADO"})

    def finalizar_contrato(self):
        return self.write({"state": "FINALIZADO","state_simplificado":"LIQUIDADO"})

    def cambio_estado_boton_adjudicar(self):
        return self.write({"state": "ADJUDICADO"})


    def cambio_estado_boton_adendum(self):
        return self.write({"state": "adendum"})

    def cambio_estado_boton_desistir(self):
        return self.write({"state": "FINALIZADO","state_simplificado":"DESISTIDO"})







    def validar_cliente_en_otro_contrato(self, ):
        if self.cliente.id:
            contratos=self.env['contrato'].search([('cliente','=',self.cliente.id)])
            if len(contratos)>0:
                raise ValidationError("El cliente {0} ya está asignado en el contrato {1}".format(self.cliente.name,contratos.secuencia))



    # @api.constrains("grupo")
    # def validar_cliente_en_grupo(self, ):
    #     contratos=self.env["contrato"].search([])
    #     for l in contratos:
    #         if l.grupo.id:
    #             obj_cliente_integrante=self.env['integrante.grupo.adjudicado'].search([('adjudicado_id','=',l.cliente.id)])
    #             obj_cliente_integrante.unlink()
    #             dctCliente={
    #             "grupo_id":l.grupo.id,
    #             "adjudicado_id":l.cliente.id
    #             }
    #             obj_cliente_integrante=self.env['integrante.grupo.adjudicado'].create(dctCliente)
    #             obj_cliente_integrante.agregar_contrato()


####Job que coloca la bandera estado en mora de los contratos se ejecuta cada minuto
    def job_colocar_contratos_en_mora(self, ):

        hoy=date.today()
        contratos=self.env['contrato'].search([])

        for contrato in contratos:
            mes_estado_cuenta=contrato.tabla_amortizacion.filtered(lambda l: l.estado_pago=="pendiente" and l.fecha<hoy)
            if mes_estado_cuenta:
                contrato.en_mora=True
            else:
                contrato.en_mora=False
            mes_estado_cuenta=contrato.tabla_amortizacion.filtered(lambda l: l.fecha.year == hoy.year and l.fecha.month == hoy.month and l.estado_pago=="pendiente")
            for mes in mes_estado_cuenta:
                elif hoy.day>mes.fecha.day:
                    if mes.saldo<=10.00:
                        contrato.en_mora=False
                    else:
                        contrato.en_mora=True
                else:
                    contrato.en_mora=False

###  Job para inactivar acorde a cuotas vencidas en el contrato

    def job_para_inactivar_contrato(self, ):

        hoy=date.today()
        dateMonthStart="%s-%s-%s" %(hoy.year, hoy.month,(calendar.monthrange(hoy.year, hoy.month)[1]))

        dateMonthStart=datetime.strptime(dateMonthStart, '%Y-%m-%d').date()

        numeroCuotasMaximo =  int(self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.maximo_cuotas_vencidas'))

        contratos=self.env['contrato'].search([('state','in',['ACTIVADO'])])

        for contrato in contratos:
                 
            lineas_pendientes=contrato.tabla_amortizacion.filtered(lambda l: l.fecha<dateMonthStart and l.estado_pago=='pendiente')
            if len(lineas_pendientes)>=numeroCuotasMaximo:
                contrato.state='NO ACTIVADO'


###  Job para inactivar acorde a cuotas vencidas en el contrato

    def job_para_inactivar_contratos_congelados(self, ):

        hoy=date.today()
        dateMonthStart="%s-%s-%s" %(hoy.year, hoy.month,(calendar.monthrange(hoy.year, hoy.month)[1]))

        dateMonthStart=datetime.strptime(dateMonthStart, '%Y-%m-%d').date()

        numeroCuotasMaximo =  int(self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.maximo_cuotas_congeladas'))

        contratos=self.env['contrato'].search([('state','in',['congelar_contrato'])])

        for contrato in contratos:
                 
            lineas_pendientes=contrato.tabla_amortizacion.filtered(lambda l: l.fecha<dateMonthStart and l.estado_pago=='pendiente')
            if len(lineas_pendientes)>=numeroCuotasMaximo:
                contrato.state='NO ACTIVADO'


    def job_enviar_correos_contratos_congelados_por_vencer(self, ):

        hoy=date.today()
        dateMonthStart="%s-%s-%s" %(hoy.year, hoy.month,(calendar.monthrange(hoy.year, hoy.month)[1]))

        dateMonthStart=datetime.strptime(dateMonthStart, '%Y-%m-%d').date()

        contratos=self.env['contrato'].search([('state','in',['congelar_contrato'])])
        for contrato in contratos:
            congelamiento=self.env['contrato.congelamiento'].search([('contrato_id','=',contrato.id)])
            if congelamiento:
                diferencia=((dateMonthStart-congelamiento.fecha).total_seconds())/86400
                if difernecia>=60:
                    self.envio_correos_plantilla('email_contrato_notificacion_de_congelamiento',contrato.id)

#Job para registrar calificacion de contratos en mora de acuerdo al job job_colocar_contratos_en_mora se ejecuta el 6 de cada mes

    def job_registrar_calificacion_contratos_en_mora(self, ):

        hoy=date.today()
        contratos=self.env['contrato'].search([('en_mora','=',True)])

        for contrato in contratos:
            obj_calificador=self.env['calificador.cliente']
            motivo=self.env.ref('gzl_adjudicacion.calificacion_2')
            obj_calificador.create({'partner_id': contrato.cliente.id,'motivo':motivo.motivo,'calificacion':motivo.calificacion})


        contratos=self.env['contrato'].search([('en_mora','=',False)])

        for contrato in contratos:

            obj_calificador=self.env['calificador.cliente']
            motivo=self.env.ref('gzl_adjudicacion.calificacion_1')
            obj_calificador.create({'partner_id': contrato.cliente.id,'motivo':motivo.motivo,'calificacion':motivo.calificacion})



###Job que envia correos segun bandera en mora

    def job_enviar_correos_contratos_en_mora(self, ):
        contratos=self.env['contrato'].search([('en_mora','=',True)])
        for contrato in contratos:  
            self.envio_correos_plantilla('email_contrato_en_mora',contrato.id)

####Job para enviar correo contrato pago por vencer

    def job_enviar_correos_contratos_pago_por_vencer(self, ):

        hoy=date.today()
        contratos=self.env['contrato'].search([('state','in',['adjudicado','ACTIVADO'])])

        for contrato in contratos:
            mes_estado_cuenta=contrato.tabla_amortizacion.filtered(lambda l: l.fecha.year == hoy.year and l.fecha.month == hoy.month)
            if len(mes_estado_cuenta)>0:
                self.envio_correos_plantilla('email_contrato_notificacion_de_pago',contrato.id)

###Job migración
    def job_contratos_migrados(self):
        contratos_ids=self.env["contrato"].search([])
        for l in contratos_ids:
            if l.idTipoContrato=="E":
                l.tipo_de_contrato = 2
            if l.idTipoContrato=="PA":
                l.tipo_de_contrato = 1
            if l.idTipoContrato=="PP":
                l.tipo_de_contrato = 4
            if l.idTipoContrato=="P":
                l.tipo_de_contrato = 5
            grupo_id=self.env["grupo.adjudicado"].search([("idGrupo","=",l.idGrupo)])
            if grupo_id:
                l.grupo=grupo_id.id
            cliente_id=self.env["res.partner"].search([("codigo_cliente","=",l.idClienteContrato)])
            if cliente_id:
                l.cliente=cliente_id.id
            if l.idEstadoContrato=="A":
                l.state="ACTIVADO"
                l.state_simplificado=False
            if l.idEstadoContrato=="F":
                l.state="FINALIZADO"
                l.state_simplificado="LIQUIDADO" 
            if l.idEstadoContrato=="I":
                l.state="FINALIZADO"
                l.state_simplificado="DESISTIDO"
            if l.idEstadoContrato=="J":
                l.state="ADJUDICADO"
                l.state_simplificado="ENTREGADO"
            if l.idEstadoContrato=="P":
                l.state="NO ACTIVADO"
                l.state_simplificado="DESACTIVADO"

    def cambio_estado_congelar_contrato(self):
        #Cambio de estado
        congelamientos_ids=self.env['contrato.congelamiento'].search([('contrato_id','=',self.id)])
        if congelamientos_ids:
            raise ValidationError("Solo puede aplicar Congelamiento una vez al contrato.")
        
        #Se obtiene el listado de cuotas pendientes ordenadas de forma ascedente en la fecha de pago.
        tabla=self.env['contrato.estado.cuenta'].search([('estado_pago','=','pendiente'),('contrato_id','=',self.id)],order='fecha asc')

        if len(tabla)>0:
            dct={'contrato_id':self.id,'fecha':tabla[0].fecha}
            self.env['contrato.congelamiento'].create(dct)
        else:
            raise ValidationError("No se puede congelar un contrato que no posee Estado de Cuenta generado")
        self.state='NO ACTIVADO'
        self.state_simplificado="DESACTIVADO"


    def reactivar_contrato_congelado(self):
        obj_fecha_congelamiento=self.env['contrato.congelamiento'].search([('contrato_id','=',self.id),('pendiente','=',True)],limit=1)


        if obj_fecha_congelamiento:
            hoy=date.today()

            fecha_reactivacion="%s-%s-%s" % (hoy.year, hoy.month,(calendar.monthrange(hoy.year, hoy.month)[1]))
            fecha_reactivacion = datetime.strptime(fecha_reactivacion, '%Y-%m-%d').date()

            detalle_estado_cuenta_pendiente=self.tabla_amortizacion.filtered(lambda l:  l.fecha>=obj_fecha_congelamiento.fecha  and l.fecha<fecha_reactivacion)

            i=0
            for detalle in detalle_estado_cuenta_pendiente:
                i+=1
            tabla=self.env['contrato.estado.cuenta'].search([('contrato_id','=',self.id)],order='fecha asc')

            self.fecha_inicio_pago+=relativedelta(months=i)            
            for detalle in tabla:
                detalle.fecha+=relativedelta(months=i)

            obj_fecha_congelamiento.pendiente=False
            self.state='ACTIVADO'
            self.state_simplificado=False

        else:
            raise ValidationError("No se encontró un contrato congelado.")

    def envio_correos_plantilla(self, plantilla,id_envio):

        try:
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('gzl_adjudicacion', plantilla)[1]
        except ValueError:
            template_id = False
#Si existe capturo el template
        if template_id:
            obj_template=self.env['mail.template'].browse(template_id)

            email_id=obj_template.send_mail(id_envio)



    def pagar_cuotas_por_adelantado(self):
        view_id = self.env.ref('gzl_adjudicacion.wizard_adelantar_cuotas_form').id


        return {'type': 'ir.actions.act_window',
                'name': 'Adelantar Pago',
                'res_model': 'wizard.adelantar.cuotas',
                'target': 'new',
                'view_mode': 'form',
                'views': [[view_id, 'form']],
                'context': {
                    'default_contrato_id': self.id,
                }
        }


    def obtener_contrato(self):
        for l in self:
            contrato_documento=self.env['sign.request.item'].search([('partner_id','=',l.cliente.id)], limit=1)
            if contrato_documento:
                contrato_documento.ensure_one()
                return {
                'name': 'Signed Document',
                'type': 'ir.actions.act_url',
                'url': '/sign/document/%(request_id)s/%(access_token)s' % {'request_id': contrato_documento.sign_request_id.id, 'access_token': contrato_documento.access_token},
                }

    def actualizar_rubros_por_adelantado(self):
        view_id = self.env.ref('gzl_adjudicacion.wizard_actualizar_rubro_form').id


        return {'type': 'ir.actions.act_window',
                'name': 'Actualizar Rubro',
                'res_model': 'wizard.actualizar.rubro',
                'target': 'new',
                'view_mode': 'form',
                'views': [[view_id, 'form']],
                'context': {
                    'default_contrato_id': self.id,
                }
        }


    def modificar_tabla_contrato(self):
        #if len(self.actualizacion_ids)>1:
            #raise ValidationError("El contrato ya sufrio modificacion con anterioridad")
        view_id = self.env.ref('gzl_adjudicacion.wizard_crear_valores_form').id


        return {'type': 'ir.actions.act_window',
                'name': 'Modificar contrato',
                'res_model': 'actualizacion.contrato.valores',
                'target': 'new',
                'view_mode': 'form',
                'views': [[view_id, 'form']],
                'context': {
                    'default_contrato_id': self.id,
                    'default_socio_id': self.cliente.id,
                    'default_monto_financiamiento': self.monto_financiamiento,
                    'default_monto_financiamiento_anterior': self.monto_financiamiento,
                }
        }




    def enviar_correos_contrato(self,):

        obj_rol=self.env['adjudicaciones.team'].search([('active','=',True),('correos','!=',False)]).mapped('correos')
        correos=''
        for correo in obj_rol:
            correos=correos+correo+','

        return correos


#CRUD METHODS

    def write(self, vals):

        crm = super(Contrato, self).write(vals)
        return crm

class ContratoCongelamiento(models.Model):
    _name = 'contrato.congelamiento'
    _description = 'Bitacora de Congelamiento'

    contrato_id = fields.Many2one('contrato')
    fecha = fields.Date(String='Fecha Congelamiento')
    pendiente = fields.Boolean(String='Pendiente de Activación',default=True)


class ContratoEstadoCuenta(models.Model):
    _name = 'contrato.estado.cuenta'
    _description = 'Contrato - Tabla de estado de cuenta de Aporte'
    _rec_name = 'numero_cuota'

    idContrato = fields.Char("ID de Contrato en base")

    contrato_id = fields.Many2one('contrato')
    numero_cuota = fields.Char(String='Número de Cuota')
    fecha = fields.Date(String='Fecha Pago')
    fecha_pagada = fields.Date(String='Fecha Pagada')
    currency_id = fields.Many2one(
        'res.currency', readonly=True, default=lambda self: self.env.company.currency_id)


    cuota_capital = fields.Monetary(
        string='Cuota Capital', currency_field='currency_id')
    cuota_adm = fields.Monetary(
        string='Cuota Adm', currency_field='currency_id')

    iva_adm = fields.Monetary(
        string='Iva Adm', currency_field='currency_id')

    factura_id = fields.Many2one('account.move', string='Factura')
    # pago_ids = fields.Many2many('account.payment','contrato_estado_cuenta_payment_rel', 'estado_cuenta_id','payment_id', string='Pagos')
    seguro = fields.Monetary(string='Seguro', currency_field='currency_id')
    rastreo = fields.Monetary(string='Rastreo', currency_field='currency_id')
    otro = fields.Monetary(string='Otro', currency_field='currency_id')
    monto_pagado = fields.Monetary(
        string='Monto Pagado', currency_field='currency_id',compute="calcular_monto_pagado",store=True)
    saldo = fields.Monetary(string='Saldo', currency_field='currency_id' ,compute="calcular_monto_pagado",store=True)
    certificado = fields.Binary(string='Certificado')
    cuotaAdelantada = fields.Boolean(string='Cuota Adelantada')
    estado_pago = fields.Selection([('pendiente', 'Pendiente'),
                                    ('pagado', 'Pagado'),
                                    ('congelado', 'Congelado'),
                                    ('varias', 'Varias(Cesión)')
                                    ], string='Estado de Pago', default='pendiente')

    programado=fields.Monetary(string="Cuota Programada", currency_field='currency_id')
    pago_ids = fields.One2many(
        'account.payment', 'pago_id', track_visibility='onchange')
    
    saldo_kimera = fields.Monetary(
        string='Saldo Kimera', currency_field='currency_id')

    fondo_reserva = fields.Monetary(
        string='Fondo Reserva', currency_field='currency_id')

    iva = fields.Monetary(
        string='Iva ', currency_field='currency_id')
    
    referencia = fields.Char(String='Referencia')

    saldo_cuota_capital = fields.Monetary(
        string='Saldo cuota capital', currency_field='currency_id')
    saldo_cuota_administrativa = fields.Monetary(
        string='Saldo cuota adm ', currency_field='currency_id')
    saldo_fondo_reserva = fields.Monetary(
        string='Saldo fondo de reserva ', currency_field='currency_id')
    
    saldo_iva = fields.Monetary(
        string='Saldo Iva ', currency_field='currency_id')
    
    saldo_programado = fields.Monetary(
        string='Saldo Programado ', currency_field='currency_id')
    
    saldo_seguro = fields.Monetary(
        string='Saldo Seguro ', currency_field='currency_id')
    
    saldo_rastreo = fields.Monetary(
        string='Saldo rastreo ', currency_field='currency_id')
    
    saldo_otros = fields.Monetary(
        string='Saldo Otros ', currency_field='currency_id')
    
    saldo_tabla = fields.Monetary(
        string='Saldo Tabla ', currency_field='currency_id')

    @api.depends("saldo_seguro","saldo_rastreo","saldo_otros","saldo_cuota_capital","saldo_cuota_administrativa","saldo_iva")
    def calcular_monto_pagado(self):
        for l in self:
            monto=sum(l.ids_pagos.mapped("valor_asociado"))
            l.monto_pagado=monto
            l.saldo=l.cuota_capital+l.cuota_adm+l.iva_adm + l.seguro+ l.rastreo + l.otro + l.programado - l.monto_pagado

    


    def actualizar_rubros_detalle(self):
        estado_cuenta_ids=self.env["contrato.estado.cuenta"].search([])
        for x in estado_cuenta_ids:
            cuota_actual=0
            saldos=0
            if x['cuota_capital']:
                cuota_actual+=x['cuota_capital']
            if x['cuota_adm']:
                cuota_actual+=x["cuota_adm"]
            if x['iva_adm']:
                cuota_actual+=x["iva_adm"]
            if x['fondo_reserva']:
                cuota_actual+=x["fondo_reserva"]
            if x['programado']:
                cuota_actual+=x["programado"]
            if x['seguro']:
                cuota_actual+=x["seguro"]
            if x['rastreo']:
                cuota_actual+=x["rastreo"]
            if x['otro']:
                cuota_actual+=x["otro"]
            if x["fecha_pagada"]:
                x["estado_pago"]="pagado"
                x["saldo_cuota_capital"]=0
                x["saldo_cuota_administrativa"]=0
                x["saldo_iva"]=0
                x["saldo_fondo_reserva"]=0
                x["programado"]=0
                x["saldo_programado"]=0
                x["saldo_seguro"]=0
                x["saldo_rastreo"]=0
                x["saldo_otros"]=0
                id_registro=self.env["account.payment.cuotas"].create({"cuotas_id":x["id"],
                                                                        "monto_pagado":cuota_actual,
                                                                        "valor_asociado":cuota_actual})





    #####Comentar función luego de la migración
    def job_actualizar_valores(self):
        estado_cuenta_ids=self.env["contrato.estado.cuenta"].search([("estado_pago","!=","pagado")])
        for x in estado_cuenta_ids:
            if x['monto_pagado']:
                pagos_ids=self.env["account.payment.cuotas"].search([('cuotas_id','=',x['id'])])  
                if pagos_ids:
                    pass
                else:
                    id_registro=self.env["account.payment.cuotas"].create({"cuotas_id":x["id"],
                                                                        "monto_pagado":x["monto_pagado"],
                                                                        "valor_asociado":x["monto_pagado"]})
            




class PagoContratoEstadoCuenta(models.Model):
    _inherit = 'account.payment'

    pago_id = fields.Many2one('contrato.estado.cuenta', string="Detalle Estado de Cuenta")
    
    actividad_id = fields.Many2one('mail.activity',string="Actividades")


    
class ContratoAdendum(models.Model):
    _name = 'contrato.adendum'
    _description = 'Contrato Adendum'


    contrato_id = fields.Many2one('contrato',string="Contrato")
    socio_id = fields.Many2one('res.partner',string="Socio")
    observacion = fields.Char(string='Observacion')
    monto_financiamiento = fields.Monetary(
        string='Monto Financiamiento', currency_field='currency_id', track_visibility='onchange')
    plazo_meses = fields.Many2one('numero.meses',default=lambda self: self.env.ref('gzl_adjudicacion.{0}'.format('numero_meses60')).id ,track_visibility='onchange' )

    currency_id = fields.Many2one(
        'res.currency', readonly=True, default=lambda self: self.env.company.currency_id)



class ContratoHistorio(models.Model):
    _name = 'contrato.estado.cuenta.historico.cabecera'
    _description = 'Contrato Historico Tabla de estado de cuenta de Aporte'

    currency_id = fields.Many2one(
        'res.currency', readonly=True, default=lambda self: self.env.company.currency_id)
    contrato_id = fields.Many2one('contrato')
    tabla_amortizacion = fields.One2many(
        'contrato.estado.cuenta.historico.detalle', 'contrato_id', track_visibility='onchange')
    motivo_adendum = fields.Char(String='Motivo Adendum')
    cuota_capital = fields.Monetary(
        string='Cuota Capital', currency_field='currency_id')
    monto_financiamiento = fields.Monetary(
        string='Monto Financiamiento', currency_field='currency_id')
    plazo_meses = fields.Many2one('numero.meses',default=lambda self: self.env.ref('gzl_adjudicacion.{0}'.format('numero_meses60')).id ,track_visibility='onchange' )

    cuota_capital_anterior = fields.Monetary(
        string='Cuota Capital', currency_field='currency_id')
    monto_financiamiento_anterior = fields.Monetary(
        string='Monto Financiamiento', currency_field='currency_id')
    plazo_meses_anterior = fields.Many2one('numero.meses',default=lambda self: self.env.ref('gzl_adjudicacion.{0}'.format('numero_meses60')).id ,track_visibility='onchange' )    
    
class ContratoEstadoCuentaHsitorico(models.Model):
    _name = 'contrato.estado.cuenta.historico.detalle'
    _description = 'Contrato Historico Tabla de estado de cuenta de Aporte'

    contrato_id = fields.Many2one('contrato.estado.cuenta.historico.cabecera')
    numero_cuota = fields.Char(String='Número de Cuota')
    fecha = fields.Date(String='Fecha Pago')
    fecha_pagada = fields.Date(String='Fecha Pagada')
    currency_id = fields.Many2one(
        'res.currency', readonly=True, default=lambda self: self.env.company.currency_id)
    cuota_capital = fields.Monetary(
        string='Cuota Capital', currency_field='currency_id')
    cuota_adm = fields.Monetary(
        string='Cuota Adm', currency_field='currency_id')

    iva_adm = fields.Monetary(
        string='Iva Adm', currency_field='currency_id')

    factura_id = fields.Many2one('account.move', string='Factura')
    # pago_ids = fields.Many2many('account.payment','contrato_estado_cuenta_payment_rel', 'estado_cuenta_id','payment_id', string='Pagos')
    seguro = fields.Monetary(string='Seguro', currency_field='currency_id')
    rastreo = fields.Monetary(string='Rastreo', currency_field='currency_id')
    otro = fields.Monetary(string='Otro', currency_field='currency_id')
    monto_pagado = fields.Monetary(
        string='Monto Pagado', currency_field='currency_id',compute="calcular_monto_pagado",store=True)
    saldo = fields.Monetary(string='Saldo', currency_field='currency_id' ,compute="calcular_monto_pagado",store=True)
    certificado = fields.Binary(string='Certificado')
    cuotaAdelantada = fields.Boolean(string='Cuota Adelantada')
    estado_pago = fields.Selection([('pendiente', 'Pendiente'),
                                    ('pagado', 'Pagado'),
                                    ('congelado', 'Congelado'),
                                    ('varias', 'Varias(Cesión)')
                                    ], string='Estado de Pago', default='pendiente')

    pago_ids = fields.One2many(
        'account.payment', 'pago_id', track_visibility='onchange')
    


# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
import datetime
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
from dateutil.parser import parse
import calendar
from dateutil.relativedelta import relativedelta


class Contrato(models.Model):
    _name = 'contrato'
    _description = 'Contrato'
    _rec_name = 'secuencia'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    en_mora = fields.Boolean(stirng="Contrato en Mora")

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
    ], string='Pago', default='mes_actual', track_visibility='onchange')
    monto_financiamiento = fields.Monetary(
        string='Monto Financiamiento', currency_field='currency_id', track_visibility='onchange')
    tasa_administrativa = fields.Float(
        string='Tasa Administrativa(%)', track_visibility='onchange',default=lambda self: self.capturar_valores_por_defecto_tasa_administrativa())
    valor_inscripcion = fields.Monetary(
        string='Valor Inscripción', currency_field='currency_id', track_visibility='onchange')
    tipo_de_contrato = fields.Many2one(
        'tipo.contrato.adjudicado', string='Tipo de Contrato', track_visibility='onchange')
    codigo_grupo = fields.Char(
        string='Código de Grupo', track_visibility='onchange')
    provincias = fields.Many2one(
        'res.country.state', string='Provincia', track_visibility='onchange')
    archivo = fields.Binary(string='Archivo')
    fecha_contrato = fields.Date(
        string='Fecha Contrato', track_visibility='onchange')

    plazo_meses = fields.Many2one('numero.meses',default=lambda self: self.env.ref('gzl_adjudicacion.{0}'.format('numero_meses60')).id ,track_visibility='onchange' )


    cuota_adm = fields.Monetary(
        string='Cuota Administrativa',store=True, compute='calcular_valores_contrato', currency_field='currency_id', track_visibility='onchange')
    factura_inscripcion = fields.Many2one(
        'account.move', string='Factura Incripción', track_visibility='onchange')
    active = fields.Boolean(string='Activo', default=True)
    state = fields.Selection(selection=[
        ('borrador', 'Borrador'),
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('congelar_contrato', 'Congelar Contrato'),
        ('adjudicar', 'Adjudicado'),
        ('adendum', 'Realizar Adendum'),
        ('cerrado', 'Cerrado'),
        ('desistir', 'Desistir'),
    ], string='Estado', default='borrador', track_visibility='onchange')
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

    monto_pagado = fields.Float(
        string='Monto Pagado', compute="calcular_monto_pagado", store=True, track_visibility='onchange')

    tabla_amortizacion = fields.One2many(
        'contrato.estado.cuenta', 'contrato_id', track_visibility='onchange')

    congelar_contrato_ids = fields.One2many(
        'contrato.congelamiento', 'contrato_id', track_visibility='onchange')



    numero_cuotas_pagadas = fields.Integer(
        string='Cuotas Pagadas', compute="calcular_cuotas_pagadas", store=True, track_visibility='onchange')



    @api.constrains('state')
    def crear_registro_fondo_grupo(self):
        if self.grupo and self.state!='borrador':
            self.grupo.calcular_monto_pagado()

            if self.state in ['desistir','inactivo','congelar_contrato']:
                transacciones=self.env['transaccion.grupo.adjudicado']

                dct={
                'grupo_id':self.grupo.id,
                'debe':self.monto_pagado ,
                'adjudicado_id':self.cliente.id,
                'contrato_id':self.id,
                'state':self.state
                }


                transacciones.create(dct)

            if self.state in ['activo']:
                transacciones=self.env['transaccion.grupo.adjudicado']

                dct={
                'grupo_id':self.grupo.id,
                'haber':self.monto_pagado ,
                'adjudicado_id':self.cliente.id,
                'contrato_id':self.id,
                'state':self.state
                }


                transacciones.create(dct)





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
    
    @api.depends('plazo_meses', 'monto_financiamiento')
    def calcular_valores_contrato(self):
        for rec in self:

            if int(rec.plazo_meses.numero):
                rec.cuota_capital = rec.monto_financiamiento/int(rec.plazo_meses.numero)
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
                cuota_adm = rec.monto_financiamiento *tasa_administrativa / 100 / 12
                iva = cuota_adm * 0.12

                cuota_administrativa_neto= cuota_adm + iva
                saldo = cuota_capital+cuota_adm+iva
                self.env['contrato.estado.cuenta'].create({
                                                    'numero_cuota':i+1,
                                                    'fecha':rec.fecha_inicio_pago + relativedelta(months=i),
                                                    'cuota_capital':cuota_capital,
                                                    'cuota_adm':cuota_adm,
                                                    'iva_adm':iva,
                                                    'saldo':saldo,
                                                    'contrato_id':self.id,                                                    
                                                        })
                                                        

    @api.depends("estado_de_cuenta_ids.monto_pagado")
    def calcular_monto_pagado(self,):
        for l in self:
            monto=round(sum(l.estado_de_cuenta_ids.mapped("monto_pagado"),2))
            l.monto_pagado=monto




    @api.model
    def create(self, vals):
        vals['secuencia'] = self.env['ir.sequence'].next_by_code('contrato')
        dia_corte =  self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.dia_corte')
        tasa_administrativa =  self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.tasa_administrativa')

        vals['tasa_administrativa'] = float(tasa_administrativa)
        vals['dia_corte'] = dia_corte

        self.validar_cliente_en_otro_contrato()


        return super(Contrato, self).create(vals)

    @api.onchange('cliente', 'grupo')
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
        self.write({"state": "activo"})



    def cambio_estado_boton_adendum(self):
        return self.write({"state": "adendum"})

    def cambio_estado_boton_adjudicar(self):
        return self.write({"state": "adjudicar"})


    def cambio_estado_boton_desistir(self):
        return self.write({"state": "desistir"})




    def validar_cliente_en_otro_contrato(self, ):
        if self.cliente.id:
            contratos=self.env['contrato'].search([('cliente','=',self.cliente.id)])
            if len(contratos)>0:
                raise ValidationError("El cliente {0} ya está asignado en el contrato {1}".format(self.cliente.name,contratos.secuencia))



    @api.constrains("grupo")
    def validar_cliente_en_grupo(self, ):
        if self.grupo.id:
            obj_cliente_integrante=self.env['integrante.grupo.adjudicado'].search([('adjudicado_id','=',self.cliente.id)])
            obj_cliente_integrante.unlink()

            dctCliente={
            "grupo_id":self.grupo.id,
            "adjudicado_id":self.cliente.id

            }

            obj_cliente_integrante=self.env['integrante.grupo.adjudicado'].create(dctCliente)
            obj_cliente_integrante.agregar_contrato()



    def job_colocar_contratos_en_mora(self, ):

        hoy=date.today()
        contratos=self.env['contrato'].search([('state','in',['adjudicado','activo'])])

        for contrato in contratos:
            mes_estado_cuenta=contrato.tabla_amortizacion.filtered(lambda l: l.fecha.year == hoy.year and l.fecha.month == hoy.month)
            if len(mes_estado_cuenta)>0:
                if not mes_estado_cuenta=='pagado':
                    contrato.en_mora=True
                else:
                    contrato.en_mora=False


    def job_registrar_calificacion_contratos_en_mora(self, ):

        hoy=date.today()
        contratos=self.env['contrato'].search([('en_mora','=',True)])

        for contrato in contratos:
            obj_calificador=self.env['calificador.cliente']
            motivo=self.env.ref('gzl_adjudicacion.calificacion_2')
            obj_calificador.create({'partner_id': contrato.cliente.id,'motivo':motivo.motivo,'calificacion':motivo.calificacion})


        contratos=self.env['contrato'].search([('state','in',['adjudicado','activo'])])

        for contrato in contratos:
            mes_estado_cuenta=contrato.tabla_amortizacion.filtered(lambda l: l.fecha.year == hoy.year and l.fecha.month == hoy.month)
            if len(mes_estado_cuenta)>0:
                if  mes_estado_cuenta=='pagado':
                    obj_calificador=self.env['calificador.cliente']
                    motivo=self.env.ref('gzl_adjudicacion.calificacion_1')
                    obj_calificador.create({'partner_id': contrato.cliente.id,'motivo':motivo.motivo,'calificacion':motivo.calificacion})




    def job_enviar_correos_contratos_en_mora(self, ):

        hoy=date.today()
        contratos=self.env['contrato'].search([('en_mora','=',True)])

        for contrato in contratos:
                 
            self.envio_correos_plantilla('email_contrato_en_mora',contrato.id)






    def job_para_inactivar_contrato(self, ):

        hoy=date.today()
        dateMonthStart="%s-%s-01" % (hoy.year, hoy.mes)
        dateMonthStart=datetime.strptime(dateMonthStart, '%Y-%m-%d') 


        contratos=self.env['contrato'].search([('state','in',['activo'])])

        for contrato in contratos:
                 
            lineas_pendientes=contrato.tabla_amortizacion.filtered(lambda l: l.fecha<dateMonthStart and estado_pago=='pendiente')
            if len(lineas_pendientes)>=3:
                contrato.state='inactivo'










    def job_enviar_correos_contratos_pago_por_vencer(self, ):

        hoy=date.today()
        contratos=self.env['contrato'].search([('state','in',['adjudicado','activo'])])

        for contrato in contratos:
            mes_estado_cuenta=contrato.tabla_amortizacion.filtered(lambda l: l.fecha.year == hoy.year and l.fecha.month == hoy.month)
            if len(mes_estado_cuenta)>0:
                self.envio_correos_plantilla('email_contrato_notificacion_de_pago',contrato.id)

    def cambio_estado_congelar_contrato(self):

        self.state='congelar_contrato'

        tabla=self.env['contrato.estado.cuenta'].search([('estado_pago','=','pendiente'),('contrato_id','=',self.id)],order='fecha asc')

        if len(tabla)>0:
            dct={'contrato_id':self.id,'fecha':tabla[0].fecha}
            self.env['contrato.congelamiento'].create(dct)



    def reactivar_contrato_congelado(self):
        obj_fecha_congelamiento=self.env['contrato.congelamiento'].search([('contrato_id','=',self.id),('pendiente','=',True)],limit=1)

        hoy=date.today()

        fecha_reactivacion="%s-%s-%s" % (hoy.year, hoy.month,(calendar.monthrange(hoy.year, hoy.month)[1]))
        fecha_reactivacion = datetime.strptime(fecha_fin_tarea, '%y-%m-%d')

        detalle_estado_cuenta_pendiente=self.contrato.tabla_amortizacion.filtered(lambda l:  l.fecha>=obj_fecha_congelamiento.fecha  and l.fecha<fecha_reactivacion)

        nuevo_detalle_estado_cuenta_pendiente=detalle_estado_cuenta_pendiente.copy()

        for detalle in detalle_estado_cuenta_pendiente:

            detalle.cuota_capital=0
            detalle.cuota_adm=0
            detalle.seguro=0
            detalle.rastreo=0
            detalle.otro=0
            detalle.monto_pagado=0
            detalle.saldo=0

        tabla=self.env['contrato.estado.cuenta'].search([('contrato_id','=',self.id)],order='fecha desc')


        contador=1
        for detalle in nuevo_detalle_estado_cuenta_pendiente:
            detalle.fecha=tabla[0].fecha +relativedelta(months=contador)
            detalle.numero_cuota=tabla[0].numero_cuota +contador
            contador+=1






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
                'name': 'Validar Pago',
                'res_model': 'wizard.adelantar.cuotas',
                'target': 'new',
                'view_mode': 'form',
                'views': [[view_id, 'form']],
                'context': {
                    'default_contrato_id': self.id,
                }
        }


    def modificar_contrato_por_rubro(self,):


        numero_cuota=12
        month=month
        year=year

        self.funcion_modificar_contrato_por_rubro_seguro(self.rastreo,'rastreo')
        self.funcion_modificar_contrato_por_rubro_seguro(self.otro,'otro')
        self.funcion_modificar_contrato_por_rubro_seguro(self.seguro,'seguro')



    def funcion_modificar_contrato_por_rubro_seguro(self,valor,variable):


        numero_cuota=12
        month=month
        year=year

        obj_detalle=self.tabla_amortizacion.filtered(lambda l: l.fecha.year==year and l.fecha.month==month)


        contador=0

        for l in self.tabla_amortizacion.filtered(lambda l: l.numero_cuota>=obj_detalle.numero_cuota):
            l.write({variable:valor/12})

            contador+=1
            if contador==12:
                break




    def enviar_correos_contrato(self,):

        obj_rol=self.env['adjudicaciones.team'].search([('active','=',True),('correos','!=',False)]).mapped('correos')
        correos=''
        for correo in obj_rol:
            correos=correos+correo+','

        return correos









class ContratoCongelamiento(models.Model):
    _name = 'contrato.congelamiento'
    _description = 'Bitacora de Congelamiento'

    contrato_id = fields.Many2one('contrato')
    fecha = fields.Date(String='Fecha Congelamiento')
    pendiente = fields.Boolean(String='Pendiente de Activación')






class ContratoEstadoCuenta(models.Model):
    _name = 'contrato.estado.cuenta'
    _description = 'Contrato - Tabla de estado de cuenta de Aporte'

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
    estado_pago = fields.Selection([('pendiente', 'Pendiente'),
                                    ('pagado', 'Pagado')
                                    ], string='Estado de Pago', default='pendiente')

    pago_ids = fields.One2many(
        'account.payment', 'pago_id', track_visibility='onchange')
    






    @api.depends("pago_ids")
    def calcular_monto_pagado(self):

        for l in self:
            monto=sum(l.pago_ids.mapped("amount"))
            l.monto_pagado=monto

            l.saldo=l.cuota_capital+l.cuota_adm+l.iva_adm + l.seguro+ l.rastreo + l.otro - l.monto_pagado







    def pagar_cuota(self):
        view_id = self.env.ref('gzl_adjudicacion.wizard_pago_cuota_amortizaciones_contrato').id

        hoy= date.today()

        pagos_pendientes=self.contrato_id.tabla_amortizacion.filtered(lambda l: l.estado_pago=='pendiente' and l.fecha<self.fecha)
        if len(pagos_pendientes)>0 :
            raise ValidationError('Tengo pagos pendientes a la fecha, por favor realizar los pagos pendientes.')




        return {'type': 'ir.actions.act_window',
                'name': 'Validar Pago',
                'res_model': 'wizard.pago.cuota.amortizacion.contrato',
                'target': 'new',
                'view_mode': 'form',
                'views': [[view_id, 'form']],
                'context': {
                    'default_tabla_amortizacion_id': self.id,
                    'default_amount': self.saldo,
                    'default_payment_method_id': 2,


                }
        }

class PagoContratoEstadoCuenta(models.Model):
    _inherit = 'account.payment'

    pago_id = fields.Many2one('contrato.estado.cuenta', string="Detalle Estado de Cuenta")
    




# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, tools,  _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime,timedelta,date
import re


class DevolucionMonto(models.Model):   
    _name = 'devolucion.monto'   
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name= 'secuencia'

    
    secuencia = fields.Char(index=True)
    contrato_id = fields.Many2one('contrato')
    cliente = fields.Many2one(
        'res.partner', string="Nombre de Asociado", related='contrato_id.cliente',track_visibility='onchange')
    fecha_contrato = fields.Date(
        string='Fecha Contrato',related="contrato_id.fecha_contrato", track_visibility='onchange')
    tipo_de_contrato = fields.Many2one(
        'tipo.contrato.adjudicado', string='Tipo de Plan', related="contrato_id.tipo_de_contrato",track_visibility='onchange')
    vatAdjudicado = fields.Char(related="cliente.vat", string='Cedula del Asociado',store=True, default=' ')

    celular = fields.Char(related="cliente.phone", string='Celular',store=True, default=' ')
    correo = fields.Char(related="cliente.email", string='Correo',store=True, default=' ')

    monto  = fields.Monetary(related="contrato_id.monto_financiamiento",
        string='Monto Financiamiento', currency_field='currency_id', track_visibility='onchange')
    asesor = fields.Many2one('res.partner',related="contrato_id.asesor",string="Cerrador")
    asesor_postventa = fields.Many2one('res.partner',related="contrato_id.asesor",string="Cerrador")

    supervisor = fields.Many2one('res.users',related="contrato_id.supervisor",string="Supervisor")
    grupo = fields.Many2one(
        'grupo.adjudicado', related="contrato_id.grupo",string="Grupo", track_visibility='onchange')
    
    valor_inscripcion = fields.Monetary(
        string='Valor Inscripción',related="contrato_id.valor_inscripcion", currency_field='currency_id', track_visibility='onchange')

    ciudad = fields.Many2one(
        'res.country.city', string='Ciudad', related="contrato_id.ciudad", track_visibility='onchange')
    
    fsolicitud  = fields.Date(string='Fecha de Ingreso de Solicitud')
    state = fields.Selection(selection=[
        ('borrador', 'Borrador'),
        ('postventa', 'Analisis Postventa'),
        ('legal', 'Analisis Legal'),
        ('adjudicaciones', 'Analisis Adjudicacion'),
        ('verifvalores', 'Verificacion de Valores'),
        ('aprobgerencia', 'Aprobacion Gerencia'),
        ('salidadinero', 'Salida Dinero'),
        ('notificacion', 'Notificacion Cliente'),
        ('liquidacion', 'Liquidacion de vendedor'),
    ], string='Estado', default='borrador', track_visibility='onchange')

    tipo_devolucion = fields.Selection(selection=[
        ('DEVOLUCION DE VALORES SIN FIRMAS', 'DEVOLUCION DE VALORES SIN FIRMAS'),
        ('DEVOLUCION DE RESERVA', 'DEVOLUCION DE RESERVA'),
        ('DEVOLUCION DE LICITACION', 'DEVOLUCION DE LICITACION'),
        ('DEVOLUCION POR DESISTIMIENTO DEL CONTRATO', 'DEVOLUCION POR DESISTIMIENTO DEL CONTRATO'),
        ('DEVOLUCION POR CALIDAD DE VENTA', 'DEVOLUCION POR CALIDAD DE VENTA')], string='Tipo', track_visibility='onchange')


    tipo_accion = fields.Selection(selection=[
        ('CLIENTE', 'CLIENTE'),
        ('ABOGADO', 'ABOGADO'),
        ('CONSEJO', 'CONSEJO'),
        ('DEFENSORIA', 'DEFENSORIA'),
        ('FISCALIA', 'FISCALIA'),
        ('CAMARA DE COMERCIO', 'CAMARA DE COMERCIO')], string='Tipo', track_visibility='onchange')

    alerta = fields.Selection(selection=[
        ('CLIENTE', 'CLIENTE'),
        ('ABOGADO', 'ABOGADO'),
        ('CONSEJO DE LA JUDICATURA', 'CONSEJO'),
        ('DEFENSORIA', 'DEFENSORIA'),
        ('FISCALIA', 'FISCALIA')], string='Alerta', track_visibility='onchange')


    causa_sin_firma_reserva = fields.Selection(selection=[
        ('NO INTERESADO EN EL CONTRATO', 'NO INTERESADO EN EL CONTRATO'),
        ('NO DISPONE DEL DINERO', 'NO DISPONE DEL DINERO'),
        ('OTRO', 'OTRO')], string='Causas', track_visibility='onchange')



    causas_licitacion = fields.Selection(selection=[
        ('NO DESEA NINGUN VEHICULO OFRECIDO', 'NO DESEA NINGUN VEHICULO OFRECIDO'),
        ('NO CUMPLE CON PERFIL DE CREDITO', 'NO CUMPLE CON PERFIL DE CREDITO'),
        ('NO CUMPLE CON POLIZA DE SEGURO', 'NO CUMPLE CON POLIZA DE SEGURO'),
        ('INSATISFECHO CON EL PROCESO', 'INSATISFECHO CON EL PROCESO'),
        ('CLIENTE NO ADJUDICADO', 'CLIENTE NO ADJUDICADO'),
        ('LICITACION INCOMPLETA', 'LICITACION INCOMPLETA'),
        ('OTRO', 'OTRO')], string='Causas', track_visibility='onchange')


    causas_desistimiento = fields.Selection(selection=[
        ('MALA VENTA', 'MALA VENTA'),
        ('ENFERMEDAD', 'ENFERMEDAD'),
        ('MUERTE', 'MUERTE'),
        ('DESASTRE NATURAL', 'DESASTRE NATURAL'),
        ('NO DISPONE DE LOS RECURSOS', 'NO DISPONE DE LOS RECURSOS'),
        ('OTRO', 'OTRO')], string='Causas', track_visibility='onchange')


    causas_calidad_venta = fields.Selection(selection=[
        ('MALA VENTA', 'MALA VENTA'),
        ('NO ESTA DE ACUERDO CON EL PROCESO', 'NO ESTA DE ACUERDO CON EL PROCESO'),
        ('ENFERMEDAD', 'ENFERMEDAD'),
        ('MUERTE', 'MUERTE')], string='Causas', track_visibility='onchange')

    currency_id = fields.Many2one(
        'res.currency', readonly=True, default=lambda self: self.env.company.currency_id)

    valor_cancelado_sin_firma = fields.Monetary(
        string='VALOR CANCELADO SIN FIRMA', currency_field='currency_id')

    valor_reserva = fields.Monetary(
        string='VALOR DE RESERVA', currency_field='currency_id')

    valor_licitacion = fields.Monetary(
        string='VALOR DE LICITACION', currency_field='currency_id')

    valor_desistimiento = fields.Monetary(
        string='VALOR DESISTIMIENTO', currency_field='currency_id')

    capital_pagado_fecha = fields.Monetary(
        string='CAPITAL PAGADO A LA FECHA', currency_field='currency_id')

    administrativo_pagado_fecha = fields.Monetary(
        string='ADMINISTRATI VO PAGADO A LA FECHA', currency_field='currency_id')

    iva_pagado = fields.Monetary(
        string='IVA PAGADO', currency_field='currency_id')

    cuota_capital=fields.Monetary(
        string='Cuota Capital', currency_field='currency_id')

    valores_facturados = fields.Monetary(
        string='VALORES FACTURADOS', currency_field='currency_id')

    inscripcion = fields.Monetary(
        string='CUOTA DE INSCRIPCION', currency_field='currency_id')

    notas_credito = fields.Monetary(
        string='NOTAS DE CREDITO', currency_field='currency_id')
    ingreso_caja = fields.Monetary(
        string='INGRESOS DE CAJA', currency_field='currency_id')
    ingreso_banco = fields.Monetary(
        string='INGRESOS DE BANCOS', currency_field='currency_id')

    @api.onchange("contrato_id")
    def obtener_valores(self):
        for l in self:
            if l.contrato_id:
                capital_pagado_fecha=sum(l.contrato_id.estado_de_cuenta_ids.mapped("cuota_capital"))-sum(l.contrato_id.estado_de_cuenta_ids.mapped("saldo_cuota_capital"))
                administrativo_pagado_fecha=sum(l.contrato_id.estado_de_cuenta_ids.mapped("cuota_adm"))-sum(l.contrato_id.estado_de_cuenta_ids.mapped("saldo_cuota_administrativa"))
                iva_pagado=sum(l.contrato_id.estado_de_cuenta_ids.mapped("iva_adm"))-sum(l.contrato_id.estado_de_cuenta_ids.mapped("saldo_iva"))
                valor_desistimiento=capital_pagado_fecha*0.85
                valores_facturados=0
                notas_credito=0
                lista_facturas=[]
                facturas_obj=self.env['account.move'].search([('contrato_id','=',l.contrato_id.id),('type','=','out_invoice'),('state','=','posted')])    
                
                for x in facturas_obj:
                    lista_facturas.append(x.id)
                    valores_facturados+=x.amount_total
                    notas_credito_obj=self.env['account.move'].search([('reversed_entry_id','=',x.id),('type','=','out_refund'),('state','=','posted')])
                    for y in notas_credito_obj:
                        notas_credito+=y.amount_total
                        lista_facturas.append(y.id)
                valor_inscripcion=l.factura_inscripcion.amount_total
                pagos_obj=self.env['account.payment'].search([('partner_id','=',l.cliente.id),('payment_type','=','inbound'),('state','in',['reconciled','posted'])])
                ingreso_caja=0
                ingreso_banco=0
                for pagos in pagos_obj:
                    for pago in pagos.payment_line_ids:
                        if pagos.journal_id.type=='cash':
                            ingreso_caja+=pagos.amount
                        elif pagos.journal_id.type=='bank':
                            ingreso_banco+=pagos.amount

                l.capital_pagado_fecha=capital_pagado_fecha
                l.administrativo_pagado_fecha=administrativo_pagado_fecha
                l.iva_pagado=iva_pagado
                l.valores_facturados=valores_facturados
                l.inscripcion=valor_inscripcion
                l.notas_credito=notas_credito
                l.ingreso_caja=ingreso_caja
                l.ingreso_banco=ingreso_banco
                l.cuota_capital=ingreso_banco+ingreso_caja+notas_credito-valores_facturados
                l.valor_desistimiento=valor_desistimiento


    calidad_venta = fields.Selection(selection=[
        ('MALA VENTA', 'MALA VENTA'),
        ('NO ESTA DE ACUERDO CON EL PROCESO', 'NO ESTA DE ACUERDO CON EL PROCESO'),
        ('MUERTE', 'MUERTE'),
        ('ENFERMEDAD', 'ENFERMEDAD')], string='Calidad de Venta', track_visibility='onchange')

    documentos_postventa = fields.One2many('devolucion.documentos.postventa','devolucion_id',track_visibility='onchange')
    observacion_contabilidad=fields.Text(string="Observaciones")
    observacion_legal=fields.Text(string="Observaciones")
    documentos_legal = fields.One2many('devolucion.documentos.legal','devolucion_id',track_visibility='onchange')
    observacion_adjudicaciones=fields.Text(string="Observaciones")
    resumen_postventa=fields.Text(string="RESUMEN DEL CASO POR POSTVENTA")
    resumen_adjudicaciones=fields.Text(string="RESUMEN DEL CASO POR ADJUDICACIONES")
    simulacion_fondos=fields.Text(string="SIMULACION DE FONDOS")

    @api.onchange('tipo_accion')
    @api.depends('tipo_accion')
    def llenar_tabla_legal(self):
        obj_documentos_legal=self.env['documentos.legal'].search([('tipo_accion','=',self.tipo_accion)])  
        lista_ids=[]
        for doc in obj_documentos_legal:
            id_registro=self.env['devolucion.documentos.legal'].create({'documento_id':doc.id})
            lista_ids.append(int(id_registro))
        self.update({'documentos_legal':[(6,0,lista_ids)]})
       
    @api.onchange('tipo_devolucion')
    @api.depends('tipo_devolucion')
    def llenar_tabla_posventa(self):
        obj_documentos_postventa=self.env['documentos.postventa'].search([('tipo_devolucion','=',self.tipo_devolucion)])
        lista_ids=[]
        for doc in obj_documentos_postventa:
            id_registro=self.env['devolucion.documentos.postventa'].create({'documento_id':doc.id})
            lista_ids.append(int(id_registro))
        self.update({'documentos_postventa':[(6,0,lista_ids)]})
###REQUISITOS


    rolAsignado = fields.Many2one('adjudicaciones.team', string="Rol Asignado", track_visibility='onchange')
    
    rolGerenciaFin = fields.Many2one('adjudicaciones.team', string="Rol Gerencia Financiera", track_visibility='onchange',default=lambda self:self.env.ref('gzl_adjudicacion.tipo_rol4'))
    rolAdjudicacion = fields.Many2one('adjudicaciones.team', string="Rol Adjudicacion", track_visibility='onchange',default=lambda self:self.env.ref('gzl_adjudicacion.tipo_rol2'))

    rolpostventa = fields.Many2one('adjudicaciones.team', string="Rol Post venta", track_visibility='onchange',default=lambda self:self.env.ref('gzl_adjudicacion.tipo_rol5'))
    rollegal = fields.Many2one('adjudicaciones.team', string="Rol Legal", track_visibility='onchange',default=lambda self:self.env.ref('gzl_adjudicacion.tipo_rol6'))

    rolcontab = fields.Many2one('adjudicaciones.team', string="Rol contabilidad Financiera", track_visibility='onchange',default=lambda self:self.env.ref('gzl_adjudicacion.tipo_rol7'))
    rolnomina = fields.Many2one('adjudicaciones.team', string="Rol Nomina", track_visibility='onchange',default=lambda self:self.env.ref('gzl_adjudicacion.tipo_rol8'))

    @api.model
    def create(self, vals):
        vals['secuencia'] = self.env['ir.sequence'].next_by_code('devolucion.adjudicado')
        return super(DevolucionMonto, self).create(vals)
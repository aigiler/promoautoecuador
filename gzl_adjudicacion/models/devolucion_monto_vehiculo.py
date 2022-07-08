# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, tools,  _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime,timedelta,date
import re


class DevolucionMonto(models.Model):   
    _name = 'devolucion.monto'   
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name= 'secuencia'

    contrato_id = fields.Many2one('contrato')
    cliente = fields.Many2one(
        'res.partner', string="Nombre de Asociado",track_visibility='onchange')
    
    secuencia = fields.Char(index=True)
    fecha_contrato = fields.Date(
        string='Fecha Contrato',related="contrato_id.fecha_contrato", track_visibility='onchange')
    tipo_de_contrato = fields.Many2one(
        'tipo.contrato.adjudicado', string='Tipo de Plan', related="contrato_id.tipo_de_contrato",track_visibility='onchange')
    vatAdjudicado = fields.Char(related="cliente.vat", string='Cedula del Asociado',store=True, default=' ')

    celular = fields.Char(related="cliente.phone", string='Celular',store=True, default=' ')
    correo = fields.Char(related="cliente.email", string='Correo',store=True, default=' ')

    monto  = fields.Monetary(related="contrato_id.monto_financiamiento",
        string='Monto Financiamiento', currency_field='currency_id', track_visibility='onchange')
    asesor = fields.Many2one('res.partner',related="contrato_id.asesor",string="Asesor")
    asesor_postventa = fields.Many2one('res.partner',string="Asesor Postventa")

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
                valor_inscripcion=l.contrato_id.factura_inscripcion.amount_total
                valor_cancelado_sin_firma=0
                valor_reserva=0
                en_caja=0
                en_banco=0
                if not l.contrato_id.factura_inscripcion:
                    crm_id=self.env['crm.lead'].search([('contrato_id','=',l.contrato_id.id)],limit=1)
                    if crm_id:
                        sale_order=self.env['sale.order'].search([('opportunity_id','=',crm_id.id),('state','!=','cancel')])
                        for line in sale_order:
                            factura=self.env['account.move'].search([('invoice_origin','=',line.name),('state','!=','cancel')])
                            if not factura:
                                pago_inscripcion=self.env['account.payment'].search([('pago_inscripcion','=',True),('cotizacion','=',line.id),('partner_id','=',l.cliente.id),('payment_type','=','inbound'),('state','in',['reconciled','posted'])])
                                for inscripcion in pago_inscripcion:
                                    valor_cancelado_sin_firma+=inscripcion.amount
                                pago_reserva=self.env['account.payment'].search([('pago_reserva','=',True),('cotizacion','=',line.id),('partner_id','=',l.cliente.id),('payment_type','=','inbound'),('state','in',['reconciled','posted'])])
                                for reserva in pago_reserva:
                                    valor_reserva+=reserva.amount
                                    if pago_reserva.journal_id.type=='cash':
                                        en_caja+=reserva.amount
                                    elif pago_reserva.journal_id.type=='bank':
                                        en_banco+=reserva.amount


                else:
                    lista_facturas.append(l.contrato_id.factura_inscripcion.id)

                l.valor_cancelado_sin_firma=valor_cancelado_sin_firma
                l.valor_reserva=valor_reserva
                pagos_obj=self.env['account.payment'].search([('partner_id','=',l.cliente.id),('payment_type','=','inbound'),('state','in',['reconciled','posted'])])
                ingreso_caja=0
                ingreso_banco=0
                for pagos in pagos_obj:
                    bandera=False
                    for fac in pagos.invoice_ids:
                        if fac.id in lista_facturas and not bandera:
                            if pagos.journal_id.type=='cash':
                                ingreso_caja+=pagos.amount
                            elif pagos.journal_id.type=='bank':
                                ingreso_banco+=pagos.amount
                            bandera=True

                l.capital_pagado_fecha=capital_pagado_fecha
                l.administrativo_pagado_fecha=administrativo_pagado_fecha
                l.iva_pagado=iva_pagado
                l.valores_facturados=valores_facturados
                l.inscripcion=valor_inscripcion
                l.notas_credito=notas_credito
                if l.contrato_id.factura_inscripcion:
                    l.ingreso_caja=ingreso_caja-en_caja
                    l.ingreso_banco=ingreso_banco-en_banco
                else:
                    l.ingreso_caja=ingreso_caja
                    l.ingreso_banco=ingreso_banco
                l.cuota_capital=ingreso_banco+ingreso_caja+notas_credito-valores_facturados
                l.valor_desistimiento=valor_desistimiento


    @api.onchange("tipo_devolucion")
    def calcular_desistimiento(self):
        for l in self:
            if l.tipo_devolucion=='DEVOLUCION DE VALORES SIN FIRMAS':
                penalizacion=self.env['ir.config_parameter'].search([('key','=','desistimiento_sin_firma')],limit=1)
                l.valor_desistimiento=l.valor_cancelado_sin_firma*((100-int(penalizacion.value))/100)

            elif l.tipo_devolucion=='DEVOLUCION DE RESERVA':
                penalizacion=self.env['ir.config_parameter'].search([('key','=','desistimiento_reserva')],limit=1)
                l.valor_desistimiento=l.valor_reserva*((100-int(penalizacion.value))/100)

            elif l.tipo_devolucion=='DEVOLUCION DE LICITACION':
                penalizacion=self.env['ir.config_parameter'].search([('key','=','devolucion_licitacion')],limit=1)
                l.valor_desistimiento=l.valor_licitacion*((100-int(penalizacion.value))/100)

            elif l.tipo_devolucion=='DEVOLUCION POR DESISTIMIENTO DEL CONTRATO':
                penalizacion=self.env['ir.config_parameter'].search([('key','=','desistimiento_contrato')],limit=1)
                l.valor_desistimiento=l.capital_pagado_fecha*((100-int(penalizacion.value))/100)

            elif l.tipo_devolucion=='DEVOLUCION POR CALIDAD DE VENTA':
                penalizacion=self.env['ir.config_parameter'].search([('key','=','desistimiento_calidad')],limit=1)
                l.valor_desistimiento=l.valor_cancelado_sin_firma*((100-int(penalizacion.value))/100)+l.valor_reserva*((100-int(penalizacion.value))/100)


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
    resolucion_gerencia=fields.Text(string="Resolución de Gerencia")
    pago_id=fields.Many2one("account.payment")
    journal_id = fields.Many2one('account.journal', string='Banco', tracking=True, domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, string='Company', readonly=True)

    def generar_pago(self):
        for l in self:
            if self.journal_id:
                pago_metodo=self.env.ref('gzl_facturacion_electronica.out_transfer')
                if l.tipo_devolucion=='DEVOLUCION DE VALORES SIN FIRMAS' or l.tipo_devolucion=='DEVOLUCION DE RESERVA' or l.tipo_devolucion=='DEVOLUCION POR CALIDAD DE VENTA':
                    cuenta_contrapartida=4613
                else:
                    cuenta_contrapartida=4590

                tupla=[(0, 0, {
                            'name': "Devolucion de Valores",
                            'amount_currency':  0.0,
                            'currency_id': self.env.company.currency_id,
                            'debit': 0.00 ,
                            'credit':  l.valor_desistimiento,
                            'date_maturity': self.fsolicitud,
                            'partner_id': self.cliente.id,
                            'account_id':self.cliente.property_account_receivable_id.id,
                            'analytic_account_id':False,}),
                            (0, 0, {
                            'name': "Devolucion de Valores",
                            'amount_currency':  0.0,
                            'currency_id': self.env.company.currency_id,
                            'debit': l.valor_desistimiento ,
                            'credit':  0.00,
                            'date_maturity': self.fsolicitud,
                            'partner_id': self.cliente.id,
                            'account_id': cuenta_contrapartida,
                            'analytic_account_id':False,})]

                move_vals = {
                    'date':  self.fsolicitud,
                    'ref': "Devolucion de Valores",
                    'journal_id': 3,
                    'currency_id': self.env.company.currency_id,
                    'partner_id':  self.cliente.id,
                    'line_ids': tupla,
                }
                move_id=self.env['account.move'].create(move_vals).post()

                pago_id=self.env['account.payment'].create({"journal_id":l.journal_id.id,'partner_id':self.cliente.id,
                                                                    'payment_type':'outbound','amount':l.valor_desistimiento,
                                                                    'payment_method_id':pago_metodo.id,
                                                                    'state':'draft',
                                                                    'tipo_transaccion':'Pago',
                                                                    'company_id':self.env.company.id,
                                                                    'partner_type':"customer"})
                self.pago_id=pago_id.id
            else:
                raise ValidationError("Seleccione el Banco con el cual desea realizar la devolución.")
            
    @api.onchange('tipo_accion')
    @api.depends('tipo_accion')
    def llenar_tabla_legal(self):
        obj_documentos_legal=self.env['documentos.legal'].search([('tipo_accion','in',(self.tipo_accion,'TODOS'))])  
        lista_ids=[]
        for doc in obj_documentos_legal:
            id_registro=self.env['devolucion.documentos.legal'].create({'documento_id':doc.id})
            lista_ids.append(int(id_registro))
        self.update({'documentos_legal':[(6,0,lista_ids)]})
       
    @api.onchange('tipo_devolucion')
    @api.depends('tipo_devolucion')
    def llenar_tabla_posventa(self):
        obj_documentos_postventa=self.env['documentos.postventa'].search([('tipo_devolucion','=',(self.tipo_devolucion,'TODOS'))])
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

    def validarrol(self):
        roles=self.env['adjudicaciones.team'].search([('id','=',self.rolAsignado.id)])
        for x in roles:
          if self.env.user in x.member_ids:
            return True
          else:
            raise ValidationError("Debe estar asignado al rol %s"% self.rolAsignado.name)
        return True


    def validar_documentos_postventa(self):
        for l in self:
            for x in l.documentos_postventa:
                if not x.archivo:
                    raise ValidationError("Debe cargar los documentos solicitados para el tipo de devolución ingresado") 


    def validar_documentos_legal(self):
        for l in self:
            for x in l.documentos_legal:
                if not x.archivo:
                    raise ValidationError("Debe cargar los documentos solicitados para el tipo de acción ingresado") 
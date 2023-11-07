# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError

import numpy_financial as npf

from dateutil.parser import parse

class WizardAdelantarCuotas(models.Model):
    _name = 'wizard.cesion.derecho'
    _description="Cesión de Derecho"
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']    

    contrato_id = fields.Many2one('contrato')
    name=fields.Char("Name")
    monto_a_ceder = fields.Float( string='Monto a Ceder',store=True)
    contrato_a_ceder= fields.Many2one('contrato',string="Contrato a Ceder")
    carta_adjunto = fields.Binary('Carta de Cesión', attachment=True)
    comprobante_pago = fields.Binary('Comprobante de Pago', attachment=True)
    otro_documento = fields.Binary('Otro Documento', attachment=True)
    partner_id=fields.Many2one("res.partner", "Cliente a Ceder")
    cliente_id=fields.Many2one("res.partner", "Cliente Cedente")

    pago_id=fields.Many2one("account.payment", "Pago Generado")
    ejecutado=fields.Boolean(default=False)
    actividad_id = fields.Many2one('mail.activity',string="Actividades")
    rolcontab = fields.Many2one('adjudicaciones.team', string="Rol contabilidad Financiera", track_visibility='onchange',default=lambda self:self.env.ref('gzl_adjudicacion.tipo_rol7'))
    rolpostventa = fields.Many2one('adjudicaciones.team', string="Rol Post venta", track_visibility='onchange',default=lambda self:self.env.ref('gzl_adjudicacion.tipo_rol5'))
    rolDelegado = fields.Many2one('adjudicaciones.team', string="Rol Delegado", track_visibility='onchange',default=lambda self:self.env.ref('gzl_adjudicacion.tipo_rol8'))
    rolAdjudicaciones = fields.Many2one('adjudicaciones.team', string="Rol Delegado", track_visibility='onchange',default=lambda self:self.env.ref('gzl_adjudicacion.tipo_rol2'))
    cesion_id=fields.Many2one("ir.attachment",string="Documento Cesión de Derecho")

    forma_pago = fields.Selection(selection=[
            ('caja', 'Caja'),
            ('banco', 'Banco'),
            ], string='Estado', copy=True, tracking=True,track_visibility='onchange')    

    state = fields.Selection(selection=[
            ('inicio', 'Ingreso de solicitud'),
            ('en_curso', 'En Proceso de Pago'),
            ('pre_cierre', 'Proceso de cierre'),
            ('cerrado', 'Cerrado')
            ], string='Estado', copy=True, tracking=True, default='inicio',track_visibility='onchange')

    def crear_documento(self):
        for l in self:
            cesion_id=self.env['cesion.derecho'].create({"cesion_id":self.id})
            dct=cesion_id.print_report_xls(self)
            self.cesion_id=dct["documento"]["id"]
            return dct

    @api.constrains("contrato_a_ceder")
    @api.onchange("contrato_a_ceder")
    def obtener_nombre(self):
        for l in self:
            name=" "
            if l.contrato_a_ceder:
                name="Cesión de Derecho al Contrato "+l.contrato_a_ceder.secuencia
            l.name=name
    
    def crear_activity(self,rol,mensaje):
        if self.actividad_id:
            self.actividad_id.action_done()
        actividad_id=self.env['mail.activity'].create({
                'res_id': self.id,
                'res_model_id': self.env['ir.model']._get('wizard.cesion.derecho').id,
                'activity_type_id': 4,
                'summary': "Ha sido asignado al proceso de Cesión de Derecho. "+str(mensaje),
                'user_id': rol.user_id.id,
                'date_deadline':datetime.now()+ relativedelta(days=1)
            })
        self.actividad_id=actividad_id.id

    def ejecutar_cesion(self):
      #  self.validarrol(self.rolAdjudicaciones)


        if self.env.user.id != self.rolAdjudicaciones.user_id.id:
            raise ValidationError("La solicitud solo debe ser finalizada por el responsable de Adjudicaciones "+self.rolAdjudicaciones.user_id.name)



         
        for l in self:
            lista_final=[]
            if l.pago_id and l.carta_adjunto:
                l.contrato_a_ceder.es_cesion=True
                id_contrato=l.contrato_a_ceder.copy()
                l.contrato_id=id_contrato.id
                anio = str(datetime.today().year)
                mes = str(datetime.today().month)
                fechaPago =  anio+"-"+mes+"-{0}".format(id_contrato.dia_corte.zfill(2)) 
                feha_pago=parse(fechaPago).date().strftime('%Y-%m-%d')
                l.contrato_id.fecha_inicio_pago = feha_pago
                detalle_estado_cuenta_uno=self.contrato_a_ceder.tabla_amortizacion.filtered(lambda l:  l.numero_cuota == "1")
                nuevo_detalle_estado_cuenta_pendiente=[]
                
                for detalle in detalle_estado_cuenta_uno:
                    detalle_id=detalle.copy()
                    #nuevo_detalle_estado_cuenta_pendiente.append(detalle_id.id)
                    cuota_actual=self.env['contrato.estado.cuenta'].browse(detalle_id.id)
                    cuota_actual.contrato_id=id_contrato.id
                    cuota_actual.fecha=l.contrato_id.fecha_inicio_pago
                    lista_final.append({'cuota':1,'fecha_pago':cuota_actual.fecha})
                    cuota_actual.factura_id=False
                    if detalle.estado_pago=='pagado':
                        cuota_actual.estado_pago="varias"
                    pagos_asociados=self.env['account.payment.cuotas'].search([('cuotas_id','=',detalle.id)])
                    for pag in pagos_asociados:
                        id_pago=self.env['account.payment.cuotas'].create({'pago_id':pag.pago_id.id,
                                                        'monto_pagado':pag.monto_pagado,
                                                        'valor_asociado':pag.valor_asociado,
                                                        'cuotas_id':cuota_actual.id})
                i=2
                j=1
                detalle_estado_cuenta_pendiente=self.contrato_a_ceder.tabla_amortizacion.filtered(lambda l:  l.numero_cuota != "1" and l.estado_pago=='pendiente' and not l.programado)
                for detalle in detalle_estado_cuenta_pendiente:
                    detalle_id=detalle.copy()
                    cuota_actual=self.env['contrato.estado.cuenta'].browse(detalle_id.id)
                    cuota_actual.contrato_id=id_contrato.id
                    cuota_actual.numero_cuota=i
                    cuota_actual.fecha=l.contrato_id.fecha_inicio_pago + relativedelta(months=j)
                    cuota_actual.saldo_cuota_capital=detalle.saldo_cuota_capital
                    cuota_actual.saldo_cuota_administrativa=detalle.saldo_cuota_administrativa
                    cuota_actual.saldo_iva=detalle.saldo_iva
                    cuota_actual.saldo_seguro=detalle.saldo_seguro
                    cuota_actual.saldo_rastreo=detalle.saldo_rastreo
                    cuota_actual.saldo_programado=detalle.saldo_programado
                    cuota_actual.saldo_otros=detalle.saldo_otros
                    pagos_asociados=self.env['account.payment.cuotas'].search([('cuotas_id','=',detalle.id)])
                    for pag in pagos_asociados:
                        id_pago=self.env['account.payment.cuotas'].create({'pago_id':pag.pago_id.id,
                                                        'monto_pagado':pag.monto_pagado,
                                                        'valor_asociado':pag.valor_asociado,
                                                        'cuotas_id':cuota_actual.id})

                    cuota_actual.factura_id=False
                    lista_final.append({'cuota':i,'fecha_pago':cuota_actual.fecha})
                    i+=1
                    j+=1
                detalle_estado_cuenta_pendienta=self.contrato_a_ceder.tabla_amortizacion.filtered(lambda l: l.estado_pago=='pagado' and l.numero_cuota != "1" and not l.programado)
                for detalle in detalle_estado_cuenta_pendienta:
                    detalle_id=detalle.copy()
                    #nuevo_detalle_estado_cuenta_pendiente.append(detalle_id.id)
                    cuota_actual=self.env['contrato.estado.cuenta'].browse(detalle_id.id)
                    cuota_actual.contrato_id=id_contrato.id
                    cuota_actual.numero_cuota=i
                    if detalle.estado_pago=='pagado':
                        cuota_actual.estado_pago="varias"
                    cuota_actual.factura_id=False
                    cuota_actual.saldo_cuota_capital=0
                    cuota_actual.saldo_cuota_administrativa=0
                    cuota_actual.saldo_iva=0
                    cuota_actual.saldo_seguro=0
                    cuota_actual.saldo_rastreo=0
                    cuota_actual.saldo_programado=0
                    cuota_actual.saldo_otros=0
                    pagos_asociados=self.env['account.payment.cuotas'].search([('cuotas_id','=',detalle.id)])
                    for pag in pagos_asociados:
                        id_pago=self.env['account.payment.cuotas'].create({'pago_id':pag.pago_id.id,
                                                        'monto_pagado':pag.monto_pagado,
                                                        'valor_asociado':pag.valor_asociado,
                                                        'cuotas_id':cuota_actual.id})

                    cuota_actual.fecha=l.contrato_id.fecha_inicio_pago+ relativedelta(months=j)
                    lista_final.append({'cuota':i,'fecha_pago':cuota_actual.fecha})
                    i+=1
                    j+=1
                programado=self.contrato_a_ceder.tabla_amortizacion.filtered(lambda l: l.programado>0.00)
                for detalle in programado:
                    detalle_id=detalle.copy()
                    #nuevo_detalle_estado_cuenta_pendiente.append(detalle_id.id)
                    cuota_actual=self.env['contrato.estado.cuenta'].browse(detalle_id.id)
                    cuota_actual.contrato_id=id_contrato.id
                    if detalle.estado_pago=='pagado':
                        cuota_actual.estado_pago="varias"
                    for x in lista_final:
                        if x['cuota']==int(cuota_actual.numero_cuota):
                            cuota_actual.fecha=x['fecha_pago']
                    i+=1

                l.contrato_a_ceder.nota="El cliente "+l.contrato_a_ceder.cliente.name+" le cedió el contrato a "+l.partner_id.name
                l.contrato_a_ceder.cesion_id=l.id
                detalle_contrato_original=l.contrato_a_ceder.tabla_amortizacion.filtered(lambda l: l.monto_pagado==0)
                detalle_contrato_original.unlink()
                l.contrato_id.cliente=l.partner_id.id
                l.state="cerrado"
                l.contrato_id.state=l.contrato_a_ceder.state
                l.contrato_id.state_simplificado=l.contrato_a_ceder.state_simplificado
                l.contrato_a_ceder.state='FINALIZADO'
                l.contrato_a_ceder.state_simplificado="DESISTIDO NO PAGADO"
                l.contrato_id.nota="El cliente "+l.contrato_a_ceder.cliente.name+" le cedió el contrato a "+l.partner_id.name
                l.contrato_id.cesion_id=l.id
                if l.actividad_id:
                    l.actividad_id.action_done()

    def descargar(self):
        return True

    def validarrol(self,rol):
        roles=self.env['adjudicaciones.team'].search([('id','=',rol.id)])
        for x in roles:
          if self.env.user.id in x.member_ids.ids:
            return True
          else:
            raise ValidationError("Debe estar asignado al rol %s"% rol.name)
        return True

    def enviar_contabilidad(self):
        #if self.carta_adjunto:
        self.validarrol(self.rolpostventa)   
        mensaje="Favor registrar el Pago de la Cesión de Derecho: "+self.name
        if self.forma_pago=='caja':
            self.crear_activity(self.rolDelegado,mensaje)
        elif self.forma_pago=='banco':
            self.crear_activity(self.rolcontab,mensaje)
        else:
            raise ValidationError("Debe indicar la forma de Pago.")
        self.state='en_curso'
        #else:
        #    raise ValidationError("Debe adjuntar el documento pertinente para continuar con el proceso.")


    def pago_procesado(self):
        if self.pago_id and self.carta_adjunto:
            if self.forma_pago=="caja":
                self.validarrol(self.rolDelegado) 
            else:
                self.validarrol(self.rolcontab)  
            mensaje="El pago se encuentra asociado a la Cesión de Derecho. "+self.name+' Favor de ejecutarla'
            self.crear_activity(self.rolpostventa,mensaje)
            self.state='pre_cierre'
        else:
            raise ValidationError("En caso de haber procesado el pago asocielo a esta cesión de derecho o verifique que el documento se encuentre adjunto")

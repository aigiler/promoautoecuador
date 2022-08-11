# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError

import numpy_financial as npf

from dateutil.parser import parse

class WizardAdelantarCuotas(models.Model):
    _name = 'wizard.cesion.derecho'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']    

    contrato_id = fields.Many2one('contrato')
    name=fields.Char("Name")
    monto_a_ceder = fields.Float( string='Monto a Ceder',store=True)
    contrato_a_ceder= fields.Many2one('contrato',string="Contrato a Ceder")
    carta_adjunto = fields.Binary('Carta de Cesión', attachment=True)
    partner_id=fields.Many2one("res.partner", "Cliente a Ceder")
    pago_id=fields.Many2one("account.payment", "Pago Generado")
    ejecutado=fields.Boolean(default=False)
    actividad_id = fields.Many2one('mail.activity',string="Actividades")
    rolcontab = fields.Many2one('adjudicaciones.team', string="Rol contabilidad Financiera", track_visibility='onchange',default=lambda self:self.env.ref('gzl_adjudicacion.tipo_rol7'))
    rolpostventa = fields.Many2one('adjudicaciones.team', string="Rol Post venta", track_visibility='onchange',default=lambda self:self.env.ref('gzl_adjudicacion.tipo_rol5'))

    state = fields.Selection(selection=[
            ('inicio', 'Ingreso de solicitud'),
            ('en_curso', 'En Proceso de Pago'),
            ('pre_cierre', 'Proceso de cierre'),
            ('cerrado', 'Cerrado')
            ], string='Estado', copy=True, tracking=True, default='inicio',track_visibility='onchange')

    @api.contrains("contrato_a_ceder")
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
                'res_model_id': self.env['ir.model']._get('devolucion.monto').id,
                'activity_type_id': 4,
                'summary': "Ha sido asignado al proceso de Cesión de Derecho. "+str(mensaje),
                'user_id': rol.user_id.id,
                'date_deadline':datetime.now()+ relativedelta(days=1)
            })
        self.actividad_id=actividad_id.id
    # def ejecutar_cesion(self):
    #     for l in self:
    #         if l.contrato_id:
    #             if l.partner_id:
    #                 l.name="Cesion al contrato "+str(l.contrato_id.secuencia)
    #                 l.contrato_id.nota=" "+str(self.contrato_id.cliente.name)+' Cede el contrato a la persona: '+str(self.partner_id.name)
    #                 l.contrato_id.cliente=self.partner_id.id
    #                 l.contrato_id.cesion_id=self.id
    #                 l.ejecutado=True

    def ejecutar_cesion(self):
        for l in self:
            lista_final=[]
            if l.pago_id and l.carta_adjunto:
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
                i=2
                j=1
                detalle_estado_cuenta_pendiente=self.contrato_a_ceder.tabla_amortizacion.filtered(lambda l:  l.numero_cuota != "1" and l.estado_pago=='pendiente' and not l.programado)
                for detalle in detalle_estado_cuenta_pendiente:
                    detalle_id=detalle.copy()
                    ##nuevo_detalle_estado_cuenta_pendiente.append(detalle_id.id)
                    cuota_actual=self.env['contrato.estado.cuenta'].browse(detalle_id.id)
                    cuota_actual.contrato_id=id_contrato.id
                    cuota_actual.numero_cuota=i
                    cuota_actual.fecha=l.contrato_id.fecha_inicio_pago + relativedelta(months=j)
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
                    cuota_actual.saldo_cuota_capital=detalle.cuota_capital
                    cuota_actual.saldo_cuota_administrativa=detalle.cuota_adm
                    cuota_actual.saldo_iva=detalle.iva_adm
                    cuota_actual.saldo_seguro=detalle.seguro
                    cuota_actual.saldo_rastreo=detalle.rastreo
                    cuota_actual.saldo_programado=detalle.programado
                    cuota_actual.saldo_otros=detalle.otro
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
                if l.actividad_id:
                    l.actividad_id.action_done()
    
    def enviar_contabilidad(self):            
        mensaje="Favor registrar el Pago de la Cesión de Derecho: "+self.name
        self.crear_activity(self.rolcontab,mensaje)
        self.state='en_curso'


    def pago_procesado(self):
        mensaje="El pago se encuentra asociado a la Cesión de Derecho. "+self.name+' Favor de ejecutarla'
        self.crear_activity(self.rolpostventa,mensaje)
        self.state='pre_cierre'
        

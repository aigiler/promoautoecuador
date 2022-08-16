# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError
import numpy_financial as npf
import math


class TablaAdendum(models.Model):
    _name="tabla.adendum"

    currency_id = fields.Many2one(
        'res.currency', readonly=True, default=lambda self: self.env.company.currency_id)

    numero_cuota = fields.Char(String='Número de Cuota')

    fecha = fields.Date(String='Fecha Pago')
    cuota_capital = fields.Monetary(
        string='Cuota Capital', currency_field='currency_id')
    cuota_adm = fields.Monetary(
        string='Cuota Adm', currency_field='currency_id')

    iva_adm = fields.Monetary(
        string='Iva Adm', currency_field='currency_id')
    saldo = fields.Monetary(string='Saldo', currency_field='currency_id' ,compute="calcular_monto_pagado",store=True)

    estado_pago = fields.Selection([('pendiente', 'Pendiente'),
                                    ('pagado', 'Pagado'),
                                    ('congelado', 'Congelado'),
                                    ('varias', 'Varias(Cesión)')
                                    ], string='Estado de Pago', default='pendiente')

    adendum_id = fields.Many2one('wizard.contrato.adendum',string="Adendum")
    procesado=fields.Boolean(default=False)

class WizardContratoAdendum(models.Model):
    _name = 'wizard.contrato.adendum'
    _description = 'Contrato Adendum'


    contrato_id = fields.Many2one('contrato',string="Contrato")
    socio_id = fields.Many2one('res.partner',string="Socio")
    ejecutado = fields.Boolean(string="Ejecutado", default = False)
    monto_financiamiento = fields.Monetary(
        string='Monto Financiamiento', currency_field='currency_id', track_visibility='onchange')
    plazo_meses = fields.Many2one('numero.meses',default=lambda self: self.env.ref('gzl_adjudicacion.{0}'.format('numero_meses60')).id ,track_visibility='onchange' )
    cuota_adm = fields.Monetary(
        string='Cuota Administrativa',store=True, compute='calcular_cuota', currency_field='currency_id', track_visibility='onchange')
    
    currency_id = fields.Many2one(
        'res.currency', readonly=True, default=lambda self: self.env.company.currency_id)
    ##valores anteriores
    monto_financiamiento_anterior = fields.Monetary(
        string='Monto Financiamiento', currency_field='currency_id', track_visibility='onchange')
    plazo_meses_anterior = fields.Many2one('numero.meses',default=lambda self: self.env.ref('gzl_adjudicacion.{0}'.format('numero_meses60')).id ,track_visibility='onchange' )
    cuota_anterior = fields.Monetary(currency_field='currency_id', track_visibility='onchange')
    observacion = fields.Char(string='Observacion')
    valor_inscripcion = fields.Monetary(
        string='Valor Inscripción', currency_field='currency_id', track_visibility='onchange')

    tabla_adendum_id=fields.One2many("tabla.adendum","adendum_id", track_visibility='onchange')

    rolAdjudicacion = fields.Many2one('adjudicaciones.team', string="Rol Adjudicacion", track_visibility='onchange',default=lambda self:self.env.ref('gzl_adjudicacion.tipo_rol2'))
    rolpostventa = fields.Many2one('adjudicaciones.team', string="Rol Post venta", track_visibility='onchange',default=lambda self:self.env.ref('gzl_adjudicacion.tipo_rol5'))
    nota=fields.Char()
    state = fields.Selection(selection=[
            ('inicio', 'Ingreso de Solicitud'),
            ('aprobacion', 'En Proceso de Aprobación'),
            ('procesado', 'Procesado')
            ], string='Estado', copy=False, tracking=True, default='inicio',track_visibility='onchange')


    @api.depends('monto_financiamiento')
    def calcular_cuota(self):
        for l in self:
            cuotaAdministrativa=0
            if l.monto_financiamiento:
                cuotaAdministrativa= (l.monto_financiamiento*((l.contrato_id.tasa_administrativa/100)/12))*l.plazo_meses.numero
                
                
            l.cuota_adm = cuotaAdministrativa

    @api.onchange("contrato_id")
    @api.constrains("contrato_id")
    def validar_datos(self):
        for l in self:
            if l.contrato_id:
                l.cuota_anterior=l.contrato_id.cuota_adm+l.contrato_id.iva_administrativo+l.contrato_id.cuota_capital
                l.monto_financiamiento_anterior=l.contrato_id.monto_financiamiento
                l.plazo_meses_anterior=l.contrato_id.plazo_meses.id
                l.plazo_meses=l.contrato_id.plazo_meses.id

    def validar_tabla(self,):

        lista_tabla=[]
        if self.monto_financiamiento and self.plazo_meses:
            pagos=self.contrato_id.tabla_amortizacion.filtered(lambda l: l.estado_pago=='pagado')
            cuotas_pgadas=sum(pagos.mapped("cuota_capital"))
            adm_pgadas=sum(pagos.mapped("cuota_adm"))
            pagos_pendiente=self.contrato_id.tabla_amortizacion.filtered(lambda l: l.estado_pago!='pagado' and l.factura_id)
            cuotas_pendientes_pago=sum(pagos_pendiente.mapped("cuota_capital"))
            adm_pendientes_pago=sum(pagos_pendiente.mapped("cuota_adm"))
            abonos=self.contrato_id.tabla_amortizacion.filtered(lambda l: l.estado_pago!='pagado' and l.monto_pagado>0 and not l.factura_id)
            cuotas_pendientes_abono=sum(abonos.mapped("cuota_capital"))
            adm_pendientes_abono=sum(abonos.mapped("cuota_adm"))
            pago_capital=cuotas_pgadas+cuotas_pendientes_pago+cuotas_pendientes_abono
            pago_adm=adm_pgadas+adm_pendientes_pago+adm_pendientes_abono

            nuevoMontoReeestructura=self.monto_financiamiento-pago_capital
            nuevoCuotaAdm=self.cuota_adm-pago_adm

            cuotasPagadas=self.contrato_id.tabla_amortizacion.filtered(lambda l: l.estado_pago=='pagado' and l.cuotaAdelantada==False)
            numcuotas_congeladas=self.contrato_id.tabla_amortizacion.filtered(lambda l:  l.cuota_capital == 0 and l.programado == 0)

            cuotasAdelantadas=self.contrato_id.tabla_amortizacion.filtered(lambda l: l.estado_pago=='pagado' and l.cuotaAdelantada==True)


            numeroCuotasPagadaTotal=len(cuotasAdelantadas) + len(cuotasPagadas)


            diferenciaPlazoAdendum= abs(self.contrato_id.plazo_meses.numero - self.plazo_meses.numero)

            numeroCuotasTotal=diferenciaPlazoAdendum

            intervalo_nuevo=self.plazo_meses.numero - numeroCuotasPagadaTotal + len(numcuotas_congeladas)-len(pagos_pendiente)-len(abonos)


            entrada=False
            #if self.env.user.id == self.rolpostventa.user_id.id:
            porcentaje_perm_adendum =  float(self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.porcentaje_perm_adendum'))
            #if self.env.user.id == self.rolAdjudicacion.user_id.id:
            #    porcentaje_perm_adendum =  float(self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.porcentaje_perm_adendum_postventa'))

            valor_porcentaje = (self.contrato_id.monto_financiamiento * porcentaje_perm_adendum)/100
            valor_menos_porc = self.contrato_id.monto_financiamiento - valor_porcentaje
            valor_mayor_porc = self.contrato_id.monto_financiamiento + valor_porcentaje
            # el monto de financiamiento nuevo debe ser menos o mas el 30% del monto de financiamiento q ya estaba

            # el monto de financiamiento nuevo debe ser menos o mas el 30% del monto de financiamiento q ya estaba
            if self.monto_financiamiento >= valor_menos_porc and self.monto_financiamiento <= valor_mayor_porc : 
                pass
            else:
                porcentaje_perm_adendum =  float(self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.porcentaje_perm_adendum'))
                self.nota="El valor del nuevo financiamiento excede o disminuye el monto máximo permitido configurado {0}%.".format(porcentaje_perm_adendum)
                if self.env.user.id == self.rolAdjudicacion.user_id.id:
                    pass
                elif self.env.user.id == self.rolpostventa.user_id.id:
                    self.state="aprobacion"
                else:
                    raise ValidationError("No tienes permiso para ejecutar esta acción")



            #aqui se muestran las cuotas que han sido pagadas ya sean por adelanto o no
            obj_contrato=self.env['contrato.estado.cuenta'].search([('contrato_id','=',self.contrato_id.id),('estado_pago','=','pagado')])
            lista_cuotapagadas=[]
            cont =0
            monto_finan_contrato= 0.00
            for l in obj_contrato:
                if l.programado!=0:
                    entrada=True
                cont+=1
                dct ={}
                dct['numero_cuota'] = cont
                dct['fecha']= l.fecha
                dct['cuota_capital']= l.cuota_capital
                dct['cuota_adm']= l.cuota_adm
                dct['iva_adm']= l.iva_adm
                dct['saldo']= l.saldo
                dct['adendum_id']= self.id
                dct['procesado']= True
                dct['estado_pago']= l.estado_pago
                #dct['currency_id']= l.currency_id
                lista_cuotapagadas.append(dct)

            obj_contrato_facturados=self.env['contrato.estado.cuenta'].search([('contrato_id','=',self.contrato_id.id),('factura_id','!=',False),('estado_pago','=','pendiente')])
            monto_finan_contrato= 0.00
            for l in obj_contrato_facturados:
                if l.programado!=0:
                    entrada=True
                cont+=1
                dct ={}
                dct['numero_cuota'] = cont
                dct['fecha']= l.fecha
                dct['cuota_capital']= l.cuota_capital
                dct['cuota_adm']= l.cuota_adm
                dct['iva_adm']= l.iva_adm
                dct['saldo']= l.saldo
                dct['adendum_id']= self.id
                dct['procesado']= True
                dct['estado_pago']= l.estado_pago
                #dct['currency_id']= l.currency_id
                lista_cuotapagadas.append(dct)

            obj_contrato_abonos=self.env['contrato.estado.cuenta'].search([('contrato_id','=',self.contrato_id.id),('factura_id','=',False),('ids_pagos','!=',False),('estado_pago','=','pendiente')])
            monto_finan_contrato= 0.00
            for l in obj_contrato_abonos:
                if l.programado!=0:
                    entrada=True
                cont+=1
                dct ={}
                dct['numero_cuota'] = cont
                dct['fecha']= l.fecha
                dct['cuota_capital']= l.cuota_capital
                dct['cuota_adm']= l.cuota_adm
                dct['iva_adm']= l.iva_adm
                dct['saldo']= l.saldo
                dct['contrato_id']= self.contrato_id.id
                dct['estado_pago']= l.estado_pago
                dct['procesado']= True
                lista_cuotapagadas.append(dct)

            #obj_contrato_detalle=self.env['contrato.estado.cuenta'].search([('contrato_id','=',self.contrato_id.id),('estado_pago','!=','pagado'),('factura_id','=',False),('ids_pagos','=',False)])
            #obj_contrato_detalle.unlink()

            
            if not entrada:
                if self.contrato_id.cuota_pago and self.contrato_id.tiene_cuota:
                    #self.contrato_id.monto_programado=self.monto_financiamiento*(self.contrato_id.porcentaje_programado/100)
                    #if self.contrato_id.tipo_de_contrato.code=='programo':
                    #    self.contrato_id.cuota_pago=self.plazo_meses.numero
                    nuevoMontoReeestructura=nuevoMontoReeestructura-self.contrato_id.monto_programado

            ####crear cuotas pagadas para listar segun el nuevo plazo o monto
            for a in lista_cuotapagadas:
                dct_tabla={ 'numero_cuota':a['numero_cuota'],
                        'fecha':a['fecha'],
                        'cuota_capital':a['cuota_capital'],
                        'cuota_adm':a['cuota_adm'],
                        'iva_adm':a['iva_adm'],
                        'saldo':a['saldo'],
                        'estado_pago':a['estado_pago'], 
                        'procesado': True                                              
                            }
                #self.env['tabla.adendum'].create(dct_tabla)
                lista_tabla.append(dct_tabla)
            #crear el nuevo estado de cuenta 

            cuota_adm_nueva=(nuevoCuotaAdm/int(intervalo_nuevo))
            cuota_adm_nueva=round(cuota_adm_nueva, 2)
            cuota_capital_nueva = (nuevoMontoReeestructura/int(intervalo_nuevo))
            cuota_capital_nueva =round(cuota_capital_nueva, 2)
            #raise ValidationError(str(cuota_capital_nueva)+'-- cuota_capital_nueva')
            contb=0
            #raise ValidationError('{0},{1}'.format(intervalo_nuevo,cont))
            for i in range(cont, int(intervalo_nuevo+cont)):
                contb +=1
                cuota_capital = (nuevoMontoReeestructura/int(intervalo_nuevo))
                cuota_capital =round(cuota_capital, 2)
                cuota_adm = self.monto_financiamiento * self.contrato_id.tasa_administrativa / 100 / 12
                iva = cuota_adm_nueva * 0.12

                #monto_finan_contrato+= cuota_capital
                cuota_asignada=i+1
                cuota_administrativa_neto= cuota_adm + iva
                saldo = cuota_capital+cuota_adm_nueva+iva
                dct_tabla={
                                                    'numero_cuota':i+1, 
                                                    'fecha':self.contrato_id.fecha_inicio_pago + relativedelta(months=i),
                                                    'cuota_capital':cuota_capital_nueva,
                                                    'cuota_adm':cuota_adm_nueva,
                                                    'iva_adm':iva,
                                                    'saldo':saldo,
                                                    #'saldo_cuota_capital':cuota_capital,
                                                    #'saldo_cuota_administrativa':cuota_adm,
                                                    #'saldo_iva':iva,
                                                    'procesado': False,
                                                        }
                lista_tabla.append(dct_tabla)               
            lista_ids=[]
            for prueba in lista_tabla:
                id_registro=self.env['tabla.adendum'].create(prueba) 
                lista_ids.append(id_registro.id)
            self.update({'tabla_adendum_id':[(6,0,lista_ids)]}) 


            ##########################################validar que la cuota capital este bien ####################################################
            monto_adm_contrato=sum(self.contrato_id.tabla_amortizacion.mapped('cuota_adm'))
            monto_adm_contrato= round(monto_adm_contrato,2)
            cuota_admin_contrato=self.cuota_adm

            vls_adm=[]
            if  monto_adm_contrato  > cuota_admin_contrato:
                valor_sobrante = monto_adm_contrato - cuota_admin_contrato 
                valor_sobrante = round(valor_sobrante,2)
                parte_decimal, parte_entera = math.modf(valor_sobrante)
                #raise ValidationError('{0},{1},{2}'.format(valor_sobrante,parte_decimal,parte_entera))
                if parte_decimal==0:
                    valor_a_restar=0
                elif parte_decimal >=1:
                    valor_a_restar= (valor_sobrante/parte_decimal)*0.1
                else:
                    valor_a_restar= (valor_sobrante/parte_decimal)*0.01
                #raise ValidationError('aaaaaaaaaaaaa{0}'.format(valor_a_restar)) 
                obj_contrato=self.env['tabla.adendum'].search([('adendum_id','=',self.id),('estado_pago','=','pendiente'),('procesado','=',False)] , order ='fecha desc')
                #raise ValidationError('aaaaaaaaaaaaa{0}'.format(obj_contrato))
                for c in obj_contrato:
                    if valor_sobrante != 0.00 or valor_sobrante != 0 or valor_sobrante != 0.0:
                        #if c.programado == 0.00 or c.programado == 0 or c.programado == 0.0:
                        c.update({
                            'cuota_adm': c.cuota_adm - valor_a_restar,
                            'adendum_id':self.id,
                        })
                        vls_adm.append(valor_sobrante)
                        valor_sobrante = valor_sobrante -valor_a_restar
                        valor_sobrante = round(valor_sobrante,2)
                        
                        
            if  monto_adm_contrato  < cuota_admin_contrato:
                valor_sobrante = cuota_admin_contrato  - monto_adm_contrato 
                valor_sobrante = round(valor_sobrante,2)
                parte_decimal, parte_entera = math.modf(valor_sobrante)
                if parte_decimal==0:
                    valor_a_restar=0
                elif parte_decimal >=1:
                    valor_a_restar= (valor_sobrante/parte_decimal)*0.1
                else:
                    valor_a_restar= (valor_sobrante/parte_decimal)*0.01

                obj_contrato=self.env['tabla.adendum'].search([('adendum_id','=',self.id),('estado_pago','=','pendiente'),('procesado','=',False)] , order ='fecha desc')

                for c in obj_contrato:
                    if valor_sobrante != 0.00 or valor_sobrante != 0 or valor_sobrante != 0.0:
                        #if c.programado == 0.00 or c.programado == 0 or c.programado == 0.0:
                        #raise ValidationError(str(valor_sobrante)+'--'+str(parte_decimal)+'----'+str(valor_a_restar))
                        c.update({
                            'cuota_adm': c.cuota_adm + valor_a_restar,
                            'adendum_id':self.id,
                        })  
                        vls_adm.append(valor_sobrante)
                        valor_sobrante = valor_sobrante -valor_a_restar
                        valor_sobrante = round(valor_sobrante,2)

            valor_sobrante=0
            valor_a_restar=0
            parte_decimal=0
            parte_entera=0
            monto_finan_contrato = sum(self.contrato_id.tabla_amortizacion.mapped('cuota_capital'))
            monto_finan_contrato = round(monto_finan_contrato,2)
            monto_financiamiento_contrato=self.monto_financiamiento
            if self.contrato_id.tiene_cuota:
                monto_financiamiento_contrato=self.monto_financiamiento-self.contrato_id.monto_programado

            vls=[]
            if  monto_finan_contrato  > monto_financiamiento_contrato:
                valor_sobrante = monto_finan_contrato - monto_financiamiento_contrato 
                valor_sobrante = round(valor_sobrante,2)
                parte_decimal, parte_entera = math.modf(valor_sobrante)
                #raise ValidationError('{0},{1},{2}'.format(valor_sobrante,parte_decimal,parte_entera))
                if parte_decimal==0:
                    valor_a_restar=0
                elif parte_decimal >=1:
                    valor_a_restar= (valor_sobrante/parte_decimal)*0.1
                else:
                    valor_a_restar= (valor_sobrante/parte_decimal)*0.01
                #raise ValidationError('aaaaaaaaaaaaa{0}'.format(valor_a_restar)) 
                obj_contrato=self.env['tabla.adendum'].search([('adendum_id','=',self.id),('estado_pago','=','pendiente'),('procesado','=',False)] , order ='fecha desc')
                #raise ValidationError('aaaaaaaaaaaaa{0}'.format(obj_contrato))
                for c in obj_contrato:
                    if valor_sobrante != 0.00 or valor_sobrante != 0 or valor_sobrante != 0.0:
                        #if c.programado == 0.00 or c.programado == 0 or c.programado == 0.0:
                        c.update({
                            'cuota_capital': c.cuota_capital - valor_a_restar,
                            'adendum_id':self.id,
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

                obj_contrato=self.env['tabla.adendum'].search([('adendum_id','=',self.contrato_id.id),('estado_pago','=','pendiente'),('procesado','=',False)] , order ='fecha desc')

                for c in obj_contrato:
                    if valor_sobrante != 0.00 or valor_sobrante != 0 or valor_sobrante != 0.0:
                        #if c.programado == 0.00 or c.programado == 0 or c.programado == 0.0:
                        #raise ValidationError(str(valor_sobrante)+'--'+str(parte_decimal)+'----'+str(valor_a_restar))
                        c.update({
                            'cuota_capital': c.cuota_capital + valor_a_restar,
                            'adendum_id':self.id,
                        })  
                        vls.append(valor_sobrante)
                        valor_sobrante = valor_sobrante -valor_a_restar
                        valor_sobrante = round(valor_sobrante,2)
            ##si esta ejecutado se ocultara el boton de validar                  
            #self.ejecutado =True
            #asignar nuevos valores 
            #self.contrato_id.monto_financiamiento = self.monto_financiamiento
            cuota_inscripcion_anterior=self.contrato_id.valor_inscripcion
            nuevo_valor_inscripcion=self.monto_financiamiento*0.05
            if nuevo_valor_inscripcion>cuota_inscripcion_anterior:
                self.valor_inscripcion=self.monto_financiamiento*0.05
            ##crear_nueva factura
            #self.contrato_id.plazo_meses =self.plazo_meses.id
            #self.contrato_id.cuota_capital=cuota_capital_nueva
            #self.contrato_id.ejecutado = True
            #self.env['contrato.adendum'].create({
            #                'contrato_id': self.contrato_id.id,
            #                'socio_id':self.socio_id.id,
            #                'monto_financiamiento':self.monto_financiamiento,
            #                'plazo_meses':self.plazo_meses.id,
            #                'observacion':self.observacion,
            #                #'currency_id':self.contrato_id.id,
            #            })  

            




































































































    def ejecutar_cambio(self,):
        if self.env.user.id == self.rolpostventa.user_id.id and self.env.user.id != self.rolAdjudicacion.user_id.id:
            porcentaje_perm_adendum_postventa =  float(self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.porcentaje_perm_adendum_postventa'))
            valor_porcentaje_post = (self.contrato_id.monto_financiamiento * porcentaje_perm_adendum_postventa)/100
            valor_menos_porc_post = self.contrato_id.monto_financiamiento - valor_porcentaje_post
            porcentaje_perm_adendum =  float(self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.porcentaje_perm_adendum'))
            valor_porcentaje_perm = (self.contrato_id.monto_financiamiento * porcentaje_perm_adendum)/100
            valor_menor_porc_pperm = self.contrato_id.monto_financiamiento - valor_porcentaje_perm

            if self.monto_financiamiento < valor_menos_porc_post or self.monto_financiamiento<valor_menor_porc_pperm:
                self.state="aprobacion"
                return True
        elif self.env.user.id != self.rolpostventa.user_id.id and self.env.user.id != self.rolAdjudicacion.user_id.id:
            raise ValidationError("No tiene permiso para realizar esta acción")
        if  self.contrato_id.ejecutado:
            raise ValidationError("El contrato solo puede realizar un adendum")
        elif self.contrato_id.state !='activo':
            raise ValidationError("El contrato solo puede realizar un adendum en estado activo")
        else:

            obj=self.contrato_id

            pagos=self.contrato_id.tabla_amortizacion.filtered(lambda l: l.estado_pago=='pagado')
            cuotas_pgadas=sum(pagos.mapped("cuota_capital"))
            adm_pgadas=sum(pagos.mapped("cuota_adm"))
            pagos_pendiente=self.contrato_id.tabla_amortizacion.filtered(lambda l: l.estado_pago!='pagado' and l.factura_id)
            cuotas_pendientes_pago=sum(pagos_pendiente.mapped("cuota_capital"))
            adm_pendientes_pago=sum(pagos_pendiente.mapped("cuota_adm"))
            abonos=self.contrato_id.tabla_amortizacion.filtered(lambda l: l.estado_pago!='pagado' and l.monto_pagado>0 and not l.factura_id)
            cuotas_pendientes_abono=sum(abonos.mapped("cuota_capital"))
            adm_pendientes_abono=sum(abonos.mapped("cuota_adm"))
            pago_capital=cuotas_pgadas+cuotas_pendientes_pago+cuotas_pendientes_abono
            pago_adm=adm_pgadas+adm_pendientes_pago+adm_pendientes_abono

            nuevoMontoReeestructura=self.monto_financiamiento-pago_capital
            nuevoCuotaAdm=self.cuota_adm-pago_adm

            cuotasPagadas=self.contrato_id.tabla_amortizacion.filtered(lambda l: l.estado_pago=='pagado' and l.cuotaAdelantada==False)
            numcuotas_congeladas=self.contrato_id.tabla_amortizacion.filtered(lambda l:  l.cuota_capital == 0 and l.programado == 0)

            cuotasAdelantadas=self.contrato_id.tabla_amortizacion.filtered(lambda l: l.estado_pago=='pagado' and l.cuotaAdelantada==True)


            numeroCuotasPagadaTotal=len(cuotasAdelantadas) + len(cuotasPagadas)


            diferenciaPlazoAdendum= abs(self.contrato_id.plazo_meses.numero - self.plazo_meses.numero)

            numeroCuotasTotal=diferenciaPlazoAdendum

            intervalo_nuevo=self.plazo_meses.numero - numeroCuotasPagadaTotal + len(numcuotas_congeladas)-len(pagos_pendiente)-len(abonos)
            #raise ValidationError('{0}'.format(intervalo_nuevo))
            #raise ValidationError('{0},{1},{2},{3}'.format(numeroCuotasPagadaTotal,len(abonos),intervalo_nuevo,self.plazo_meses.numero))
            #lleno lista con estado de cuenta anterior 
            estado_cuenta_anterior=[]
            for e in self.contrato_id.estado_de_cuenta_ids:
                dct ={}
                dct['numero_cuota'] = e.numero_cuota
                dct['fecha']= e.fecha
                dct['cuota_capital']= e.cuota_capital
                dct['cuota_adm']= e.cuota_adm
                dct['iva_adm']= e.iva_adm
                dct['saldo']= e.saldo
                dct['contrato_id']= self.contrato_id.id
                dct['estado_pago']= e.estado_pago
                dct['cuotaAdelantada']= e.cuotaAdelantada
                dct['fecha_pagada']= e.fecha_pagada
                dct['seguro']= e.seguro
                dct['rastreo']= e.rastreo
                dct['factura_id']= e.factura_id.id 
                estado_cuenta_anterior.append(dct)


            entrada=False
            if self.env.user.id == self.rolpostventa.user_id.id:
                porcentaje_perm_adendum =  float(self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.porcentaje_perm_adendum_postventa'))
            if self.env.user.id == self.rolAdjudicacion.user_id.id:
                porcentaje_perm_adendum =  float(self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.porcentaje_perm_adendum'))

            #porcentaje_perm_adendum =  float(self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.porcentaje_perm_adendum'))
            valor_porcentaje = (self.contrato_id.monto_financiamiento * porcentaje_perm_adendum)/100
            valor_menos_porc = self.contrato_id.monto_financiamiento - valor_porcentaje
            valor_mayor_porc = self.contrato_id.monto_financiamiento + valor_porcentaje
            # el monto de financiamiento nuevo debe ser menos o mas el 30% del monto de financiamiento q ya estaba
            if self.monto_financiamiento >= valor_menos_porc and self.monto_financiamiento <= valor_mayor_porc : 
                pass
            else:
                porcentaje_perm_adendum =  float(self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.porcentaje_perm_adendum'))
                self.nota="El valor del nuevo financiamiento excede o disminuye el monto máximo permitido configurado {0}%.".format(porcentaje_perm_adendum)
                if self.env.user.id == self.rolAdjudicacion.user_id.id:
                    pass
                elif self.env.user.id == self.rolpostventa.user_id.id:
                    self.state="aprobacion"
                    return True
                else:
                    raise ValidationError("No tienes permiso para ejecutar esta acción")

                #aqui se muestran las cuotas que han sido pagadas ya sean por adelanto o no
            obj_contrato=self.env['contrato.estado.cuenta'].search([('contrato_id','=',self.contrato_id.id),('estado_pago','=','pagado')])
            lista_cuotapagadas=[]
            cont =0
            monto_finan_contrato= 0.00
            for l in obj_contrato:
                if l.programado!=0:
                    entrada=True
                cont+=1
                dct ={}
                dct['numero_cuota'] = cont
                dct['fecha']= l.fecha
                dct['cuota_capital']= l.cuota_capital
                dct['cuota_adm']= l.cuota_adm
                dct['iva_adm']= l.iva_adm
                dct['saldo']= l.saldo
                dct['contrato_id']= self.contrato_id.id
                dct['estado_pago']= l.estado_pago
                dct['currency_id']= l.currency_id
                lista_cuotapagadas.append(dct)

            obj_contrato_facturados=self.env['contrato.estado.cuenta'].search([('contrato_id','=',self.contrato_id.id),('factura_id','!=',False),('estado_pago','=','pendiente')])
            monto_finan_contrato= 0.00
            for l in obj_contrato_facturados:
                if l.programado!=0:
                    entrada=True
                cont+=1
                dct ={}
                dct['numero_cuota'] = cont
                dct['fecha']= l.fecha
                dct['cuota_capital']= l.cuota_capital
                dct['cuota_adm']= l.cuota_adm
                dct['iva_adm']= l.iva_adm
                dct['saldo']= l.saldo
                dct['contrato_id']= self.contrato_id.id
                dct['estado_pago']= l.estado_pago
                dct['currency_id']= l.currency_id
                lista_cuotapagadas.append(dct)

            obj_contrato_abonos=self.env['contrato.estado.cuenta'].search([('contrato_id','=',self.contrato_id.id),('factura_id','=',False),('ids_pagos','!=',False),('estado_pago','=','pendiente')])
            monto_finan_contrato= 0.00
            for l in obj_contrato_abonos:
                if l.programado!=0:
                    entrada=True
                cont+=1
                dct ={}
                dct['numero_cuota'] = cont
                dct['fecha']= l.fecha
                dct['cuota_capital']= l.cuota_capital
                dct['cuota_adm']= l.cuota_adm
                dct['iva_adm']= l.iva_adm
                dct['saldo']= l.saldo
                dct['contrato_id']= self.contrato_id.id
                dct['estado_pago']= l.estado_pago
                dct['currency_id']= l.currency_id
                lista_cuotapagadas.append(dct)

            obj_contrato_detalle=self.env['contrato.estado.cuenta'].search([('contrato_id','=',self.contrato_id.id),('estado_pago','!=','pagado'),('factura_id','=',False),('ids_pagos','=',False)])
            obj_contrato_detalle.unlink()

            
            if not entrada:
                if self.contrato_id.cuota_pago and self.contrato_id.tiene_cuota:
                    self.contrato_id.monto_programado=self.monto_financiamiento*(self.contrato_id.porcentaje_programado/100)
                    if self.contrato_id.tipo_de_contrato.code=='programo':
                        self.contrato_id.cuota_pago=self.plazo_meses.numero
                    nuevoMontoReeestructura=nuevoMontoReeestructura-self.contrato_id.monto_programado

            ####crear cuotas pagadas para listar segun el nuevo plazo o monto
            #for a in lista_cuotapagadas:
            #    self.env['contrato.estado.cuenta'].create({
            #                                        'numero_cuota':a['numero_cuota'],
            #                                        'fecha':a['fecha'],
            #                                        'cuota_capital':a['cuota_capital'],
            #                                        'cuota_adm':a['cuota_adm'],
            #                                        'iva_adm':a['iva_adm'],
            #                                        'saldo':a['saldo'],
            #                                        'contrato_id':a['contrato_id'],
            #                                        'estado_pago':a['estado_pago'],                                                
            #                                            })
            #crear el nuevo estado de cuenta 

            cuota_adm_nueva=(nuevoCuotaAdm/int(intervalo_nuevo))
            cuota_adm_nueva=round(cuota_adm_nueva, 2)
            cuota_capital_nueva = (nuevoMontoReeestructura/int(intervalo_nuevo))
            cuota_capital_nueva =round(cuota_capital_nueva, 2)
            #raise ValidationError(str(cuota_capital_nueva)+'-- cuota_capital_nueva')
            contb=0
            #raise ValidationError('{0},{1}'.format(intervalo_nuevo,cont))
            for i in range(cont, int(intervalo_nuevo+cont)):
                contb +=1
                cuota_capital = (nuevoMontoReeestructura/int(intervalo_nuevo))
                cuota_capital =round(cuota_capital, 2)
                cuota_adm = self.monto_financiamiento * self.contrato_id.tasa_administrativa / 100 / 12
                iva = cuota_adm_nueva * 0.12

                #monto_finan_contrato+= cuota_capital
                cuota_asignada=i+1
                cuota_administrativa_neto= cuota_adm + iva
                saldo = cuota_capital+cuota_adm_nueva+iva
                self.env['contrato.estado.cuenta'].create({
                                                    'numero_cuota':i+1, 
                                                    'fecha':self.contrato_id.fecha_inicio_pago + relativedelta(months=i),
                                                    'cuota_capital':cuota_capital_nueva,
                                                    'cuota_adm':cuota_adm_nueva,
                                                    'iva_adm':iva,
                                                    'saldo':saldo,
                                                    'saldo_cuota_capital':cuota_capital,
                                                    'saldo_cuota_administrativa':cuota_adm,
                                                    'saldo_iva':iva,
                                                    'contrato_id':self.contrato_id.id,                                      
                                                        })
               

                if self.contrato_id.tiene_cuota and not entrada:

                    if cuota_asignada==self.contrato_id.cuota_pago:
                        self.env['contrato.estado.cuenta'].create({'numero_cuota':self.contrato_id.cuota_pago,
                                                                            'contrato_id':self.contrato_id.id,
                                                                            'cuota_capital':0,
                                                                            'cuota_adm':0,
                                                                            'iva_adm':0,
                                                                            'saldo':self.contrato_id.monto_programado,
                                                                            'saldo_cuota_capital':0,
                                                                            'saldo_cuota_administrativa':0,
                                                                            'saldo_iva':0,
                                                                            'fecha':self.contrato_id.fecha_inicio_pago + relativedelta(months=i) + relativedelta(months=i),
                                                                            'saldo_programado':self.contrato_id.monto_programado,
                                                                            'programado':self.contrato_id.monto_programado})


            #si se creo el nuevo estado de cuenta agregar el estado de cuenta anterior a las tablas de bitacora
            obj_estado_cuenta_nuevo=self.env['contrato.estado.cuenta'].search([('contrato_id','=',self.contrato_id.id)])
            if len(obj_estado_cuenta_nuevo) >0:
                obj_contrato_historico=self.env['contrato.estado.cuenta.historico.cabecera'].create({
                                                    #'numero_cuota':self.contrato_id.numero_cuota,
                                                    'contrato_id':self.contrato_id.id,
                                                    'motivo_adendum':' adendum',
                                                    'cuota_capital':cuota_capital_nueva,
                                                    'monto_financiamiento':self.monto_financiamiento,
                                                    'plazo_meses':self.plazo_meses.id,
                                                    'cuota_capital_anterior':self.contrato_id.cuota_capital,
                                                    'monto_financiamiento_anterior':self.contrato_id.monto_financiamiento,
                                                    'plazo_meses_anterior':self.contrato_id.plazo_meses.id,
                                                    #'currency_id':self.contrato_id.currency_id.id,                                                
                                                        })            


                ####Crear bitacora detalle de estado de cuenta 
                obj_estado_cuenta_cabecera=self.env['contrato.estado.cuenta.historico.cabecera'].search([('contrato_id','=',self.contrato_id.id)])
                if len(obj_estado_cuenta_cabecera) >0:
                    #raise ValidationError(type(obj_estado_cuenta_cabecera.id)+'--obj_estado_cuenta_cabecera.id')
                    for cta_ant in estado_cuenta_anterior:
                        self.env['contrato.estado.cuenta.historico.detalle'].create({
                                                            'numero_cuota':cta_ant['numero_cuota'],
                                                            'fecha':cta_ant['fecha'] ,
                                                            'cuota_capital':cta_ant['cuota_capital'],
                                                            'cuota_adm':cta_ant['cuota_adm'],
                                                            'iva_adm':cta_ant['iva_adm'],
                                                            'saldo':cta_ant['saldo'],
                                                            'estado_pago':cta_ant['estado_pago'], 
                                                            'cuotaAdelantada':cta_ant['cuotaAdelantada'] ,  
                                                            'seguro':cta_ant['seguro'],  
                                                            'fecha_pagada':cta_ant['fecha_pagada'] ,  
                                                            'rastreo':cta_ant['rastreo'],  
                                                            'factura_id':cta_ant['factura_id'] ,#or None,          
                                                            'contrato_id':obj_contrato_historico.id, 
                                                                })


            ##########################################validar que la cuota capital este bien ####################################################
            monto_adm_contrato=sum(self.contrato_id.tabla_amortizacion.mapped('cuota_adm'))
            monto_adm_contrato= round(monto_adm_contrato,2)
            cuota_admin_contrato=self.cuota_adm

            vls_adm=[]
            if  monto_adm_contrato  > cuota_admin_contrato:
                valor_sobrante = monto_adm_contrato - cuota_admin_contrato 
                valor_sobrante = round(valor_sobrante,2)
                parte_decimal, parte_entera = math.modf(valor_sobrante)
                #raise ValidationError('{0},{1},{2}'.format(valor_sobrante,parte_decimal,parte_entera))
                if parte_decimal==0:
                    valor_a_restar=0
                elif parte_decimal >=1:
                    valor_a_restar= (valor_sobrante/parte_decimal)*0.1
                else:
                    valor_a_restar= (valor_sobrante/parte_decimal)*0.01
                #raise ValidationError('aaaaaaaaaaaaa{0}'.format(valor_a_restar)) 
                obj_contrato=self.env['contrato.estado.cuenta'].search([('contrato_id','=',self.contrato_id.id),('estado_pago','=','pendiente'),('factura_id','=',False)] , order ='fecha desc')
                #raise ValidationError('aaaaaaaaaaaaa{0}'.format(obj_contrato))
                for c in obj_contrato:
                    if valor_sobrante != 0.00 or valor_sobrante != 0 or valor_sobrante != 0.0:
                        if c.programado == 0.00 or c.programado == 0 or c.programado == 0.0:
                            c.update({
                                'cuota_adm': c.cuota_adm - valor_a_restar,
                                'contrato_id':self.contrato_id.id,
                            })
                            vls_adm.append(valor_sobrante)
                            valor_sobrante = valor_sobrante -valor_a_restar
                            valor_sobrante = round(valor_sobrante,2)
                        
                        
            if  monto_adm_contrato  < cuota_admin_contrato:
                valor_sobrante = cuota_admin_contrato  - monto_adm_contrato 
                valor_sobrante = round(valor_sobrante,2)
                parte_decimal, parte_entera = math.modf(valor_sobrante)
                if parte_decimal==0:
                    valor_a_restar=0
                elif parte_decimal >=1:
                    valor_a_restar= (valor_sobrante/parte_decimal)*0.1
                else:
                    valor_a_restar= (valor_sobrante/parte_decimal)*0.01

                obj_contrato=self.env['contrato.estado.cuenta'].search([('contrato_id','=',self.contrato_id.id),('estado_pago','=','pendiente'),('factura_id','=',False)] , order ='fecha desc')

                for c in obj_contrato:
                    if valor_sobrante != 0.00 or valor_sobrante != 0 or valor_sobrante != 0.0:
                        if c.programado == 0.00 or c.programado == 0 or c.programado == 0.0:
                        #raise ValidationError(str(valor_sobrante)+'--'+str(parte_decimal)+'----'+str(valor_a_restar))
                            c.update({
                                'cuota_adm': c.cuota_adm + valor_a_restar,
                                'contrato_id':self.contrato_id.id,
                            })  
                            vls_adm.append(valor_sobrante)
                            valor_sobrante = valor_sobrante -valor_a_restar
                            valor_sobrante = round(valor_sobrante,2)

            valor_sobrante=0
            valor_a_restar=0
            parte_decimal=0
            parte_entera=0
            monto_finan_contrato = sum(self.contrato_id.tabla_amortizacion.mapped('cuota_capital'))
            monto_finan_contrato = round(monto_finan_contrato,2)
            monto_financiamiento_contrato=self.monto_financiamiento
            if self.contrato_id.tiene_cuota:
                monto_financiamiento_contrato=self.monto_financiamiento-self.contrato_id.monto_programado

            vls=[]
            if  monto_finan_contrato  > monto_financiamiento_contrato:
                valor_sobrante = monto_finan_contrato - monto_financiamiento_contrato 
                valor_sobrante = round(valor_sobrante,2)
                parte_decimal, parte_entera = math.modf(valor_sobrante)
                #raise ValidationError('{0},{1},{2}'.format(valor_sobrante,parte_decimal,parte_entera))
                if parte_decimal==0:
                    valor_a_restar=0
                elif parte_decimal >=1:
                    valor_a_restar= (valor_sobrante/parte_decimal)*0.1
                else:
                    valor_a_restar= (valor_sobrante/parte_decimal)*0.01
                #raise ValidationError('aaaaaaaaaaaaa{0}'.format(valor_a_restar)) 
                obj_contrato=self.env['contrato.estado.cuenta'].search([('contrato_id','=',self.contrato_id.id),('estado_pago','=','pendiente'),('factura_id','=',False)] , order ='fecha desc')
                #raise ValidationError('aaaaaaaaaaaaa{0}'.format(obj_contrato))
                for c in obj_contrato:
                    if valor_sobrante != 0.00 or valor_sobrante != 0 or valor_sobrante != 0.0:
                        if c.programado == 0.00 or c.programado == 0 or c.programado == 0.0:
                            c.update({
                                'cuota_capital': c.cuota_capital - valor_a_restar,
                                'contrato_id':self.contrato_id.id,
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

                obj_contrato=self.env['contrato.estado.cuenta'].search([('contrato_id','=',self.contrato_id.id),('estado_pago','=','pendiente'),('factura_id','=',False)] , order ='fecha desc')

                for c in obj_contrato:
                    if valor_sobrante != 0.00 or valor_sobrante != 0 or valor_sobrante != 0.0:
                        if c.programado == 0.00 or c.programado == 0 or c.programado == 0.0:
                        #raise ValidationError(str(valor_sobrante)+'--'+str(parte_decimal)+'----'+str(valor_a_restar))
                            c.update({
                                'cuota_capital': c.cuota_capital + valor_a_restar,
                                'contrato_id':self.contrato_id.id,
                            })  
                            vls.append(valor_sobrante)
                            valor_sobrante = valor_sobrante -valor_a_restar
                            valor_sobrante = round(valor_sobrante,2)
            ##si esta ejecutado se ocultara el boton de validar                  
            self.ejecutado =True
            #asignar nuevos valores 
            self.contrato_id.monto_financiamiento = self.monto_financiamiento
            cuota_inscripcion_anterior=self.contrato_id.valor_inscripcion
            nuevo_valor_inscripcion=self.monto_financiamiento*0.05
            if nuevo_valor_inscripcion>cuota_inscripcion_anterior:
                self.contrato_id.valor_inscripcion=self.monto_financiamiento*0.05
            ##crear_nueva factura
            self.contrato_id.plazo_meses =self.plazo_meses.id
            self.contrato_id.cuota_capital=cuota_capital_nueva
            self.contrato_id.ejecutado = True
            self.env['contrato.adendum'].create({
                            'contrato_id': self.contrato_id.id,
                            'socio_id':self.socio_id.id,
                            'monto_financiamiento':self.monto_financiamiento,
                            'plazo_meses':self.plazo_meses.id,
                            'observacion':self.observacion,
                            #'currency_id':self.contrato_id.id,
                        })  
            self.state="procesado"

                
                #raise ValidationError("El monto de financiamiento no esta en el rango permitido")
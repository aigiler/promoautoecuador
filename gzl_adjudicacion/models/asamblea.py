from odoo import api, fields, models
import json
from odoo.exceptions import UserError, ValidationError
from datetime import date, timedelta
import datetime



class ParticipantesAsamblea(models.Model):
    _name = 'participantes.asamblea.clientes'
    _description = 'Participantes de la Asamblea'
    

    currency_id = fields.Many2one(
        'res.currency', readonly=True, default=lambda self: self.env.company.currency_id)    
    asamblea_id = fields.Many2one('asamblea')
    grupo_cliente = fields.Many2one('grupo.adjudicado',related="asamblea_id.grupo_cliente")
    contrato_id = fields.Many2one('contrato', string="Contrato")
    tipo_asamblea = fields.Many2one('tipo.contrato.adjudicado', string='Tipo',track_visibility='onchange',related="contrato_id.tipo_de_contrato")
    adjudicado_id = fields.Many2one('res.partner', related="contrato_id.cliente",string="Nombre")

    plazo_meses = fields.Many2one('numero.meses',related="contrato_id.plazo_meses")
    monto_financiamiento = fields.Monetary(related='contrato_id.monto_financiamiento',string='Monto Financiamiento', currency_field='currency_id', track_visibility='onchange')
    cuota=fields.Float("Cuota",compute="obtener_valor_cuota",store=True)
    monto_programado=fields.Float("Monto Programado",related="contrato_id.porcentaje_programado",store=True)
    cuota_programada=fields.Float("Cuota Programada(%)", related="contrato_id.cuota_pago", store=True)
    licitacion_valor=fields.Float("Licitación")
    cuotas_licitadas=fields.Integer("Cuotas Licitadas")
    cuotas_pagadas=fields.Integer(related="contrato_id.numero_cuotas_pagadas",string="Cuotas Pagadas")
    total_cuotas=fields.Integer("Total")
    cuota_capital=fields.Monetary("Cuota Capital", currency_field='currency_id',related="contrato_id.cuota_capital")
    total_or=fields.Float("O.R")
    seleccionado=fields.Boolean(string="Seleccionado", dafault=False)
    nota=fields.Selection(string="Nota",selection=[
        ('GANADOR', 'GANADOR'),
        ('SUPLENTE', 'SUPLENTE')]
        )
    entrega_vehiculo_id = fields.Many2one('entrega.vehiculo',string="Solicitud de entrega vehículo" ,track_visibility='onchange')

    @api.onchange("seleccionado")
    def validar_asignación(self):
        for l in self:
            if l.seleccionado:
                pass
            else:
                l.nota=""
        l.asamblea_id.calcular_licitacion()

    @api.onchange("contrato_id")
    @api.constrains("contrato_id")
    def obtener_valor_cuota(self):
        cuota=0
        licitacion_valor=0
        for l in self:
            if l.contrato_id:
                cuota=l.contrato_id.cuota_adm+l.contrato_id.iva_administrativo+l.contrato_id.cuota_capital
            l.cuota=cuota



    def iniciar_proceso(self):
        entrega_vehiculo=self.env['entrega.vehiculo']
        for l in self:
            if not l.entrega_vehiculo_id:
                rol_asignado=self.env.ref('gzl_adjudicacion.tipo_rol3')
                entrega=entrega_vehiculo.create({'asamblea_id':l.asamblea_id.id,
                                        'nombreSocioAdjudicado':l.adjudicado_id.id,
                                        'contrato_id':l.contrato_id.id,
                                        'rolAsignado':rol_asignado.id ,
                                        'montoEnviadoAsamblea':l.monto_financiamiento})
                l.contrato_id.entrega_vehiculo_id=entrega.id
                l.entrega_vehiculo_id=entrega.id


    @api.onchange("licitacion_valor")
    @api.constrains("licitacion_valor")
    def obtener_cuotas_licitadas(self):
        cuotas_licitadas=0
        for l in self:
            if l.licitacion_valor and l.cuota:
                cuotas_licitadas=l.licitacion_valor/l.cuota
            l.cuotas_licitadas=cuotas_licitadas
            l.total_or=cuotas_licitadas*l.cuota_capital

    @api.onchange("cuotas_licitadas","cuotas_pagadas")
    @api.constrains("cuotas_licitadas","cuotas_pagadas","contrato_id")
    def calcular_total(self):
        total=0
        total=self.cuotas_pagadas+self.cuotas_licitadas
        self.total_cuotas=total

class ParticipantesEvaluaciónAsamblea(models.Model):
    _name = 'participantes.evaluacion.asamblea.clientes'
    _description = 'Participantes de la Asamblea Evaluación'
    
    currency_id = fields.Many2one(
        'res.currency', readonly=True, default=lambda self: self.env.company.currency_id)    
    asamblea_id = fields.Many2one('asamblea')
    grupo_cliente = fields.Many2one('grupo.adjudicado',related="asamblea_id.grupo_cliente")
    contrato_id = fields.Many2one('contrato', string="Contrato")
    adjudicado_id = fields.Many2one('res.partner', string="Nombre",related="contrato_id.cliente")
    monto_financiamiento = fields.Monetary(related='contrato_id.monto_financiamiento',string='Monto Financiamiento', currency_field='currency_id', track_visibility='onchange')
    cuotas_pagadas=fields.Integer(related="contrato_id.numero_cuotas_pagadas",string="Cuotas Pagadas")
    seleccionado=fields.Boolean(string="Seleccionado", dafault=False)
    nota=fields.Selection(string="Nota",selection=[
        ('GANADOR', 'GANADOR'),
        ('SUPLENTE', 'SUPLENTE')]
        )
    entrega_vehiculo_id = fields.Many2one('entrega.vehiculo',string="Solicitud de entrega vehículo" ,track_visibility='onchange')


    def iniciar_proceso(self):
        entrega_vehiculo=self.env['entrega.vehiculo']
        for l in self:
            if not l.entrega_vehiculo_id:
                rol_asignado=self.env.ref('gzl_adjudicacion.tipo_rol3')
                entrega=entrega_vehiculo.create({'asamblea_id':l.asamblea_id.id,
                                        'nombreSocioAdjudicado':l.adjudicado_id.id,
                                        'contrato_id':l.contrato_id.id,
                                        'rolAsignado':rol_asignado.id ,
                                        'montoEnviadoAsamblea':l.monto_financiamiento})
                l.contrato_id.entrega_vehiculo_id=entrega.id
                l.entrega_vehiculo_id=entrega.id

    @api.onchange("seleccionado")
    def validar_asignación(self):
        for l in self:
            if l.seleccionado:
                pass
            else:
                l.nota=""
        l.asamblea_id.calcular_licitacion()

class Asamblea(models.Model):
    _name = 'asamblea'
    _description = 'Proceso de Asamblea'
    _rec_name = 'secuencia'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    descripcion = fields.Text('Descripcion',  required=True,track_visibility='onchange')
    active = fields.Boolean(default=True,track_visibility='onchange')
    fecha_inicio = fields.Datetime(String='Fecha Inicio',track_visibility='onchange')
    fecha_fin = fields.Datetime(String='Fecha Fin',track_visibility='onchange')
    secuencia = fields.Char(index=True)
    grupo_cliente = fields.Many2one('grupo.adjudicado')
    ejecutado=fields.Boolean(default=False)
    integrantes_licitacion_id=fields.One2many('participantes.asamblea.clientes', 'asamblea_id',track_visibility='onchange')
    integrantes_evaluacion_id=fields.One2many('participantes.evaluacion.asamblea.clientes', 'asamblea_id',track_visibility='onchange')
    state = fields.Selection(selection=[
            ('borrador', 'Borrador'),
            ('inicio', 'Ingreso de Socios'),
            ('en_curso', 'En Curso'),
            ('pre_cierre', 'Pre cierre'),
            ('cerrado', 'Cerrado')
            ], string='Estado', copy=False, tracking=True, default='inicio',track_visibility='onchange')
    currency_id = fields.Many2one(
        'res.currency', readonly=True, default=lambda self: self.env.company.currency_id)
    licitaciones=fields.Monetary(string='Licitaciones', currency_field='currency_id', track_visibility='onchange')
    evaluacion=fields.Monetary(string='Evaluación', currency_field='currency_id', track_visibility='onchange')
    fondos_mes=fields.Monetary(string='Fondos del Mes', currency_field='currency_id', track_visibility='onchange')
    adjudicados = fields.Monetary(string='Adjudicados', currency_field='currency_id', track_visibility='onchange')
    recuperacionCartera = fields.Monetary(string='Recuperación de Cartera', currency_field='currency_id', track_visibility='onchange')
    invertir_licitacion=fields.Monetary(string='Invertir-Licitacion', currency_field='currency_id', track_visibility='onchange')
    saldo=fields.Monetary(string='Saldo', compute="obtener_saldo",currency_field='currency_id', track_visibility='onchange')

    programo=fields.Monetary(string='Plan Programo', currency_field='currency_id', track_visibility='onchange')
    
    monto_financiamiento=fields.Monetary(string='Monto', currency_field='currency_id', track_visibility='onchange')
    

    @api.model
    def create(self, vals):
        vals['secuencia'] = self.env['ir.sequence'].next_by_code('asamblea')
        res = self.env['res.config.settings'].sudo(1).search([], limit=1, order="id desc")
        return super(Asamblea, self).create(vals)

    @api.constrains('secuencia')
    def constrains_valor_por_defecto(self): 
        res = self.env['res.config.settings'].sudo(1).search([], limit=1, order="id desc")
    
    def obtener_integrantes(self):
        for l in self:
            lista_evaluacion=[]
            lista_licitacion=[]
            if l.grupo_cliente:
                contratos_ids=self.env["contrato"].search([('numero_cuotas_pagadas','>',0),('en_mora','=',False),('state','=','ACTIVADO'),('grupo','=',self.grupo_cliente.id)],order='numero_cuotas_pagadas desc')
                for x in contratos_ids:
                    
                    tupla={
                           'contrato_id': x.id,
                          }
                    lista_licitacion.append(tupla)
                    if x.tipo_de_contrato.name=='Evaluación':
                        tupla={
                           'contrato_id': x.id,}
                        lista_evaluacion.append(tupla)
            lista_evaluacion_ids=[]
            lista_licitacion_ids=[]
            for prueba in lista_evaluacion:
                id_registro=self.env['participantes.evaluacion.asamblea.clientes'].create(prueba) 
                lista_evaluacion_ids.append(id_registro.id)
            for prueba in lista_licitacion:
                id_registro=self.env['participantes.asamblea.clientes'].create(prueba) 
                lista_licitacion_ids.append(id_registro.id)
            self.update({'integrantes_evaluacion_id':[(6,0,lista_evaluacion_ids)]}) 
            self.update({'integrantes_licitacion_id':[(6,0,lista_licitacion_ids)]}) 


    @api.onchange("integrantes_licitacion_id","integrantes_evaluacion_id")
    def calcular_valores(self):
        self.calcular_licitacion()

    def obtener_ganadores_suplentes(self):
        for l in self:
            parametros_licitacion=self.env['tipo.asamblea'].search([('name','=','licitacion')],limit=1)
            parametros_exacto=self.env['tipo.asamblea'].search([('name','=','exacto')],limit=1)
            parametros_evaluacion=self.env['tipo.asamblea'].search([('name','=','evaluacion')],limit=1)
            parametros_programo=self.env['tipo.asamblea'].search([('name','=','programo')],limit=1)

            saldoActual=l.saldo

            if saldoActual:
                valorNeto=saldoActual
                if parametros_licitacion:

                    numero_ganadores=int(parametros_licitacion.numero_ganadores)
                    ganadores=self.env['participantes.asamblea.clientes'].search([('asamblea_id','=',self.id),('cuotas_licitadas','>',0),('seleccionado','=',False)],order='cuotas_licitadas desc')
                    ganadores_seleccionados=0
                    invertir_licitacion=0
                    for ganador in ganadores:
                        if ganadores_seleccionados<numero_ganadores:
                            invertir_licitacion+=ganador.monto_financiamiento-ganador.total_or
                            if (saldoActual-invertir_licitacion)>=0:
                                saldoActual=saldoActual-invertir_licitacion
                                ganador.seleccionado=True
                                ganador.nota="GANADOR"
                                ganadores_seleccionados+=1
                        else:
                            pass
                    numero_suplentes=int(parametros_licitacion.numero_suplentes)
                    suplentes=self.env['participantes.asamblea.clientes'].search([('asamblea_id','=',self.id),('cuotas_licitadas','>',0),('seleccionado','=',False)],order='cuotas_licitadas desc')
                    suplentes_seleccionados=0
                    invertir_licitacion=0
                    for suplente in suplentes:
                        if suplentes_seleccionados<numero_suplentes:
                            invertir_licitacion+=suplente.monto_financiamiento-suplente.total_or
                            if (valorNeto-invertir_licitacion)>=0:
                                valorNeto=valorNeto-invertir_licitacion
                                suplente.seleccionado=True
                                suplente.nota="SUPLENTE"
                                suplentes_seleccionados+=1
                        else:
                            pass
            if saldoActual:
                valorNeto=saldoActual
                if parametros_exacto:
                    numero_ganadores=int(parametros_exacto.numero_ganadores)
                    ganadores_seleccionados=0
                    hoy=date.today()
                    ganadores=self.env['participantes.asamblea.clientes'].search([('asamblea_id','=',self.id),('seleccionado','=',False)])
                    for ganador in ganadores:
                        if ganador.contrato_id.tipo_de_contrato.code=="exacto":
                            if ganadores_seleccionados<numero_ganadores:
                                cuota_id=ganador.contrato_id.estado_de_cuenta_ids.filtered(lambda l: l.programado>0.00 and l.fecha.month==hoy.month and l.fecha.year==hoy.year)
                                if cuota_id:
                                    if (saldoActual-ganador.monto_financiamiento)>=0:
                                        saldoActual=saldoActual-ganador.monto_financiamiento
                                        ganador.licitacion_valor=l.programado
                                        ganador.seleccionado=True
                                        ganador.nota="GANADOR"
                                        ganadores_seleccionados+=1
                            else:
                                pass

                    numero_suplentes=int(parametros_exacto.numero_suplentes)
                    suplentes=self.env['participantes.asamblea.clientes'].search([('asamblea_id','=',self.id),('seleccionado','=',False)])
                    suplentes_seleccionados=0
                    for suplente in suplentes:
                        if suplente.contrato_id.tipo_de_contrato.code=="exacto":
                            if suplentes_seleccionados<numero_suplentes:
                                cuota_id=suplente.contrato_id.estado_de_cuenta_ids.filtered(lambda l: l.programado>0.00 and l.fecha.month==hoy.month and l.fecha.year==hoy.year)
                                if cuota_id:
                                    if (valorNeto-suplente.monto_financiamiento)>=0:
                                        valorNeto=valorNeto-suplente.monto_financiamiento
                                        suplente.licitacion_valor=l.programado
                                        suplente.seleccionado=True
                                        suplente.nota="SUPLENTE"
                                        suplentes_seleccionados+=1
                            else:
                                pass
            if saldoActual:
                valorNeto=saldoActual
                if parametros_programo:
                    numero_ganadores=int(parametros_programo.numero_ganadores)
                    ganadores_seleccionados=0
                    hoy=date.today()
                    ganadores=self.env['participantes.asamblea.clientes'].search([('asamblea_id','=',self.id),('seleccionado','=',False)])
                    for ganador in ganadores:
                        if ganador.contrato_id.tipo_de_contrato.code=="programo":
                            if ganadores_seleccionados<numero_ganadores:
                                if ganador.contrato_id.porcentaje_programado==ganador.contrato_id.plazo_meses.porcentaje:
                                    cuota_id=ganador.contrato_id.estado_de_cuenta_ids.filtered(lambda l: l.numero_cuota==str(ganador.contrato_id.plazo_meses.numero) and l.fecha.month==hoy.month and l.fecha.year==hoy.year)
                                    if cuota_id:
                                        if (saldoActual-ganador.monto_financiamiento)>=0:
                                            saldoActual=saldoActual-ganador.monto_financiamiento
                                            ganador.licitacion_valor=l.programado
                                            ganador.seleccionado=True
                                            ganador.nota="GANADOR"
                                            ganadores_seleccionados+=1
                                else:
                                    pass

                    numero_suplentes=int(parametros_programo.numero_suplentes)
                    suplentes=self.env['participantes.asamblea.clientes'].search([('asamblea_id','=',self.id),('seleccionado','=',False)])
                    suplentes_seleccionados=0
                    for suplente in suplentes:
                        if suplente.contrato_id.tipo_de_contrato.code=="programo":
                            if suplente.contrato_id.porcentaje_programado==ganador.contrato_id.plazo_meses.porcentaje:
                                if suplentes_seleccionados<numero_suplentes:
                                    cuota_id=suplente.contrato_id.estado_de_cuenta_ids.filtered(lambda l: l.numero_cuota==str(suplente.contrato_id.plazo_meses.numero) and l.fecha.month==hoy.month and l.fecha.year==hoy.year)
                                    if cuota_id:
                                        if (valorNeto-suplente.monto_financiamiento)>=0:
                                            valorNeto=valorNeto-suplente.monto_financiamiento
                                            suplente.licitacion_valor=l.programado
                                            suplente.seleccionado=True
                                            suplente.nota="SUPLENTE"
                                            suplentes_seleccionados+=1
                                else:
                                    pass

            if saldoActual:
                valorNeto=saldoActual
                if parametros_evaluacion:
                    numero_ganadores_eva=int(parametros_evaluacion.numero_ganadores)
                    ganadores_eva=self.env['participantes.evaluacion.asamblea.clientes'].search([('asamblea_id','=',self.id),('cuotas_pagadas','>',0),('seleccionado','=',False)],order='cuotas_pagadas desc')
                    for ganador_eva in ganadores_eva:
                        if ganadores_seleccionados<numero_ganadores:
                            if (saldoActual-ganador_eva.monto_financiamiento)>=0:
                                saldoActual=saldoActual-ganador_eva.monto_financiamiento
                                ganador.seleccionado=True
                                ganador.nota="GANADOR"
                                ganadores_seleccionados+=1
                        else:
                            pass
                        
                    numero_suplentes=int(parametros_evaluacion.numero_suplentes)
                    suplentes=self.env['participantes.evaluacion.asamblea.clientes'].search([('asamblea_id','=',self.id),('cuotas_pagadas','>',0),('seleccionado','=',False)],order='cuotas_pagadas desc')
                    suplentes_seleccionados=0
                    for suplente in suplentes:
                        if suplentes_seleccionados<numero_suplentes:
                            if (valorNeto-suplente.monto_financiamiento)>=0:
                                valorNeto=valorNeto-suplente.monto_financiamiento
                                suplente.seleccionado=True
                                suplente.nota="SUPLENTE"
                                suplentes_seleccionados+=1
                        else:
                            pass

            l.ejecutado=True
            l.calcular_licitacion()


    @api.constrains("grupo_cliente")
    @api.onchange("grupo_cliente")
    def obtener_valores(self):
        self.obtener_integrantes()
        for l in self:
            fondos_mes=0
            recuperacionCartera=0
            adjudicados=0
            hoy=date.today()
            ##grupoParticipante=l.grupo_cliente.transacciones_ids.filtered(lambda l: l.create_date.month==hoy.month and l.create_date.year==hoy.year)
            grupoParticipante=l.grupo_cliente.transacciones_ids
            l.recuperacionCartera= sum(grupoParticipante.mapped('haber'))
            l.adjudicados= sum(grupoParticipante.mapped('debe'))
            l.fondos_mes=l.recuperacionCartera-l.adjudicados


    @api.depends('fondos_mes','invertir_licitacion','programo','evaluacion')
    @api.onchange('fondos_mes','invertir_licitacion','programo','evaluacion')
    @api.constrains('fondos_mes','invertir_licitacion','programo','evaluacion')
    def obtener_saldo(self):
        for l in self:
            l.saldo=l.fondos_mes-l.invertir_licitacion-l.programo-l.evaluacion

    def calcular_licitacion(self):
        total=0
        monto_financiamiento=0
        programado=0
        for l in self.integrantes_licitacion_id:
            if l.seleccionado and l.nota=='GANADOR' and l.licitacion_valor:
                total+=l.total_or
                monto_financiamiento+=l.monto_financiamiento
            elif l.seleccionado and l.nota=='GANADOR' and l.tipo_asamblea.code=="programo" and l.licitacion_valor==0:
                programado+=l.monto_financiamiento
        self.licitaciones=total
        self.invertir_licitacion=monto_financiamiento-total
        self.programo=programado
        total_eva=0
        
        for x in self.integrantes_evaluacion_id:
            if l.seleccionado and l.nota=='GANADOR':
                total_eva+=l.monto_financiamiento
        self.evaluacion=total_eva

    def cambio_estado_boton_precierre(self):
        self.write({"state": "pre_cierre"})

    def cambio_estado_boton_cerrado(self):
        self.write({"state": "cerrado"})



class IntegrantesGrupoAsamblea(models.Model):
    _name = 'integrante.grupo.adjudicado.asamblea.clientes'
    _description = 'Integrantes de Grupo Participante en asamblea'

    adjudicado_id = fields.Many2one('res.partner', string="Nombre")

class JuntaGrupoAsamblea(models.Model):
    _name = 'junta.grupo.asamblea'
    _description = 'Comité que realiza la asamblea'

    asamblea_id = fields.Many2one('asamblea', string='Asamblea')
    empleado_id = fields.Many2one('hr.employee', string="Empleado")
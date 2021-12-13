# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
import datetime
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
from dateutil.parser import parse


class Contrato(models.Model):
    _name = 'contrato'
    _description = 'Contrato'
    _rec_name = 'secuencia'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    secuencia = fields.Char(index=True)
    currency_id = fields.Many2one(
        'res.currency', readonly=True, default=lambda self: self.env.company.currency_id)
    cliente = fields.Many2one(
        'res.partner', string="Cliente", track_visibility='onchange')
    grupo = fields.Many2one(
        'grupo.adjudicado', string="Grupo", track_visibility='onchange')
    dia_corte = fields.Char(string='Día de Corte', default=lambda self: self._capturar_valores_por_defecto())
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
        string='Tasa Administrativa(%)', track_visibility='onchange')
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
    plazo_meses = fields.Selection([('60', '60 Meses'),
                                    ('72', '72 Meses')
                                    ], string='Plazo (meses)',default='60', track_visibility='onchange')
    cuota_adm = fields.Monetary(
        string='Cuota Administrativa', currency_field='currency_id', track_visibility='onchange')
    factura_inscripcion = fields.Many2one(
        'account.move', string='Factura Incripción', track_visibility='onchange')
    active = fields.Boolean(string='Activo', default=True)
    state = fields.Selection(selection=[
        ('borrador', 'Borrador'),
        ('congelar_contrato', 'Congelar Contrato'),
        ('adjudicar', 'Adjudicar'),
        ('adendum', 'Realizar Adendum'),
        ('desistir', 'Desistir'),
    ], string='Estado', default='borrador', track_visibility='onchange')
    observacion = fields.Char(string='Observación',
                              track_visibility='onchange')
    ciudad = fields.Many2one(
        'res.country.city', string='Ciudad', domain="[('provincia_id','=',provincias)]", track_visibility='onchange')
    archivo_adicional = fields.Binary(
        string='Archivo Adicional', track_visibility='onchange')
    fecha_inicio_pago = fields.Date(
        string='Fecha Inicio de Pago', compute='calcular_fecha_pago', track_visibility='onchange')
    cuota_capital = fields.Monetary(
        string='Cuota Capital', currency_field='currency_id', compute='calcular_valores_contrato', track_visibility='onchange')
    iva_administrativo = fields.Monetary(
        string='Iva Administrativo', currency_field='currency_id', track_visibility='onchange')
    estado_de_cuenta_ids = fields.One2many(
        'contrato.estado.cuenta', 'contrato_id', track_visibility='onchange')
    fecha_adjudicado = fields.Date(
        string='Fecha Adj.', track_visibility='onchange')

    monto_pagado = fields.Float(
        string='Monto Pagado', compute="calcular_monto_pagado", store=True, track_visibility='onchange')

    tabla_amortizacion = fields.One2many(
        'contrato.estado.cuenta', 'contrato_id', track_visibility='onchange')



    def _capturar_valores_por_defecto(self):
        dia_corte =  self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.dia_corte')
        tasa_administrativa =  self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.tasa_administrativa')

        self.tasa_administrativa = tasa_administrativa
        self.dia_corte = dia_corte
    

    @api.depends('pago')
    def calcular_fecha_pago(self):
        for rec in self:
            rec.dia_corte = 5
            if rec.pago == 'mes_actual':
                anio = str(datetime.today().year)
                mes = str(datetime.today().month)
                fechaPago =  anio+"-"+mes+"-05" 
                rec.fecha_inicio_pago = parse(fechaPago).date().strftime('%Y-%m-%d')
            elif rec.pago == 'siguiente_mes':
                fechaMesSeguiente = datetime.today() + relativedelta(months=1)
                mesSgte=str(fechaMesSeguiente.month)
                anioSgte=str(fechaMesSeguiente.year)
                fechaPago = anioSgte+"-"+mesSgte+"-05"
                rec.fecha_inicio_pago = parse(fechaPago).date().strftime('%Y-%m-%d')
            else:
                rec.fecha_inicio_pago =''
    
    @api.depends('plazo_meses', 'monto_financiamiento')
    def calcular_valores_contrato(self):
        dia_corte =  self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.dia_corte')
        tasa_administrativa =  self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.tasa_administrativa')
        for rec in self:


            rec.dia_corte = dia_corte
            if int(rec.plazo_meses):
                rec.cuota_capital = rec.monto_financiamiento/int(rec.plazo_meses)
                cuotaAdministrativa= rec.monto_financiamiento*((tasa_administrativa/100)/12)
                rec.iva_administrativo = cuotaAdministrativa * 1.12
                rec.cuota_adm = cuotaAdministrativa

            


    def detalle_tabla_amortizacion(self):
        dia_corte =  self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.dia_corte')
        tasa_administrativa =  self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.tasa_administrativa')


        for rec in self:
            for i in range(1, int(rec.plazo_meses)+1):
                cuota_capital = rec.monto_financiamiento/int(rec.plazo_meses)
                cuota_adm = cuota_capital *tasa_administrativa/100
                iva = cuota_adm * 0.12
                saldo = cuota_capital+cuota_adm+iva
                self.env['contrato.estado.cuenta'].create({
                                                    'numero_cuota':i,
                                                    'fecha':rec.fecha_inicio_pago + relativedelta(months=i),
                                                    'cuota_capital':cuota_capital,
                                                    'cuota_adm':cuota_adm,
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

        vals['tasa_administrativa'] = tasa_administrativa
        vals['dia_corte'] = dia_corte
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

    @api.constrains('cliente', 'secuencia')
    def constrains_valor_por_defecto(self):
        dia_corte =  self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.dia_corte')
        tasa_administrativa =  self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.tasa_administrativa')
        self.tasa_administrativa = tasa_administrativa
        self.dia_corte = dia_corte

    def cambio_estado_boton_borrador(self):
        return self.write({"state": "congelar_contrato"})

    def cambio_estado_congelar_contrato(self):
        return self.write({"state": "adjudicar"})

    def cambio_estado_boton_adendum(self):
        return self.write({"state": "adendum"})

    def cambio_estado_boton_desistir(self):
        return self.write({"state": "desistir"})






    @api.constrains('cliente')
    def constrains_valor_por_defecto(self):
        dia_corte =  self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.dia_corte')
        tasa_administrativa =  self.env['ir.config_parameter'].sudo().get_param('gzl_adjudicacion.tasa_administrativa')

        self.tasa_administrativa = tasa_administrativa
        self.dia_corte = dia_corte



    @api.constrains("cliente")
    def validar_cliente_en_otro_contrato(self, ):
        if self.cliente.id:
            contratos=self.env['contrato'].search([('cliente','=',self.cliente.id),('id','!=',self.id)],limit=1)
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
    factura_id = fields.Many2one('account.move', string='Factura')
    # pago_ids = fields.Many2many('account.payment','contrato_estado_cuenta_payment_rel', 'estado_cuenta_id','payment_id', string='Pagos')
    seguro = fields.Monetary(string='Seguro', currency_field='currency_id')
    rastreo = fields.Monetary(string='Rastreo', currency_field='currency_id')
    otro = fields.Monetary(string='Otro', currency_field='currency_id')
    monto_pagado = fields.Monetary(
        string='Monto Pagado', currency_field='currency_id')
    saldo = fields.Monetary(string='Saldo', currency_field='currency_id')
    certificado = fields.Binary(string='Certificado')
    estado_pago = fields.Selection([('pendiente', 'Pendiente'),
                                    ('pagado', 'Pagado')
                                    ], string='Estado de Pago', default='pendiente')


    
    def pagar_cuota(self):
        view_id = self.env.ref('gzl_crm.wizard_pago_cuota_amortizaciones').id
        return {'type': 'ir.actions.act_window',
                'name': 'Validar Pago',
                'res_model': 'wizard.pago.cuota.amortizacion',
                'target': 'new',
                'view_mode': 'form',
                'views': [[view_id, 'form']],
                'context': {
                    'default_tabla_amortizacion_id': self.id,
                }
        }
# -*- coding: utf-8 -*-
import datetime
import dateutil.relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date


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
    dia_corte = fields.Char(string='Día de Corte')
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
                                    ], string='Plazo (meses)', track_visibility='onchange')
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
    fecha_inicio_pago = fields.Char(
        string='Fecha Inicio de Pago', track_visibility='onchange')
    cuota_capital = fields.Monetary(
        string='Cuota Capital', currency_field='currency_id', track_visibility='onchange')
    iva_administrativo = fields.Monetary(
        string='Iva Administrativo', currency_field='currency_id', track_visibility='onchange')
    estado_de_cuenta_ids = fields.One2many(
        'contrato.estado.cuenta', 'contrato_id', track_visibility='onchange')
    fecha_adjudicado = fields.Date(
        string='Fecha Adj.', track_visibility='onchange')

    monto_pagado = fields.Float(
        string='Monto Pagado', compute="calcular_monto_pagado", store=True, track_visibility='onchange')

    tabla_amortizacion_contrato = fields.One2many(
        'contrato.estado.cuenta', 'contrato_id', track_visibility='onchange')

    # @api.depends("pago")
    # def calcular_fecha_pago(self):
    #     for rec in self:
    #         rec.dia_corte = 5
    #         d = datetime.datetime.today()
    #         d2 = d + dateutil.relativedelta.relativedelta(months=1)
    #         fecha_inicio_pago = ''

    def detalle_tabla_amortizacion(self):
        ahora = datetime.now()
        try:
            ahora = ahora.replace(day = self.dia_pago)
        except:
            raise ValidationError('La fecha no existe, por favor ingrese otro día de pago.')
        for i in range(1, int(self.numero_cuotas)+1):
            cuota_capital = self.planned_revenue/int(self.numero_cuotas)
            cuota_adm = cuota_capital *0.04
            iva = cuota_adm * 0.12
            saldo = cuota_capital+cuota_adm+iva
            self.env['tabla.amortizacion'].create({'oportunidad_id':self.id,
                                                   'numero_cuota':i,
                                                   'fecha':ahora + relativedelta(months=i),
                                                   'cuota_capital':cuota_capital,
                                                   'cuota_adm':cuota_adm,
                                                   'iva':iva,
                                                   'saldo':saldo
                                                    })
        self.cuota_capital = cuota_capital
        self.iva =  iva 




    


    @api.depends("estado_de_cuenta_ids.monto_pagado")
    def calcular_monto_pagado(self,):
        for l in self:
            monto=round(sum(l.estado_de_cuenta_ids.mapped("monto_pagado"),2))
            l.monto_pagado=monto




    @api.model
    def create(self, vals):
        vals['secuencia'] = self.env['ir.sequence'].next_by_code('contrato')
        res = self.env['res.config.settings'].sudo(
            1).search([], limit=1, order="id desc")
        vals['tasa_administrativa'] = res.tasa_administrativa
        vals['dia_corte'] = res.dia_corte
        for rec in self:
            for l in self.tabla_amortizacion:
                    self.env['contrato.estado.cuenta'].create({
                                            'contrato_id':rec.contrato.id,
                                            'numero_cuota':l.numero_cuota,
                                            'fecha': l.fecha,
                                            'cuota_capital':l.cuota_capital,
                                            'cuota_adm':l.cuota_adm,
                                            #'iva':l.iva
                                        })
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
        res = self.env['res.config.settings'].sudo(
            1).search([], limit=1, order="id desc")
        self.tasa_administrativa = res.tasa_administrativa
        self.dia_corte = res.dia_corte

    def cambio_estado_boton_borrador(self):
        return self.write({"state": "congelar_contrato"})

    def cambio_estado_congelar_contrato(self):
        return self.write({"state": "adjudicar"})

    def cambio_estado_boton_adendum(self):
        return self.write({"state": "adendum"})

    def cambio_estado_boton_desistir(self):
        return self.write({"state": "desistir"})


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








class TablaAmortizacion(models.Model):
    _name = 'tabla.amortizacion'
    _description = 'Tabla de Amortización'

    oportunidad_id = fields.Many2one('crm.lead')
    numero_cuota = fields.Char(String='Número de Cuota')
    fecha = fields.Date(String='Fecha Pago')
    currency_id = fields.Many2one('res.currency', readonly=True, default=lambda self: self.env.company.currency_id)
    cuota_capital = fields.Monetary(string='Cuota Capital', currency_field='currency_id')
    cuota_adm = fields.Monetary(string='Cuota Adm', currency_field='currency_id')
    iva = fields.Monetary(string='Iva', currency_field='currency_id')
    seguro = fields.Monetary(string='Seguro', currency_field='currency_id')
    saldo = fields.Monetary(string='Saldo', currency_field='currency_id')
    rastreo = fields.Monetary(string='Rastreo', currency_field='currency_id')
    otro = fields.Monetary(string='Otro', currency_field='currency_id')
    estado_pago = fields.Selection([('pendiente', 'Pendiente'), 
                                      ('pagado', 'Pagado')
                                    ],string='Estado de Pago', default='pendiente') 
    factura_id = fields.Many2one('account.move')
    pago_id = fields.Many2one('account.payment')
    
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
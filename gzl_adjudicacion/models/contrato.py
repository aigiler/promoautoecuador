# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Contrato(models.Model):
    _name = 'contrato'
    _description = 'Contrato'
    _rec_name = 'secuencia'

    secuencia = fields.Char(index=True)
    currency_id = fields.Many2one('res.currency', readonly=True, default=lambda self: self.env.company.currency_id)
    cliente = fields.Many2one('res.partner', string="Cliente")
    grupo = fields.Many2one('grupo.adjudicado', string="Grupo")
    dia_corte = fields.Char(string='Día de Corte')
    saldo_a_favor_de_capital_por_adendum = fields.Monetary(string='Saldo a Favor de Capital por Adendum', currency_field='currency_id')
    pago = fields.Selection(selection=[
        ('mes_actual', 'Mes Actual'),
        ('siguiente_mes', 'Siguiente Mes'),
        ('personalizado', 'Personalizado')
        ], string='Pago', default='mes_actual')
    monto_financiamiento = fields.Monetary(string='Monto Financiamiento', currency_field='currency_id')
    tasa_administrativa = fields.Float(string='Tasa Administrativa(%)')
    valor_inscripcion = fields.Monetary(string='Valor Inscripción', currency_field='currency_id')
    tipo_de_contrato = fields.Many2one('tipo.contrato.adjudicado', string='Tipo de Contrato')
    codigo_grupo = fields.Char(string='Código de Grupo')
    provincias = fields.Many2one('res.country.state', string='Provincia')
    archivo = fields.Binary(string='Archivo')
    fecha_contrato = fields.Date(string='Fecha Contrato')
    plazo_meses = fields.Selection([('60', '60 Meses'), 
                                    ('72', '72 Meses')
                                    ],string='Plazo (meses)') 
    cuota_adm = fields.Monetary(string='Cuota Administrativa', currency_field='currency_id') 
    factura_inscripcion = fields.Many2one('account.move', string='Factura Incripción')
    active = fields.Selection(selection=[
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo')
        ], string='Estado', default='activo')
    estado = fields.Selection(selection=[
        ('borrador', 'Borrador'),
        ('congelar_contrato', 'Congelar Contrato'),
        ('adjudicar', 'Adjudicar'),
        ('adendum', 'Realizar Adendum'),
        ('desistir', 'Desistir'),
        ], string='Estado', default='borrador')
    observacion = fields.Char(string='Observación')
    ciudad = fields.Many2one('res.country.city', string='Ciudad', domain="[('provincia_id','=',provincias)]") 
    archivo_adicional = fields.Binary(string='Archivo Adicional')
    fecha_inicio_pago = fields.Char(string='Fecha Inicio de Pago')
    cuota_capital = fields.Monetary(string='Cuota Capital', currency_field='currency_id')
    iva_administrativo = fields.Monetary(string='Iva Administrativo', currency_field='currency_id')
    estado_de_cuenta_ids = fields.One2many('contrato.estado.cuenta', 'contrato_id')


    @api.onchange('cliente', 'grupo')
    def onchange_provincia(self):
        self.env.cr.execute("""select id from res_country_state where country_id={0}""".format(self.env.ref('base.ec').id))
        res = self.env.cr.dictfetchall()
        if res:
            list_res=[]
            for l in res:
                list_res.append(l['id'])
            return {'domain': {'provincias': [('id', 'in', list_res)]}}

    
    @api.constrains('cliente', 'secuencia')
    def constrains_valor_por_defecto(self): 
        res = self.env['res.config.settings'].sudo(1).search([], limit=1, order="id desc")
        self.tasa_administrativa= res.tasa_administrativa
        self.dia_corte = res.dia_corte



class ContratoEstadoCuenta(models.Model):
    _name = 'contrato.estado.cuenta'
    _description = 'Contrato - Tabla de estado de cuenta de Aporte'

    contrato_id = fields.Many2one('contrato')
    numero_cuota = fields.Char(String='Número de Cuota')
    fecha = fields.Date(String='Fecha Pago')
    fecha_pagada = fields.Date(String='Fecha Pagada')
    currency_id = fields.Many2one('res.currency', readonly=True, default=lambda self: self.env.company.currency_id)
    cuota_capital = fields.Monetary(string='Cuota Capital', currency_field='currency_id')
    cuota_adm = fields.Monetary(string='Cuota Adm', currency_field='currency_id')
    factura_id = fields.Many2one('account.move', string='Factura')
    pago_ids = fields.Many2many('account.payment', string='Pagos')
    seguro = fields.Monetary(string='Seguro', currency_field='currency_id')
    rastreo = fields.Monetary(string='Rastreo', currency_field='currency_id')
    otro = fields.Monetary(string='Otro', currency_field='currency_id')
    monto_pagado = fields.Monetary(string='Monto Pagado', currency_field='currency_id')
    saldo = fields.Monetary(string='Saldo', currency_field='currency_id')
    certificado = fields.Binary(string='Certificado')
    estado_pago = fields.Selection([('pendiente', 'Pendiente'), 
                                      ('pagado', 'Pagado')
                                    ],string='Estado de Pago', default='pendiente') 
    
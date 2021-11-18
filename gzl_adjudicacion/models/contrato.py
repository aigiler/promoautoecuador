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
        ('mes_actual', 'Pagar Desde Mes Actual'),
        ('siguiente_mes', 'Siguiente Mes'),
        ('personalizado', 'Personalizado')
        ], string='Pago', default='mes_actual')
    monto_financiamiento = fields.Monetary(string='Monto Financiamiento', currency_field='currency_id')
    tasa_administrativa = fields.Float(string='Tasa Administrativa (%)')
    valor_inscripcion = fields.Monetary(string='Valor Inscripción', currency_field='currency_id')
    tipo_de_contrato = fields.Many2one('tipo.contrato.adjudicado', string='Tipo de Contrato')
    codigo_grupo = fields.Char(string='Código de Grupo')
    provincias = fields.Many2one('res.country.state', string='Provincia')
    #archivo = fields.
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
    observacion = fields.Char(string='Observación')
    ciudad = fields.Many2one('res.country.city', string='Ciudad', domain="[('provincia_id','=',provincias)]") 
    #archivo_adicional =
    fecha_inicio_pago = fields.Char(string='Fecha Inicio de Pago')
    cuota_capital = fields.Monetary(string='Cuota Capital', currency_field='currency_id')
    iva_administrativo = fields.Monetary(string='Iva Administrativo', currency_field='currency_id')
    
    @api.onchange('cliente', 'grupo')
    def onchange_provincia(self):
        self.env.cr.execute("""select id from res_country_state where country_id={0}""".format(self.env.ref('base.ec').id))
        res = self.env.cr.dictfetchall()
        if res:
            list_res=[]
            for l in res:
                list_res.append(l['id'])
            return {'domain': {'provincias': [('id', 'in', list_res)]}}
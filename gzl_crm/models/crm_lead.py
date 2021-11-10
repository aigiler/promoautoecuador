# -*- coding: utf-8 -*-

from odoo import api, fields, models

class CrmLead(models.Model):
    
    _inherit = 'crm.lead'

    is_won = fields.Boolean(related='stage_id.is_won')
    contacto_name = fields.Char(string='Nombre Completo')
    contacto_cedula = fields.Char(string='Cédula')
    contacto_correo = fields.Char(string='Correo Electrónico')
    contacto_telefono = fields.Char(string='Teléfono')
    contacto_domicilio = fields.Char(string='Domicilio')
    tasa_interes = fields.Integer(string='Tasa de Inter+és')
    numero_cuotas = fields.Integer(string='Número de Cuotas')
    dia_pago = fields.Integer(string='Día de Pagos')
    tabla_amortizacion = fields.One2many('tabla.amortizacion', 'oportunidad_id' )
    
    def detalle_tabla_amortizacion(self):
        print('---')

    def crear_adjudicado(self):
        if self.stage_id.is_won:
            self.env['res.partner'].create({
                                        'name':self.partner_id.name,
                                        'type':'contact',
                                        'tipo':'adjudicado',
                                        'monto':self.planned_revenue or 0,
                                        'function':self.partner_id.function or None,
                                        'email':self.partner_id.email or None,
                                        'phone':self.partner_id.phone or None,
                                        'mobile':self.partner_id.mobile or None,
            })



class TablaAmortizacion(models.Model):
    _name = 'tabla.amortizacion'
    _description = 'Tabla de Amortización'

    oportunidad_id = fields.Many2one('crm.lead')
    numero_cuota = fields.Char(String='Número de Cuota')
    fecha = fields.Date(String='Fecha')
    currency_id = fields.Many2one('res.currency', readonly=True, default=lambda self: self.env.company.currency_id)
    cuota = fields.Monetary(string='Cuota', currency_field='currency_id')
    capital = fields.Monetary(string='Capital', currency_field='currency_id')
    interes = fields.Monetary(string='Interes', currency_field='currency_id')
    saldo = fields.Monetary(string='Saldo', currency_field='currency_id')
            
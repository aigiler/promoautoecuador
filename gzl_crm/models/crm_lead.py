# -*- coding: utf-8 -*-

from odoo import api, fields, models

class CrmLead(models.Model):
    
    _inherit = 'crm.lead'

    is_won = fields.Boolean(related='stage_id.is_won')
    contacto_name = fields.Char(String='Nombre Completo')
    contacto_cedula = fields.Char(String='Cédula')
    contacto_correo = fields.Char(String='Correo Electrónico')
    contacto_telefono = fields.Char(String='Teléfono')
    contacto_domicilio = fields.Char(String='Domicilio')
    tasa_interes = fields.Integer(String='Tasa de Interes')
    numero_cuotas = fields.Integer(String='Número de Cuotas')
    dia_pago = fields.Integer(String='Día de Pagos')
    tabla_amortizacion = fields.One2many('tabla.amortizacion', 'oportunidad_id' )
    
    def detalle_tabla_amortizacion(self):


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
    cuota = fields.fields.Monetary(string='Cuota')
    capital = fields.fields.Monetary(string='Capital')
    interes = fields.fields.Monetary(string='Interes')
    saldo = fields.fields.Monetary(string='Saldo')
            
# -*- coding: utf-8 -*-

from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo.exceptions import ValidationError

import numpy_financial as npf


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
    tipo_contrato = fields.Many2one('tipo.contrato.adjudicado', string='Tipo de Contrato')
    tabla_amortizacion = fields.One2many('tabla.amortizacion', 'oportunidad_id' )
    cotizaciones_ids = fields.One2many('sale.order', 'oportunidad_id')

    def detalle_tabla_amortizacion(self):
        self._cr.execute(""" delete from tabla_amortizacion where oportunidad_id={0}""".format(self.id))
        capital = self.planned_revenue
        tasa = self.tasa_interes/100
        plazo = self.numero_cuotas
        cuota = round(npf.pmt(tasa, plazo, -capital, 0), 0)
        saldo = capital
        ahora = datetime.now()
        try:
            ahora = ahora.replace(day = self.dia_pago)
        except:
            raise ValidationError('La fecha no existe, por favor ingrese otro día de pago.')
        for i in range(1, plazo+1):
            pago_capital = npf.ppmt(tasa, i, plazo, -capital, 0)
            pago_int = cuota - pago_capital
            saldo -= pago_capital  
            self.env['tabla.amortizacion'].create({'oportunidad_id':self.id,
                                                   'numero_cuota':i,
                                                   'fecha':ahora + relativedelta(months=i),
                                                   'cuota':cuota,
                                                   'capital':pago_capital,
                                                   'interes':pago_int,
                                                   'saldo':saldo
                                                    })
                                            
                                               
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

    
    def crear_contrato(self):
        plantillas = self.env['sign.template'].search([('attachment_id.tipo_plantilla','=','adjudicacion')])
        for l in plantillas:
           # modelo sign.send.request ---- sign_directly()
           #sign_directly_without_mail  
            enviar_ahora = self.env['sign.request'].search([('template_id','=',l.id)])
            enviar_ahora.send_completed_document()

    
    @api.onchange('stage_id.is_won')
    def crear_factura_automatica(self):
        if self.stage_id.is_won:
            view_id = self.env.ref('gzl_crm.wizard_cotizaciones_crm').id
            return {'type': 'ir.actions.act_window',
                    'name': _('Cotizaciones'),
                    'res_model': 'sale.order',
                    'target': 'new',
                    'view_mode': 'form',
                    'views': [[view_id, 'form']],
                    'domain': [('oportunidad_id', '=', self.id)],
                    'context': {'oportunidad_id': self.id}
            }

    


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
    
    
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    oportunidad_id = fields.Many2one('crm.lead')
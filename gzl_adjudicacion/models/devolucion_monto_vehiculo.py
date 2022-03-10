# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, tools,  _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime,timedelta,date
import re


class DevolucionMonto(models.Model):   
    _name = 'devolucion.monto'   
    #_inherit = 'entrega.vehiculo' 
    _rec_name= 'secuencia'

    secuencia = fields.Char(index=True)

    monto = fields.Float(string='Monto')
    contrato_id = fields.Many2one('contrato')
    fsolicitud  = fields.Date(string='Fecha de Solicitud')
    state = fields.Selection(selection=[
        ('borrador', 'Borrador'),
        ('postventa', 'Analisis Postventa'),
        ('legal', 'Analisis Legal'),
        ('adjudicaciones', 'Analisis Adjudicacion'),
        ('verifvalores', 'Verificacion de Valores'),
        ('aprobgerencia', 'Aprobacion Gerencia'),
        ('salidadinero', 'Salida Dinero'),
        ('notificacion', 'Notificacion Cliente'),
        ('liquidacion', 'Liquidacion de vendedor'),
    ], string='Estado', default='borrador', track_visibility='onchange')


    @api.model
    def create(self, vals):
        vals['secuencia'] = self.env['ir.sequence'].next_by_code('devolucion.adjudicado')


        return super(DevolucionMonto, self).create(vals)
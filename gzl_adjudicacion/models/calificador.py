# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date


class Partner(models.Model):
    _inherit = 'res.partner'


    calificaciones = fields.One2many('calificador.cliente', 'partner_id',track_visibility='onchange')
    calificacion = fields.Float( string="Calificacion",compute="calcular_calificacion",store=True)
    ##proveedor_recurrente=fields.Boolean(string="Proveedor Recurrente", default=False)


    @api.depends('calificaciones')
    def calcular_calificacion(self,):
        for l in self:
            l.calificacion=sum(l.calificaciones.mapped('calificacion'))

    def obtener_proveedores_recurrente(self):
        hoy=date.today()
        proveedores_ids=self.env['res.partner'].search([('proveedor_recurrente','=',True)])
        for x in proveedores_ids:
            factura_ids=self.env['account.move'].search([('partner_id','=',x.id),('type','=','in_invoice')])
            factura_mes=factura_ids.filtered(lambda l: l.invoice_date.year == hoy.year and l.invoice_date.month == hoy.month)
            if len(factura_mes)==0:
                self.envio_correos_plantilla('email_facturas_recurrentes',x.id)



    def envio_correos_plantilla(self, plantilla,id_envio):

        try:
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('gzl_adjudicacion', plantilla)[1]
        except ValueError:
            template_id = False
#Si existe capturo el template
        if template_id:
            obj_template=self.env['mail.template'].browse(template_id)

            email_id=obj_template.send_mail(id_envio)






class CalificadorCliente(models.Model):
    _name = 'calificador.cliente'
    _description = 'Calificacion de cliente'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    partner_id = fields.Many2one('res.partner', string="Cliente")
    motivo = fields.Char( string="Motivo")
    calificacion = fields.Float( string="Calificacion")















class CalificadorClienteParametros(models.Model):
    _name = 'calificador.cliente.parametros'
    _description = 'Paràmetros Calificacion de cliente'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    motivo = fields.Char( string="Motivo")
    calificacion = fields.Float( string="Calificacion")

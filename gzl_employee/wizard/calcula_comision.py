# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import xlsxwriter
from io import BytesIO
import base64
from calendar import monthrange

class CalculoComision(models.TransientModel):
    _name = "calcula.comision"
    name = fields.Many2one('hr.employee', string='Empleado', required=True)
    date = fields.Selection(selection=[
            ('01', 'Enero'),
            ('02', 'Febrero'),
            ('03', 'Marzo'),
            ('04', 'Abril'),
            ('05', 'Mayo'),
            ('06', 'Junio'),
            ('07', 'Julio'),
            ('08', 'Agosto'),
            ('09', 'Septiembre'),
            ('10', 'Octubre'),
            ('11', 'Noviembre'),
            ('12', 'Diciembre'),
        ], string='Fecha', required=True)

    def calculo_comision(self):
        dct={}
        lis=[]
        cont=0
        partner_ids = self.env['res.partner']
        partner = partner_ids.search([('active','=',True),('vat','=',self.name.identification_id)])
        #self.env['detalle.oportunidades']
        action = self.env.ref('gzl_employee.action_calculo_comision_detalle_crm').read()[0]
        return action 
class DetalleOportunidades(models.TransientModel):
    _name = 'detalle.oportunidades'
    _inherit = ["crm.lead"]
    crmlead = fields.Many2one('crm.lead', string='Oportunidad')
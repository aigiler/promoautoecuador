# -*- coding: utf-8 -*-
import string
from odoo import api, fields, models, tools
from datetime import date, timedelta, datetime
from dateutil import relativedelta as rdelta 
import xlsxwriter
from io import BytesIO
import base64
from odoo.exceptions import ValidationError


class User(models.Model):
    _inherit = 'res.users'

    codigo_asesor=fields.Char("Codigo de Asesor")

class ReportCrm(models.TransientModel):
    _name = "report.crm.ventas"

    date_start = fields.Date('Fecha Inicio', required=True)
    date_end = fields.Date('Fecha Corte', required=True, default = date.today())


    def print_report_xls(self):
        today = date.today()
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data)
        name = 'REPORTE DE VENTAS '+ str(today.year)
        self.xslx_body(workbook,name)
        workbook.close()
        file_data.seek(0)
        attachment = self.env['ir.attachment'].create({
            'datas': base64.b64encode(file_data.getvalue()),
            'name': name,
            'store_fname': name,
            'type': 'binary',
        })
        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url += "/web/content/%s?download=true" %(attachment.id)
        return{
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }

    def xslx_body(self,workbook,name):
        bold = workbook.add_format({'bold':True,'border':0, 'bg_color':'#442484','color':'#FFFFFF'})
        bold.set_center_across()
        bold.set_font_size(14)
        bold2 = workbook.add_format({'bold':True,'border':0, 'bg_color':'#989899','color':'#FFFFFF'})
        bold2.set_center_across()
        format_title = workbook.add_format({'bold':True,'border':0})
        format_title.set_center_across()
        body_right = workbook.add_format({'align': 'right','border':1})
        body_left = workbook.add_format({'align': 'left','border':0})
        body_center = workbook.add_format({'align': 'center','border':0})
        body_center.set_center_across()
        format_title2 = workbook.add_format({'align': 'center', 'bold':True,'border':0 })
        sheet = workbook.add_worksheet(name)
        mesesDic = {
                "1":'ENERO',
                "2":'FEBRERO',
                "3":'MARZO',
                "4":'ABRIL',
                "5":'MAYO',
                "6":'JUNIO',
                "7":'JULIO',
                "8":'AGOSTO',
                "9":'SEPTIEMBRE',
                "10":'OCTUBRE',
                "11":'NOVIEMBRE',
                "12":'DICIEMBRE'
            }
                year = self.date_start.year
        mes_start = self.date_start.month
        mes_end = self.date_end.month
        dia_start = self.date_start.day
        dia_end = self.date_end.day
        sheet.insert_image('A1', "any_name.png",
                           {'image_data':  BytesIO(base64.b64decode( self.env.company.imagen_excel_company)), 'x_scale': 0.9, 'y_scale': 0.8,'x_scale': 0.8,
                            'y_scale':     0.8, 'align': 'left','bg_color':'#442484'})
        
        sheet.merge_range('B1:Q1', ' ', bold)
        sheet.merge_range('A2:Q2', 'REPORTE DE VENTAS DEL '+str(dia_start)+' DE '+str(mesesDic[str(mes_start)])+' DEL '+str(year)+' AL '+str(dia_end)+' DE '+str(mesesDic[str(mes_end)])+' DEL '+str(year), bold)
        sheet.set_column('A:A', 20)
        sheet.set_column('B:B', 45)
        sheet.set_column('C:C', 16)
        sheet.set_column('D:D', 18)
        sheet.set_column('E:E', 25)
        sheet.set_column('F:F', 17)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:H', 15)
        sheet.set_column('I:I', 16)
        sheet.set_column('J:J', 17)
        sheet.set_column('K:K', 17)
        
      
        sheet.write(2, 0, 'SEMANA', bold2)
        sheet.write(2, 1, 'FECHA DE INGRESO', bold2)
        sheet.write(2, 2, 'CLIENTE', bold2)
        sheet.write(2, 3, 'NUMERO', bold2)
        sheet.write(2, 4, 'CONTRATO', bold2)
        sheet.write(2, 5, 'MONTO', bold2)
        sheet.write(2, 6, 'SUBTOTAL', bold2)
        sheet.write(2, 7, 'IVA', bold2)
        sheet.write(2, 8, 'TOTAL', bold2)
        sheet.write(2, 9, 'CODIGO ASESOR', bold2)
        
        sheet.write(2, 10, 'ASESOR', bold2)
        sheet.write(2, 11, 'SUPERVISOR', bold2)
        sheet.write(2, 12, 'FACTURA', bold2)
        row=3
        crm = self.env['crm.lead'].search([('create_date','>=',self.date_start),('create_date','<=',self.date_end)])
        for l in crm:
            sheet.write(row,0, semana, body_center)
            sheet.write(row, 1, l.create_date or '###', body_center)
            sheet.write(row, 2,l.partner_id.name or '###', body_center)
            sheet.write(row, 3, l.partner_id.vat or '####', body_center)
            sheet.write(row, 4, l.contrato_id.secuencia or '###', body_center)
            sheet.write(row, 5, l.planned_revenue or '####', body_center)
            sheet.write(row, 6, round(l.valor_inscripcion-(l.valor_inscripcion*0.12),2) or '###', body_center)
            sheet.write(row, 7, round(l.valor_inscripcion*0.12,2) or '###', body_center)
            sheet.write(row, 8, round(l.valor_inscripcion,2) or '###', body_center)
            sheet.write(row, 9, l.user_id.codigo_asesor or '###', body_center)
            sheet.write(row, 10, l.user_id.name or '###', body_center)
            sheet.write(row, 11, l.team_id.user_id.id or '###', body_center)
            sheet.write(row, 12, l.factura_inscripcion_id.name or '###', body_center)
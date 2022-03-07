# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from datetime import date, timedelta, datetime
from dateutil import relativedelta as rdelta 
import xlsxwriter
from io import BytesIO
import base64

class ReportComisiones(models.TransientModel):
    _name = "report.comisiones"

    date_start = fields.Date('Fecha Inicio', required=True)
    date_end = fields.Date('Fecha Corte', required=True, default = date.today())

  

    def print_report_xls(self):
        today = date.today()
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data)
        name = 'REPORTE COMISIONISTAS '+ str(today.year)
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
        format_title = workbook.add_format({'bold':True,'border':0})
        format_title.set_center_across()
        body_right = workbook.add_format({'align': 'right','border':1})
        body_left = workbook.add_format({'align': 'left','border':1})
        body_center = workbook.add_format({'align': 'center','border':1})
        format_title2 = workbook.add_format({'align': 'center', 'bold':True,'border':0 })
        sheet = workbook.add_worksheet(name)
        sheet.insert_image('B1', '../img/logo.png', {'x_offset': 15, 'y_offset': 10})
        sheet.merge_range('B2:E2', name.upper(), bold)
        sheet.set_column('A:A', 42)
        sheet.set_column('B:B', 45)
        sheet.set_column('C:C', 16)
        sheet.set_column('D:D', 18)
        sheet.set_column('E:E', 16)
        sheet.set_column('F:F', 17)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:H', 11)
        sheet.set_column('I:I', 11)
        sheet.set_column('J:J', 11)
        sheet.set_column('K:K', 11)
        sheet.set_column('L:L', 11)
        sheet.set_column('M:M', 11)
        #data = self.report_vacations_data()
      
        sheet.write(2, 0, 'PERIODO DE PAGO', bold)
        sheet.write(2, 1, 'CARGO', bold)
        sheet.write(2, 2, 'AGENCIA', bold)
        sheet.write(2, 3, 'CONTRATO N', bold)
        sheet.write(2, 4, 'NOMBRE', bold)
        sheet.write(2, 4, 'SUBTOTAL', bold)
        sheet.write(2, 4, 'IVA', bold)
        sheet.write(2, 4, 'TOTAL A RECIBIR', bold)
        sheet.write(2, 4, 'ESTADO', bold)
        sheet.write(2, 4, 'OBSERVACION', bold)
        row=3
        #for l in data:
        #    sheet.write(row, 0, l['nro'], body_right)
        #    sheet.write(row, 1, l['colaborador'], body_left)
        #    sheet.write(row, 2, l['fecha_ingreso'] or '', body_center)
        #    sheet.write(row, 3, l['dias_gozados'] or '', body_right)
        #    sheet.write(row, 4, l['dias_pendientes'] or '', body_right)
        #    row+=1
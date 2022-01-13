
# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from datetime import date, timedelta,datetime
from dateutil.relativedelta import relativedelta
import xlsxwriter
from io import BytesIO
import base64
from odoo.exceptions import AccessError, UserError, ValidationError

import calendar
import datetime as tiempo
import itertools


class ReporteEstadoDeCuenta(models.TransientModel):
    _name = "reporte.estado.de.cuenta"

    contrato_id = fields.Many2one('contrato',string='Contrato')


    def print_report_xls(self):
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data)
        name = 'Estado de Cuenta'
        self.xslx_body(workbook, name)


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



    def xslx_body(self, workbook, name):
        bold = workbook.add_format({'bold':True,'border':1})
        bold.set_center_across()
        format_title = workbook.add_format({'font_name':'Cambria','font_size':  16,'bold':True})
        format_title.set_center_across()
        format_subtitle = workbook.add_format({'font_name':'Cambria','font_size':  14,'bold':True, 'bottom':1})
        format_subtitle.set_center_across()
        format_datos = workbook.add_format({'font_name':'Arial','font_size':  14,'align': 'left'})
        currency_format = workbook.add_format({'num_format': '[$$-409]#,##0.00','border':1,'text_wrap': True })
        currency_format.set_align('vcenter')

        date_format = workbook.add_format({'num_format': 'dd/mm/yy', 'align': 'right','border':1,'text_wrap': True })
        date_format.set_align('vcenter')
        date_format_day = workbook.add_format({'align': 'right','border':1,'text_wrap': True })
        date_format_day.set_align('vcenter')
        date_format_title = workbook.add_format({'num_format': 'yyyy-mm-dd', 'align': 'justify','text_wrap': True})
        date_format_title.set_align('vcenter')

        body = workbook.add_format({'align': 'center' , 'border':1,'text_wrap': True})
        body.set_align('vcenter')
        body_right = workbook.add_format({'align': 'right', 'border':1 })
        body_left = workbook.add_format({'align': 'left','bold':True})
        format_title2 = workbook.add_format({'align': 'center', 'bold':True,'border':1 })
        sheet = workbook.add_worksheet(name)
        sheet.insert_image('A1', 'resumen.jpg')
        sheet.merge_range('A3:M3', 'PROMOAUTO ECUADOR PROMOAUTOECUADOR S.A', format_title)
        sheet.merge_range('A5:I5', 'AV. JUAN TANCA MARENGO Y 2DO CALLEJON PLAZA SAI BABA', format_datos)
        sheet.merge_range('A6:C6', 'GUAYAQUIL - Ecuador', format_datos)
        sheet.merge_range('A7:C7', 'RUC: 0993261564001', format_datos)
        sheet.merge_range('K6:M6', self.contrato_id.ciudad.nombre_ciudad +', ' + self.create_date.strftime('%Y-%m-%d'), format_datos)
        sheet.merge_range('A8:M8', 'ESTADO DE CUENTA DE APORTES', format_subtitle)
        sheet.write('J9', 'Ced/RUC: '+ self.contrato_id.cliente.vat, format_datos)
        sheet.merge_range('A9:I9', 'Cliente: '+ self.contrato_id.cliente.name, format_datos)
        #sheet.merge_range('J9:J9', 'Ced/RUC: '+ self.contrato_id.cliente.vat, format_datos)
        #sheet.merge_range('J10:J10', 'Tipo de contrato: '+ self.contrato_id.tipo_de_contrato.name, format_datos)
        #sheet.merge_range('J12:J12', 'Monto financiamiento: '+ self.contrato_id.tipo_de_contrato.name, format_datos)
        #sheet.merge_range('M12:M12', 'Plazo: '+ self.contrato_id.tipo_de_contrato.name, format_datos)
        sheet.write('J10', 'Ced/RUC: '+ 'Tipo de contrato: '+ self.contrato_id.tipo_de_contrato.name, format_datos)
        sheet.write('J12', 'Monto financiamiento: '+ self.contrato_id.tipo_de_contrato.name, format_datos)
        sheet.write('M12', 'Plazo: '+ self.contrato_id.tipo_de_contrato.name, format_datos)
        sheet.merge_range('A10:I10', 'Grupo: '+'['+ self.contrato_id.grupo.codigo+'] '+ self.contrato_id.grupo.name, format_datos)
        #sheet.merge_range('A11:I11', 'Estado: '+ self.contrato_id.state+'('+self.contrato_id.fecha_adjudicado+')', format_datos)
        sheet.merge_range('A11:I11', 'Estado: '+ self.contrato_id.state , format_datos)
        sheet.merge_range('A12:I12', 'Valor Inscripción: $'+ str(self.contrato_id.valor_inscripcion), format_datos)
        #sheet.merge_range('D3:E3', self.contrato_id.monto_financiamiento, format_datos)

        title_main=['No','Fecha','Fecha Pagada','Cuota Capital' ,'Cuota Administrativa', 'Iva Adm.', 'Factura','Seguro','Rastreo','Otros','Monto Pagado','Saldo','Estado de Pago']

        ##Titulos
        colspan=13
        for col, head in enumerate(title_main):
            sheet.set_column('{0}:{0}'.format(chr(col + ord('A'))), len(head) + 13)
            sheet.write(13, col, head, bold)

        line = itertools.count(start=14)


        for linea in self.contrato_id.estado_de_cuenta_ids:

            current_line = next(line)
            sheet.write(current_line, 0, linea.numero_cuota ,body)
            sheet.write(current_line, 1, linea.fecha, date_format)
            sheet.write(current_line, 2, linea.fecha_pagada or ''  , date_format)
            sheet.write(current_line, 3, linea.cuota_capital , currency_format)
            sheet.write(current_line, 4, linea.cuota_adm ,currency_format)
            sheet.write(current_line, 5, linea.iva_adm ,currency_format)
            sheet.write(current_line, 6, linea.factura_id.name or ''  , body)
            sheet.write(current_line, 7, linea.seguro,currency_format)
            sheet.write(current_line, 8, linea.rastreo,currency_format)
            sheet.write(current_line, 9, linea.otro, currency_format)
            sheet.write(current_line, 10, linea.monto_pagado, currency_format)
            sheet.write(current_line, 11, linea.saldo, currency_format)
            if linea.estado_pago=='pendiente':
                sheet.write(current_line, 12, 'Pendiente', body)
            else:
                sheet.write(current_line, 12, 'Pagado', body)



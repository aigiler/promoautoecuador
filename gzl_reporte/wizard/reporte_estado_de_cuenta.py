
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
    
    
    

    def print_report_pdf(self):
        return self.env.ref('gzl_reporte.reporte_estado_de_cuenta_pdf_id').report_action(self)


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
        format_subtitle = workbook.add_format({'font_name':'Arial','font_size':  14,'bold':True, 'bottom':1})
        format_subtitle.set_center_across()
        format_datos = workbook.add_format({'font_name':'Arial','font_size':  12,'align': 'left'})
        currency_format = workbook.add_format({'font_name':'Arial','font_size':  12,'num_format': '[$$-409]#,##0.00','text_wrap': True,'align':'center' })
        currency_format.set_align('vcenter')
        formato_cabecera_tabla = workbook.add_format({'font_name':'Arial','font_size':  12,'align':'center','bold':True, 'bottom':1, 'top':1})
        formato_pie_tabla = workbook.add_format({'font_name':'Arial','font_size':  12,'align':'left','bold':True, 'bottom':1, 'top':1})
        date_format = workbook.add_format({'font_name':'Arial','font_size':  12,'num_format': 'yyyy-mm-dd', 'align': 'center','text_wrap': True })
        date_format.set_align('vcenter')
        date_format_day = workbook.add_format({'align': 'right','border':1,'text_wrap': True })
        date_format_day.set_align('vcenter')
        date_format_title = workbook.add_format({'num_format': 'yyyy-mm-dd', 'align': 'justify','text_wrap': True})
        date_format_title.set_align('vcenter')

        body = workbook.add_format({'font_name':'Arial','font_size':  12,'align': 'left', 'indent':4 , 'border':0,'text_wrap': True})
        body.set_align('vcenter')
        sheet = workbook.add_worksheet(name)
        #
        buf_image=io.BytesIO(self.env.company.image_1920)
        sheet.insert_image('A2',base64.b64encode(buf_image.getvalue()),{'image_data': buf_image})
        sheet.merge_range('A3:I3', self.env.company.name.upper(), format_title)
        sheet.merge_range('A5:I5', self.env.company.street.upper(), format_datos)
        # self.env.company.city.name
        sheet.merge_range('A6:C6', self.env.company.city.upper() + ' - ' +self.env.company.country_id.name.upper(), format_datos)
        sheet.merge_range('A7:C7', self.env.company.vat, format_datos)
        sheet.merge_range('H6:I6', self.contrato_id.ciudad.nombre_ciudad +', ' + self.create_date.strftime('%Y-%m-%d'), format_datos)
        sheet.merge_range('A8:I8', 'ESTADO DE CUENTA DE APORTES', format_subtitle)
        sheet.write('H9', 'Ced/RUC: '+ self.contrato_id.cliente.vat, format_datos)
        sheet.merge_range('A9:C9', 'Cliente: '+ self.contrato_id.cliente.name, format_datos)
        sheet.write('H10', 'Tipo de contrato: '+ self.contrato_id.tipo_de_contrato.name.upper(), format_datos)
        sheet.write('G12', 'Monto financiamiento: $'+ str(self.contrato_id.monto_financiamiento), format_datos)
        sheet.write('I12', 'Plazo: '+ str(self.contrato_id.plazo_meses.numero)+ ' Meses' , format_datos)
        sheet.merge_range('A10:C10', 'Grupo: '+'['+ self.contrato_id.grupo.codigo+'] '+ self.contrato_id.grupo.name, format_datos)
        if self.contrato_id.state == 'adjudicar':
            sheet.merge_range('A11:C11', 'Estado: '+ self.contrato_id.state.upper() +'(' +self.contrato_id.fecha_adjudicado.strftime('%Y-%m-%d')+')' , format_datos)
        else:
            sheet.merge_range('A11:C11', 'Estado: '+ self.contrato_id.state.upper(), format_datos)
        sheet.merge_range('A12:C12', 'Valor Inscripción: $'+ str(self.contrato_id.valor_inscripcion), format_datos)

        title_main=['cuota','Fecha pago','Cuota Capital' ,'Cuota Adm.', 'Iva','Seguro','Rastreo','Otro','Saldo']

        ##Titulos
        colspan=13
        for col, head in enumerate(title_main):
            sheet.set_column('{0}:{0}'.format(chr(col + ord('A'))), len(head) + 13)
            sheet.write(13, col, head.upper(), formato_cabecera_tabla)

        line = itertools.count(start=14)
        fila = 14
        fila_current=0

        for linea in self.contrato_id.estado_de_cuenta_ids:
            current_line = next(line)
            sheet.write(current_line, 0, linea.numero_cuota ,body)
            sheet.write(current_line, 1, linea.fecha, date_format)
            #sheet.write(current_line, 2, linea.fecha_pagada or ''  , date_format)
            sheet.write(current_line, 2, linea.cuota_capital , currency_format)
            sheet.write(current_line, 3, linea.cuota_adm ,currency_format)
            sheet.write(current_line, 4, linea.iva_adm ,currency_format)
            #sheet.write(current_line, 6, linea.factura_id.name or ''  , body)
            sheet.write(current_line, 5, linea.seguro,currency_format)
            sheet.write(current_line, 6, linea.rastreo,currency_format)
            sheet.write(current_line, 7, linea.otro, currency_format)
            #sheet.write(current_line, 10, linea.monto_pagado, currency_format)
            sheet.write(current_line, 8, linea.saldo, currency_format)
            # if linea.estado_pago=='pendiente':
            #     sheet.write(current_line, 12, 'Pendiente', body)
            # else:
            #     sheet.write(current_line, 12, 'Pagado', body)
            fila_current=current_line


        sheet.merge_range('A{0}:B{0}'.format(fila_current+2), 'TOTALES: ', formato_pie_tabla)
        lista_col_formulas=[2,3,4,5,6,7,8]
        for col in lista_col_formulas:
            col_formula = {
                            'from_col': chr(65 +col),
                            'to_col': chr(65 +col),
                            'from_row': fila+1,
                            'to_row': fila_current+1,

                        }
            currency_bold=workbook.add_format({'num_format': '[$$-409]#,##0.00','text_wrap': True ,'font_name':'Arial','font_size':  12,'align':'center','bold':True, 'bottom':1, 'top':1})

            sheet.write_formula(
                                    fila_current+1 ,col ,
                                    '=SUM({from_col}{from_row}:{to_col}{to_row})'.format(
                                        **col_formula
                                    ), currency_bold)



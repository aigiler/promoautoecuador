
# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from datetime import date, timedelta,datetime
from dateutil.relativedelta import relativedelta

import xlsxwriter
from PIL import Image
import xlwt
from io import BytesIO
import base64
import os
from odoo.exceptions import AccessError, UserError, ValidationError

import calendar
import datetime as tiempo
import itertools
import subprocess
from subprocess import getoutput
import os
import io

class ReporteEstadoDeCuentaIndividual(models.TransientModel):
    _name = "reporte.estado.de.cuenta"


    partner_id = fields.Many2one('res.partner',string='Cliente')
    contrato_id = fields.Many2one('contrato',string='Contrato')
    url_doc = fields.Char('Url doc')    
    
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
        ##url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = "https://promoauto.odoo.com/web/content/%s?download=true"%(attachment.id) 
        return{
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }

    def print_report_pdf(self):
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data)
        name = 'Estado de Cuenta.xlsx'
        self.xslx_body(workbook, name)
        workbook.close()
        file_data.seek(0)
        obj_attch = self.env['ir.attachment'].create({
            'datas': base64.b64encode(file_data.getvalue()),
            'name': name,
            'store_fname': name,
            'type': 'binary',
        })

        direccion_xls_libro=self.env['ir.attachment']._get_path(obj_attch.datas,obj_attch.checksum)[1]
        nombre_bin=obj_attch.checksum
        nombre_archivo=obj_attch.name
        os.chdir(direccion_xls_libro.rstrip(nombre_bin))
        print(os.chdir(direccion_xls_libro.rstrip(nombre_bin)))
        os.rename(nombre_bin,nombre_archivo)
        subprocess.getoutput("""libreoffice --headless --convert-to pdf *.xlsx""") 
        try:
            with open(direccion_xls_libro.rstrip(nombre_bin)+nombre_archivo.split('.')[0]+'.pdf', "rb") as f:
                data = f.read()
                file=bytes(base64.b64encode(data))
        except:
            raise ValidationError(_('No existen datos para generar informe'))
        obj_attch.unlink()
        obj_attch=self.env['ir.attachment'].create({
                                                    'name':nombre_archivo.split('.')[0]+'.pdf',
                                                    'datas':file,
                                                    'type':'binary', 
                                                    'store_fname':nombre_archivo.split('.')[0]+'.pdf'
                                                    })

        ##url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = "https://promoauto.odoo.com/web/content/%s?download=true"%(obj_attch.id) 

        return{
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }


    def job_enviar_correo_estado_cuenta(self):
        contratos_ids=self.env['contrato'].search([('state','in',['ACTIVADO','ADJUDICADO ENTREGADO','ADJUDICADO NO ENTREGADO'])])
        lis=[]
        for l in contratos_ids:
            if  l.cliente:   
                reporte_id=self.env['reporte.estado.de.cuenta'].create({'partner_id':l.cliente.id,
                                                                        'contrato_id':l.id})
                
                url_object=reporte_id.print_report_pdf()
                reporte_id.update({'url_doc': url_object['url']})
                self.envio_correos_plantilla('email_estado_cuenta',reporte_id.id)

    def envio_correos_plantilla(self, plantilla,id_envio):
        try:
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('gzl_adjudicacion', plantilla)[1]
        except ValueError:
            template_id = False
        if template_id:
            obj_template=self.env['mail.template'].browse(template_id)

            email_id=obj_template.send_mail(id_envio)
            obj_mail=self.env['mail.mail'].browse(email_id)
            obj_mail.send()


    def xslx_body(self, workbook, name):
        bold = workbook.add_format({'bold':True,'border':1})
        bold.set_center_across()
        format_title = workbook.add_format({'font_name':'Cambria','font_size':  16,'bold':True})
        format_title.set_center_across()
        format_subtitle = workbook.add_format({'font_name':'Arial','font_size':  14,'bold':True, 'bottom':1})
        format_subtitle.set_center_across()
        format_datos = workbook.add_format({'font_name':'Arial','font_size':  8,'align': 'left'})
        format_datos_cab = workbook.add_format({'font_name':'Arial','font_size':  8,'align': 'right'})
        num_contrato = workbook.add_format({'font_name':'Arial','font_size':  10,'bold':True,'align':'right'})

        currency_format = workbook.add_format({'font_name':'Arial','font_size':  8,'num_format': '[$$-409]#,##0.00','text_wrap': True,'align':'center' })
        currency_format.set_align('vcenter')
        formato_cabecera_tabla = workbook.add_format({'font_name':'Arial','font_size':  8,'align':'center','valign':'vcenter','bold':True, 'bottom':1, 'top':1,'text_wrap':True})
        formato_pie_tabla = workbook.add_format({'font_name':'Arial','font_size':  8,'align':'left','bold':True, 'bottom':1, 'top':1})
        date_format = workbook.add_format({'font_name':'Arial','font_size':  8,'num_format': 'yyyy-mm-dd', 'align': 'center','text_wrap': True })
        date_format.set_align('vcenter')
        date_format_day = workbook.add_format({'align': 'right','border':1,'text_wrap': True })
        date_format_day.set_align('vcenter')
        date_format_title = workbook.add_format({'num_format': 'yyyy-mm-dd', 'align': 'justify','text_wrap': True})
        date_format_title.set_align('vcenter')

        body = workbook.add_format({'align': 'vcenter','font_name':'Arial','font_size':8,'border':0,'text_wrap': True})
        sheet = workbook.add_worksheet(name)

        sheet.insert_image('B1', '../static/description/promoauto.png', {'x_offset': 15, 'y_offset': 10})
        sheet.merge_range('A3:I3', self.env.company.name, format_title)
        sheet.merge_range('A5:I5', self.env.company.street, format_datos)
        # self.env.company.city.name
        sheet.merge_range('A6:C6', self.env.company.city.upper() + ' - ' +self.env.company.country_id.name.upper(), format_datos)
        sheet.merge_range('A7:C7', "RUC: "+self.env.company.vat, format_datos)
        #         sheet.merge_range('H6:I6', self.contrato_id.ciudad.nombre_ciudad +', ' + self.create_date.strftime('%Y-%m-%d'), format_datos)

        if self.contrato_id.fecha_contrato:
            sheet.merge_range('G6:I6', self.env.company.city.upper() +', ' + self.contrato_id.fecha_contrato.strftime('%Y-%m-%d'), format_datos_cab)


        if self.contrato_id.secuencia:
            sheet.merge_range('G7:I7', 'No. ' + self.contrato_id.secuencia, num_contrato)
        sheet.merge_range('A8:I8', 'ESTADO DE CUENTA DE APORTES', format_subtitle)
        #
        if self.contrato_id.cliente:
            sheet.merge_range('A9:D9', 'Cliente: '+ self.contrato_id.cliente.name, format_datos)


        if self.contrato_id.grupo: 
            sheet.merge_range('A11:C11', 'Grupo: '+'['+ self.contrato_id.grupo.codigo+'] '+ self.contrato_id.grupo.name, format_datos)
        if self.contrato_id.state == 'ADJUDICADO':
            fecha_adjudicado_text=""
            if self.contrato_id.fecha_adjudicado:
                fecha_adjudicado_text= self.contrato_id.fecha_adjudicado.strftime('%Y-%m-%d')+')'



            sheet.merge_range('A12:C12', 'Estado: '+ self.contrato_id.state.upper() +'(' +fecha_adjudicado_text+')' , format_datos)
        else:
            sheet.merge_range('A12:C12', 'Estado: '+ self.contrato_id.state.upper(), format_datos)
        sheet.merge_range('A13:C13', 'Valor Inscripción: $'+ str('{:.2f}'.format(self.contrato_id.valor_inscripcion)), format_datos)
        
        if self.contrato_id.cliente:
            sheet.write('G9', 'Ced/RUC: '+ self.contrato_id.cliente.vat , format_datos)


        if self.contrato_id.tipo_de_contrato:
            sheet.write('G11', 'Tipo de contrato: '+ self.contrato_id.tipo_de_contrato.name.upper(), format_datos)
        sheet.write('G12', 'Monto financiamiento: $'+ str('{:.2f}'.format(self.contrato_id.monto_financiamiento)), format_datos)
        plazo_contrato=self.contrato_id.plazo_meses_numero
        if self.contrato_id.plazo_meses_numero==0:
            plazo_contrato=self.contrato_id.plazo_meses.numero
        sheet.write('G13', 'Plazo: '+ str(plazo_contrato)+ ' Meses' , format_datos)
        #
        title_main=['cuota','Fecha de Pago','Fecha Pagada','Cuota Capital' ,'Cuota Adm.','Iva','Seguro','Rastreo','Saldo']

        ##Titulos
        colspan=15
        for col, head in enumerate(title_main):
            sheet.set_column('{0}:{0}'.format(chr(col + ord('A'))),7)
            sheet.write(14, col, head.upper(), formato_cabecera_tabla)



        line = itertools.count(start=15)
        fila = 15
        fila_current=0
        total_cuota_capital=0
        total_cuota_adm=0
        total_iva_adm=0
        total_seguro=0
        total_rastreo=0
        total_otro=0
        total_saldo=0
        query="SELECT * FROM contrato_estado_cuenta where contrato_id={0}  order by fecha".format(self.contrato_id.id)
        self.env.cr.execute(query)
        estado_cuenta_ids=self.env.cr.dictfetchall()
        for linea in estado_cuenta_ids:
            current_line = next(line)
            sheet.write(current_line, 0, linea["numero_cuota"] ,body)
            sheet.write(current_line, 1, linea["fecha"], date_format)
            sheet.write(current_line, 2, linea["fecha_pagada"] or "", date_format)
            sheet.write(current_line, 3, linea["cuota_capital"] , currency_format)
            total_cuota_capital+=linea["cuota_capital"]
            if linea["programado"]:
                if linea["programado"]>0:
                    sheet.write(current_line, 3, linea["programado"] , currency_format)
                    total_cuota_capital+=linea["programado"]

            sheet.write(current_line, 4, linea["cuota_adm"] ,currency_format)           
            sheet.write(current_line, 5, linea["iva_adm"] ,currency_format)
            sheet.write(current_line, 6, linea["seguro"] or 0.00,currency_format)
            sheet.write(current_line, 7, linea["rastreo"] or 0.00,currency_format)
            sheet.write(current_line, 8, linea["saldo"] or 0.00, currency_format)
            if linea["cuota_adm"]:
                total_cuota_adm+=linea["cuota_adm"]
            if linea["iva_adm"]:
                total_iva_adm+=linea["iva_adm"]
            if linea["seguro"]:
                total_seguro+=linea["seguro"]
            if linea["rastreo"]:
                total_rastreo+=linea["rastreo"]
            if linea["otro"]:
                total_otro+=linea["otro"]
            if linea["saldo"]:
                total_saldo+=linea["saldo"]
            fila_current=current_line

        currency_bold=workbook.add_format({'num_format': '[$$-409]#,##0.00','text_wrap': True ,'font_name':'Arial','font_size':  8,'align':'center','bold':True, 'bottom':1, 'top':1})

        sheet.merge_range('A{0}:C{0}'.format(fila_current+2), 'TOTALES: ', formato_pie_tabla)
        sheet.write('D{0}'.format(fila_current+2), total_cuota_capital , currency_bold)
        sheet.write('E{0}'.format(fila_current+2), total_cuota_adm , currency_bold)
        sheet.write('F{0}'.format(fila_current+2), total_iva_adm , currency_bold)
        sheet.write('G{0}'.format(fila_current+2), total_seguro , currency_bold)
        sheet.write('H{0}'.format(fila_current+2), total_rastreo , currency_bold)
        sheet.write('I{0}'.format(fila_current+2), total_saldo , currency_bold)
        sheet.merge_range('A{0}:I{0}'.format(fila_current+3), '', formato_cabecera_tabla)


class ReporteEstadoDeCuentaMasivo(models.Model):
    _name = "reporte.estado.de.cuenta.masivo"


    partner_id = fields.Many2one('res.partner',string='Cliente')
    contrato_id = fields.Many2one('contrato',string='Contrato')
    adjunto_id = fields.Many2one('ir.attachment',string='Contrato PDF')
    url_doc = fields.Char('Url doc')    
    


    def print_report_pdf(self):
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data)
        name = 'Estado de Cuenta.xlsx'
        self.xslx_body(workbook, name)
        workbook.close()
        file_data.seek(0)
        obj_attch = self.env['ir.attachment'].create({
            'datas': base64.b64encode(file_data.getvalue()),
            'name': name,
            'store_fname': name,
            'type': 'binary',
        })

        direccion_xls_libro=self.env['ir.attachment']._get_path(obj_attch.datas,obj_attch.checksum)[1]
        nombre_bin=obj_attch.checksum
        nombre_archivo=obj_attch.name
        os.chdir(direccion_xls_libro.rstrip(nombre_bin))
        print(os.chdir(direccion_xls_libro.rstrip(nombre_bin)))
        os.rename(nombre_bin,nombre_archivo)
        subprocess.getoutput("""libreoffice --headless --convert-to pdf *.xlsx""") 
        try:
            with open(direccion_xls_libro.rstrip(nombre_bin)+nombre_archivo.split('.')[0]+'.pdf', "rb") as f:
                data = f.read()
                file=bytes(base64.b64encode(data))
        except:
            raise ValidationError(_('No existen datos para generar informe'))
        obj_attch.unlink()
        obj_attch=self.env['ir.attachment'].create({
                                                    'name':nombre_archivo.split('.')[0]+'.pdf',
                                                    'datas':file,
                                                    'type':'binary', 
                                                    'store_fname':nombre_archivo.split('.')[0]+'.pdf'
                                                    })

        ##url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = "https://promoauto.odoo.com/web/content/%s?download=true"%(obj_attch.id) 

        return obj_attch


    def job_enviar_correo_estado_cuenta(self,estado,grupo,tipo_de_contrato=False):
        if tipo_de_contrato:
            contratos_ids=self.env['contrato'].search([('state','=',estado),('grupo','=',grupo),('tipo_de_contrato','=',tipo_de_contrato)])
        else:
            contratos_ids=self.env['contrato'].search([('state','=',estado),('grupo','=',grupo),('id','in',[32041,32042])])

        lis=[]
        for l in contratos_ids:
            if  l.cliente:   
                reporte_id=self.env['reporte.estado.de.cuenta.masivo'].create({'partner_id':l.cliente.id,
                                                                        'contrato_id':l.id})
                
                url_object=reporte_id.print_report_pdf()
                reporte_id.update({'adjunto_id':url_object.id })
                self.envio_correos_plantilla('email_estado_cuenta',reporte_id)

    def envio_correos_plantilla(self, plantilla,id_envio):
        try:
            ir_model_data = self.env['ir.model.data']
            template_id = ir_model_data.get_object_reference('gzl_adjudicacion', plantilla)[1]
        except ValueError:
            template_id = False
        if template_id:
            lista_adjunto=[]
            obj_template=self.env['mail.template'].browse(template_id)

            email_id=obj_template.send_mail(id_envio.id)
            obj_mail=self.env['mail.mail'].browse(email_id)
            lista_adjunto.append(int(id_envio.adjunto_id.id))
            obj_mail.update({'attachment_ids':[(6,0,lista_adjunto)],'auto_delete':False}) 
            obj_mail.send()


    def xslx_body(self, workbook, name):
        bold = workbook.add_format({'bold':True,'border':1})
        bold.set_center_across()
        format_title = workbook.add_format({'font_name':'Cambria','font_size':  16,'bold':True})
        format_title.set_center_across()
        format_subtitle = workbook.add_format({'font_name':'Arial','font_size':  14,'bold':True, 'bottom':1})
        format_subtitle.set_center_across()
        format_datos = workbook.add_format({'font_name':'Arial','font_size':  8,'align': 'left'})
        format_datos_cab = workbook.add_format({'font_name':'Arial','font_size':  8,'align': 'right'})
        num_contrato = workbook.add_format({'font_name':'Arial','font_size':  10,'bold':True,'align':'right'})

        currency_format = workbook.add_format({'font_name':'Arial','font_size':  8,'num_format': '[$$-409]#,##0.00','text_wrap': True,'align':'center' })
        currency_format.set_align('vcenter')
        formato_cabecera_tabla = workbook.add_format({'font_name':'Arial','font_size':  8,'align':'center','valign':'vcenter','bold':True, 'bottom':1, 'top':1,'text_wrap':True})
        formato_pie_tabla = workbook.add_format({'font_name':'Arial','font_size':  8,'align':'left','bold':True, 'bottom':1, 'top':1})
        date_format = workbook.add_format({'font_name':'Arial','font_size':  8,'num_format': 'yyyy-mm-dd', 'align': 'center','text_wrap': True })
        date_format.set_align('vcenter')
        date_format_day = workbook.add_format({'align': 'right','border':1,'text_wrap': True })
        date_format_day.set_align('vcenter')
        date_format_title = workbook.add_format({'num_format': 'yyyy-mm-dd', 'align': 'justify','text_wrap': True})
        date_format_title.set_align('vcenter')

        body = workbook.add_format({'align': 'vcenter','font_name':'Arial','font_size':8,'border':0,'text_wrap': True})
        sheet = workbook.add_worksheet(name)

        sheet.insert_image('B1', '../static/description/promoauto.png', {'x_offset': 15, 'y_offset': 10})
        sheet.merge_range('A3:I3', self.env.company.name, format_title)
        sheet.merge_range('A5:I5', self.env.company.street, format_datos)
        # self.env.company.city.name
        sheet.merge_range('A6:C6', self.env.company.city.upper() + ' - ' +self.env.company.country_id.name.upper(), format_datos)
        sheet.merge_range('A7:C7', "RUC: "+self.env.company.vat, format_datos)
        #         sheet.merge_range('H6:I6', self.contrato_id.ciudad.nombre_ciudad +', ' + self.create_date.strftime('%Y-%m-%d'), format_datos)

        if self.contrato_id.fecha_contrato:
            sheet.merge_range('G6:I6', self.env.company.city.upper() +', ' + self.contrato_id.fecha_contrato.strftime('%Y-%m-%d'), format_datos_cab)


        if self.contrato_id.secuencia:
            sheet.merge_range('G7:I7', 'No. ' + self.contrato_id.secuencia, num_contrato)
        sheet.merge_range('A8:I8', 'ESTADO DE CUENTA DE APORTES', format_subtitle)
        #
        if self.contrato_id.cliente:
            sheet.merge_range('A9:D9', 'Cliente: '+ self.contrato_id.cliente.name, format_datos)


        if self.contrato_id.grupo: 
            sheet.merge_range('A11:C11', 'Grupo: '+'['+ self.contrato_id.grupo.codigo+'] '+ self.contrato_id.grupo.name, format_datos)
        if self.contrato_id.state == 'ADJUDICADO':
            fecha_adjudicado_text=""
            if self.contrato_id.fecha_adjudicado:
                fecha_adjudicado_text= self.contrato_id.fecha_adjudicado.strftime('%Y-%m-%d')+')'



            sheet.merge_range('A12:C12', 'Estado: '+ self.contrato_id.state.upper() +'(' +fecha_adjudicado_text+')' , format_datos)
        else:
            sheet.merge_range('A12:C12', 'Estado: '+ self.contrato_id.state.upper(), format_datos)
        sheet.merge_range('A13:C13', 'Valor Inscripción: $'+ str('{:.2f}'.format(self.contrato_id.valor_inscripcion)), format_datos)
        
        if self.contrato_id.cliente:
            sheet.write('G9', 'Ced/RUC: '+ self.contrato_id.cliente.vat , format_datos)


        if self.contrato_id.tipo_de_contrato:
            sheet.write('G11', 'Tipo de contrato: '+ self.contrato_id.tipo_de_contrato.name.upper(), format_datos)
        sheet.write('G12', 'Monto financiamiento: $'+ str('{:.2f}'.format(self.contrato_id.monto_financiamiento)), format_datos)
        plazo_contrato=self.contrato_id.plazo_meses_numero
        if self.contrato_id.plazo_meses_numero==0:
            plazo_contrato=self.contrato_id.plazo_meses.numero
        sheet.write('G13', 'Plazo: '+ str(plazo_contrato)+ ' Meses' , format_datos)
        #
        title_main=['cuota','Fecha de Pago','Fecha Pagada','Cuota Capital' ,'Cuota Adm.','Iva','Seguro','Rastreo','Saldo']

        ##Titulos
        colspan=15
        for col, head in enumerate(title_main):
            sheet.set_column('{0}:{0}'.format(chr(col + ord('A'))),7)
            sheet.write(14, col, head.upper(), formato_cabecera_tabla)



        line = itertools.count(start=15)
        fila = 15
        fila_current=0
        total_cuota_capital=0
        total_cuota_adm=0
        total_iva_adm=0
        total_seguro=0
        total_rastreo=0
        total_otro=0
        total_saldo=0
        query="SELECT * FROM contrato_estado_cuenta where contrato_id={0}  order by fecha".format(self.contrato_id.id)
        self.env.cr.execute(query)
        estado_cuenta_ids=self.env.cr.dictfetchall()
        for linea in estado_cuenta_ids:
            current_line = next(line)
            sheet.write(current_line, 0, linea["numero_cuota"] ,body)
            sheet.write(current_line, 1, linea["fecha"], date_format)
            sheet.write(current_line, 2, linea["fecha_pagada"] or "", date_format)
            sheet.write(current_line, 3, linea["cuota_capital"] , currency_format)
            total_cuota_capital+=linea["cuota_capital"]
            if linea["programado"]:
                if linea["programado"]>0:
                    sheet.write(current_line, 3, linea["programado"] , currency_format)
                    total_cuota_capital+=linea["programado"]

            sheet.write(current_line, 4, linea["cuota_adm"] ,currency_format)           
            sheet.write(current_line, 5, linea["iva_adm"] ,currency_format)
            sheet.write(current_line, 6, linea["seguro"] or 0.00,currency_format)
            sheet.write(current_line, 7, linea["rastreo"] or 0.00,currency_format)
            sheet.write(current_line, 8, linea["saldo"] or 0.00, currency_format)
            if linea["cuota_adm"]:
                total_cuota_adm+=linea["cuota_adm"]
            if linea["iva_adm"]:
                total_iva_adm+=linea["iva_adm"]
            if linea["seguro"]:
                total_seguro+=linea["seguro"]
            if linea["rastreo"]:
                total_rastreo+=linea["rastreo"]
            if linea["otro"]:
                total_otro+=linea["otro"]
            if linea["saldo"]:
                total_saldo+=linea["saldo"]
            fila_current=current_line

        currency_bold=workbook.add_format({'num_format': '[$$-409]#,##0.00','text_wrap': True ,'font_name':'Arial','font_size':  8,'align':'center','bold':True, 'bottom':1, 'top':1})

        sheet.merge_range('A{0}:C{0}'.format(fila_current+2), 'TOTALES: ', formato_pie_tabla)
        sheet.write('D{0}'.format(fila_current+2), total_cuota_capital , currency_bold)
        sheet.write('E{0}'.format(fila_current+2), total_cuota_adm , currency_bold)
        sheet.write('F{0}'.format(fila_current+2), total_iva_adm , currency_bold)
        sheet.write('G{0}'.format(fila_current+2), total_seguro , currency_bold)
        sheet.write('H{0}'.format(fila_current+2), total_rastreo , currency_bold)
        sheet.write('I{0}'.format(fila_current+2), total_saldo , currency_bold)
        sheet.merge_range('A{0}:I{0}'.format(fila_current+3), '', formato_cabecera_tabla)




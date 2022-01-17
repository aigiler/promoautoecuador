# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from datetime import date, timedelta,datetime
from dateutil.relativedelta import relativedelta
import xlsxwriter
from io import BytesIO
import base64
from odoo.exceptions import AccessError, UserError, ValidationError
from .funciones import *
import calendar
import datetime as tiempo
import itertools




class ReporteAnticipo(models.TransientModel):
    _name = "report.impuestos"
    #_inherit = "reporte.proveedor.cliente"
    date_from = fields.Date('Desde')
    date_to = fields.Date('Hasta')
    def obtener_listado_retenciones(self,filtro,variable,tipo_imp,taxes):
        
        documents = [ 'out_invoice', 
                    'in_invoice', 
                    'out_refund', 
                    'in_refund', 
                    'out_debit',
                    'in_debit',
                    'liq_purchase']
        filtro.append(('type','in',documents))            


#######filtro de facturas
        lista_retenciones=[]
        #TAXES = ['ret_vat_b', 'ret_vat_srv', 'ret_ir', 'no_ret_ir'] 
        ingeg=['vat','vat0']
        move=self.env['account.retention'].search(filtro)
        #raise ValidationError((str(len(move))))
        cont=0
        dct={}
        for line in move:
            obj_line=self.env['account.retention.line'].search([('retention_id','=',line.id)], order ='id desc')
            #raise ValidationError((str(obj_line)))
            
            #for line in obj_line:
                #raise ValidationError((str(line.tax_ids.name)))
            
            if obj_line:
                #raise ValidationError((str(obj_line)))
                for i in obj_line:
                    #obj_tax=self.env['account.tax'].search([('name','=',i.name)], order ='name desc')
                    if tipo_imp =='ret':
                        if variable == i.tax_id.type_tax_use and i.group_id.code in taxes :
                            cont=cont+1
                            dct={}
                            #if name[cont-1].name== a.name:
                            dct['id']=line.id 
                            dct['move']=line.invoice_id.id
                            dct['name_ret']=i.tax_id.name
                            dct['cod_ret']=i.code
                            dct['code_group']=i.group_id.code
                            dct['name_group']=i.group_id.name
                            dct['amount']=i.base_ret
                            dct['valor_retenido']=i.amount
                            lista_retenciones.append(dct)    
        #if cont:
         #   raise ValidationError((str(cont)+' cont'))
        return lista_retenciones
    def obtener_listado_partner_payment(self,filtro,variable,tipo_imp):
        
        documents = [ 'out_invoice', 
                    'in_invoice', 
                    'out_refund', 
                    'in_refund', 
                    'out_debit',
                    'in_debit',
                    'liq_purchase']
        filtro.append(('type','in',documents))            


#######filtro de facturas
        lista_retenciones=[]
        TAXES = ['ret_vat_b', 'ret_vat_srv', 'ret_ir', 'no_ret_ir'] 
        ingeg=['vat','vat0']
        move=self.env['account.move'].search(filtro)
        for l in move:
            obj_line=self.env['account.move.line'].search([('move_id','=',l.id)])
            #raise ValidationError((str(obj_line)))
            
            for line in obj_line:
                #raise ValidationError((str(line.tax_ids.name)))
                dct={}
                if line.tax_ids:
                    #raise ValidationError((str(line.tax_ids.name)))
                    for i in line.tax_ids:
                        obj_tax=self.env['account.tax'].search([('name','=',i.name)], order ='name desc')
                        if tipo_imp =='ret':
                            if variable == i.type_tax_use and i.tax_group_id.code in TAXES :
                                
                                #if name[cont-1].name== a.name:
                                dct['id']=line.id 
                                dct['move']=line.move_id
                                dct['name_ret']=i.name
                                dct['cod_ret']=i.l10n_ec_code_applied
                                dct['code_group']=i.tax_group_id.code
                                dct['name_group']=i.tax_group_id.name
                                dct['amount']=line.price_subtotal
                                lista_retenciones.append(dct)
                        elif tipo_imp =='ie':
                            if variable == i.type_tax_use and i.tax_group_id.code in ingeg :
                                dct['id']=line.id 
                                dct['move']=line.move_id
                                dct['name']=i.name
                                if l.type_name:
                                    dct['tipo_doc']=l.type
                                else:
                                    dct['tipo_doc']='Null'
                                dct['code']=i.l10n_ec_code_applied
                                dct['code_group']=i.tax_group_id.code
                                dct['name_group']=i.tax_group_id.name
                                dct['amount']=line.price_subtotal
                                lista_retenciones.append(dct)                                

        return lista_retenciones
    def print_report_xls(self):
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data)
        name = 'RETENCIONES'
        self.xslx_body(workbook, name)
        
        name = 'INGRESOS-EGRESOS'
        self.xslx_body_ing_eg(workbook, name)

        workbook.close()
        file_data.seek(0)
        
        
        name = 'Reporte de Impuestos'

        
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
        bold = workbook.add_format({'bold':True,'border':0})
        bold_no_border = workbook.add_format({'bold':True})
        bold.set_center_across()
        format_title = workbook.add_format({'bold':True,'border':1})
        format_title_left = workbook.add_format({'bold':True,'border':1,'align': 'left'})
        format_title_left_14 = workbook.add_format({'bold':True,'border':1,'align': 'left','size': 14})
        format_title_center_14 = workbook.add_format({'bold':True,'border':1,'align': 'center','size': 14})


        format_title.set_center_across()
        currency_format = workbook.add_format({'num_format': '[$$-409]#,##0.00','border':1,'text_wrap': True })
        currency_format.set_align('vcenter')

        
        date_format = workbook.add_format({'num_format': 'dd/mm/yy', 'align': 'right','border':1,'text_wrap': True })
        date_format.set_align('vcenter')
        date_format_day = workbook.add_format({'align': 'right','border':1,'text_wrap': True })
        date_format_day.set_align('vcenter')
        date_format_title = workbook.add_format({'num_format': 'dd/mm/yy', 'align': 'left','text_wrap': True})
        date_format_title.set_align('vcenter')

        body = workbook.add_format({'align': 'center' , 'border':1,'text_wrap': True})
        body.set_align('vcenter')
        body_right = workbook.add_format({'align': 'right', 'border':1 })
        body_left = workbook.add_format({'align': 'left','bold':True})
        format_title2 = workbook.add_format({'align': 'center', 'bold':False,'border':0 })
        sheet = workbook.add_worksheet(name)

        sheet.set_portrait()
        sheet.set_paper(9)  # A4

        sheet.set_margins(left=0.4, right=0.4, top=0.4, bottom=0.2)
        sheet.set_print_scale(100)
        sheet.fit_to_pages(1,2)



        
        sheet.merge_range('B1:F1', self.env.company.name.upper(), workbook.add_format({'bold':True,'border':0,'align': 'center','size': 14}))
        sheet.merge_range('B2:F2', 'INFORME DE IMPUESTOS SOBRE RENTENCIONES EN COMPRAS Y VENTAS ', workbook.add_format({'bold':True,'border':0,'align': 'center'}))
 



        title_main=['Codigo de retención ','Concepto de retención ', 'Base imponible ', 'Valor retenido ']
        bold.set_bg_color('b8cce4')

        ##Titulos
        filtro=[('date','>=',self.date_from),
            ('date','<=',self.date_to),('company_id', '=', self.env.company.id),('state', '=', 'done')]        
        taxes= ['ret_vat_srv','ret_vat_b']
        ret_purchase=self.obtener_listado_retenciones(filtro,'purchase','ret',taxes) 
        
        fila=5
        columna=1
        fila_base=0
        fila_tit_renta=0
        fila_tit_iva=0
        if ret_purchase:
            colspan=4
            fila+=1
            fila_tit_iva = fila
            cont =0
            for l in ret_purchase:
                    #fila+=1                    
                #raise ValidationError((str(l)))
                if l['code_group'] in ['ret_vat_srv','ret_vat_b']:
                    cont =cont+1
                    if cont ==1:
                        sheet.merge_range('B'+str(fila)+':F'+str(fila), 'REPORTE DE RETENCIONES AL IVA  EN COMPRAS ', workbook.add_format({'bold':True,'border':0,'align': 'center','size': 14})) 
                        fila+=1
                        for col, head in enumerate(title_main):
                            sheet.set_column('{0}:{0}'.format(chr(col + ord('A'))), len(head) + 7)
                            sheet.write(fila, col+1, head, bold)   
                        fila_base=fila+1
                    ret_iva= True
                    fila+=1
                    
                    sheet.write(fila, columna, str(l['cod_ret']), format_title2)
                    #columna+=1
                    sheet.write(fila, columna+1, l['name_ret'], format_title2)
                    sheet.write(fila, columna+2, l['amount'], format_title2)
                    sheet.write(fila, columna+3, l['valor_retenido'], format_title2)
                    #sheet.write(fila, columna+4, l['id'], format_title2)
            #raise ValidationError((str(fila)))
            fila=fila+1
            sheet.write(fila, 2, 'Total', format_title2)
            sheet.write(fila,3, '=+SUM(D'+str(fila_base)+':D'+str(fila)+')', format_title2)
            sheet.write(fila,4, '=+SUM(E'+str(fila_base)+':E'+str(fila)+')', format_title2)
            cont =0
            fila_base=0
            fila=fila+2
            taxes= ['ret_ir','no_ret_ir']
            ret_purchase2=self.obtener_listado_retenciones(filtro,'purchase','ret',taxes) 
            for r in ret_purchase2:
                #raise ValidationError((str(l)))
                if r['code_group']  in ['ret_ir','no_ret_ir']:
                    cont =cont +1 
                    if cont ==1:
                        sheet.merge_range('B'+str(fila)+':F'+str(fila), 'REPORTE DE RETENCIONES A LA RENTA  EN COMPRAS ', workbook.add_format({'bold':True,'border':0,'align': 'center','size': 14}))
                        fila+=1
                        for col, head in enumerate(title_main):
                            sheet.set_column('{0}:{0}'.format(chr(col + ord('A'))), len(head) + 7)
                            sheet.write(fila, col+1, head, bold)
                        fila_base=fila+1
                                        
                    ret_renta= True
                    fila+=1
                    #raise ValidationError((str(fila)))
                    sheet.write(fila, columna, str(r['cod_ret']), format_title2)
                    #columna+=1
                    sheet.write(fila, columna+1, r['name_ret'], format_title2)
                    sheet.write(fila, columna+2, r['amount'], format_title2)
                    sheet.write(fila, columna+3, r['valor_retenido'], format_title2)
                    #sheet.write(fila, columna+4, l['id'], format_title2)
                    #fila+=1 
            fila+=1
            sheet.write(fila, 2, 'Total', format_title2)
            sheet.write(fila,3, '=+SUM(D'+str(fila_base)+':D'+str(fila)+')', format_title2)
            sheet.write(fila,4, '=+SUM(E'+str(fila_base)+':E'+str(fila)+')', format_title2)            
            fila+=1
            #raise ValidationError((str(fila)))
 
        #######################VENTA#################################################################################333
        taxes=['ret_vat_srv','ret_vat_b']
        ret_venta=self.obtener_listado_retenciones(filtro,'sale','ret',taxes)
        fila_tit_renta=0
        fila_tit_iva=0
        if ret_venta:
            cont=0
            colspan=4
            fila+=1
            fila_tit_iva=fila
            fila_base =0
            for p in ret_venta:
                #raise ValidationError((str(l)))
                if l['code_group'] in ['ret_vat_srv','ret_vat_b']:
                    cont+=1
                    if cont == 1:
                        sheet.merge_range('B'+str(fila)+':F'+str(fila), 'REPORTE DE RETENCIONES AL IVA  EN  VENTAS ', workbook.add_format({'bold':True,'border':0,'align': 'center','size': 14}))
                        fila+=1
                        for col, head in enumerate(title_main):
                            sheet.set_column('{0}:{0}'.format(chr(col + ord('A'))), len(head) + 7)
                            sheet.write(fila, col+1, head, bold)       
                        fila_base=fila+1
                    fila+=1
                    #raise ValidationError((str(fila)))
                    sheet.write(fila, columna, str(p['cod_ret']), format_title2)
                    sheet.write(fila, columna+1, p['name_ret'], format_title2)
                    sheet.write(fila, columna+2, p['amount'], format_title2)
                    sheet.write(fila, columna+3, p['valor_retenido'], format_title2)
                    #sheet.write(fila, columna+4, l['id'], format_title2)
                    #fila+=1
            fila+=1
            sheet.write(fila, 2, 'Total', format_title2)
            sheet.write(fila,3, '=+SUM(D'+str(fila_base)+':D'+str(fila)+')', format_title2)
            sheet.write(fila,4, '=+SUM(E'+str(fila_base)+':E'+str(fila)+')', format_title2)    
            fila+=1
            cont =0
            fila_base =0
            taxes=['ret_ir','no_ret_ir']
            ret_venta2=self.obtener_listado_retenciones(filtro,'sale','ret',taxes)
            for vent in ret_venta2:
                if vent['code_group'] not in ['ret_vat_srv','ret_vat_b']:
                    cont +=1
                    if cont == 1:
                        sheet.merge_range('B'+str(fila)+':F'+str(fila), 'REPORTE DE RETENCIONES A LA RENTA  EN  VENTAS ', workbook.add_format({'bold':True,'border':0,'align': 'center','size': 14}))
                        fila+=1
                        for col, head in enumerate(title_main):
                            sheet.set_column('{0}:{0}'.format(chr(col + ord('A'))), len(head) + 7)
                            sheet.write(fila, col+1, head, bold) 
                        fila_base=fila+1
                    fila+=1
                    sheet.write(fila, columna, str(vent['cod_ret']), format_title2)
                    sheet.write(fila, columna+1, vent['name_ret'], format_title2)
                    sheet.write(fila, columna+2, vent['amount'], format_title2)
                    sheet.write(fila, columna+3, vent['valor_retenido'], format_title2)
                    #sheet.write(fila, columna+4, l['id'], format_title2)
                    #fila+=1
                         
            fila+=1
            sheet.write(fila, 2, 'Total', format_title2)
            sheet.write(fila,3, '=+SUM(D'+str(fila_base)+':D'+str(fila)+')', format_title2)
            sheet.write(fila,4, '=+SUM(E'+str(fila_base)+':E'+str(fila)+')', format_title2)  
        sheet.set_column('A:A', 23)
        sheet.set_column('B:B', 23)
        sheet.set_column('H:H', 60)



    def xslx_body_ing_eg(self, workbook, name):
        bold = workbook.add_format({'bold':True,'border':0})
        bold_no_border = workbook.add_format({'bold':True})
        bold.set_center_across()
        format_title = workbook.add_format({'bold':True,'border':1})
        format_title_left = workbook.add_format({'bold':True,'border':1,'align': 'left'})
        format_title_left_14 = workbook.add_format({'bold':True,'border':1,'align': 'left','size': 14})
        format_title_center_14 = workbook.add_format({'bold':True,'border':1,'align': 'center','size': 14})


        format_title.set_center_across()
        currency_format = workbook.add_format({'num_format': '[$$-409]#,##0.00','border':1,'text_wrap': True })
        currency_format.set_align('vcenter')

        
        date_format = workbook.add_format({'num_format': 'dd/mm/yy', 'align': 'right','border':1,'text_wrap': True })
        date_format.set_align('vcenter')
        date_format_day = workbook.add_format({'align': 'right','border':1,'text_wrap': True })
        date_format_day.set_align('vcenter')
        date_format_title = workbook.add_format({'num_format': 'dd/mm/yy', 'align': 'left','text_wrap': True})
        date_format_title.set_align('vcenter')

        body = workbook.add_format({'align': 'center' , 'border':1,'text_wrap': True})
        body.set_align('vcenter')
        body_right = workbook.add_format({'align': 'right', 'border':1 })
        body_left = workbook.add_format({'align': 'left','bold':True})
        format_title2 = workbook.add_format({'align': 'center', 'bold':False,'border':0 })
        sheet = workbook.add_worksheet(name)

        sheet.set_portrait()
        sheet.set_paper(9)  # A4

        sheet.set_margins(left=0.4, right=0.4, top=0.4, bottom=0.2)
        sheet.set_print_scale(100)
        sheet.fit_to_pages(1,2)



        
        sheet.merge_range('B3:F3', self.env.company.name.upper(), workbook.add_format({'bold':True,'border':0,'align': 'center','size': 14}))
        sheet.merge_range('B4:F4', 'INFORME DE IMPUESTOS SOBRE COMPRAS Y VENTAS ', workbook.add_format({'bold':True,'border':0,'align': 'center'}))
 



        title_main=['RESUMEN DE ADQUISICIONES Y PAGOS ','CODIGO', 'VALOR BRUTO', 'VALOR NETO','IMPUESTO GENERADO']
        bold.set_bg_color('b8cce4')
        ##Titulos
        filtro=[('invoice_date','>=',self.date_from),
            ('invoice_date','<=',self.date_to),('company_id', '=', self.env.company.id),('state', '=', 'posted')]        
        ret_purchase=self.obtener_listado_partner_payment(filtro,'purchase','ie') 
        fila=5
        columna=1
        ret_iva=False
        ret_renta=False
        fila_tit_renta=0
        fila_tit_iva=0
        cont_invoice=0
        if ret_purchase:
            colspan=4
            fila_tit_iva = fila
            for l in ret_purchase:
                #raise ValidationError((str(l)))
                #if l['code_group'] in ['ret_vat_srv','ret_vat_b']:
                ret_iva= True
                fila+=1
                if l['tipo_doc'] in ['in_invoice','out_invoice']:
                    cont_invoice+=1
                sheet.write(fila, columna, str(l['name']), format_title2)
                #columna+=1
                sheet.write(fila, columna+1, l['code'], format_title2)
                sheet.write(fila, columna+2, l['amount'], format_title2)#tipo_doc
                sheet.write(fila, columna+3, l['tipo_doc'], format_title2)
            fila_tit_renta = fila +1    
            if ret_iva:
               
               for col, head in enumerate(title_main):
                    sheet.set_column('{0}:{0}'.format(chr(col + ord('A'))), len(head) + 7)
                    sheet.write(fila_tit_iva+1, col+1, head, bold)
            fila+=2
            sheet.write(fila, columna, 'TOTAL COMPRAS ', format_title2)
            sheet.write(fila, columna+2, '=+SUM(D8:D'+str(fila-1)+')', format_title2)
            fila=fila +2
            sheet.write(fila, columna, 'RESUMEN DE DOCUMENTOS', format_title2)
            if cont_invoice > 1:
                #raise ValidationError((str(fila)))
                sheet.write(fila,columna+2, 'FACTURAS', format_title2)
                sheet.write(fila,columna+3, str(cont_invoice), format_title2)
        #######################VENTA
        ret_venta=self.obtener_listado_partner_payment(filtro,'sale','ie')
        fila_tit_renta=0
        fila_tit_iva=0
        cont_invoice=0
        if ret_venta:
            ret_iva=False
            ret_renta=False
            colspan=4
            
            fila_tit_iva=fila
            fila+=2
            for p in ret_venta:
                #raise ValidationError((str(l)))
                #if l['code_group'] in ['ret_vat_srv','ret_vat_b']:
                ret_iva= True
                fila+=1
                if l['tipo_doc'] in ['in_invoice','out_invoice']:
                    cont_invoice+=1
                #raise ValidationError((str(fila)))
                sheet.write(fila, columna, str(p['name']), format_title2)
                sheet.write(fila, columna+1, p['code'], format_title2)
                sheet.write(fila, columna+2, p['amount'], format_title2)
                sheet.write(fila, columna+3, p['tipo_doc'], format_title2)
                    #fila+=1
            fila_tit_renta=fila+1
            title_main=['RESUMEN DE VENTAS - INGRESOS','CODIGO', 'VALOR BRUTO', 'VALOR NETO','IMPUESTO GENERADO']
            if ret_iva:
                
                fila+=1
                for col, head in enumerate(title_main):
                    sheet.set_column('{0}:{0}'.format(chr(col + ord('A'))), len(head) + 7)
                    sheet.write(fila_tit_iva+2, col+1, head, bold)
                    
            fila+=2
            sheet.write(fila, columna, 'TOTAL COMPRAS ', format_title2)
            sheet.write(fila, columna+2, '=+SUM(D'+str(fila_tit_iva+2)+':D'+str(fila-1)+')', format_title2)
            fila=fila+2
            sheet.write(fila, columna, 'RESUMEN DE DOCUMENTOS', format_title2)
            if cont_invoice > 1:
                #raise ValidationError((str(fila)))
                sheet.write(fila,columna+2, 'FACTURAS', format_title2)
                sheet.write(fila,columna+3, str(cont_invoice), format_title2)                
                          
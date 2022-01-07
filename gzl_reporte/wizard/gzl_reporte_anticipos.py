
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


class ReporteAnticipo(models.TransientModel):
    _name = "reporte.anticipo"

    partner_id =  fields.Many2one('res.partner',string='Socio',)





    def print_report_xls(self):
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data)
        name = 'Informe de Credito y Cobranza'
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
        format_title2 = workbook.add_format({'align': 'center', 'bold':True,'border':1 })
        sheet = workbook.add_worksheet(name)

        sheet.set_portrait()
        sheet.set_paper(9)  # A4

        sheet.set_margins(left=0.4, right=0.4, top=0.4, bottom=0.2)
        sheet.set_print_scale(100)
        sheet.fit_to_pages(1,2)



        
        sheet.merge_range('A1:G1', self.env.company.name.upper(), workbook.add_format({'bold':True,'border':0,'align': 'left','size': 14}))
        sheet.merge_range('A2:G2', 'RUC: '+self.env.company.vat, workbook.add_format({'bold':True,'border':0,'align': 'left'}))
        sheet.merge_range('A3:G3', 'Dirección: '+self.env.company.street, workbook.add_format({'bold':True,'border':0,'align': 'left'}))
        sheet.merge_range('A4:G4', 'Teléfono: '+self.env.company.phone, workbook.add_format({'bold':True,'border':0,'align': 'left'}))

        sheet.merge_range('A5:G5', 'Informe de Credito y Cobranza', workbook.add_format({'bold':True,'border':0,'align': 'center','size': 14}))
        bold.set_bg_color('b8cce4')
        
        



    def print_report_pdf(self):
        return self.env.ref('gzl_reporte.repote_anticipo_pdf_id').report_action(self)



        
    def obtenerDatos(self,):

        filtro=[('payment_date','>=',self.date_from),
            ('payment_date','<=',self.date_to),('tipo_transaccion','=','Anticipo')]


        lista_partner=self.obtener_listado_partner_payment(filtro)
        lines=[]
        

        for partner in lista_partner:
            filtro=[('payment_date','>=',self.date_from),
                ('payment_date','<=',self.date_to),('tipo_transaccion','=','Anticipo')]
            
            lines.append({'numero_documento':partner['nombre'],'reglon':'titulo'})

            lista_anticipos=self.obtener_listado_payment_por_empresa(partner['id'],filtro)
            for dct in lista_anticipos:
                dct['reglon']='detalle'
                lines.append(dct)
            dctTotal={}
            dctTotal['numero_documento']='Total '+ partner['nombre']

            dctTotal['monto_anticipo']=round(sum(map(lambda x:x['monto_anticipo'],lista_anticipos)),2)
            dctTotal['monto_aplicado']=round(sum(map(lambda x:x['monto_aplicado'],lista_anticipos)),2)
            dctTotal['monto_adeudado']=round(sum(map(lambda x:x['monto_adeudado'],lista_anticipos)),2)
            dctTotal['reglon']='total_detalle'


            lines.append(dctTotal)
        dctTotalGeneral={}
        dctTotalGeneral['numero_documento']='Total General'

        dctTotalGeneral['monto_anticipo']=round(sum(map(lambda x:x['monto_anticipo'],list(filter(lambda x: x['reglon']=='total_detalle', lines)))),2)
        dctTotalGeneral['monto_aplicado']=round(sum(map(lambda x:x['monto_aplicado'],list(filter(lambda x: x['reglon']=='total_detalle', lines)))),2)
        dctTotalGeneral['monto_adeudado']=round(sum(map(lambda x:x['monto_adeudado'],list(filter(lambda x: x['reglon']=='total_detalle', lines)))),2)
        dctTotalGeneral['reglon']='total_general'

        lines.append(dctTotalGeneral)
        lista_obj=[]
        for l in lines:
            obj_detalle=self.env['reporte.anticipo.detalle'].create(l)
            lista_obj.append(obj_detalle)

        return lista_obj



class ReporteAnticipoDetalle(models.TransientModel):
    _name = "reporte.anticipo.detalle"

    numero_documento = fields.Char('Nro. Documento')
    fecha_emision = fields.Date('Fc. Emision')
    fecha_vencimiento = fields.Date('Fc. Vencimiento')
    monto_anticipo = fields.Float('Monto Anticipo')
    monto_aplicado = fields.Float('Monto Aplicado')
    monto_adeudado = fields.Float('Monto Adeudado')
    observaciones = fields.Char('Observaciones')
    reglon = fields.Char('Reglon')


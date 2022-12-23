# -*- coding: utf-8 -*-
import string
from odoo import api, fields, models, tools
from datetime import date, timedelta, datetime
from dateutil import relativedelta as rdelta 
import xlsxwriter
from io import BytesIO
import base64
from odoo.exceptions import ValidationError

class ReportAdjudicados(models.TransientModel):
    _name = "reporte.adjudicados"

    grupo=fields.Many2one('grupo.adjudicado',string="Grupo")

    def print_report_xls(self):
        today = date.today()
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data)
        name = 'REPORTE DE ADJUDICADOS '+ str(today.year)
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
        
        formato_fecha = workbook.add_format({'align':'center','valign':'vcenter','font_size': 13,'text_wrap':True,
                                                'border':True,'bg_color':'#FFFFFF','color':'#0f0000','num_format': 'dd/mm/yy'})
        formato_numero = workbook.add_format({'align':'center','valign':'vcenter','font_size': 13,'text_wrap':True,
                                            'border':True,'bg_color':'#FFFFFF','color':'#0f0000','num_format': '#,##0.00'})
        registros_tabla= workbook.add_format({'align':'center','valign':'vcenter','font_size': 13,'text_wrap':True,
                                                'border':True,'bg_color':'#FFFFFF','color':'#0f0000'})

        bold = workbook.add_format({'bold':True,'border':True, 'bg_color':'#442484','color':'#FFFFFF'})
        bold.set_center_across()
        bold.set_font_size(14)

        bold2 = workbook.add_format({'align':'center','valign':'vcenter','bold':True,'font_size': 13, 'bg_color':'#989899',
                                    'color':'#FFFFFF','text_wrap':True,'border':True})
        bold2.set_center_across()

        sheet = workbook.add_worksheet(name)

        sheet.insert_image('A1', "any_name.png",
                           {'image_data':  BytesIO(base64.b64decode( self.env.company.imagen_excel_company)), 'x_scale': 0.9, 'y_scale': 0.8,'x_scale': 0.8,
                            'y_scale':     0.8, 'align': 'left','bg_color':'#442484'})
        
        sheet.merge_range('A1:O1', ' ', bold)
        sheet.merge_range('A2:O2', 'REPORTE DE ADJUDICADOS', bold)
        query="SELECT * FROM contrato WHERE state='ADJUDICADO'"
        if self.grupo:
            query+=" and grupo={0} ".format(self.grupo.id)
        self.env.cr.execute(query)
        contrato_ids=self.env.cr.dictfetchall()
        lista_final=[]
        for contrato_id in contrato_ids:
            contrato=self.env['contrato'].search([('id','=',contrato_id['id'])])
            dct={'grupo':contrato.grupo.name or '',
                    'socio':contrato.cliente.name  or '',
                    'fecha_adjudicado':contrato.fecha_adjudicado or '',
                    'fecha_entrega':contrato.fecha_entrega or '',
                    "concesionario":contrato.entrega_vehiculo_id.nombreConsesionario.name or '',
                    "vehiculo":contrato.entrega_vehiculo_id.estadoVehiculo or '',
                    "marca_modelo":str(contrato.entrega_vehiculo_id.marcaVehiculo)+str(contrato.entrega_vehiculo_id.modeloHomologado) or '',
                    "fecha_orden":contrato.entrega_vehiculo_id.fecha_orden or '',
                    "comision_factura":contrato.entrega_vehiculo_id.comisionFacturaConcesionario or 0,
                    "monto_vehiculo":contrato.entrega_vehiculo_id.montoVehiculo or 0,
                    "asamblea":contrato.entrega_vehiculo_id.asamblea_id.name or "",
                    "tipo":contrato.tipo_de_contrato.name  or '',
                    'plazo':contrato.plazo_meses.numero  or '',
                    'monto':contrato.monto_financiamiento  or 0,
                    'estado':contrato.state_simplificado,
                    }
            lista_final.append(dct)
        sheet.set_column('A:A', 10)
        sheet.set_column('B:B', 10)
        sheet.set_column('C:C', 10)
        sheet.set_column('D:D', 30)
        sheet.set_column('E:E', 15)
        sheet.set_column('F:F', 15)
        sheet.set_column('G:G', 15)
        sheet.set_column('H:H', 15)
        sheet.set_column('I:I', 20)
        sheet.set_column('J:J', 25)
        sheet.set_column('K:K', 25)
        sheet.set_column('L:L', 15)
        sheet.set_column('M:M', 13)
        sheet.set_column('N:N', 13)
        sheet.set_column('O:O', 10)

        sheet.write(4, 0, 'Grupo', bold2)
        sheet.write(4, 1, 'Socio', bold2)
        sheet.write(4, 2, 'Fecha de Adjudicación', bold2)
        sheet.write(4, 3, 'Fecha de Entrega', bold2)
        sheet.write(4, 4, 'Concesionario', bold2)
        sheet.write(4, 5, 'Vehiculo', bold2)
        sheet.write(4, 6, 'Marca/Modelo', bold2)
        sheet.write(4, 7, 'Fecha Orden de Compra', bold2)
        sheet.write(4, 8, 'Comisión, Patio o Concesionario', bold2)
        sheet.write(4, 9, 'Valor del Vehículo', bold2)
        sheet.write(4, 10, 'Asamblea', bold2)
        sheet.write(4, 11, 'Método', bold2)
        sheet.write(4, 12, 'Plazo', bold2)
        sheet.write(4, 13, 'Monto Adjudicado', bold2)
        sheet.write(4, 14, 'Estado', bold2)
        row=5

        lista_asesores=[]
        for line in lista_final:
            sheet.write(row,0, line['grupo'], registros_tabla)
            sheet.write(row, 1, line['socio'], registros_tabla)
            sheet.write(row, 2,line['fecha_adjudicado'], formato_fecha)
            sheet.write(row, 3, line['fecha_entrega'], formato_fecha)
            sheet.write(row, 4, line['concesionario'], registros_tabla)
            sheet.write(row, 5, line['vehiculo'], registros_tabla)
            sheet.write(row, 6,line['marca_modelo'] , registros_tabla)
            sheet.write(row, 7, line['fecha_orden'], formato_fecha)
            sheet.write(row, 8, line['comision_factura'], formato_numero)
            sheet.write(row, 9, line['monto_vehiculo'], formato_numero)
            sheet.write(row, 10, line['asamblea'], registros_tabla)
            sheet.write(row, 11, line['tipo'], formato_fecha)
            sheet.write(row, 12,line['plazo'], registros_tabla)
            sheet.write(row, 13, line['monto'], formato_numero)
            sheet.write(row, 14, line['estado'], registros_tabla)
            row+=1



# -*- coding: utf-8 -*-
import string
from odoo import api, fields, models, tools
from datetime import date, timedelta, datetime
from dateutil import relativedelta as rdelta 
import xlsxwriter
from io import BytesIO
import base64
from odoo.exceptions import ValidationError
import statistics


# class Users(models.Model):
#     _inherit = 'res.users'

#     codigo_asesor=fields.Char("Codigo de Asesor")

class RangoPagos(models.Model):
    _name = 'rango.pagos'
    _description = 'Rango Pagos'

    name = fields.Char( string="Nombre",compute='nombre_rango')
    minimo = fields.Integer( string="Minimo")
    maximo = fields.Integer(string="Maximo")
    codigo_rango = fields.Integer(string="Codigo")

    @api.depends('minimo','maximo')
    def nombre_rango(self):
        for l in self:
            if l.minimo:
                l.name=str(l.minimo)+' al '
            if l.maximo:
                l.name+=str(l.maximo)+' de cada mes'

class ReportTrazabilidad(models.TransientModel):
    _name = "reporte.pagos.trazabilidad"

    grupo=fields.Many2one('grupo.adjudicado',string="Grupo")
    rango=fields.Many2one('rango.pagos',string="Rango de Pagos")
    estado_contrato=fields.Selection([
                                    ('pendiente', 'Pendiente'),
                                    ('activo', 'Activo'),
                                    ('inactivo', 'Inactivo'),
                                    ('congelar_contrato', 'Congelado'),
                                    ('adjudicar', 'Adjudicado'),
                                    ('adendum', 'Realizar Adendum'),
                                    ('finalizado', 'Finalizado'),
                                    ('cedido', 'Cesión de Derecho'),
                                    ('desistir', 'Desistido'),
                                ],string="Estado del Contrato")
    estado_deuda=fields.Selection(selection=[('todos', 'Todos'),
                                            ('al_dia', 'Al día'),
                                            ('en_mora', 'En Mora')],required=True)

    def print_report_xls(self):
        today = date.today()
        file_data = BytesIO()
        workbook = xlsxwriter.Workbook(file_data)
        name = 'REPORTE DE Trazabilidad Pagos '+ str(today.year)
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
        
        sheet.merge_range('B1:F1', ' ', bold)
        sheet.merge_range('A2:F2', 'REPORTE DE TRAZABILIDAD DE PAGOS', bold)
        
        if self.grupo and not self.estado_contrato:
            if self.estado_deuda=='todos':
                contrato_ids = self.env['contrato'].search([('cliente','!=',False),('grupo','=',self.grupo.id)])
            elif self.estado_deuda=='al_dia':
                contrato_ids = self.env['contrato'].search([('cliente','!=',False),('grupo','=',self.grupo.id),('en_mora','=',False)])
            elif self.estado_deuda=='en_mora':
                contrato_ids = self.env['contrato'].search([('cliente','!=',False),('grupo','=',self.grupo.id),('en_mora','=',True)])
       
        elif self.grupo and self.estado_contrato:
            if self.estado_deuda=='todos':
                contrato_ids = self.env['contrato'].search([('cliente','!=',False),('grupo','=',self.grupo.id),('state','=',self.estado_contrato)])
            elif self.estado_deuda=='al_dia':
                contrato_ids = self.env['contrato'].search([('cliente','!=',False),('grupo','=',self.grupo.id),('en_mora','=',False),('state','=',self.estado_contrato)])
            elif self.estado_deuda=='en_mora':
                contrato_ids = self.env['contrato'].search([('cliente','!=',False),('grupo','=',self.grupo.id),('en_mora','=',True),('state','=',self.estado_contrato)])
       

        elif not self.grupo and self.estado_contrato:
            if self.estado_deuda=='todos':
                contrato_ids = self.env['contrato'].search([('cliente','!=',False),('state','=',self.estado_contrato)])
            elif self.estado_deuda=='al_dia':
                contrato_ids = self.env['contrato'].search([('cliente','!=',False),('en_mora','=',False),('state','=',self.estado_contrato)])
            elif self.estado_deuda=='en_mora':
                contrato_ids = self.env['contrato'].search([('cliente','!=',False),('en_mora','=',True),('state','=',self.estado_contrato)])
        
        elif not self.grupo and not self.estado_contrato:
            if self.estado_deuda=='todos':
                contrato_ids = self.env['contrato'].search([('cliente','!=',False)])
            elif self.estado_deuda=='al_dia':
                contrato_ids = self.env['contrato'].search([('cliente','!=',False),('en_mora','=',False)])
            elif self.estado_deuda=='en_mora':
                contrato_ids = self.env['contrato'].search([('cliente','!=',False),('en_mora','=',True)])
       

        lista_clientes=[]
        detalle_pagos=[]
        rangos_ids=self.env['rango.pagos'].search([])
        lista_rangos=[]
        for x in rangos_ids:
            lista_rangos.append({'minimo':x.minimo,'maximo':x.maximo,'codigo_rango':x.codigo_rango})

        for contrato in contrato_ids:
            lista_clientes.append(contrato.id)
            dct={'cliente':contrato.cliente.name,
                'contrato':contrato.secuencia,
                'cliente':contrato.cliente.name,
                'estado_contrato':contrato.state,
                'estado_deuda':'Al dia',
                'rango':[],
                'grupo_asignado':'',
                'grupo':contrato.grupo.name}
            if contrato.en_mora:
                dct['estado_deuda']:'En mora'
            for detalle in contrato.estado_de_cuenta_ids:
                if detalle.fecha_pagada:
                    for rang in lista_rangos:
                        if detalle.fecha_pagada.day>=rang['minimo'] and detalle.fecha_pagada.day<=rang['maximo']:
                            dct['rango'].append(rang['codigo_rango'])
            detalle_pagos.append(dct)
        for lista_final in detalle_pagos:
            max_mode=0
            if lista_final['rango']:
                list_table = statistics._counts(lista_final['rango'])
                len_table = len(list_table)

                if len_table == 1:
                    max_mode = statistics.mode(lista_final['rango'])
                else:
                    new_list = []
                    for i in range(len_table):
                        new_list.append(list_table[i][0])
                    max_mode = max(new_list) # use the max value here


                nombre_rango=self.env['rango.pagos'].search([('codigo_rango','=',int(max_mode))])
                lista_final['grupo_asignado']=nombre_rango.name

        sheet.set_column('A:A', 10)
        sheet.set_column('B:B', 10)
        sheet.set_column('C:C', 10)
        sheet.set_column('D:D', 30)
        sheet.set_column('E:E', 15)
        sheet.set_column('F:F', 15)
      

        sheet.write(4, 0, 'Rango', bold2)
        sheet.write(4, 1, 'Grupo', bold2)
        sheet.write(4, 2, 'Contrato', bold2)
        sheet.write(4, 3, 'Cliente.', bold2)
        sheet.write(4, 4, 'Estado', bold2)
        sheet.write(4, 5, 'Etado de Deuda', bold2)
        row=5   
        lista_asesores=[]
        

        for line in detalle_pagos:
            if self.rango:
                if self.rango.name==line['grupo_asignado']:
                    sheet.write(row,0, line['grupo_asignado'], registros_tabla)
                    sheet.write(row, 1, line['grupo'], registros_tabla)
                    sheet.write(row, 2,line['contrato'], registros_tabla)
                    sheet.write(row, 3, line['cliente'], registros_tabla)
                    sheet.write(row, 4, line['estado_contrato'], registros_tabla)
                    sheet.write(row, 5, line['estado_deuda'], registros_tabla)

                    row+=1
            else:
                if line['grupo_asignado']:
                    sheet.write(row,0, line['grupo_asignado'], registros_tabla)
                    sheet.write(row, 1, line['grupo'], registros_tabla)
                    sheet.write(row, 2,line['contrato'], registros_tabla)
                    sheet.write(row, 3, line['cliente'], registros_tabla)
                    sheet.write(row, 4, line['estado_contrato'], registros_tabla)
                    sheet.write(row, 5, line['estado_deuda'], registros_tabla)

                    row+=1
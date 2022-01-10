# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import os
import re
import json
import base64
import logging
import mimetypes
import odoo.tools 
import hashlib
from odoo import api, fields, models, tools, SUPERUSER_ID
from datetime import datetime,timedelta,date
import time
from odoo import _
from odoo.exceptions import ValidationError, except_orm
from dateutil.relativedelta import *
from . import informe_excel

import base64
from base64 import urlsafe_b64decode

import shutil












class InformeCreditoCrobranza(models.TransientModel):
    _name = "informe.credito.cobranza"

    partner_id =  fields.Many2one('res.partner',string='Socio',)
    clave =  fields.Char( default="informe_credito_cobranza")



    def print_report_xls(self):

        if self.clave=='informe_credito_cobranza':
            dct=self.crear_plantilla_informe_credito_cobranza()
            return dct



    def crear_plantilla_informe_credito_cobranza(self,):
        #Instancia la plantilla
        obj_plantilla=self.env['plantillas.dinamicas.informes'].search([('identificador_clave','=','informe_credito_cobranza')],limit=1)
        if obj_plantilla:

            plantilla=obj_plantilla.archivos_ids
            if len(plantilla):
                lista=[]
                #Crea el documento en la muk_dms.file para poderlo instanciar

                

          #      some_bytes = plantilla.plantilla

                # Open in "wb" mode to
                # write a new file, or 
                # "ab" mode to append

        #        f = open("/src/user/gzl_reporte/reports/Informe_Credito_Cobranza.xlsx", "wb")
       #         f.write(some_bytes)

                # f.read()

     #           f.close()
                shutil.copy2(obj_plantilla.directorio,obj_plantilla.directorio_out)

                    
                    
                    
            #####Campos de Cabecera
            campos=obj_plantilla.campos_ids.filtered(lambda l: len(l.child_ids)==0)

            lista_campos=[]
            for campo in campos:

                print(campo.name, campo.fila)
                dct={}
                resultado=self.mapped(campo.name)
                if len(resultado)>0:
                    dct['valor']=resultado[0]
                else:
                    dct['valor']=''

                dct['fila']=campo.fila
                dct['columna']=campo.columna
                lista_campos.append(dct)



            informe_excel.informe_credito_cobranza(obj_plantilla.directorio_out,lista_campos)


            with open(obj_plantilla.directorio_out, "rb") as f:
                data = f.read()
                file=bytes(base64.b64encode(data))


        obj_attch=self.env['ir.attachment'].create({
                                                     'name':'Informe_Credito_Cobranza.xlsx',
                                                      'datas':file,
                                                      'type':'binary', 
                                                      'store_fname':'Informe_Credito_Cobranza.xlsx'
                                                      })


                

            
           
        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url += "/web/content/%s?download=true" %(obj_attch.id)
        return{
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }



        #except:
         #   raise ValidationError(_('No existe informacion para generar el informe'))








































#     def crear_plantilla_informe_cctv(self):
#         if len(self.plantilla_dinamica.plantilla)>0:
#             plantilla= self.plantilla_dinamica.plantilla


#             lista=[]
#             for l in plantilla:
#                 lista.append(l.id)
#             if len(lista)>0:
#                 obj=self.env['ir.attachment'].browse(lista[0])

#                 dct={

#                 'name':obj.datas_fname,            
#                 'content':obj.datas,
#                 'directory':int(self.id),
#                 }

#                 obj_file=self.env['muk_dms.file'].create(dct)


#                 ruta_del_documento=obj_file.path

#                 #####Campos de Cabecera
#                 campos=self.plantilla_dinamica.campos_ids.filtered(lambda l: len(l.child_ids)==0)

#                 lista_campos=[]
#                 for campo in campos:

#                     print(campo.name, campo.fila)
#                     dct={}
#                     resultado=self.mapped(campo.name)
#                     if len(resultado)>0:
#                         dct['valor']=resultado[0]
#                     else:
#                         dct['valor']=''

#                     dct['fila']=campo.fila
#                     dct['columna']=campo.columna
#                     lista_campos.append(dct)

#                 #######Campo Detalle crear Json

#                 ###DVR


#                 lista_dvr=[]
#                 dvr_ids=self.mapped('x_dvr_ids')

#                 for dvr in dvr_ids:

#                     campos_dvr=self.plantilla_dinamica.campos_ids.filtered(lambda l: 'x_dvr_ids' in l.name )
#                     dct_dvr={}
#                     lista_campos_detalle=[]
#                     for campo in campos_dvr.child_ids:
#                         dct_campos_dvr={}
#                         resultado=dvr.mapped(campo.name)
#                         if len(resultado)>0:
#                             dct_campos_dvr['valor']=resultado[0]
#                         else:
#                             dct_campos_dvr['valor']=''

#                         dct_campos_dvr['fila']=campo.fila
#                         dct_campos_dvr['columna']=campo.columna
#                         lista_campos_detalle.append(dct_campos_dvr)
#                     dct_dvr['campos']=lista_campos_detalle


#                     canales=dvr.mapped('x_canales_ids')
#                     campos_canales=self.plantilla_dinamica.campos_ids.filtered(lambda l: 'x_canales_ids' in l.name )
#                     lista_canales_dvr=[]

#                     for canal in canales:

#                         dct_canal={}
#                         lista_campos_detalle=[]
#                         for campo in campos_canales.child_ids:
#                             dct_campos_canales={}
#                             resultado=canal.mapped(campo.name)
#                             if len(resultado)>0:
#                                 dct_campos_canales['valor']=resultado[0]
#                             else:
#                                 dct_campos_canales['valor']=''

#                             dct_campos_canales['fila']=campo.fila
#                             dct_campos_canales['columna']=campo.columna
#                             lista_campos_detalle.append(dct_campos_canales)
#                         dct_canal['campos']=lista_campos_detalle
#                         dct_canal['nombre']=canal.mapped('x_canal_nombre')[0]
#                         lista_canales_dvr.append(dct_canal)

#                     dct_dvr['canales']=lista_canales_dvr
#                     lista_dvr.append(dct_dvr)

# ##########Controles de Acceso

#                 lista_controles=[]
#                 dvr_ids=self.mapped('x_control_acceso_ids')

#                 for dvr in dvr_ids:

#                     campos_dvr=self.plantilla_dinamica.campos_ids.filtered(lambda l: 'x_control_acceso_ids' in l.name )
#                     dct_dvr={}
#                     lista_campos_detalle=[]
#                     for campo in campos_dvr.child_ids:
#                         dct_campos_dvr={}
#                         resultado=dvr.mapped(campo.name)
#                         if len(resultado)>0:
#                             dct_campos_dvr['valor']=resultado[0]
#                         else:
#                             dct_campos_dvr['valor']=''

#                         dct_campos_dvr['fila']=campo.fila
#                         dct_campos_dvr['columna']=campo.columna
#                         lista_campos_detalle.append(dct_campos_dvr)
#                     dct_dvr['campos']=lista_campos_detalle


#                     canales=dvr.mapped('x_puertas_ids')
#                     campos_canales=self.plantilla_dinamica.campos_ids.filtered(lambda l: 'x_puertas_ids' in l.name )
#                     lista_canales_dvr=[]

#                     for canal in canales:

#                         dct_canal={}
#                         lista_campos_detalle=[]
#                         for campo in campos_canales.child_ids:
#                             dct_campos_canales={}
#                             resultado=canal.mapped(campo.name)
#                             if len(resultado)>0:
#                                 dct_campos_canales['valor']=resultado[0]
#                             else:
#                                 dct_campos_canales['valor']=''

#                             dct_campos_canales['fila']=campo.fila
#                             dct_campos_canales['columna']=campo.columna
#                             lista_campos_detalle.append(dct_campos_canales)
#                         dct_canal['campos']=lista_campos_detalle
#                         dct_canal['nombre']=canal.mapped('x_puerta_nombre')[0]
#                         lista_canales_dvr.append(dct_canal)

#                     dct_dvr['puertas']=lista_canales_dvr
#                     lista_controles.append(dct_dvr)
#                     print(lista_controles)




# ########Sargent
#                 lista_sargent=[]
#                 dvr_ids=self.mapped('x_llave_sargent_ids')

#                 for dvr in dvr_ids:

#                     campos_dvr=self.plantilla_dinamica.campos_ids.filtered(lambda l: 'x_llave_sargent_ids' in l.name )
#                     dct_dvr={}
#                     lista_campos_detalle=[]
#                     for campo in campos_dvr.child_ids:
#                         dct_campos_dvr={}
#                         resultado=dvr.mapped(campo.name)
#                         if len(resultado)>0:
#                             dct_campos_dvr['valor']=resultado[0]
#                         else:
#                             dct_campos_dvr['valor']=''

#                         dct_campos_dvr['fila']=campo.fila
#                         dct_campos_dvr['columna']=campo.columna
#                         lista_campos_detalle.append(dct_campos_dvr)
#                     dct_dvr['campos']=lista_campos_detalle
#                     lista_sargent.append(dct_dvr)

# ########Cyber Keys
#                 lista_cyber_keys=[]
#                 dvr_ids=self.mapped('x_cyber_key_ids')

#                 for dvr in dvr_ids:

#                     campos_dvr=self.plantilla_dinamica.campos_ids.filtered(lambda l: 'x_cyber_key_ids' in l.name )
#                     dct_dvr={}
#                     lista_campos_detalle=[]
#                     for campo in campos_dvr.child_ids:
#                         dct_campos_dvr={}
#                         resultado=dvr.mapped(campo.name)
#                         if len(resultado)>0:
#                             dct_campos_dvr['valor']=resultado[0]
#                         else:
#                             dct_campos_dvr['valor']=''

#                         dct_campos_dvr['fila']=campo.fila
#                         dct_campos_dvr['columna']=campo.columna
#                         lista_campos_detalle.append(dct_campos_dvr)
#                     dct_dvr['campos']=lista_campos_detalle
#                     lista_cyber_keys.append(dct_dvr)


# ########Cerradura
#                 lista_cerradura_electronica=[]
#                 dvr_ids=self.mapped('x_cerradura_electro')

#                 for dvr in dvr_ids:

#                     campos_dvr=self.plantilla_dinamica.campos_ids.filtered(lambda l: 'x_cerradura_electro' in l.name )
#                     dct_dvr={}
#                     lista_campos_detalle=[]
#                     for campo in campos_dvr.child_ids:
#                         dct_campos_dvr={}
#                         resultado=dvr.mapped(campo.name)
#                         if len(resultado)>0:
#                             dct_campos_dvr['valor']=resultado[0]
#                         else:
#                             dct_campos_dvr['valor']=''

#                         dct_campos_dvr['fila']=campo.fila
#                         dct_campos_dvr['columna']=campo.columna
#                         lista_campos_detalle.append(dct_campos_dvr)
#                     dct_dvr['campos']=lista_campos_detalle
#                     lista_cerradura_electronica.append(dct_dvr)


#                 informe_excel.informe_formato_cctv(ruta_del_documento,lista_campos,lista_dvr,lista_controles,lista_sargent,lista_cyber_keys,lista_cerradura_electronica)


#             with open('/mnt/extra-addons/muk_dms/static/src/php/Gestor_Informes'+ruta_del_documento, "rb") as f:
#                 data = f.read()
#                 file=bytes(base64.b64encode(data))
               

#             obj_file.unlink()

#             dct={

#             'name':obj.datas_fname,            
#             'content':file,
#             'directory':int(self.id),
#             }

#             obj_file_nuevo=self.env['muk_dms.file'].create(dct)









#     def crear_plantilla_informe_alarma(self):
#         if len(self.plantilla_dinamica.plantilla)>0:
#             plantilla= self.plantilla_dinamica.plantilla


#             lista=[]
#             for l in plantilla:
#                 lista.append(l.id)
#             if len(lista)>0:
#                 obj=self.env['ir.attachment'].browse(lista[0])

#                 dct={

#                 'name':obj.datas_fname,            
#                 'content':obj.datas,
#                 'directory':int(self.id),
#                 }

#                 obj_file=self.env['muk_dms.file'].create(dct)


#                 ruta_del_documento=obj_file.path

#                 #####Campos de Cabecera
#                 campos=self.plantilla_dinamica.campos_ids.filtered(lambda l: len(l.child_ids)==0)

#                 lista_campos=[]
#                 for campo in campos:

#                     print(campo.name, campo.fila)
#                     dct={}
#                     resultado=self.mapped(campo.name)
#                     if len(resultado)>0:
#                         dct['valor']=resultado[0]
#                     else:
#                         dct['valor']=''

#                     dct['fila']=campo.fila
#                     dct['columna']=campo.columna
#                     lista_campos.append(dct)

#                 #######Campo Detalle crear Json

#                 ###Expansor
#                 lista_alarmas=[]




#                 alarmas_expansores=self.mapped('x_expansor_ids.x_alarmas_ids')

#                 campos_alarmas=self.plantilla_dinamica.campos_ids.filtered(lambda l: 'x_alarmas_ids' in l.name )

#                 for alarmas in alarmas_expansores:
#                     dct_alarma={}
#                     lista_campos_detalle=[]
#                     for campo in campos_alarmas.child_ids:
#                         dct={}
#                         resultado=alarmas.mapped(campo.name)
#                         if len(resultado)>0:
#                             dct['valor']=resultado[0]
#                         else:
#                             dct['valor']=''

#                         dct['fila']=campo.fila
#                         dct['columna']=campo.columna
#                         lista_campos_detalle.append(dct)

#                     dct_alarma['nombre']=alarmas.mapped('x_zona_nombre')[0]
#                     dct_alarma['campos']=lista_campos_detalle
#                     lista_alarmas.append(dct_alarma)
#                 print(lista_alarmas)
#                 informe_excel.informe_formato_alarmas(ruta_del_documento,lista_campos,lista_alarmas)


#             with open('/mnt/extra-addons/muk_dms/static/src/php/Gestor_Informes'+ruta_del_documento, "rb") as f:
#                 data = f.read()
#                 file=bytes(base64.b64encode(data))
               


#             #except:
#              #   raise ValidationError(_('No existe informacion para generar el informe'))
#             obj_file.unlink()

#             dct={

#             'name':obj.datas_fname,            
#             'content':file,
#             'directory':int(self.id),
#             }

#             obj_file_nuevo=self.env['muk_dms.file'].create(dct)











#     def print_report_xls(self):
#         file_data = BytesIO()
#         workbook = xlsxwriter.Workbook(file_data)
#         name = 'Informe de Credito y Cobranza'
#         self.xslx_body(workbook, name)
        

#         workbook.close()
#         file_data.seek(0)
        

        
#         attachment = self.env['ir.attachment'].create({
#             'datas': base64.b64encode(file_data.getvalue()),
#             'name': name,
#             'store_fname': name,
#             'type': 'binary',
#         })
#         url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
#         url += "/web/content/%s?download=true" %(attachment.id)
#         return{
#             "type": "ir.actions.act_url",
#             "url": url,
#             "target": "new",
#         }






        
#     def xslx_body(self, workbook, name):
#         bold = workbook.add_format({'bold':True,'border':1})
#         bold_no_border = workbook.add_format({'bold':True})
#         bold.set_center_across()
#         format_title = workbook.add_format({'bold':True,'border':1})
#         format_title_left = workbook.add_format({'bold':True,'border':1,'align': 'left'})
#         format_title_left_14 = workbook.add_format({'bold':True,'border':1,'align': 'left','size': 14})
#         format_title_center_14 = workbook.add_format({'bold':True,'border':1,'align': 'center','size': 14})


#         format_title.set_center_across()
#         currency_format = workbook.add_format({'num_format': '[$$-409]#,##0.00','border':1,'text_wrap': True })
#         currency_format.set_align('vcenter')

        
#         date_format = workbook.add_format({'num_format': 'dd/mm/yy', 'align': 'right','border':1,'text_wrap': True })
#         date_format.set_align('vcenter')
#         date_format_day = workbook.add_format({'align': 'right','border':1,'text_wrap': True })
#         date_format_day.set_align('vcenter')
#         date_format_title = workbook.add_format({'num_format': 'dd/mm/yy', 'align': 'left','text_wrap': True})
#         date_format_title.set_align('vcenter')

#         body = workbook.add_format({'align': 'center' , 'border':1,'text_wrap': True})
#         body.set_align('vcenter')
#         body_right = workbook.add_format({'align': 'right', 'border':1 })
#         body_left = workbook.add_format({'align': 'left','bold':True})
#         format_title2 = workbook.add_format({'align': 'center', 'bold':True,'border':1 })
#         sheet = workbook.add_worksheet(name)

#         sheet.set_portrait()
#         sheet.set_paper(9)  # A4

#         sheet.set_margins(left=0.4, right=0.4, top=0.4, bottom=0.2)
#         sheet.set_print_scale(100)
#         sheet.fit_to_pages(1,2)







#     def print_report_pdf(self):
#         return self.env.ref('gzl_reporte.repote_anticipo_pdf_id').report_action(self)



        
#     def obtenerDatos(self,):

#         filtro=[('payment_date','>=',self.date_from),
#             ('payment_date','<=',self.date_to),('tipo_transaccion','=','Anticipo')]


#         lista_partner=self.obtener_listado_partner_payment(filtro)
#         lines=[]
        

#         for partner in lista_partner:
#             filtro=[('payment_date','>=',self.date_from),
#                 ('payment_date','<=',self.date_to),('tipo_transaccion','=','Anticipo')]
            
#             lines.append({'numero_documento':partner['nombre'],'reglon':'titulo'})

#             lista_anticipos=self.obtener_listado_payment_por_empresa(partner['id'],filtro)
#             for dct in lista_anticipos:
#                 dct['reglon']='detalle'
#                 lines.append(dct)
#             dctTotal={}
#             dctTotal['numero_documento']='Total '+ partner['nombre']

#             dctTotal['monto_anticipo']=round(sum(map(lambda x:x['monto_anticipo'],lista_anticipos)),2)
#             dctTotal['monto_aplicado']=round(sum(map(lambda x:x['monto_aplicado'],lista_anticipos)),2)
#             dctTotal['monto_adeudado']=round(sum(map(lambda x:x['monto_adeudado'],lista_anticipos)),2)
#             dctTotal['reglon']='total_detalle'


#             lines.append(dctTotal)
#         dctTotalGeneral={}
#         dctTotalGeneral['numero_documento']='Total General'

#         dctTotalGeneral['monto_anticipo']=round(sum(map(lambda x:x['monto_anticipo'],list(filter(lambda x: x['reglon']=='total_detalle', lines)))),2)
#         dctTotalGeneral['monto_aplicado']=round(sum(map(lambda x:x['monto_aplicado'],list(filter(lambda x: x['reglon']=='total_detalle', lines)))),2)
#         dctTotalGeneral['monto_adeudado']=round(sum(map(lambda x:x['monto_adeudado'],list(filter(lambda x: x['reglon']=='total_detalle', lines)))),2)
#         dctTotalGeneral['reglon']='total_general'

#         lines.append(dctTotalGeneral)
#         lista_obj=[]
#         for l in lines:
#             obj_detalle=self.env['reporte.anticipo.detalle'].create(l)
#             lista_obj.append(obj_detalle)

#         return lista_obj



# class ReporteAnticipoDetalle(models.TransientModel):
#     _name = "reporte.anticipo.detalle"

#     numero_documento = fields.Char('Nro. Documento')
#     fecha_emision = fields.Date('Fc. Emision')
#     fecha_vencimiento = fields.Date('Fc. Vencimiento')
#     monto_anticipo = fields.Float('Monto Anticipo')
#     monto_aplicado = fields.Float('Monto Aplicado')
#     monto_adeudado = fields.Float('Monto Adeudado')
#     observaciones = fields.Char('Observaciones')
#     reglon = fields.Char('Reglon')



# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from datetime import date, timedelta,datetime
from dateutil.relativedelta import relativedelta
import xlsxwriter
from io import BytesIO
import base64
from odoo.exceptions import AccessError, UserError, ValidationError
#from . import l10n_ec_check_printing.amount_to_text_es
from . import amount_to_text_es
from datetime import datetime
import calendar
import datetime as tiempo
import itertools
from . import congelamiento_documento
import shutil



class CongelamientoWozard(models.TransientModel):
    _name = "congelamiento.report"
    
    partner_id = fields.Many2one('res.partner',string='Cliente')
    contrato_id = fields.Many2one('contrato',string='Contrato')
    clave =  fields.Char( default="congelamiento")
    motivo =  fields.Char(string= "Motivo")


    def print_report_xls(self):
        dct=self.crear_plantilla_contrato_congelamiento()
        return dct


    def crear_plantilla_contrato_congelamiento(self,):
        obj_plantilla=self.env['plantillas.dinamicas.informes'].search([('identificador_clave','=',self.clave)],limit=1)
        
        if obj_plantilla:
            mesesDic = {
                "1":'Enero',
                "2":'Febrero',
                "3":'Marzo',
                "4":'Abril',
                "5":'Mayo',
                "6":'Junio',
                "7":'Julio',
                "8":'Agosto',
                "9":'Septiembre',
                "10":'Octubre',
                "11":'Noviembre',
                "12":'Diciembre'
            }
                

            shutil.copy2(obj_plantilla.directorio,obj_plantilla.directorio_out)
            campos=obj_plantilla.campos_ids.filtered(lambda l: len(l.child_ids)==0)
            
            lista_campos=[]
            estado_cuenta=[]
            estado_cuenta_anterior=[]
            for campo in campos:
                dct={}
                resultado=self.mapped(campo.name)
                if campo.identificar_docx =='num_contrato':
                    dct={}
                    dct['valor'] = resultado[0]
                    dct['identificar_docx']=campo.identificar_docx
                    lista_campos.append(dct)
                else:
                    if campo.name!=False:
                        dct={}
                        if len(resultado)>0:
                            dct['valor']=str(resultado[0])
                        else:
                            dct['valor']=''
                    dct['identificar_docx']=campo.identificar_docx
                    lista_campos.append(dct)
                        
            year = datetime.now().year
            mes = datetime.now().month
            dia = datetime.now().day
            fechacontr = str(dia)+' de '+str(mesesDic[str(mes)])+' del '+str(year)
            dct = {}
            dct['identificar_docx']='fecha_actual'
            dct['valor']=fechacontr
            lista_campos.append(dct)

            congelamiento_documento.crear_documento_congelamiento(obj_plantilla.directorio_out,lista_campos)
            with open(obj_plantilla.directorio_out, "rb") as f:
                data = f.read()
                file=bytes(base64.b64encode(data))


        obj_attch=self.env['ir.attachment'].create({
                                                    'name':'Congelamiento.docx',
                                                    'datas':file,
                                                    'type':'binary', 
                                                    'store_fname':'Congelamiento.docx'
                                                    })

        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url += "/web/content/%s?download=true" %(obj_attch.id)
        return{
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }
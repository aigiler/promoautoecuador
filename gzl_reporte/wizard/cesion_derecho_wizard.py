
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
from . import cesion_derecho_documento
import shutil



class CesionDerecho(models.TransientModel):
    _name = "cesion.derecho"
    
    cesion_id =fields.Many2one("wizard.cesion.derecho", string="Adendum")

    def print_report_xls(self,cesion_id):
        dct=self.crear_plantilla_cesion_derecho(cesion_id)
        return dct



    def crear_plantilla_cesion_derecho(self,cesion_id):
        dct={}
        obj_plantilla=self.env['plantillas.dinamicas.informes'].search([('identificador_clave','=','cesion_derecho')],limit=1)
        lista_campos=[]
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
            for campo in campos:
                dct={}
                resultado=self.mapped(campo.name)
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
            valordia = amount_to_text_es.amount_to_text(dia)
            valordia = valordia.split()
            valordia = valordia[0]
            fechacontr = 'a los '+valordia.lower()+' dias del mes de '+str(mesesDic[str(mes)])+' del Año '+str(year)
            dct['identificar_docx']='fecha_actual'
            dct['valor']=fechacontr
            lista_campos.append(dct)
            cesion_derecho_documento.crear_documento_cesion(obj_plantilla.directorio_out,lista_campos)



            with open(obj_plantilla.directorio_out, "rb") as f:
                data = f.read()
                file=bytes(base64.b64encode(data))

        obj_attch=self.env['ir.attachment'].create({
                                                    'name':'Contrato_adendum.docx',
                                                    'datas':file,
                                                    'type':'binary', 
                                                    'store_fname':'Contrato_adendum.docx'
                                                    })

        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url += "/web/content/%s?download=true" %(obj_attch.id)
        return{
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
            "documento":obj_attch
        }
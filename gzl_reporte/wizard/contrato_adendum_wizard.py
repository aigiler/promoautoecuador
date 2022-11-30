
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
from . import contrato_adendum_documento
import shutil



class ContratoAdendum(models.TransientModel):
    _name = "contrato.adendum.report"
    
    adendum_id =fields.Many2one("wizard.contrato.adendum", string="Adendum")
    clave =  fields.Char( default="contrato_adendum")


    def print_report_xls(self):
        #raise ValidationError(str(self.clave))
        if self.clave=='contrato_adendum':
            dct=self.crear_plantilla_contrato_adendum()
            return dct



    def crear_plantilla_contrato_adendum(self,):
        obj_plantilla=self.env['plantillas.dinamicas.informes'].search([('identificador_clave','=','contrato_adendum')],limit=1)
        
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
                if campo.identificar_docx =='fecha_suscripcion':
                    dct={}
                    year = resultado[0].year
                    mes = resultado[0].month
                    dia = resultado[0].day
                    fechacontr2 = str(dia)+' de '+str(mesesDic[str(mes)])+' del '+str(year)
                    dct['valor'] = fechacontr2
                    dct['identificar_docx']=campo.identificar_docx
                    lista_campos.append(dct)
                elif campo.identificar_docx =='num_contrato':
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
            #print(mesesDic[str(mes)][:3])
            valordia = amount_to_text_es.amount_to_text(dia)
            valordia = valordia.split()
            valordia = valordia[0]
            fechacontr = 'a los '+valordia.lower()+' dias del mes de '+str(mesesDic[str(mes)])+' del Año '+str(year)
            dct = {}
            dct['identificar_docx']='txt_factual'
            dct['valor']=fechacontr
            lista_campos.append(dct)

            contrato_adendum_documento.crear_documento_adendum(obj_plantilla.directorio_out,lista_campos)


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
        }
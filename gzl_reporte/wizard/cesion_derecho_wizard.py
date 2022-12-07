
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
        if self.clave=='cesion_derecho':
            dct=self.crear_plantilla_cesion_derecho(cesion_id)
            return dct



    def crear_plantilla_cesion_derecho(self,cesion_id):
        obj_plantilla=self.env['plantillas.dinamicas.informes'].search([('identificador_clave','=','cesion_derecho')],limit=1)
        lista_campos=[]
        dct['identificar_docx']='name_socio'
        dct['valor']=cesion_id.contrato_a_ceder.cliente.name
        lista_campos.append(dct)
        dct['identificar_docx']='vat_socio'
        dct['valor']=cesion_id.contrato_a_ceder.cliente.vat
        lista_campos.append(dct)
        dct['identificar_docx']='estado_civil_socio'
        dct['valor']=cesion_id.contrato_a_ceder.cliente.estado_civil
        lista_campos.append(dct)
        dct['identificar_docx']='direccion_socio'
        dct['valor']=cesion_id.contrato_a_ceder.cliente.street
        lista_campos.append(dct)
        dct['identificar_docx']='name_cesionario'
        dct['valor']=cesion_id.partner_id.name
        lista_campos.append(dct)
        dct['identificar_docx']='vat_cesionario'
        dct['valor']=cesion_id.partner_id.vat
        lista_campos.append(dct)
        dct['identificar_docx']='estado_civil_cesionario'
        dct['valor']=cesion_id.partner_id.estado_civil
        lista_campos.append(dct)
        dct['identificar_docx']='direccion_cesionario'
        dct['valor']=cesion_id.partner_id.street
        lista_campos.append(dct)
        dct['identificar_docx']='fecha_suscripcion'
        dct['valor']=cesion_id.contrato_a_ceder.fecha_contrato
        lista_campos.append(dct)
        dct['identificar_docx']='monto_financiamiento'
        dct['valor']=cesion_id.contrato_a_ceder.monto_financiamiento
        lista_campos.append(dct)
        dct['identificar_docx']='plazo_meses'
        dct['valor']=cesion_id.contrato_a_ceder.plazo_meses.numero
        lista_campos.append(dct)
        dct['identificar_docx']='provincia_cesionario'
        dct['valor']=cesion_id.partner_id.state_id.name
        lista_campos.append(dct)
        dct['identificar_docx']='canton_cesionario'
        dct['valor']=cesion_id.partner_id.city
        lista_campos.append(dct)
        dct['identificar_docx']='email_cesionario'
        dct['valor']=cesion_id.partner_id.email
        lista_campos.append(dct)
        year = datetime.now().year
        mes = datetime.now().month
        dia = datetime.now().day
        #print(mesesDic[str(mes)][:3])
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
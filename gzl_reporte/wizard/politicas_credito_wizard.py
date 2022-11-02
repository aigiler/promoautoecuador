
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
from . import crear_pagare
import shutil



class RequisitosCredito(models.TransientModel):
    _name = "requisitos.credito"
    

    clave =  fields.Char( default="requisitos_credito")


    def print_report_xls(self):
        dct=self.crear_plantilla_requisitos_credito()
        return dct

    def crear_plantilla_requisitos_credito(self,):
        obj_plantilla=self.env['plantillas.dinamicas.informes'].search([('identificador_clave','=','requisitos_credito')],limit=1)

        if obj_plantilla:
            shutil.copy2(obj_plantilla.directorio,obj_plantilla.directorio_out)
            with open(obj_plantilla.directorio_out, "rb") as f:
                data = f.read()
                file=bytes(base64.b64encode(data))
        obj_attch=self.env['ir.attachment'].create({
                                                    'name':'Politicas de Credito.docx',
                                                    'datas':file,
                                                    'type':'binary', 
                                                    'store_fname':'Politicas de Credito.docx'
                                                    })

        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url += "/web/content/%s?download=true" %(obj_attch.id)
        return{
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }

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
from . import crear_carta_finalizacion
import shutil



class CartaFinalizacion(models.TransientModel):
    _name = "carta.finalizacion.report"
    
    partner_id = fields.Many2one('res.partner',string='Cliente')
    contrato_id = fields.Many2one('contrato',string='Contrato')
    clave =  fields.Char( default="carta_finalizacion")
    vehiculo_id = fields.Many2one('entrega.vehiculo',string='entrega.vehiculo')

    @api.depends("contrato_id")
    @api.onchange("contrato_id")
    def obtener_vehiculo(self):
        for l in self:
            if l.contrato_id:
                vehiculo_id = self.env['entrega.vehiculo'].search(
                        [('nombreSocioAdjudicado', '=', self.contrato_id.cliente.id),('estado','=','entrega_vehiculo')], limit=1)
                partner_id = self.env['res.partner'].search(
                        [('id', '=', self.contrato_id.cliente.id)], limit=1)

                self.vehiculo_id=vehiculo_id
                self.partner_id=partner_id

    def print_report_xls(self):
        if self.clave=='carta_finalizacion':
            dct=self.crear_plantilla_contrato_reserva()
            return dct

    def crear_plantilla_contrato_reserva(self,):
        obj_plantilla=self.env['plantillas.dinamicas.informes'].search([('identificador_clave','=','carta_finalizacion')],limit=1)
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
            for campo in campos:
                dct={}
                resultado=self.mapped(campo.name)
                if campo.identificar_docx =='fecha_contrato':
                    #raise ValidationError('{0}'.format(resultado))
                    dct={}
                    year = resultado[0].year
                    mes = resultado[0].month
                    dia = resultado[0].day
                    fechacontr2 = str(dia)+' de '+str(mesesDic[str(mes)])+' del '+str(year)
                    dct['valor'] = fechacontr2
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
            dct['identificar_docx']='txt_factual'
            dct['valor']=fechacontr
            lista_campos.append(dct)
            crear_carta_finalizacion.crear_carta_finalizacion(obj_plantilla.directorio_out,lista_campos)
            with open(obj_plantilla.directorio_out, "rb") as f:
                data = f.read()
                file=bytes(base64.b64encode(data))
        obj_attch=self.env['ir.attachment'].create({
                                                    'name':'Carta_Finalizacion.docx',
                                                    'datas':file,
                                                    'type':'binary', 
                                                    'store_fname':'Carta_Finalizacion.docx'
                                                    })

        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url += "/web/content/%s?download=true" %(obj_attch.id)
        return{
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }
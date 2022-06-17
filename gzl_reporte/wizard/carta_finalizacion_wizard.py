
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

    @api.depends("partner_id")
    @api.onchange("partner_id")
    def obtener_vehiculo(self):
        for l in self:
            if l.partner_id:
                vehiculo_id = self.env['entrega.vehiculo'].search(
                        [('nombreSocioAdjudicado', '=', self.partner_id.id)], limit=1)
                contrato_id = self.env['contrato'].search(
                        [('cliente', '=', self.partner_id.id)], limit=1)
                #if vehiculo_id:
                #    self.vehiculo_id=vehiculo_id.id
                #if contrato_id:
                #    self.contrato_id=contrato_id.id
        self.vehiculo_id=190
        self.contrato_id=8605

    def print_report_xls(self):
        #raise ValidationError(str(self.clave))
        if self.clave=='carta_finalizacion':
            dct=self.crear_plantilla_contrato_reserva()
            return dct



    def crear_plantilla_contrato_reserva(self,):
        #Instancia la plantilla
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
            #fecha_suscripcion

            #####Se sacan los campos de la plantilla del objeto plantillas.dinamicas.informes
            campos=obj_plantilla.campos_ids.filtered(lambda l: len(l.child_ids)==0)
            
            lista_campos=[]
            estado_cuenta=[]
            estado_cuenta_anterior=[]
            for campo in campos:
                #if campo:
                #    raise ValidationError(str(campo.vat))
                dct={}

                resultado=self.mapped(campo.name)
                
                if campo.identificar_docx =='fecha_contrato':
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
            
            #if resultado:
            #    raise ValidationError(str(lista_campos))
            
            year = datetime.now().year
            mes = datetime.now().month
            dia = datetime.now().day
            #print(mesesDic[str(mes)][:3])
            valordia = amount_to_text_es.amount_to_text(dia)
            valordia = valordia.split()
            valordia = valordia[0]
            fechacontr = str(valordia)+' de '+str(mesesDic[str(mes)])+' del '+str(year)
            dct = {}
            dct['identificar_docx']='txt_factual'
            dct['valor']=fechacontr
            lista_campos.append(dct)
            #if fechacontr: 
            #    raise ValidationError(str(fechacontr) )
            estado_cuenta.append(self.contrato_id)
            #obj_estado_cuenta_cabecera=self.env['contrato.estado.cuenta.historico.cabecera'].search([('contrato_id','=',self.contrato_id.id)])
            #estado_cuenta_anterior.append(obj_estado_cuenta_cabecera)
            #crear_documento_contrato_reserva.crear_documento_reserva(obj_plantilla.directorio_out,lista_campos,estado_cuenta)
            #raise ValidationError(str(lista_campos))
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
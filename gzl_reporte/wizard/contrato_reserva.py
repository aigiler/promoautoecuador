
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
from . import crear_documento_contrato_reserva
import shutil



class ContratoResrva(models.TransientModel):
    _name = "contrato.reserva"
    
    contrato_id = fields.Many2one('contrato',string='Contrato')
    clave =  fields.Char( default="contrato_reserva")
    vehiculo_id = fields.Many2one('entrega.vehiculo',string='entrega.vehiculo')


    def print_report_xls(self):

        if self.clave=='contrato_reserva':
            dct=self.crear_plantilla_contrato_reserva()
            return dct



    def crear_plantilla_contrato_reserva(self,):
        #Instancia la plantilla
        obj_plantilla=self.env['plantillas.dinamicas.informes'].search([('identificador_clave','=','contrato_reserva')],limit=1)
        if obj_plantilla:


            shutil.copy2(obj_plantilla.directorio,obj_plantilla.directorio_out)


            #####Se sacan los campos de la plantilla del objeto plantillas.dinamicas.informes
            campos=obj_plantilla.campos_ids.filtered(lambda l: len(l.child_ids)==0)
            
            lista_campos=[]
            estado_cuenta=[]
            for campo in campos:
                #if campo:
                #    raise ValidationError(str(campo.vat))
                dct={}
                #vehiculoooo
                if campo.name == 'vehiculo_id.tipoVehiculo':
                    
                    obj_veh=self.env['entrega.vehiculo'].search([])
                    
                    for l in obj_veh :
                        #vehiculo_serie  vehiculo_motor vehiculo_color  vehiculo_anio vehiculo_pais_origen vehiculo_combustible vehiculo_pasajeros vehiculo_tonelaje. 
                        #raise ValidationError(str(l.nombreGarante.id)+' -jg- '+campo.name)
                        if l.nombreSocioAdjudicado.id == self.contrato_id.cliente.id: #vehiculo_clase 238
                            dct ={}
                            dct['valor']=l.tipoVehiculo
                            dct['identificar_docx']='vehiculo_tipo'
                            lista_campos.append(dct)
                            dct ={}
                            dct['valor']=l.claseVehiculo
                            dct['identificar_docx']='vehiculo_clase'
                            lista_campos.append(dct)
                            dct ={}
                            dct['valor']=l.marcaVehiculo
                            dct['identificar_docx']='vehiculo_marca'
                            lista_campos.append(dct)
                            dct ={}
                            dct['valor']=l.modeloVehiculoSRI
                            dct['identificar_docx']='modelo_regist_sri'
                            lista_campos.append(dct)
                            dct ={}
                            dct['valor']=l.modeloHomologado
                            dct['identificar_docx']='modelo_homologado_ant'
                            lista_campos.append(dct)
                            dct ={}
                            dct['valor']=l.serieVehiculo
                            dct['identificar_docx']='vehiculo_serie'
                            lista_campos.append(dct)
                            dct ={}
                            dct['valor']=l.motorVehiculo
                            dct['identificar_docx']='vehiculo_motor'
                            lista_campos.append(dct)
                            dct ={}
                            dct['valor']=l.colorVehiculo
                            dct['identificar_docx']='vehiculo_color'
                            lista_campos.append(dct)
                            dct ={}
                            dct['valor']=l.anioVehiculo
                            dct['identificar_docx']='vehiculo_anio'
                            lista_campos.append(dct)
                            dct ={}
                            dct['valor']=l.paisOrigenVehiculo.name
                            dct['identificar_docx']='vehiculo_pais_origen'
                            lista_campos.append(dct)
                            dct ={}
                            dct['valor']=l.conbustibleVehiculo or ''
                            dct['identificar_docx']='vehiculo_combustible'
                            lista_campos.append(dct)
                            dct ={}
                            dct['valor']=str(l.numPasajeros)
                            dct['identificar_docx']='vehiculo_pasajeros'
                            lista_campos.append(dct)
                            dct ={}
                            dct['valor']=l.tonelajeVehiculo
                            dct['identificar_docx']='vehiculo_tonelaje'
                            lista_campos.append(dct)
                            dct ={}
                            dct['valor']=str(l.plazoMeses) or '0'
                            dct['identificar_docx']='plazo_meses'    
                            lista_campos.append(dct)
                else:
                    resultado=self.mapped(campo.name)
                
                    if campo.name!=False:
                        if len(resultado)>0:

                            dct['valor']=resultado[0]

                        else:
                            dct['valor']=''

                    


                    dct['identificar_docx']=campo.identificar_docx
                    lista_campos.append(dct)
            #amount_to_text_es.amount_to_text(self.amount)
            #if resultado:
            #    raise ValidationError(str(lista_campos))
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
            year = datetime.now().year
            mes = datetime.now().month
            #print(mesesDic[str(mes)][:3])
            fechacontr = 'a los nueve días del mes de '+str(mesesDic[str(mes)])+' del Año '+str(year)
            if mes:
                raise ValidationError(str(mesesDic[str(mes)]))
            estado_cuenta.append(self.contrato_id.estado_de_cuenta_ids)
            
            #crear_documento_contrato_reserva.crear_documento_reserva(obj_plantilla.directorio_out,lista_campos,estado_cuenta)

            crear_documento_contrato_reserva.crear_documento_reserva(obj_plantilla.directorio_out,lista_campos,estado_cuenta)


            with open(obj_plantilla.directorio_out, "rb") as f:
                data = f.read()
                file=bytes(base64.b64encode(data))


        obj_attch=self.env['ir.attachment'].create({
                                                    'name':'Contrato_Reserva.docx',
                                                    'datas':file,
                                                    'type':'binary', 
                                                    'store_fname':'Contrato_Reserva.docx'
                                                    })

        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url += "/web/content/%s?download=true" %(obj_attch.id)
        return{
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }
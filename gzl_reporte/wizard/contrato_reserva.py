
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
        if self.contrato_id.garante:
            obj_plantilla=self.env['plantillas.dinamicas.informes'].search([('identificador_clave','=','contrato_reserva_garante')],limit=1)
        
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
                            lista_vehiculos=[{'identificar_docx':'vehiculo_tipo',
                                            'valor':l.tipoVehiculo},
                                            {'identificar_docx':'vehiculoclase',
                                            'valor':l.claseVehiculo},
                                            {'identificar_docx':'vehiculomarca',
                                            'valor':l.marcaVehiculo},
                                            {'identificar_docx':'modeloregistsri',
                                            'valor':l.modeloVehiculoSRI},
                                            {'identificar_docx':'modelohomologadoant',
                                            'valor':l.modeloHomologado},
                                            {'identificar_docx':'vehiculoserie',
                                            'valor':l.serieVehiculo},
                                            {'identificar_docx':'vehiculomotor',
                                            'valor':l.motorVehiculo},
                                            {'identificar_docx':'vehiculocolor',
                                            'valor':l.colorVehiculo},
                                            {'identificar_docx':'vehiculoanio',
                                            'valor':l.anioVehiculo},
                                            {'identificar_docx':'vehiculopaisorigen',
                                            'valor':l.paisOrigenVehiculo.name},
                                            {'identificar_docx':'vehiculocombustible',
                                            'valor':l.conbustibleVehiculo},
                                            {'identificar_docx':'vehiculopasajeros',
                                            'valor':str(l.numPasajeros)},
                                            {'identificar_docx':'vehiculotonelaje',
                                            'valor':l.tonelajeVehiculo},
                                            {'identificar_docx':'plazomeses',
                                            'valor':str(self.contrato_id.plazo_meses.numero)},]
  
                            lista_campos+=lista_vehiculos
                else:
                    resultado=self.mapped(campo.name)
                    if campo.name!=False:
                        if len(resultado)>0:
                            if resultado[0]==False:
                                dct['valor']=''
                            else:    
                                dct['valor']=resultado[0]

                        else:
                            dct['valor']=''
                    dct['identificar_docx']=campo.identificar_docx
                    lista_campos.append(dct)
            
            #if resultado:
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
            dia = datetime.now().day
            #print(mesesDic[str(mes)][:3])
            valordia = amount_to_text_es.amount_to_text(dia)
            valordia = valordia.split()
            valordia = valordia[0]
            fechacontr = 'a los '+valordia.lower()+' dias del mes de '+str(mesesDic[str(mes)])+' del Año '+str(year)
            lista_fecha=[{'identificar_docx':'txt_factual','valor':fechacontr}]
            lista_campos+=lista_fecha
            #if fechacontr:
            #raise ValidationError(str(lista_campos))
            #    raise ValidationError(str(fechacontr) )
            #raise ValidationError('{0}'.format(lista_campos))
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
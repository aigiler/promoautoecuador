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
from . import hoja_ruta

import base64
from base64 import urlsafe_b64decode

import shutil



class HojaRuta(models.TransientModel):
    _name = "informe.devolucion.monto"

    contrato_id =  fields.Many2one('contrato',string='Contrato')
    clave =  fields.Char( default="hoja_ruta")
    devolucion_id=fields.Many2one("devolucion.monto",string="Devolución")

    @api.onchange("contrato_id")
    def obtener_hoja_ruta(self):
        for l in self:
            if l.contrato_id:
                hoja_ruta=self.env['devolucion.monto'].search([('contrato_id','=',l.contrato_id.id)], limit=1)
                if hoja_ruta:
                    l.devolucion_id=hoja_ruta.id
                else:
                    l.devolucion_id=[]

    def print_report_xls(self):

        if self.clave=='hoja_ruta':
            dct=self.crear_plantilla_hoja_ruta()
            return dct




    def crear_plantilla_hoja_ruta(self,):
        #Instancia la plantilla
        garante=False
        obj_plantilla=self.env['plantillas.dinamicas.informes'].search([('identificador_clave','=','hoja_ruta')],limit=1)
        
        if obj_plantilla:
            salida=obj_plantilla.directorio_out

            shutil.copy2(obj_plantilla.directorio,obj_plantilla.directorio_out)
            #####Campos de Cabecera
            campos=obj_plantilla.campos_ids.filtered(lambda l: len(l.child_ids)==0)

            lista_campos=[]
            for l in self.devolucion_id:
                if l.tipo_accion=='CLIENTE':
                    dct={}
                    dct['fila']=13
                    dct['columna']=5
                    dct['hoja']=2
                    dct['valor']=l.observacion_legal
                    lista_campos.append(dct)
                elif l.tipo_accion=='ABOGADO':
                    dct={}
                    dct['fila']=17
                    dct['columna']=5
                    dct['hoja']=2
                    dct['valor']=l.observacion_legal
                    lista_campos.append(dct)
                elif l.tipo_accion=='CONSEJO':
                    dct={}
                    dct['fila']=21
                    dct['columna']=5
                    dct['hoja']=2
                    dct['valor']=l.observacion_legal
                    lista_campos.append(dct)
                elif l.tipo_accion=='DEFENSORIA':
                    dct={}
                    dct['fila']=25
                    dct['columna']=5
                    dct['hoja']=2
                    dct['valor']=l.observacion_legal
                    lista_campos.append(dct)
                elif l.tipo_accion=='FISCALIA':
                    dct={}
                    dct['fila']=29
                    dct['columna']=5
                    dct['hoja']=2
                    dct['valor']=l.observacion_legal
                    lista_campos.append(dct)
                elif l.tipo_accion=='CAMARA DE COMERCIO':
                    dct={}
                    dct['fila']=33
                    dct['columna']=5
                    dct['hoja']=2
                    dct['valor']=l.observacion_legal
                    lista_campos.append(dct)


            
            for campo in campos:
                if campo.fila in [3,4,5,6,7]:
                    dct={}
                    resultado=self.devolucion_id.mapped(campo.name)
                    if len(resultado)>0:
                        dct['valor']=resultado[0]
                    else:
                        dct['valor']=''

                    dct['fila']=campo.fila
                    dct['columna']=campo.columna
                    dct['hoja']=campo.hoja_excel
                    
                    lista_campos.append(dct)
                    dct={}
                    if len(resultado)>0:
                        dct['valor']=resultado[0]
                    else:
                        dct['valor']=''

                    dct['fila']=campo.fila
                    dct['columna']=campo.columna
                    dct['hoja']=2
                    
                    lista_campos.append(dct)
                    dct={}
                    if len(resultado)>0:
                        dct['valor']=resultado[0]
                    else:
                        dct['valor']=''

                    dct['fila']=campo.fila
                    dct['columna']=campo.columna
                    dct['hoja']=3
                    
                    lista_campos.append(dct)
                    dct={}
                    if len(resultado)>0:
                        dct['valor']=resultado[0]
                    else:
                        dct['valor']=''

                    dct['fila']=campo.fila
                    dct['columna']=campo.columna
                    dct['hoja']=4
                    
                    lista_campos.append(dct)
                    dct={}
                    if len(resultado)>0:
                        dct['valor']=resultado[0]
                    else:
                        dct['valor']=''

                    dct['fila']=campo.fila
                    dct['columna']=campo.columna
                    dct['hoja']=5
                    
                    lista_campos.append(dct)

                else:
                    dct={}
                    resultado=self.devolucion_id.mapped(campo.name)
                    if len(resultado)>0:
                        dct['valor']=resultado[0]
                    else:
                        dct['valor']=''

                    dct['fila']=campo.fila
                    dct['columna']=campo.columna
                    dct['hoja']=campo.hoja_excel
                    
                    lista_campos.append(dct)


            obj_documentos_postventa=self.devolucion_id.documentos_postventa

            lista_documentos_postventa= self.obtenerTablas(obj_plantilla,obj_documentos_postventa,'documentos_postventa','documento_id.nombre')

            obj_documentos_legal=self.devolucion_id.documentos_legal

            lista_documentos_legal= self.obtenerTablas(obj_plantilla,obj_documentos_legal,'documentos_legal','documento_id.nombre')
            


            hoja_ruta.generar_hoja_huta(salida,lista_campos,lista_documentos_postventa, lista_documentos_legal,self.devolucion_id)

            with open(salida, "rb") as f:
                data = f.read()
                file=bytes(base64.b64encode(data))


        obj_attch=self.env['ir.attachment'].create({
                                                    'name':'Hoja_de_Ruta.xlsx',
                                                    'datas':file,
                                                    'type':'binary', 
                                                    'store_fname':'Hoja de ruta.xlsx'
                                                    })

        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url += "/web/content/%s?download=true" %(obj_attch.id)
        return{
            "type": "ir.actions.act_url",
            "url": url,
            "target": "new",
        }




    def obtenerTablas(self, obj_plantilla, objetos,parametro,campoReferencia):
        lista_patrimonio=[]
        for dvr in objetos:

            campos_dvr=obj_plantilla.campos_ids.filtered(lambda l: parametro in l.name )
            dct_dvr={}
            lista_campos_detalle=[]
            for campo in campos_dvr.child_ids:
                dct_campos_dvr={}
                resultado=dvr.mapped(campo.name)
                if len(resultado)>0:
                    dct_campos_dvr['valor']=resultado[0]
                else:
                    dct_campos_dvr['valor']=''

                dct_campos_dvr['fila']=campo.fila
                dct_campos_dvr['columna']=campo.columna
                lista_campos_detalle.append(dct_campos_dvr)
            dct_dvr['nombre']=dvr.mapped(campoReferencia)[0]
            dct_dvr['campos']=lista_campos_detalle
            lista_patrimonio.append(dct_dvr)
        return lista_patrimonio


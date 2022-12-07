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
from . import orden_compra_salida_documento
import subprocess
from subprocess import getoutput
import os
import io
import base64
from base64 import urlsafe_b64decode

import shutil



class InformeCreditoCrobranza(models.TransientModel):
    _name = "informe.credito.cobranza"

    entrega_vehiculo_id =  fields.Many2one('entrega.vehiculo',string='Entrega Vehiculo',)
    clave =  fields.Char( default="")
    archivo_xls1 = fields.Binary('Archivo excel')


    def print_report_xls(self):

        if self.clave:
            dct=self.crear_plantilla_informe_credito_cobranza()
            return dct




    def crear_plantilla_informe_credito_cobranza(self,):
        #Instancia la plantilla
        garante=False
        obj_plantilla=self.env['plantillas.dinamicas.informes'].search([('identificador_clave','=',self.clave)],limit=1)
            
        if obj_plantilla:
            shutil.copy2(obj_plantilla.directorio,obj_plantilla.directorio_out)
            campos=obj_plantilla.campos_ids.filtered(lambda l: len(l.child_ids)==0)
            lista_campos=[]
            for campo in campos:
                dct={}
                resultado=self.entrega_vehiculo_id.mapped(campo.name)
                if campo.name=="comisionFacturaConcesionario":
                    resultado[0]=resultado[0]/100

                if len(resultado)>0:
                    dct['valor']=resultado[0]
                else:
                    dct['valor']=''

                dct['fila']=campo.fila
                dct['columna']=campo.columna
                dct['hoja']=campo.hoja_excel
                lista_campos.append(dct)


            fp =io.BytesIO()
            workbook=orden_compra_salida_documento.informe_credito_cobranza(obj_plantilla.directorio_out,lista_campos,self.clave)
            workbook.save(fp)
            with open(obj_plantilla.directorio_out, "rb") as f:
                data = f.read()
                file=bytes(base64.b64encode(data))


        nombre_doc=""
        if self.clave=='orden_compra':
            nombre_doc="Orden de Compra.xlsx"
        elif self.clave=="orden_salida":
            nombre_doc="Orden de Salida.xlsx"
        else:
            nombre_doc="Liquidacion de Compra.xlsx"

        obj_attch=self.env['ir.attachment'].create({
                                                    'name':nombre_doc,
                                                    'datas':file,
                                                    'type':'binary', 
                                                    'store_fname':nombre_doc
                                                    })

        
        direccion_xls_libro=self.env['ir.attachment']._get_path(obj_attch.datas,obj_attch.checksum)[1]
        nombre_bin=obj_attch.checksum
        nombre_archivo=obj_attch.name
        os.chdir(direccion_xls_libro.rstrip(nombre_bin))
        print(os.chdir(direccion_xls_libro.rstrip(nombre_bin)))
        os.rename(nombre_bin,nombre_archivo)
        subprocess.getoutput("""libreoffice --headless --convert-to pdf *.xlsx""") 
        try:
            with open(direccion_xls_libro.rstrip(nombre_bin)+nombre_archivo.split('.')[0]+'.pdf', "rb") as f:
                data = f.read()
                file=bytes(base64.b64encode(data))
        except:
            raise ValidationError(_('No existen datos para generar informe'))
        obj_attch.unlink()
        obj_attch=self.env['ir.attachment'].create({
                                                    'name':nombre_archivo.split('.')[0]+'.pdf',
                                                    'datas':file,
                                                    'type':'binary', 
                                                    'store_fname':nombre_archivo.split('.')[0]+'.pdf'
                                                    })
        self.archivo_xls1=file
        return{'xls_filename1':'Orden de Compra.pdf','archivo_xls1':file,"documento":obj_attch}








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


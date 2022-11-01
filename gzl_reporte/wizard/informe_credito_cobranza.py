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
from . import informe_excel
import subprocess
from subprocess import getoutput
import os
import base64
from base64 import urlsafe_b64decode

import shutil



class InformeCreditoCrobranza(models.TransientModel):
    _name = "informe.credito.cobranza"

    entrega_vehiculo_id =  fields.Many2one('entrega.vehiculo',string='Entrega Vehiculo',)
    clave =  fields.Char( default="")
    xls_filename1 = fields.Char('Nombre Archivo excel')
    archivo_xls1 = fields.Binary('Archivo excel')


    def print_report_xls(self):

        if self.clave:
            dct=self.crear_plantilla_informe_credito_cobranza()
            return dct




    def crear_plantilla_informe_credito_cobranza(self,):
        #Instancia la plantilla
        garante=False
        if self.clave=='orden_compra':
            obj_plantilla=self.env['plantillas.dinamicas.informes'].search([('identificador_clave','=','orden_compra')],limit=1)
        else:
            obj_plantilla=self.env['plantillas.dinamicas.informes'].search([('identificador_clave','=','orden_salida')],limit=1)
            
        if obj_plantilla:
            shutil.copy2(obj_plantilla.directorio,obj_plantilla.directorio_out)
            campos=obj_plantilla.campos_ids.filtered(lambda l: len(l.child_ids)==0)
            lista_campos=[]
            for campo in campos:
                dct={}
                resultado=self.entrega_vehiculo_id.mapped(campo.name)
                if len(resultado)>0:
                    dct['valor']=resultado[0]
                else:
                    dct['valor']=''

                dct['fila']=campo.fila
                dct['columna']=campo.columna
                dct['hoja']=campo.hoja_excel
                lista_campos.append(dct)


            fp =io.BytesIO()
            workbook=informe_excel.informe_credito_cobranza(obj_plantilla.directorio_out,lista_campos,self.clave)
            workbook.save(fp)
            with open(obj_plantilla.directorio_out, "rb") as f:
                data = f.read()
                file=bytes(base64.b64encode(data))


        obj_attch=self.env['ir.attachment'].create({
                                                    'name':'Orden de Compra.xlsx',
                                                    'datas':file,
                                                    'type':'binary', 
                                                    'store_fname':'Orden de Compra.xlsx'
                                                    })

        
        direccion_xls_libro=obj._get_path(obj_attch.datas,obj_attch.checksum)[1]
        nombre_bin=obj_attch.checksum
        nombre_archivo=obj_attch.datas_fname
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

            fecha = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H%M%S')
        filename = 'Reportes Detalle Contrato'+'.xlsx'
        self.write ( {
            'xls_filename1': filename,
            'archivo_xls1': base64.b64encode(fp.getvalue())
            }) 
        obj=self.env['ir.attachment']
        obj_xls_libro=obj.create({'name':self.xls_filename1,'datas':self.archivo_xls1,'type_l':'libro','type':'binary','datas_fname':self.xls_filename1})


        self.write({'xls_filename1':nombre_archivo.split('.')[0]+'.pdf','archivo_xls1':file})
        obj_attch.unlink()


        return{'xls_filename1':nombre_archivo.split('.')[0]+'.pdf','archivo_xls1':file}








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


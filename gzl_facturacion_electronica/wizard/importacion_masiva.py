# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from datetime import date, datetime
import base64
import json
import xmltodict 
import dateutil.parser
from odoo.exceptions import ValidationError

class WizardImportDocuments(models.TransientModel):
    _name = "wizard.import.documents.masiva"
    _description = 'Importación de Documentos en formato XML'
    
    name=fields.Char('')

    file_txt = fields.Binary('Archivo')

    
    def format_authorization_date(self, date):    
        date_conv = dateutil.parser.parse(date)
        return date_conv.strftime('%Y-%m-%d %H:%M:%S')
    
    def format_date(self, date):    
        date_conv = dateutil.parser.parse(date)
        return date_conv.strftime('%Y-%m-%d')
    
    
    def import_txt(self):
####Crea el archivo en directorio y se sobrescribe el binario para abrirlo en el siguiente bloque.
        f = open('archivo.txt') # opening a file
        f.write(self.file_txt)
        f.close() # closing file object

#### Se abre el archivo
        with open('archivo.txt') as f:
            lines = f.readlines()
            listaTotal=[]
            for l in lines:
                l=l.replace('\n','')
                lista=l.split('\t') 
                listaTotal.append(lista)



        listaLinea=[]

        error= int(self.env['ir.config_parameter'].get_param('cantidad_filas_error'))
        modulo= int(self.env['ir.config_parameter'].get_param('modulo_cantidad_filas_error'))
        nuevaLista=[]
        for i in range(0,len(listaTotal)):
            listaLinea=listaLinea+listaTotal[i] 
            if (i+error) % modulo==0:
                nuevaLista.append(listaLinea)
                listaLinea=[]

        for fila in nuevaLista[:1]:

            factura=self.env['mantenedor.importacion.masiva'].search([('code','=','FAC')])
            if fila[0] ==factura.name:



            retencion=self.env['mantenedor.importacion.masiva'].search([('code','=','RET')])
            if fila[0] ==retencion.name:



#   ['Comprobante de Retención', '008-004-000045946', '0190055965001', 'BANCO DEL AUSTRO', '30/11/2021', '01/12/2021 15:06:16', 'NORMAL', '13056626107', '0993261564001', '3011202107019005596500120080040000459465472502413', '3011202107019005596500120080040000459465472502413', '']       
#   ['COMPROBANTE', 'SERIE_COMPROBANTE', 'RUC_EMISOR', 'RAZON_SOCIAL_EMISOR', 'FECHA_EMISION', 'FECHA_AUTORIZACION', 'TIPO_EMISION', 'IDENTIFICACION_RECEPTOR', 'CLAVE_ACCESO', 'NUMERO_AUTORIZACION', 'IMPORTE_TOTAL']




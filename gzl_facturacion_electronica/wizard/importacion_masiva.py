# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from datetime import date, datetime
import base64
import json
import xmltodict 
import dateutil.parser
from odoo.exceptions import ValidationError
from base64 import b64decode,b64encode

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
            binario = b64decode(self.file_txt)
            f = open('archivo.txt', 'wb')
            f.write(binario)
            f.close()

    #### Se abre el archivo
            with open("archivo.txt",  encoding="ISO-8859-1") as f:
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
            for i in range(1,len(listaTotal)):
                listaLinea=listaLinea+listaTotal[i] 
                if (i+error) % modulo==0:
                    nuevaLista.append(listaLinea)
                    listaLinea=[]
                    
            
            for fila in nuevaLista[:1]:
                journal_id = self.env['account.journal'].search([('type','=','purchase')],limit=1)
                serie=fila[1].split('-')
            

                factura=self.env['mantenedor.importacion.masiva'].search([('code','=','FAC')])
                
                if fila[0] ==factura.name:
                    
                    partner_id = self.env['res.partner'].search([('vat','=',fila[2])],limit=1)
                    if partner_id.id == False:
                        raise ValidationError("El proveedor {1} con el RUC {0} no esta ingresado en la aplicación, proceda a ingresarlo.".format(fila[2],fila[3]))
                    
                    invoice_id = {
                        'type':'in_invoice',
                        'is_electronic':True,
                        'partner_id':partner_id.id,
                        #'type_environment':fila[6],
                        'numero_autorizacion_sri':fila[10],
                        'fecha_autorizacion_sri':self.format_authorization_date(fila[5]),
                        #'estado_autorizacion_sri':'AUT' if aut['estado']=='AUTORIZADO' else 'NAT',
                        'clave_acceso_sri':fila[9],
                        'manual_establishment':serie[0],
                        'manual_referral_guide':serie[1],
                        'manual_sequence':serie[2],
                        'l10n_latam_document_number':serie[0]+serie[1]+serie[2],
                        'invoice_date':self.format_date(fila[4]),
                        'date':self.format_date(fila[4]),
                        'journal_id':journal_id.id,
                        'state':'draft'
                    }

                    lines=[]
                    product_template=self.env.ref('gzl_facturacion_electronica.generic_product_template')
                    product = self.env['product.product'].search([('product_tmpl_id','=',product_template.id)])
                    dct_line={
                        'partner_id':partner_id.id,
                        'product_id':product.id,
                        'name': '['+product.default_code+']'+product.product_tmpl_id.name,
                        'account_id':product.categ_id.property_stock_account_input_categ_id.id,
                        'quantity':1,
                        'price_unit':float(fila[11]. replace(",",".")),
                        'discount':0.00,
                        'account_internal_type':'other',
                        'debit':float(fila[11]. replace(",",".")),
                        'credit':0.00,
                    }
                    lines.append((0, 0, dct_line))
                    invoice_id.update({'line_ids': lines})
                    move = self.env['account.move'].create(invoice_id)
                    break
                
                
                retencion=self.env['mantenedor.importacion.masiva'].search([('code','=','RET')])
                if fila[0] ==retencion.name:
                    print('cambios')




#   ['Comprobante de Retención', '008-004-000045946', '0190055965001', 'BANCO DEL AUSTRO', '30/11/2021', '01/12/2021 15:06:16', 'NORMAL', '13056626107', '0993261564001', '3011202107019005596500120080040000459465472502413', '3011202107019005596500120080040000459465472502413', '']       
#   ['COMPROBANTE', 'SERIE_COMPROBANTE', 'RUC_EMISOR', 'RAZON_SOCIAL_EMISOR', 'FECHA_EMISION', 'FECHA_AUTORIZACION', 'TIPO_EMISION', 'IDENTIFICACION_RECEPTOR', 'CLAVE_ACCESO', 'NUMERO_AUTORIZACION', 'IMPORTE_TOTAL']



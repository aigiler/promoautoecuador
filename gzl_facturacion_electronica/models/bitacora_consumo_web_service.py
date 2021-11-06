# -*- coding: utf-8 -*-
from odoo import api, fields, models, SUPERUSER_ID, tools,  _
from odoo.exceptions import AccessError, UserError, ValidationError
from .servicio_web_facturacion_electronica import *
from datetime import datetime
import json
import pytz
from base64 import b64decode,b64encode


class BitacoraConsumoServicios(models.Model):   
     
    _name = 'bitacora.consumo.servicios'    
  

    name = fields.Char( string='Comprobante',)
    invoice_id = fields.Many2one( 'account.move',string='Factura')
    retention_id = fields.Many2one( 'account.retention',string='Retencion')
    guia_remision_id = fields.Many2one( 'account.guia.remision',string='Guia de Remisión')
    state = fields.Selection([('pendiente', 'Pendiente'),('proceso', 'Proceso'),('validar', 'Validada'),('generada','XMl y Ride')
                                 ], string='Estado', required=True, default='pendiente',track_visibility='onchange')

    codigo_respuesta_web_service = fields.Char( string='Codigo Respueta',track_visibility='onchange')
    response = fields.Char( string='Response',track_visibility='onchange')
    respuesta = fields.Char( string='Respueta',track_visibility='onchange')
    etapa = fields.Char( string='Etapa',track_visibility='onchange')

    clave_acceso_sri = fields.Char( string='Clave de Acceso',track_visibility='onchange')
    numero_autorizacion_sri = fields.Char( string='Número de Autorización SRI',track_visibility='onchange')
    fecha_autorizacion_sri = fields.Datetime( string='Fecha de Autorización',track_visibility='onchange')
    estado_autorizacion_sri = fields.Selection([('PPR', 'En procesamiento'), 
                                                ('AUT', 'Autorizado'),
                                                ('NAT', 'No Autorizado'),],
                                    string='Estado de Autorización del Sri',track_visibility='onchange')




    def reenvioComprobante(self):
        url,header,diccionarioRequest=self.invoice_id.procesarComprobante()
        diccionarioRequest['facturas'][0]['claveAcceso']=self.clave_acceso_sri
        diccionarioRequest['facturas'][0]['numeroAutorizacion']=self.numero_autorizacion_sri
        diccionarioRequest['facturas'][0]['estado']=self.estado_autorizacion_sri

        response=self.invoice_id.postJson(url,header,diccionarioRequest)


        self.codigo_respuesta_web_service=str(response.status_code)
        self.response=str(json.loads(response.text))
        if response.status_code==200 :
            response = json.loads(response.text)
            dias=datetime.now(pytz.timezone('America/Guayaquil'))
            self.invoice_id.estado_autorizacion_sri=response['estado']
            self.state='proceso'
            self.invoice_id.numero_autorizacion_sri='321231231'



    def token_autorizacion(self):
        objTokenUrl=self.env.ref('gzl_facturacion_electronica.url_servicio_validar_factura')
        dct=self.invoice_id.token_autorizacion(objTokenUrl)
        self.response=str( dct)


    def seleccionComprobante(self):
        if self.invoice_id.id:
            comprobante=self.invoice_id
            model='account.move'
            nombreComprobante='Factura-{0}'.format(self.invoice_id.l10n_latam_document_number)
            dctCodDoc={
                'out_invoice':'facturas',
                'out_refund':'notasCredito',
                'out_debit':'notasDebito',
                }

            responseKey=dctCodDoc[self.invoice_id.type]
            template_id = self.env.ref('gzl_facturacion_electronica.facturacion_electronica_email_template').id



        if self.guia_remision_id.id:
            comprobante=self.guia_remision_id
            model='account.guia.remision'
            nombreComprobante='Guia-{0}'.format(self.guia_remision_id.name)
            responseKey='guiasRemision'
            template_id = self.env.ref('gzl_facturacion_electronica.guia_remision_email_template').id
        if self.retention_id.id:
            comprobante=self.retention_id
            model='account.retention'
            nombreComprobante='Retencion-{0}'.format(self.retention_id.l10n_latam_document_number)
            responseKey='retenciones'
            template_id = self.env.ref('gzl_facturacion_electronica.retencion_electronica_email_template').id
        return comprobante,model,nombreComprobante,responseKey,template_id



    def procesarComprobante(self):
        comprobante,model,nombreComprobante,responseKey,template_id=self.seleccionComprobante()


        self.etapa='Procesar Comprobante'
        if not self.numero_autorizacion_sri:
            url,header,diccionarioRequest=comprobante.procesarComprobante()
            response=comprobante.postJson(url,header,diccionarioRequest)


            self.codigo_respuesta_web_service=str(response.status_code)
            self.response=str(json.loads(response.text))
            if response.status_code==200 :
                response = json.loads(response.text)
                facturas=response['respuestas']

                for factura in facturas:                    
                    self.codigo_respuesta_web_service=factura['codigo']
                    dias=datetime.now(pytz.timezone('America/Guayaquil'))
                    comprobante.estado_autorizacion_sri='PPR'
                    self.state='proceso'
                    comprobante.numero_autorizacion_sri=''
                    self.respuesta=factura['respuesta']

                    self.estado_autorizacion_sri='PPR'

                    self.numero_autorizacion_sri=''




        else:
            raise ValidationError('La factura ya fue procesada, si desea cambiarla use Reenvio de Factura')






    def validarComprobante(self):
        comprobante,model,nombreComprobante,responseKey,template_id=self.seleccionComprobante()

        self.etapa='Validar Comprobante'


        url,header,diccionarioRequest=comprobante.validarComprobante()
        response=comprobante.postJson(url,header,diccionarioRequest)
        self.codigo_respuesta_web_service=str(response.status_code)
        self.response=str(json.loads(response.text))
        if response.status_code==200:
            response = json.loads(response.text)
            facturas=response[responseKey]


# {
#     "facturas": [
#         {
#             "claveAcceso": "0609202101099217567200110010010000012455658032318",
#             "ruc": "0992175672001",
#             "codigoExterno": "001-001-000001245",
#             "estado": "AUTORIZADO",
#             "fechaAutorizacion": "2021-10-04 21:47",
#             "numeroAutorizacion": "0609202101099217567200110010010000012455658032318",
#             "notificado": false,
#             "mensajeSRI": "Comprobante AUTORIZADO"
#         }
#     ]

# }

            for factura in facturas:                    
                if factura['estado']=='AUTORIZADO':
                    dias=datetime.now(pytz.timezone('America/Guayaquil'))
                    fecha = dias.strftime('%Y-%m-%d %H:%M:%S')
                    comprobante.fecha_autorizacion_sri=datetime.strptime(factura['fechaAutorizacion'],'%Y-%m-%d %H:%M')
                    comprobante.clave_acceso_sri=factura['claveAcceso']
                    comprobante.numero_autorizacion_sri=factura['numeroAutorizacion']
                    comprobante.estado_autorizacion_sri='AUT'

                    self.fecha_autorizacion_sri=datetime.strptime(factura['fechaAutorizacion'],'%Y-%m-%d %H:%M')
                    self.clave_acceso_sri=factura['claveAcceso']
                    self.numero_autorizacion_sri=factura['numeroAutorizacion']
                    self.estado_autorizacion_sri='AUT'


                    self.state='validar'
                    self.respuesta=factura['mensajeSRI']
               # else:
               #     comprobante.estado_autorizacion_sri=factura['estado']


    def descargarXML(self):

        comprobante,model,nombreComprobante,responseKey,template_id=self.seleccionComprobante()


        self.etapa='Descargar XML'

        if comprobante.estado_autorizacion_sri=='AUT':

            url,header=comprobante.descargarXML()
            response=comprobante.getJson(url,header)
            self.codigo_respuesta_web_service=str(response.status_code)
            self.response=str(json.loads(response.text))
            if response.status_code==200:

         #   dct={"archivo": "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QU5DSE9SXzBfMSkgOCAwIFJdPj4KZW5kb2JqCjEwIDAgb2JqCjw8L0Rlc3RzIDkgMCBSPj4KZW5kb2JqCjExIDAgb2JqCjw8L05hbWVzIDEwIDAgUi9UeXBlL0NhdGFsb2cvUGFnZXMgNyAwIFIvVmlld2VyUHJlZmVyZW5jZXM8PC9QcmludFNjYWxpbmcvQXBwRGVmYXVsdD4+Pj4KZW5kb2JqCjEyIDAgb2JqCjw8L01vZERhdGUoRDoyMDIxMTAwNjEzMjcwNS0wNScwMCcpL0NyZWF0b3IoSmFzcGVyUmVwb3J0cyBcKGZhY3R1cmFcKSkvQ3JlYXRpb25EYXRlKEQ6MjAyMTEwMDYxMzI3MDUtMDUnMDAnKS9Qcm9kdWNlcihpVGV4dCAyLjEuNyBieSAxVDNYVCk+PgplbmRvYmoKeHJlZgowIDEzCjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwNDQyMSAwMDAwMCBuIAowMDAwMDA0NzM0IDAwMDAwIG4gCjAwMDAwMDAwMTUgMDAwMDAgbiAKMDAwMDAwNDgyMiAwMDAwMCBuIAowMDAwMDAwNzk1IDAwMDAwIG4gCjAwMDAwMDE3NDkgMDAwMDAgbiAKMDAwMDAwODAxMSAwMDAwMCBuIAowMDAwMDA0Njk5IDAwMDAwIG4gCjAwMDAwMDgwNzQgMDAwMDAgbiAKMDAwMDAwODEyOCAwMDAwMCBuIAowMDAwMDA4MTYxIDAwMDAwIG4gCjAwMDAwMDgyNjYgMDAwMDAgbiAKdHJhaWxlcgo8PC9JbmZvIDEyIDAgUi9JRCBbPDliOWNiODU4YjBlMWVjYzNlZTc0ZmZjZWEzMTkwZWZkPjw5YjJlMWIxMmIyM2M3MDJkNzgyNDJjNjEwMjNkZTZlNj5dL1Jvb3QgMTEgMCBSL1NpemUgMTM+PgpzdGFydHhyZWYKODQyNAolJUVPRgo="}



                b64 = json.loads(response.text)['archivo']
                binario = b64decode(b64)
                f = open('file.xml', 'wb')
                f.write(binario)
                f.close()


                with open('file.xml', "rb") as f:
                    data = f.read()
                    file=bytes(b64encode(data))



                self.env['ir.attachment'].create({
                                                         'res_id':comprobante.id,
                                                         'res_model':model,
                                                         'name':'{0}.xml'.format(nombreComprobante),
                                                          'datas':file,
                                                          'type':'binary', 
                                                          'store_fname':'{0}.xml'.format(nombreComprobante)})

                
    def descargarRide(self):
        comprobante,model,nombreComprobante,responseKey,template_id=self.seleccionComprobante()
        self.etapa='Descargar Ride'

        if comprobante.estado_autorizacion_sri=='AUT':


            url,header=comprobante.descargarRide()
            response=comprobante.getJson(url,header)
            self.codigo_respuesta_web_service=str(response.status_code)
            self.response=str(json.loads(response.text))


            if response.status_code==200:
            
            
            #dct={"archivo":"PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9InllcyI/Pgo8YXV0b3JpemFjaW9uPgogICAgPGVzdGFkbz5BVVRPUklaQURPPC9lc3RhZG8+CiAgICA8bnVtZXJvQXV0b3JpemFjaW9uPjA2MDkyMDIxMDEwOTkyMTc1NjcyMDAxMTAwMTAwMTAwMDAwMTI0NTU2NTgwMzIzMTg8L251bWVyb0F1dG9yaXphY2lvbj4KICAgIDxmZWNoYUF1dG9yaXphY2lvbj4yMDIxLTEwLTA0VDIxOjQ3OjA2LTA1OjAwPC9mZWNoYUF1dG9yaXphY2lvbj4KICAgIDxhbWJpZW50ZT5QUlVFQkFTPC9hbWJpZW50ZT4KICAgIDxjb21wcm9iYW50ZT48IVtDREFUQVs8P3htbCB2ZXJzaW9uPSIxLjAiIGVuY29kaW5nPSJVVEYtOCI/PjxmYWN0dXJhIGlkPSJjb21wcm9iYW50ZSIgdmVyc2lvbj0iMS4xLjAiPgogICAgPGluZm9UcmlidXRhcmlhPgogICAgICAgIDxhbWJpZW50ZT4xPC9hbWJpZW50ZT4KICAgICAgICA8dGlwb0VtaXNpb24+MTwvdGlwb0VtaXNpb24+CiAgICAgICAgPHJhem9uU29jaWFsPkZVTkRBQ0nDk04gQkVOw4lGSUNBIEFDQ0nDk04gU09MSURBUklBPC9yYXpvblNvY2lhbD4KICAgICAgICA8bm9tYnJlQ29tZXJjaWFsPkZVTkRBQ0nDk04gQkVOw4lGSUNBIEFDQ0nDk04gU09MSURBUklBPC9ub21icmVDb21lcmNpYWw+CiAgICAgICAgPHJ1Yz4wOTkyMTc1NjcyMDAxPC9ydWM+CiAgICAgICAgPGNsYXZlQWNjZXNvPjA2MDkyMDIxMDEwOTkyMTc1NjcyMDAxMTAwMTAwMTAwMDAwMTI0NTU2NTgwMzIzMTg8L2NsYXZlQWNjZXNvPgogICAgICAgIDxjb2REb2M+MDE8L2NvZERvYz4KICAgICAgICA8ZXN0YWI+MDAxPC9lc3RhYj4KICAgICAgICA8cHRvRW1pPjAwMTwvcHRvRW1pPgogICAgICAgIDxzZWN1ZW5jaWFsPjAwMDAwMTI0NTwvc2VjdWVuY2lhbD4KICAgICAgICA8ZGlyTWF0cml6PkdhcnpvdGEgTXouIDE1OCBzbC4gMiBFZGlmaWNpbyBDLlMuUy5BPC9kaXJNYXRyaXo+CiAgICA8L2luZm9UcmlidXRhcmlhPgogICAgPGluZm9GYWN0dXJhPgogICAgICAgIDxmZWNoYUVtaXNpb24+MDYvMDkvMjAyMTwvZmVjaGFFbWlzaW9uPgogICAgICAgIDxkaXJFc3RhYmxlY2ltaWVudG8+R2Fyem90YSBNei4gMTU4IHNsLiAyIEVkaWZpY2lvIEMuUy5TLkE8L2RpckVzdGFibGVjaW1pZW50bz4KICAgICAgICA8b2JsaWdhZG9Db250YWJpbGlkYWQ+U0k8L29ibGlnYWRvQ29udGFiaWxpZGFkPgogICAgICAgIDx0aXBvSWRlbnRpZmljYWNpb25Db21wcmFkb3I+MDQ8L3RpcG9JZGVudGlmaWNhY2lvbkNvbXByYWRvcj4KICAgICAgICA8cmF6b25Tb2NpYWxDb21wcmFkb3I+QkFOQ08gREUgR1VBWUFRVUlMIFMuQS48L3Jhem9uU29jaWFsQ29tcHJhZG9yPgogICAgICAgIDxpZGVudGlmaWNhY2lvbkNvbXByYWRvcj4wOTkwMDQ5NDU5MDAxPC9pZGVudGlmaWNhY2lvbkNvbXByYWRvcj4KICAgICAgICA8dG90YWxTaW5JbXB1ZXN0b3M+MTAwMDAuMDwvdG90YWxTaW5JbXB1ZXN0b3M+CiAgICAgICAgPHRvdGFsRGVzY3VlbnRvPjAuMDwvdG90YWxEZXNjdWVudG8+CiAgICAgICAgPHRvdGFsQ29uSW1wdWVzdG9zPgogICAgICAgICAgICA8dG90YWxJbXB1ZXN0bz4KICAgICAgICAgICAgICAgIDxjb2RpZ28+MjwvY29kaWdvPgogICAgICAgICAgICAgICAgPGNvZGlnb1BvcmNlbnRhamU+MjwvY29kaWdvUG9yY2VudGFqZT4KICAgICAgICAgICAgICAgIDxiYXNlSW1wb25pYmxlPjEwMDAwLjA8L2Jhc2VJbXBvbmlibGU+CiAgICAgICAgICAgICAgICA8dGFyaWZhPjEyLjA8L3RhcmlmYT4KICAgICAgICAgICAgICAgIDx2YWxvcj4xMjAwLjA8L3ZhbG9yPgogICAgICAgICAgICA8L3RvdGFsSW1wdWVzdG8+CiAgICAgICAgPC90b3RhbENvbkltcHVlc3Rvcz4KICAgICAgICA8aW1wb3J0ZVRvdGFsPjExMjAwLjA8L2ltcG9ydGVUb3RhbD4KICAgICAgICA8bW9uZWRhPkRPTEFSPC9tb25lZGE+CiAgICAgICAgPHBhZ29zPgogICAgICAgICAgICA8cGFnbz4KICAgICAgICAgICAgICAgIDxmb3JtYVBhZ28+MTY8L2Zvcm1hUGFnbz4KICAgICAgICAgICAgICAgIDx0b3RhbD4xMTIwMC4wPC90b3RhbD4KICAgICAgICAgICAgICAgIDxwbGF6bz4wPC9wbGF6bz4KICAgICAgICAgICAgICAgIDx1bmlkYWRUaWVtcG8+ZGlhczwvdW5pZGFkVGllbXBvPgogICAgICAgICAgICA8L3BhZ28+CiAgICAgICAgPC9wYWdvcz4KICAgIDwvaW5mb0ZhY3R1cmE+CiAgICA8ZGV0YWxsZXM+CiAgICAgICAgPGRldGFsbGU+CiAgICAgICAgICAgIDxjb2RpZ29QcmluY2lwYWw+MTE5MDQ8L2NvZGlnb1ByaW5jaXBhbD4KICAgICAgICAgICAgPGNvZGlnb0F1eGlsaWFyPjExOTA0PC9jb2RpZ29BdXhpbGlhcj4KICAgICAgICAgICAgPGRlc2NyaXBjaW9uPlBFVUFCQTwvZGVzY3JpcGNpb24+CiAgICAgICAgICAgIDxjYW50aWRhZD4xLjA8L2NhbnRpZGFkPgogICAgICAgICAgICA8cHJlY2lvVW5pdGFyaW8+MTAwMDAuMDwvcHJlY2lvVW5pdGFyaW8+CiAgICAgICAgICAgIDxkZXNjdWVudG8+MC4wPC9kZXNjdWVudG8+CiAgICAgICAgICAgIDxwcmVjaW9Ub3RhbFNpbkltcHVlc3RvPjEwMDAwLjA8L3ByZWNpb1RvdGFsU2luSW1wdWVzdG8+CiAgICAgICAgICAgIDxpbXB1ZXN0b3M+CiAgICAgICAgICAgICAgICA8aW1wdWVzdG8+CiAgICAgICAgICAgICAgICAgICAgPGNvZGlnbz4yPC9jb2RpZ28+CiAgICAgICAgICAgICAgICAgICAgPGNvZGlnb1BvcmNlbnRhamU+MjwvY29kaWdvUG9yY2VudGFqZT4KICAgICAgICAgICAgICAgICAgICA8dGFyaWZhPjEyLjA8L3RhcmlmYT4KICAgICAgICAgICAgICAgICAgICA8YmFzZUltcG9uaWJsZT4xMDAwMC4wPC9iYXNlSW1wb25pYmxlPgogICAgICAgICAgICAgICAgICAgIDx2YWxvcj4xMjAwLjA8L3ZhbG9yPgogICAgICAgICAgICAgICAgPC9pbXB1ZXN0bz4KICAgICAgICAgICAgPC9pbXB1ZXN0b3M+CiAgICAgICAgPC9kZXRhbGxlPgogICAgPC9kZXRhbGxlcz4KPGRzOlNpZ25hdHVyZSB4bWxuczpkcz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnIyIgeG1sbnM6ZXRzaT0iaHR0cDovL3VyaS5ldHNpLm9yZy8wMTkwMy92MS4zLjIjIiBJZD0iU2lnbmF0dXJlNjgwNjA1Ij4KPGRzOlNpZ25lZEluZm8gSWQ9IlNpZ25hdHVyZS1TaWduZWRJbmZvMjM1NTkyIj4KPGRzOkNhbm9uaWNhbGl6YXRpb25NZXRob2QgQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy9UUi8yMDAxL1JFQy14bWwtYzE0bi0yMDAxMDMxNSIvPgo8ZHM6U2lnbmF0dXJlTWV0aG9kIEFsZ29yaXRobT0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnI3JzYS1zaGExIi8+CjxkczpSZWZlcmVuY2UgSWQ9IlNpZ25lZFByb3BlcnRpZXNJRDEwODAwNCIgVHlwZT0iaHR0cDovL3VyaS5ldHNpLm9yZy8wMTkwMyNTaWduZWRQcm9wZXJ0aWVzIiBVUkk9IiNTaWduYXR1cmU2ODA2MDUtU2lnbmVkUHJvcGVydGllczY3MTk5NSI+CjxkczpEaWdlc3RNZXRob2QgQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwLzA5L3htbGRzaWcjc2hhMSIvPgo8ZHM6RGlnZXN0VmFsdWU+d09VUHdlcnBZenM1eGpFSEJ5S2ZYQXNUZDBRPTwvZHM6RGlnZXN0VmFsdWU+CjwvZHM6UmVmZXJlbmNlPgo8ZHM6UmVmZXJlbmNlIFVSST0iI0NlcnRpZmljYXRlMTQyMDA2OCI+CjxkczpEaWdlc3RNZXRob2QgQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwLzA5L3htbGRzaWcjc2hhMSIvPgo8ZHM6RGlnZXN0VmFsdWU+M1hCMXRVVUpRYXpIVnRuaG5GRTF6dUxUa3ZFPTwvZHM6RGlnZXN0VmFsdWU+CjwvZHM6UmVmZXJlbmNlPgo8ZHM6UmVmZXJlbmNlIElkPSJSZWZlcmVuY2UtSUQtNDExMTczIiBVUkk9IiNjb21wcm9iYW50ZSI+CjxkczpUcmFuc2Zvcm1zPgo8ZHM6VHJhbnNmb3JtIEFsZ29yaXRobT0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnI2VudmVsb3BlZC1zaWduYXR1cmUiLz4KPC9kczpUcmFuc2Zvcm1zPgo8ZHM6RGlnZXN0TWV0aG9kIEFsZ29yaXRobT0iaHR0cDovL3d3dy53My5vcmcvMjAwMC8wOS94bWxkc2lnI3NoYTEiLz4KPGRzOkRpZ2VzdFZhbHVlPjRHZ01kUjBBa3VKRVpraUlua3hDTnJ0TkdiRT08L2RzOkRpZ2VzdFZhbHVlPgo8L2RzOlJlZmVyZW5jZT4KPC9kczpTaWduZWRJbmZvPgo8ZHM6U2lnbmF0dXJlVmFsdWUgSWQ9IlNpZ25hdHVyZVZhbHVlNzc2Njk5Ij4KWjJPZm1DVklpMHdOaUpNdEhXcTdoV2hDVUhNWlJIb3lYdGNJWHlBOHNLUzd0anZMZGdvb2UxN1F5bEx6NE1lSjFSSVlWNHZJZGVzLwpwM05rd09HcEZwbkg4MnpWejlWYml4aEdZcXd0bDhpK3h1WnJqenErcXJCVU5iL3NMTGlqWGprd2NkcWtEbWRHWlNiVVAzVVFaeDR3Ck8xZ1AxSTNISXQyckhma21tYVF1YVU0Q2VZQUgwbkRjMnJaa2RvVC9RN0JTaFhWZFV2RlQyNmVWdWhYUTZQR01CaGQvejI1WUdsR2sKZExjNitzOFVHR3VkcVhTVkJnR0NNbTNEbVBHakJEWmdoY0R1S1ZlZFJDd3J3OTBZWUhWRndNZVdIcmIwNjVjTE01YXNqYVJHU2VwSgpFVmNhSnhKL1hXWWNVMmVocVhRcUs3aU5wRnZhSjNocWlxdmFmQT09CjwvZHM6U2lnbmF0dXJlVmFsdWU+CjxkczpLZXlJbmZvIElkPSJDZXJ0aWZpY2F0ZTE0MjAwNjgiPgo8ZHM6WDUwOURhdGE+CjxkczpYNTA5Q2VydGlmaWNhdGU+Ck1JSUxlakNDQ1dLZ0F3SUJBZ0lFTzhWTzNEQU5CZ2txaGtpRzl3MEJBUXNGQURDQm1URUxNQWtHQTFVRUJoTUNSVU14SFRBYkJnTlYKQkFvTUZGTkZRMVZTU1ZSWklFUkJWRUVnVXk1QkxpQXhNVEF3TGdZRFZRUUxEQ2RGVGxSSlJFRkVJRVJGSUVORlVsUkpSa2xEUVVOSgpUMDRnUkVVZ1NVNUdUMUpOUVVOSlQwNHhPVEEzQmdOVkJBTU1NRUZWVkU5U1NVUkJSQ0JFUlNCRFJWSlVTVVpKUTBGRFNVOU9JRk5WClFrTkJMVEVnVTBWRFZWSkpWRmtnUkVGVVFUQWVGdzB5TVRBeE1qVXlNREkzTWpCYUZ3MHlOREF4TWpVeU1ESTNNakJhTUlHZU1Rc3cKQ1FZRFZRUUdFd0pGUXpFZE1Cc0dBMVVFQ2d3VVUwVkRWVkpKVkZrZ1JFRlVRU0JUTGtFdUlERXhNREF1QmdOVkJBc01KMFZPVkVsRQpRVVFnUkVVZ1EwVlNWRWxHU1VOQlEwbFBUaUJFUlNCSlRrWlBVazFCUTBsUFRqRVZNQk1HQTFVRUJSTU1NalV3TVRJeE1UVXpOekU1Ck1TY3dKUVlEVlFRRERCNUJVa05GVEVsUElFeEZUMDVCVWtSUElGSkJUVWxTUlZvZ1FWbFBWa2t3Z2dFaU1BMEdDU3FHU0liM0RRRUIKQVFVQUE0SUJEd0F3Z2dFS0FvSUJBUUMycFJYTUF3YTEwL2VZblZ5NWhVZjZVOVV3WFNjSU1FZ3FjMk1Mc1UxTit4WUIydzQ0ZFdaNApOSkE2RXNPek5WWVZRQnA0TkhyTk1qTmlESVJqN1BmaTBZektoZ2VmN3p6Y0dsYnFVbGVNbVhsaDk1Sm45cW1VY2NFZGxBOWVlQmRQCkFoRUxSU0Q5Q0JCNUpiT2ZMaU9lOXpjVW5LZjFBQ1ZnbjJFL25CSEk4SkhwbGtqRUJDMGcrUklzb3hnUUhBNEdLb24wSjl2WDJyRlkKQlA3Tys3QXcwRHBYTWxOZk4ycXAwNzN0QXFIWEZkMXpsTVZjdk1QYS9COExwdHRhK2pWZysrWXFrRG9Ja1NVUXd4Z1NMNlRwRE9teQp0V1NEbHdwSExIYzRVa0gxOFpKZUJ0RGtxbnkwUVVNYmR3S205N212Z3lIKytUdnlBRldCdzR3TkRYR3BBZ01CQUFHamdnYkJNSUlHCnZUQlpCZ2dyQmdFRkJRY0JBUVJOTUVzd1NRWUlLd1lCQlFVSE1BR0dQV2gwZEhBNkx5OXZZM053WjNjdWMyVmpkWEpwZEhsa1lYUmgKTG01bGRDNWxZeTlsYW1KallTOXdkV0pzYVdOM1pXSXZjM1JoZEhWekwyOWpjM0F3SFFZRFZSME9CQllFRkFXbGw1RjNqdGx3ZlhEVgp3Wi8vY1lJVGFmbWZNQXdHQTFVZEV3RUIvd1FDTUFBd0h3WURWUjBqQkJnd0ZvQVVYQStGcEhRUS9LMEJMQm9BUFpNWENmbzVBZFl3Ckt3WURWUjBRQkNRd0lvQVBNakF5TVRBeE1qVXlNREkzTWpCYWdROHlNREkwTURFeU5USXdNamN5TUZvd2djd0dBMVVkTGdTQnhEQ0IKd1RDQnZxQ0J1NkNCdUlhQnRXeGtZWEE2THk5c1pHRndjMlF1YzJWamRYSnBkSGxrWVhSaExtNWxkQzVsWXk5RFRqMUJWVlJQVWtsRQpRVVFnUkVVZ1EwVlNWRWxHU1VOQlEwbFBUaUJUVlVKRFFTMHhJRk5GUTFWU1NWUlpJRVJCVkVFc1QxVTlSVTVVU1VSQlJDQkVSU0JEClJWSlVTVVpKUTBGRFNVOU9JRVJGSUVsT1JrOVNUVUZEU1U5T0xFODlVMFZEVlZKSlZGa2dSRUZVUVNCVExrRXVJREVzUXoxRlF6OWsKWld4MFlWSmxkbTlqWVhScGIyNU1hWE4wUDJKaGMyVXdhd1lEVlIwZ0JHUXdZakJnQmdvckJnRUVBWUttY2dJS01GSXdVQVlJS3dZQgpCUVVIQWdJd1JCNUNBRU1BWlFCeUFIUUFhUUJtQUdrQVl3QmhBR1FBYndBZ0FHUUFaUUFnQUUwQWFRQmxBRzBBWWdCeUFHOEFJQUJrCkFHVUFJQUJGQUcwQWNBQnlBR1VBY3dCaE1JSUNuZ1lEVlIwZkJJSUNsVENDQXBFd2dlV2dRYUEvaGoxb2RIUndPaTh2YjJOemNHZDMKTG5ObFkzVnlhWFI1WkdGMFlTNXVaWFF1WldNdlpXcGlZMkV2Y0hWaWJHbGpkMlZpTDNOMFlYUjFjeTl2WTNOd29vR2ZwSUdjTUlHWgpNVGt3TndZRFZRUUREREJCVlZSUFVrbEVRVVFnUkVVZ1EwVlNWRWxHU1VOQlEwbFBUaUJUVlVKRFFTMHhJRk5GUTFWU1NWUlpJRVJCClZFRXhNREF1QmdOVkJBc01KMFZPVkVsRVFVUWdSRVVnUTBWU1ZFbEdTVU5CUTBsUFRpQkVSU0JKVGtaUFVrMUJRMGxQVGpFZE1Cc0cKQTFVRUNnd1VVMFZEVlZKSlZGa2dSRUZVUVNCVExrRXVJREV4Q3pBSkJnTlZCQVlUQWtWRE1JSEVvSUhCb0lHK2hvRzdiR1JoY0RvdgpMMnhrWVhCelpDNXpaV04xY21sMGVXUmhkR0V1Ym1WMExtVmpMME5PUFVGVlZFOVNTVVJCUkNCRVJTQkRSVkpVU1VaSlEwRkRTVTlPCklGTlZRa05CTFRFZ1UwVkRWVkpKVkZrZ1JFRlVRU3hQVlQxRlRsUkpSRUZFSUVSRklFTkZVbFJKUmtsRFFVTkpUMDRnUkVVZ1NVNUcKVDFKTlFVTkpUMDRzVHoxVFJVTlZVa2xVV1NCRVFWUkJJRk11UVM0Z01TeERQVVZEUDJObGNuUnBabWxqWVhSbFVtVjJiMk5oZEdsdgpia3hwYzNRL1ltRnpaVENCMzZDQjNLQ0IyWWFCMW1oMGRIQnpPaTh2Y0c5eWRHRnNMVzl3WlhKaFpHOXlMbk5sWTNWeWFYUjVaR0YwCllTNXVaWFF1WldNdlpXcGlZMkV2Y0hWaWJHbGpkMlZpTDNkbFltUnBjM1F2WTJWeWRHUnBjM1EvWTIxa1BXTnliQ1pwYzNOMVpYSTkKUTA0OVFWVlVUMUpKUkVGRUlFUkZJRU5GVWxSSlJrbERRVU5KVDA0Z1UxVkNRMEV0TVNCVFJVTlZVa2xVV1NCRVFWUkJMRTlWUFVWTwpWRWxFUVVRZ1JFVWdRMFZTVkVsR1NVTkJRMGxQVGlCRVJTQkpUa1pQVWsxQlEwbFBUaXhQUFZORlExVlNTVlJaSUVSQlZFRWdVeTVCCkxpQXhMRU05UlVNd0N3WURWUjBQQkFRREFnWGdNREFHQTFVZEVRUXBNQ2VCSld4eVlXMXBjbVY2UUdaMWJtUmhZMmx2Ym1GalkybHYKYm5OdmJHbGtZWEpwWVM1dmNtY3dHZ1lLS3dZQkJBR0NwbklEQVFRTURBb3dPVEkyTnpjd05qazBNQ0FHQ2lzR0FRUUJncVp5QXdJRQpFZ3dRUVZKRFJVeEpUeUJNUlU5T1FWSkVUekFYQmdvckJnRUVBWUttY2dNREJBa01CMUpCVFVsU1JWb3dGUVlLS3dZQkJBR0NwbklECkJBUUhEQVZCV1U5V1NUQWZCZ29yQmdFRUFZS21jZ01GQkJFTUQwcEZSa1VnUmtsT1FVNURTVVZTVHpBM0Jnb3JCZ0VFQVlLbWNnTUgKQkNrTUowTkJUVWxNVHlCT1JWWkJVa1ZhSUZOUFRFRlNJRElnV1NCQlIxVlRWRWxPSUVaU1JVbFNSVEFiQmdvckJnRUVBWUttY2dNSQpCQTBNQ3pVNU16UXlOalUxT0RJMU1Ca0dDaXNHQVFRQmdxWnlBd2tFQ3d3SlIxVkJXVUZSVlVsTU1ETUdDaXNHQVFRQmdxWnlBd29FCkpRd2pSbFZPUkVGRFNVOU9JRUpGVGtWR1NVTkJJRUZEUTBsUFRpQlRUMHhKUkVGU1NVRXdIUVlLS3dZQkJBR0NwbklEQ3dRUERBMHcKT1RreU1UYzFOamN5TURBeE1CY0dDaXNHQVFRQmdxWnlBd3dFQ1F3SFJVTlZRVVJQVWpBU0Jnb3JCZ0VFQVlLbWNnTWRCQVFNQWs1dgpNQjhHQ2lzR0FRUUJncVp5QXlBRUVRd1BNREF4TURBeU1EQXdNRGswTlRZMU1CTUdDaXNHQVFRQmdxWnlBeUVFQlF3RFVFWllNQkVHCkNpc0dBUVFCZ3FaeUF5SUVBd3dCTGpBTkJna3Foa2lHOXcwQkFRc0ZBQU9DQWdFQUQ0YnlreHV2bnpSZCswYW84bFZTUU16U2s0L2gKSGRlWDdNVlRUeVl2VUVsWkNKN3BhVzk2MmJWeGp1RnlwZEVVZFlMeWNXME5kdzNweG5ueWhUeHR2SmRsN3AvZWNOejEreDNqQmdtSwpzL2lsMTZCcUxrVk13WDlBNmU1V01lTDNEZ0RKQlU1bnpiRnYxZDkxenMvTk5DSVVVdkVTeHVxaGNYTGE5OHFkS2dtRGcyeEpVR25mCnEzSVVkQWVHZzkvaTY2dVp4ODZ3NFhjTjBDMFNZbUNyTDQ2UGdWVm5WcHV0U2Vma29yUmNzQ0lEL2ltZmd2TmdQVUZTU0FsY0pFVmMKeUZFd2pCSWJFT3JuSjZwV2pVSmxxdHliaUhwTW5OaWk1dFZGMWttTXMzWGJXaEhaSHRuall6czZrQTRBbXJjZVIwRTJTSVBCWnRuLwoxeHp3MXZQUkxra2o1SE5SSzd3OTQ5UUFuUzZMb2VjYWY0Vmdxa3JpazQvR1lvWTM3MVVWM0pObkZXYlJSSEFXWjFDYVRPbEVDekJUCjd6RWVtVTBlODRyQmZNeGV6NG9veHJHS09yandDTk9yZTgvZWNKU292akJNdjlQYSs3MTJiQkdtSW15Z0p0SzFwVzVSanJQeVYrSkMKdDdOVkE2RDBDZk5uWDNodWxncmlPZlQ3K3g1WTlrd0t2WlVMbFpTYXpsbHJ2Q2hBRWxTYlFYOUsxcWpua28waDVGTng1ZkFBeGd3RgpWM2loQlZkVW1MSFhBUlp1a2VrUGJHWG5yRG11MmoxNXlISnozVnZPMlVJNGt5NTJvMHhtazFXM0lsN0FxdnZ1SzVnTzBkN0NpeXFmCmhMZGhuWHBYWDJmeUdSNWlXZDFDU29KTE1oKzFBRWM3VnJOM3NnTk5LYkRLU0pJPQo8L2RzOlg1MDlDZXJ0aWZpY2F0ZT4KPC9kczpYNTA5RGF0YT4KPGRzOktleVZhbHVlPgo8ZHM6UlNBS2V5VmFsdWU+CjxkczpNb2R1bHVzPgp0cVVWekFNR3RkUDNtSjFjdVlWSCtsUFZNRjBuQ0RCSUtuTmpDN0ZOVGZzV0Fkc09PSFZtZURTUU9oTERzelZXRlVBYWVEUjZ6VEl6CllneUVZK3ozNHRHTXlvWUhuKzg4M0JwVzZsSlhqSmw1WWZlU1ovYXBsSEhCSFpRUFhuZ1hUd0lSQzBVZy9RZ1FlU1d6bnk0am52YzMKRkp5bjlRQWxZSjloUDV3UnlQQ1I2WlpJeEFRdElQa1NMS01ZRUJ3T0JpcUo5Q2ZiMTlxeFdBVCt6dnV3TU5BNlZ6SlRYemRxcWRPOQo3UUtoMXhYZGM1VEZYTHpEMnZ3ZkM2YmJXdm8xWVB2bUtwQTZDSkVsRU1NWUVpK2s2UXpwc3JWa2c1Y0tSeXgzT0ZKQjlmR1NYZ2JRCjVLcDh0RUZERzNjQ3B2ZTVyNE1oL3ZrNzhnQlZnY09NRFExeHFRPT0KPC9kczpNb2R1bHVzPgo8ZHM6RXhwb25lbnQ+QVFBQjwvZHM6RXhwb25lbnQ+CjwvZHM6UlNBS2V5VmFsdWU+CjwvZHM6S2V5VmFsdWU+CjwvZHM6S2V5SW5mbz4KPGRzOk9iamVjdCBJZD0iU2lnbmF0dXJlNjgwNjA1LU9iamVjdDEwMjEzNzEiPjxldHNpOlF1YWxpZnlpbmdQcm9wZXJ0aWVzIFRhcmdldD0iI1NpZ25hdHVyZTY4MDYwNSI+PGV0c2k6U2lnbmVkUHJvcGVydGllcyBJZD0iU2lnbmF0dXJlNjgwNjA1LVNpZ25lZFByb3BlcnRpZXM2NzE5OTUiPjxldHNpOlNpZ25lZFNpZ25hdHVyZVByb3BlcnRpZXM+PGV0c2k6U2lnbmluZ1RpbWU+MjAyMS0xMC0wNFQyMDo0NDozMi0wNTowMDwvZXRzaTpTaWduaW5nVGltZT48ZXRzaTpTaWduaW5nQ2VydGlmaWNhdGU+PGV0c2k6Q2VydD48ZXRzaTpDZXJ0RGlnZXN0PjxkczpEaWdlc3RNZXRob2QgQWxnb3JpdGhtPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwLzA5L3htbGRzaWcjc2hhMSIvPjxkczpEaWdlc3RWYWx1ZT5yakFxLzZqczNRM05GNTk2VUlOTDdJcDRVNUk9PC9kczpEaWdlc3RWYWx1ZT48L2V0c2k6Q2VydERpZ2VzdD48ZXRzaTpJc3N1ZXJTZXJpYWw+PGRzOlg1MDlJc3N1ZXJOYW1lPkNOPUFVVE9SSURBRCBERSBDRVJUSUZJQ0FDSU9OIFNVQkNBLTEgU0VDVVJJVFkgREFUQSxPVT1FTlRJREFEIERFIENFUlRJRklDQUNJT04gREUgSU5GT1JNQUNJT04sTz1TRUNVUklUWSBEQVRBIFMuQS4gMSxDPUVDPC9kczpYNTA5SXNzdWVyTmFtZT48ZHM6WDUwOVNlcmlhbE51bWJlcj4xMDAyNzg2NTI0PC9kczpYNTA5U2VyaWFsTnVtYmVyPjwvZXRzaTpJc3N1ZXJTZXJpYWw+PC9ldHNpOkNlcnQ+PC9ldHNpOlNpZ25pbmdDZXJ0aWZpY2F0ZT48L2V0c2k6U2lnbmVkU2lnbmF0dXJlUHJvcGVydGllcz48ZXRzaTpTaWduZWREYXRhT2JqZWN0UHJvcGVydGllcz48ZXRzaTpEYXRhT2JqZWN0Rm9ybWF0IE9iamVjdFJlZmVyZW5jZT0iI1JlZmVyZW5jZS1JRC00MTExNzMiPjxldHNpOkRlc2NyaXB0aW9uPkNvbnRlbmlkbyBDb21wcm9iYW50ZTwvZXRzaTpEZXNjcmlwdGlvbj48ZXRzaTpNaW1lVHlwZT50ZXh0L3htbDwvZXRzaTpNaW1lVHlwZT48L2V0c2k6RGF0YU9iamVjdEZvcm1hdD48L2V0c2k6U2lnbmVkRGF0YU9iamVjdFByb3BlcnRpZXM+PC9ldHNpOlNpZ25lZFByb3BlcnRpZXM+PC9ldHNpOlF1YWxpZnlpbmdQcm9wZXJ0aWVzPjwvZHM6T2JqZWN0PjwvZHM6U2lnbmF0dXJlPjwvZmFjdHVyYT5dXT48L2NvbXByb2JhbnRlPgo8L2F1dG9yaXphY2lvbj4K"}
            
            
                b64 = json.loads(response.text)['archivo']
                binario = b64decode(b64)
                f = open('file.pdf', 'wb')
                f.write(binario)
                f.close()


                with open('file.pdf', "rb") as f:
                    data = f.read()
                    file=bytes(b64encode(data))



                self.env['ir.attachment'].create({
                                                         'res_id':comprobante.id,
                                                         'res_model':model,
                                                         'name':'{0}.pdf'.format(nombreComprobante),
                                                          'datas':file,
                                                          'type':'binary', 
                                                          'store_fname':'{0}.pdf'.format(nombreComprobante)
                                                          })

            

    def jobEnvioServicioProcesarFactura(self,):
        
        self.env.cr.execute("""select * from bitacora_consumo_servicios where state='pendiente'  """)
        registros = self.env.cr.dictfetchall()
        hoy = datetime.now()

        for registro in registros:
            bitacora=self.env['bitacora.consumo.servicios'].browse(registro['id'])
            bitacora.procesarComprobante()




    def jobEnvioServicioValidarFactura(self,):
        
        self.env.cr.execute("""select * from bitacora_consumo_servicios where state='proceso'  """)
        registros = self.env.cr.dictfetchall()
        hoy = datetime.now()

        for registro in registros:
            bitacora=self.env['bitacora.consumo.servicios'].browse(registro['id'])
            bitacora.validarComprobante()


    def jobEnvioServicioDescargarRideXML(self,):
        
        self.env.cr.execute("""select * from bitacora_consumo_servicios where state='validar'  """)
        registros = self.env.cr.dictfetchall()
        hoy = datetime.now()

        for registro in registros:
            bitacora=self.env['bitacora.consumo.servicios'].browse(registro['id'])
            bitacora.state='generada'
            bitacora.descargarXML()
            bitacora.descargarRide()
            comprobante,model,nombreComprobante,responseKey,template_id=bitacora.seleccionComprobante()

            template = self.env['mail.template'].browse(template_id)

            email_id=template.send_mail(registro['id'])
            
            obj_mail=self.env['mail.mail'].browse(email_id)
            obj_mail.attachment_ids=self.env['ir.attachment'].search([('res_model','=','account.move'),('res_id','=',registro['invoice_id'])])
            try:
                obj_mail.send()
            except:
                pass
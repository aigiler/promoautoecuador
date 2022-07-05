# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
import datetime
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
from dateutil.parser import parse


class ItemsPatrimonio(models.Model):
    _name = 'items.patrimonio'
    _description = 'Items Patrimonio'
    _rec_name= 'nombre'
    
    nombre = fields.Char('Nombre',  required=True)
    descripcion=fields.Text('Descripcion',  required=True)
  


class ItemsDocumentosPostventa(models.Model):
    _name = 'documentos.postventa'
    _description = 'Documento Postventa'
    _rec_name= 'nombre'
    
    nombre = fields.Char('Nombre',  required=True)
    tipo_devolucion = fields.Selection(selection=[('TODOS', 'TODOS'),
        ('DEVOLUCION DE VALORES SIN FIRMAS', 'DEVOLUCION DE VALORES SIN FIRMAS'),
        ('DEVOLUCION DE RESERVA', 'DEVOLUCION DE RESERVA'),
        ('DEVOLUCION DE LICITACION', 'DEVOLUCION DE LICITACION'),
        ('DEVOLUCION POR DESISTIMIENTO DEL CONTRATO', 'DEVOLUCION POR DESISTIMIENTO DEL CONTRATO'),
        ('DEVOLUCION POR CALIDAD DE VENTA', 'DEVOLUCION POR CALIDAD DE VENTA')], string='Estado', default='borrador', track_visibility='onchange')

  

class ItemsDocumentosLegal(models.Model):
    _name = 'documentos.legal'
    _description = 'Documentos Legal'
    _rec_name= 'nombre'
    
    nombre = fields.Char('Nombre',  required=True)
    tipo_accion = fields.Selection(selection=[('TODOS', 'TODOS'),
        ('CLIENTE', 'CLIENTE'),
        ('ABOGADO', 'ABOGADO'),
        ('CONSEJO', 'CONSEJO'),
        ('DEFENSORIA', 'DEFENSORIA'),
        ('FISCALIA', 'FISCALIA'),
        ('CAMARA DE COMERCIO', 'CAMARA DE COMERCIO')], string='Estado', default='borrador', track_visibility='onchange')



class DocumentosPostventa(models.Model):
    _name = 'devolucion.documentos.postventa'
    _description = 'Requisitos'
    _rec_name= 'documento_id'
    
    documento_id=fields.Many2one("documentos.postventa",string="Nombre")
    archivo = fields.Binary('Archivo', required=True)
    devolucion_id=fields.Many2one("devolucion.monto",string="Devolución")


class DocumentosLegal(models.Model):
    _name = 'devolucion.documentos.legal'
    _description = 'Requisitos'
    _rec_name= 'documento_id'
    
    documento_id=fields.Many2one("documentos.legal",string="Nombre")
    archivo = fields.Binary('Archivo', required=True)
    devolucion_id=fields.Many2one("devolucion.monto",string="Devolución")

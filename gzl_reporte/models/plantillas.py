# -*- coding: utf-8 -*-

import xml.etree.ElementTree as xee
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError, except_orm





class PlantillasDinamicasInformes(models.Model):
    _name = 'plantillas.dinamicas.informes' 
    _description = 'Plantillas dinamicas para Informes'

    name = fields.Char( string='Nombre',required=True)
    identificador_clave = fields.Char( string='Identificador Clave')



    campos_ids = fields.One2many('campos.informe', 'informe_id', string='Identificadores para Informe')  
    archivos_ids = fields.One2many('archivos.plantilla.informe', 'informe_id', string='Archivos para Informe')  

    #directorio = fields.Many2one('muk_dms.directory',string='directorio') 
    directorio = fields.Char(string='directorio')  

class CamposInforme(models.Model):
    _name = "campos.informe"

    name = fields.Char('Nombre del Campo')
    identificar_docx = fields.Char('Identificador Documento Word')
    label = fields.Char('Label')
    informe_id = fields.Many2one('plantillas.dinamicas.informes','Informe')
    fila = fields.Integer('Fila de Documento Excel')
    columna = fields.Integer('Columna de Documento Excel')
    parent_id = fields.Many2one('campos.informe',  index=True)
    child_ids = fields.One2many('campos.informe', 'parent_id', string='Detalle')  


class ArchivosPlantilla(models.Model):
    _name = "archivos.plantilla.informe"

    informe_id = fields.Many2one('plantillas.dinamicas.informes','Informe')
    plantilla = fields.Binary(string='Plantilla para Descargars')  
    company_id = fields.Many2one('res.company','Compañia')
    color = fields.Char('Color')






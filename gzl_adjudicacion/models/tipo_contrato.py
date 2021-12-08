# -*- coding: utf-8 -*-

from odoo import api, fields, models


class TipoContratoAdjudicado(models.Model):
    
    _name = 'tipo.contrato.adjudicado'
    _description = 'Tipos de Contrato adjudicado'
  
    name=fields.Char('Nombre',  required=True)
    descripcion=fields.Text('Descripcion',  required=True)
    active=fields.Boolean( default=True)

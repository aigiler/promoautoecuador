# -*- coding: utf-8 -*-

from odoo import api, fields, models


class TipoContratoAdjudicado(models.Model):
    
    _name = 'tipo.contrato.adjudicado'
    _description = 'Tipos de Contrato adjudicado'
  
    name=fields.Char('Nombre',  required=True)
    descripcion=fields.Text('Descripcion',  required=True)
    numero_ganadores=fields.Integer('Número Ganadores',  required=True)
    numero_suplentes=fields.Integer('Número Suplentes',  required=True)
    active=fields.Boolean( default=True)

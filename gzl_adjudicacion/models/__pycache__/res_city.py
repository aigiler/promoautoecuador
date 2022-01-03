# -*- coding: utf-8 -*-

from odoo import api, fields, models


class City(models.Model):
    
    _name = 'res.country.city'
    _description = 'Tipos de Contrato adjudicado'
  
    name=fields.Char('Nombre',  required=True)
    descripcion=fields.Text('Descripcion',  required=True)
    code=fields.Char('Código',  required=True)
    numero_ganadores=fields.Integer('Número Ganadores',  required=True)
    numero_suplentes=fields.Integer('Número Suplentes',  required=True)
    active=fields.Boolean( default=True)
 
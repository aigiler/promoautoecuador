# -*- coding: utf-8 -*-

from odoo import api, fields, models


class TipoContratoAdjudicado(models.Model):
    
    _name = 'tipo.contrato.adjudicado'
    _description = 'Tipos de Contrato adjudicado'
  
    name=fields.Char('Nombre')
    descripcion=fields.Text('Descripcion')
    code=fields.Char('Código')
    numero_ganadores=fields.Integer('Número Ganadores')
    numero_suplentes=fields.Integer('Número Suplentes')
    active=fields.Boolean( default=True)
 

class TipoAsamblea(models.Model):
    
    _name = 'tipo.asamblea'
    _description = 'Tipos de Asamblea'
  
    name=fields.Selection(selection=[
        ('licitacion', 'Licitación'),
        ('evaluacion', 'Evaluación'),
        ('exacto', 'Exacto'),
        ('programo', 'Programo'),
    ], string='Tipo', default='licitación', track_visibility='onchange')

    numero_ganadores=fields.Integer('Número Ganadores')
    numero_suplentes=fields.Integer('Número Suplentes')
    active=fields.Boolean( default=True)
 
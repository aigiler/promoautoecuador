# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Asamblea(models.Model):
    
    _name = 'asamblea'
    _description = 'Proceso de Asamblea'
  
    name=fields.Char('Nombre',  required=True)
    descripcion=fields.Text('Descripcion',  required=True)
    active=fields.Boolean( default=True)
    grupo_id = fields.Many2one('grupo.adjudicado')


    integrantes = fields.One2many('integrante.grupo.adjudicado.asamblea','asamblea_id')

      
   

class IntegrantesGrupoAsamblea(models.Model):
    
    _name = 'integrante.grupo.adjudicado.asamblea'
    _description = 'Integrantes de grupo adjudicado en asamblea'
  
    descripcion=fields.Char('Descripcion')
    asamblea_id = fields.Many2one('asamblea')
    adjudicado_id = fields.Many2one('res.partner')
    monto=fields.Float('Monto',  )

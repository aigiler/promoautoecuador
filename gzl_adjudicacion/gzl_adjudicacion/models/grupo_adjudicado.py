# -*- coding: utf-8 -*-

from odoo import api, fields, models


class GrupoAdjudicado(models.Model):
    
    _name = 'grupo.adjudicado'
    _description = 'Grupo Adjudicado'
  
    name=fields.Char('Nombre',  required=True)
    descripcion=fields.Text('Descripcion',  required=True)
    active=fields.Boolean( default=True)
    integrantes = fields.One2many('integrante.grupo.adjudicado','grupo_id')
    monto_grupo = fields.Float(String="Monto")
    secuencia = fields.Char(index=True)

    @api.model
    def create(self, vals):
        g_adjudicados = super(GrupoAdjudicado, self).create(vals)
        vals['secuencia'] = self.env['ir.sequence'].next_by_code('grupo.adjudicado')
        return g_adjudicados
      
   

class IntegrantesGrupo(models.Model):
    
    _name = 'integrante.grupo.adjudicado'
    _description = 'Integrantes de Grupo Adjudicado'
  
    descripcion=fields.Char('Descripcion',  )
    grupo_id = fields.Many2one('grupo.adjudicado')
    adjudicado_id = fields.Many2one('res.partner')
    monto=fields.Float('Monto')

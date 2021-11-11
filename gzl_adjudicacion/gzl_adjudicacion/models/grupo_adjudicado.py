# -*- coding: utf-8 -*-

from odoo import api, fields, models


class GrupoAdjudicado(models.Model):
    
    _name = 'grupo.adjudicado'
    _description = 'Grupo Adjudicado'
  
    name=fields.Char('Nombre',  required=True)
    descripcion=fields.Text('Descripcion',  required=True)
    active=fields.Boolean( default=True)
    integrantes = fields.One2many('integrante.grupo.adjudicado','grupo_id')
    monto_grupo = fields.Float(String="Cartera del grupo", compute="compute_monto_cartera")
    secuencia = fields.Char(index=True)
    asamblea_id = fields.Many2one('asamblea')
    estado = fields.Selection(selection=[
            ('en_conformacion', 'En Conformación'),
            ('cerrado', 'Cerrado')
            ], string='Estado', copy=False, tracking=True, default='en_conformacion')
     

    @api.model
    def create(self, vals):
        vals['secuencia'] = self.env['ir.sequence'].next_by_code('grupo.adjudicado')
        return super(GrupoAdjudicado, self).create(vals)

    
    @api.depends('integrantes.monto')
    def compute_monto_cartera(self):
        monto=0
        for l in self.integrantes:
            monto += l.monto
        self.monto_grupo=monto
   

class IntegrantesGrupo(models.Model):
    
    _name = 'integrante.grupo.adjudicado'
    _description = 'Integrantes de Grupo Adjudicado'
  
    descripcion=fields.Char('Descripcion',  )
    grupo_id = fields.Many2one('grupo.adjudicado')
    adjudicado_id = fields.Many2one('res.partner')
    monto=fields.Float('Monto')
    nro_cuota_licitar = fields.Integer(string='Nro de Cuotas a Licitar')
    carta_licitacion = fields.Selection([('si', 'Si'), ('no', 'No')], string='Carta Licitación')
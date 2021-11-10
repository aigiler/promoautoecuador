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
    junta = fields.One2many('hr.employee', 'asamblea_id')
    fecha_inicio = fields.Datetime(String='Fecha Inicio')
    fecha_fin = fields.Datetime(String='Fecha Fin')
    secuencia = fields.Char(index=True)
    estado = fields.Selection(selection=[
            ('borrador', 'Borrador'),
            ('en_curso', 'En Curso'),
            ('seleccion_part', 'Selección de Participantes'),
            ('cerrado', 'Cerrado')
            ], string='Estado', copy=False, tracking=True, default='borrador')

    @api.model
    def create(self, vals):
        asamblea = super(Asamblea, self).create(vals)
        vals['secuencia'] = self.env['ir.sequence'].next_by_code('asamblea')
        return asamblea

    @api.onchange('grupo_id')
    def agregar_grupo_a_asamblea(self):
        self.grupo_id.integrantes=[]
        for l in self.grupo_id.integrantes:
            self.env['integrante.grupo.adjudicado.asamblea'].create({
                'descripcion':l.descripcion,
                'asamblea_id':self.id,
                'adjudicado_id':l.adjudicado_id.id,
                'monto':l.monto,
            })
      
   

class IntegrantesGrupoAsamblea(models.Model):
    _name = 'integrante.grupo.adjudicado.asamblea'
    _description = 'Integrantes de grupo adjudicado en asamblea'
  
    descripcion=fields.Char('Descripcion')
    asamblea_id = fields.Many2one('asamblea')
    adjudicado_id = fields.Many2one('res.partner')
    monto=fields.Float('Monto' )
    es_ganador = fields.Boolean(String='Ganador', default=False)

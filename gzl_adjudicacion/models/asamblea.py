# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Asamblea(models.Model):
    _name = 'asamblea'
    _description = 'Proceso de Asamblea'

    name=fields.Char('Nombre')
    descripcion=fields.Text('Descripcion',  required=True)
    active=fields.Boolean( default=True)
    integrantes = fields.One2many('integrante.grupo.adjudicado.asamblea','asamblea_id')
    junta = fields.One2many('junta.grupo.asamblea', 'asamblea_id')
    fecha_inicio = fields.Datetime(String='Fecha Inicio')
    fecha_fin = fields.Datetime(String='Fecha Fin')
    secuencia = fields.Char(index=True)
    tipo_asamblea = fields.Many2one('tipo.contrato.adjudicado', string='Tipo de Asamblea')
    state = fields.Selection(selection=[
            ('borrador', 'Borrador'),
            ('en_curso', 'En Curso'),
            ('cerrado', 'Cerrado')
            ], string='Estado', copy=False, tracking=True, default='borrador')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('asamblea')
        return super(Asamblea, self).create(vals)

    # @api.onchange('grupo_id')
    # def agregar_grupo_a_asamblea(self):
    #     self.grupo_id.integrantes=[]
    #     for l in self.grupo_id.integrantes:
    #         self.env['integrante.grupo.adjudicado.asamblea'].create({
    #             'descripcion':l.descripcion,
    #             'asamblea_id':self.id,
    #             'adjudicado_id':l.adjudicado_id.id,
    #             'monto':l.monto,
    #         })
      
   

class IntegrantesGrupoAsamblea(models.Model):
    _name = 'integrante.grupo.adjudicado.asamblea'
    _description = 'Integrantes de grupo adjudicado en asamblea'
  
    asamblea_id = fields.Many2one('asamblea')
    grupo_adjudicado_id = fields.Many2one('grupo.adjudicado')
    integrantes_g = fields.One2many(related='grupo_adjudicado_id.integrantes')
    #adjudicado_id = fields.Many2one('res.partner')
    #monto=fields.Float('Monto' )
    #es_ganador = fields.Boolean(String='Ganador', default=False)

class JuntaGrupoAsamblea(models.Model):
    _name='junta.grupo.asamblea'

    asamblea_id = fields.Many2one('asamblea', string='Asamblea')
    empleado_id = fields.Many2one('hr.employee', string="Empleado")
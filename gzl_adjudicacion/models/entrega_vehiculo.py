# -*- coding: utf-8 -*-
from gzl_adjudicacion.models.contrato import Contrato
from odoo import api, fields, models


class EntregaVehiculo(models.Model):
    _name = 'entrega.vehiculo'
    _description = 'Entrega de vehiculo'

    name=fields.Char('Nombre')
    nombre=fields.Text('Nombre / Razón social',  required=True)
    nombre = fields.Many2one('res.partner', string="Nombre / Razón social")
    identificacion = fields.Many2one('res.partner.', 'val')
    # identificacion=fields.Text('Cédula de identidad',  required=True)
    descripcion=fields.Text('Descripcion',  required=True)
    direccion=fields.Text('Dirección',  required=True)
    grupo = fields.Many2one('grupo.adjudicado', string="Grupo")
    tipo_contrato = fields.Many2one('res.partner.', 'tipo_contrato')
    #contrato=fields.One2many('contrato.estado.cuenta', 'contrato_id')
    active=fields.Boolean( default=True)
    junta = fields.One2many('junta.grupo.asamblea', 'asamblea_id')
    secuencia = fields.Char(index=True)
    state = fields.Selection(selection=[
            ('borrador', 'Borrador'),
            ('cobranzas', 'Cobranzas'),
            ('entrega_de_vehiculo', 'Entrega de vehiculo')
            ], string='Estado', copy=False, tracking=True, default='borrador')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('entrega.vehiculo')
        return super(EntregaVehiculo, self).create(vals)

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
s
class JuntaGrupoAsamblea(models.Model):
    _name='junta.grupo.asamblea'

    asamblea_id = fields.Many2one('asamblea', string='Asamblea')
    empleado_id = fields.Many2one('hr.employee', string="Empleado")
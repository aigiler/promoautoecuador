# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Asamblea(models.Model):
    _name = 'asamblea'
    _description = 'Proceso de Asamblea'
    _rec_name = 'secuencia'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    secuencia = fields.Char(index=True)
    descripcion = fields.Text('Descripcion',  required=True,track_visibility='onchange')
    active = fields.Boolean(default=True,track_visibility='onchange')
    integrantes = fields.One2many(
        'integrante.grupo.adjudicado.asamblea', 'asamblea_id',track_visibility='onchange')
    # integrantes = fields.Many2many('integrante.grupo.adjudicado')

    junta = fields.One2many('junta.grupo.asamblea', 'asamblea_id',track_visibility='onchange')
    fecha_inicio = fields.Datetime(String='Fecha Inicio',track_visibility='onchange')
    fecha_fin = fields.Datetime(String='Fecha Fin',track_visibility='onchange')
    tipo_asamblea = fields.Many2one(
        'tipo.contrato.adjudicado', string='Tipo de Asamblea',track_visibility='onchange')
    state = fields.Selection(selection=[
            ('borrador', 'Borrador'),
            ('en_curso', 'En Curso'),
            ('pre_cierre', 'Pre cierre'),
            ('cerrado', 'Cerrado')
            ], string='Estado', copy=False, tracking=True, default='borrador',track_visibility='onchange')

    @api.model
    def create(self, vals):
        vals['secuencia'] = self.env['ir.sequence'].next_by_code('contrato')
        res = self.env['res.config.settings'].sudo(1).search([], limit=1, order="id desc")
        return super(Asamblea, self).create(vals)

    @api.constrains('secuencia')
    def constrains_valor_por_defecto(self): 
        res = self.env['res.config.settings'].sudo(1).search([], limit=1, order="id desc")

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

    def cambio_estado_boton_borrador(self):
        return self.write({"state": "en_curso"})

    def cambio_estado_boton_en_curso(self):
        return self.write({"state": "pre_cierre"})

    def cambio_estado_boton_pre_cierre(self):
        return self.write({"state": "cerrado"})



class IntegrantesGrupoAsamblea(models.Model):
    _name = 'integrante.grupo.adjudicado.asamblea'
    _description = 'Integrantes de grupo adjudicado en asamblea'

    asamblea_id = fields.Many2one('asamblea')
    grupo_adjudicado_id = fields.Many2one('grupo.adjudicado')
    integrantes_g = fields.One2many(related='grupo_adjudicado_id.integrantes')
    # adjudicado_id = fields.Many2one('res.partner')
    # monto=fields.Float('Monto' )
    # es_ganador = fields.Boolean(String='Ganador', default=False)


class JuntaGrupoAsamblea(models.Model):
    _name = 'junta.grupo.asamblea'

    asamblea_id = fields.Many2one('asamblea', string='Asamblea')
    empleado_id = fields.Many2one('hr.employee', string="Empleado")





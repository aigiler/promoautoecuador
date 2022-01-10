# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class TransaccionesGrupoSocio(models.Model):
    _name = 'transaccion.grupo.adjudicado'
    _description = 'Grupo  para proceso adjudicacion'


    grupo_id = fields.Many2one('grupo.adjudicado')

    adjudicado_id = fields.Many2one('res.partner', string="Nombre")
    contrato_id = fields.Many2one('contrato', string='Contrato')
    state = fields.Selection(selection=[
        ('borrador', 'Borrador'),
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('congelar_contrato', 'Congelar Contrato'),
        ('adjudicar', 'Adjudicado'),
        ('adendum', 'Realizar Adendum'),
        ('cerrado', 'Cerrado'),
        ('desistir', 'Desistir'),
    ], string='Estado', default='borrador', track_visibility='onchange')

    debe=fields.Float('Débito')
    haber=fields.Float('Crédito')
    saldo=fields.Float('Saldo')
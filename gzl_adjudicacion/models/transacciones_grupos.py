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
        ('ACTIVADO', 'ACTIVADO'),
        ('NO ACTIVADO', 'NO ACTIVADO'),
        ('ADJUDICADO', 'ADJUDICADO'),
        ('FINALIZADO', 'FINALIZADO'),
    ], string='Estado', default='pendiente', track_visibility='onchange')

    debe=fields.Float('Débito')
    haber=fields.Float('Crédito')
    saldo=fields.Float('Saldo',compute="calculo_saldo",store=True)

    @api.depends('debe','haber')
    def calculo_saldo(self):
        for l in self:
            l.saldo=l.haber - l.debe

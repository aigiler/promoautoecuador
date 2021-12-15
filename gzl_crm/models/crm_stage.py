# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

AVAILABLE_PRIORITIES = [
    ('0', 'Low'),
    ('1', 'Medium'),
    ('2', 'High'),
    ('3', 'Very High'),
]


class Stage(models.Model):
    """ Model for case stages. This models the main stages of a document
        management flow. Main CRM objects (leads, opportunities, project
        issues, ...) will now use only stages, instead of state and stages.
        Stages are for example used to display the kanban view of records.
    """
    _inherit = "crm.stage"



    char = fields.Char( string='Correos' )

    modificacion_solo_equipo = fields.Boolean( string='Solo puede Editar el equipo asignado' )

    colocar_venta_como_ganada = fields.Boolean( string='En este estado se puede colocar la venta como ganada' )

    restringir_movimiento = fields.Boolean( string='Restringir movimiento de Estado de Oportunidad' )

    stage_anterior_id = fields.Many2one('crm.stage', string='Estado Anterior' )
    stage_siguiente_id = fields.Many2one('crm.stage', string='Estado Siguiente' )


    solicitar_adjunto_documento = fields.Boolean( string='Solicitar Adjunto de Documentos' )

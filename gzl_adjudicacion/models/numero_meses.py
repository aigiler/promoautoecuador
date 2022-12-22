# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError




class NumeroMeses(models.Model):
    _name = 'numero.meses'
    _description = 'Número de meses'
    _rec_name="numero"

    numero = fields.Integer( string="Número")
    porcentaje=fields.Float(string="Porcentaje")
    cuota_adjudicacion=fields.Char(string="Número de Cuota a Adjudicar")
    active = fields.Boolean(string="Activo",default=True)

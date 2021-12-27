# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
import datetime
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta, date
from dateutil.parser import parse


class ItemsPatrimonio(models.Model):
    _name = 'items.patrimonio.adjudicado'
    _description = 'Items Patrimonio'
    
    currency_id = fields.Many2one('res.currency', readonly=True, default=lambda self: self.env.company.currency_id)

    montoAhorroInversiones = fields.Monetary(
        string='Ahorro o Inversiones', digits=(6, 2))
    casaValor = fields.Monetary(string='Casa Valor', digits=(6, 2))
    terrenoValor = fields.Monetary(string='Terreno Valor', digits=(6, 2))
    montoMueblesEnseres = fields.Monetary(
        string='Muebles y Enseres', digits=(6, 2))
    vehiculoValor = fields.Monetary(string='Vehiculo Valor',  digits=(6, 2))
    inventarios = fields.Monetary(string='Inventarios', digits=(6, 2))
    totalActivosAdj = fields.Monetary(
        compute='calcular_total_activos', string='TOTAL ACTIVOS', digits=(6, 2))

    @api.depends('montoAhorroInversiones', 'casaValor', 'terrenoValor', 'montoMueblesEnseres', 'vehiculoValor', 'inventarios')
    def calcular_total_activos(self):
        totalActivos = 0
        for rec in self:
            totalActivos = rec.montoAhorroInversiones + rec.casaValor + rec.terrenoValor + \
                rec.vehiculoValor + rec.montoMueblesEnseres + rec.inventarios
            rec.totalActivosAdj = totalActivos

# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError

import numpy_financial as npf


class WizardAdelantarCuotas(models.Model):
    _name = 'wizard.cesion.derecho'
    
    _rec_name = 'name'

    contrato_id = fields.Many2one('contrato')
    name=fields.Char("Name")
    monto_a_ceder = fields.Float( string='Monto a Ceder',store=True)
    contrato_a_ceder= fields.Many2one('contrato',string="Contrato a Ceder")
    carta_adjunto = fields.Binary('Carta de Cesión', attachment=True)
    partner_id=fields.Many2one("res.partner", "Cliente a Ceder")
    pago_id=fields.Many2one("account.payment", "Pago Generado")
    ejecutado=fields.Boolean(default=False)

    # def ejecutar_cesion(self):
    #     for l in self:
    #         if l.contrato_id:
    #             if l.partner_id:
    #                 l.name="Cesion al contrato "+str(l.contrato_id.secuencia)
    #                 l.contrato_id.nota=" "+str(self.contrato_id.cliente.name)+' Cede el contrato a la persona: '+str(self.partner_id.name)
    #                 l.contrato_id.cliente=self.partner_id.id
    #                 l.contrato_id.cesion_id=self.id
    #                 l.ejecutado=True

    def ejecutar_cesion(self):
        for l in self:
            if l.pago_id and l.carta_adjunto:
                l.contrato_id.copy()
                #detalle_estado_cuenta_pendiente=self.tabla_amortizacion.filtered(lambda l:  l.fecha>=obj_fecha_congelamiento.fecha  and l.fecha<fecha_reactivacion)
            
            
            #nuevo_detalle_estado_cuenta_pendiente=[]
            #for detalle in detalle_estado_cuenta_pendiente:
            #    obj_detalle=detalle.copy(
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
                id_contrato=l.contrato_a_ceder.copy()
                l.contrato_id=id_contrato.id
                detalle_estado_cuenta_uno=self.contrato_a_ceder.tabla_amortizacion.filtered(lambda l:  l.numero_cuota == 1)
                nuevo_detalle_estado_cuenta_uno=[]
                for detalle in detalle_estado_cuenta_uno:
                    detalle_id=l.detalle.copy()
                    nuevo_detalle_estado_cuenta_pendiente.append(detalle_id.id)
                    cuota_actual=self.env['contrato.estado.cuenta'].browse(detalle_id.id)
                    cuota_actual.contrato_id=id_contrato.id
                i=2
                detalle_estado_cuenta_pendiente=self.contrato_a_ceder.tabla_amortizacion.filtered(lambda l:  l.numero_cuota >= 2 and l.estado_pago=='pendiente')
                for detalle in detalle_estado_cuenta_pendiente:
                    detalle_id=l.detalle.copy()
                    nuevo_detalle_estado_cuenta_pendiente.append(detalle_id.id)
                    cuota_actual=self.env['contrato.estado.cuenta'].browse(detalle_id.id)
                    cuota_actual.contrato_id=id_contrato.id
                    cuota_actual.numero_cuota=i
                    i+=1
                detalle_estado_cuenta_pendienta=self.contrato_a_ceder.tabla_amortizacion.filtered(lambda l: l.estado_pago=='pagado')
                for detalle in detalle_estado_cuenta_pendienta:
                    detalle_id=l.detalle.copy()
                    nuevo_detalle_estado_cuenta_pendiente.append(detalle_id.id)
                    cuota_actual=self.env['contrato.estado.cuenta'].browse(detalle_id.id)
                    cuota_actual.contrato_id=id_contrato.id
                    cuota_actual.numero_cuota=i
                    cuota_actual.estado_pago="varias"
                    i+=1
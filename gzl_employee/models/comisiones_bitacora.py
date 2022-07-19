# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import *
import calendar

class ComisionesBitacora(models.Model):
    _name = 'comision.bitacora'

    user_id = fields.Many2one('res.users',string="Usuario")
    supervisor_id = fields.Many2one('res.users',string="Supervisor")
    lead_id = fields.Many2one('crm.lead',string="Oportunidad")
    valor_inscripcion = fields.Float('Valor de inscripción')

    bono = fields.Float('Bono')
    porcentaje_comision = fields.Float('porcentaje comision')
    comision = fields.Float('Comisión')
    cargo = fields.Many2one('hr.job',string="Cargo")
    empleado_id = fields.Many2one('hr.employee',string="Empleado")


    active = fields.Boolean('Bono',default=True)



class FactoresEvaluar(models.Model):
    _name = 'factores.evaluar'

    name=fields.Text(string="Factor a Evaluar")
    considerado_evaluar=fields.Boolean(string="Considerar", default=False)

class FactoresEvaluados(models.Model):
    _name = 'factores.evaluados'

    name=fields.Many2one("factores.evaluar", string="Factor a Evaluar")
    descripcion=fields.Text(related="name.name", string="Factor a Evaluar")
    valor=fields.Selection( [('Excelente', 'Excelente'), ('Bueno', 'Bueno'), ('Malo', 'Malo')],string="Calificación")

    evaluacion_id=fields.Many2one("hr.appraisal", string="Factor a Evaluar")

class hrAppraisal(models.Model):
    _inherit = 'hr.appraisal'

    factores_ids=fields.One2many("factores.evaluados", "evaluacion_id",string="Factores de Evaluación")

    @api.depends("employee_id")
    @api.onchange("employee_id")
    def obtener_factores(self):
        for l in self:
            if not l.factores_ids:
                factores_ids=self.env['factores.evaluar'].search([('considerado_evaluar','=',True)])
                lista_ids=[]
                for x in factores_ids:
                    registro=self.env['factores.evaluados'].create({'name':x.id})
                    lista_ids.append(int(registro))
                self.update({'factores_ids':[(6,0,lista_ids)]})
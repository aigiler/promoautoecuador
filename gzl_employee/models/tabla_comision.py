# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import *
import calendar

class Comision(models.Model):
    _name = 'comision'

    cargo_id = fields.Many2one('hr.job',string="Cargo")
    valor_max = fields.Float('Máximo')
    valor_min = fields.Float('Mìnimo')

    comision = fields.Float('Comisión')
    bono = fields.Float('Bono')
    logica = fields.Selection(selection=[
        ('asesor', 'Borrador'),
        ('supervisor', 'Activo'),
        ('jefe', 'Inactivo'),
        ('gerente', 'Congelar Contrato'),

    ], string='Logica', default='asesor', track_visibility='onchange')

    active = fields.Boolean('Bono',default=True)


    def job_para_crear_comisiones_por_contrato(self, ):

        hoy=date.today()
        comisiones=self.env['comision'].search([('active','=',True)])

        cargos_comisiones=list(set(self.env['comision'].search([('active','=',True)]).mapped('cargo_id').ids))

 
        fecha_actual="%s-%s-01" % (hoy.year, hoy.month)
        fecha_fin="%s-%s-%s" %(hoy.year, hoy.month,(calendar.monthrange(hoy.year, hoy.month)[1]))




        for cargo in cargos_comisiones:
            empleados=self.env['hr.employee'].search([('job_id','=',cargo)])
            tipo_comision=self.env['comision'].search([('cargo_id','=',cargo)],limit=1)
            listaComision=[]

            if len(tipo_comision)>0:
                if tipo_comision.logica=='asesor':
                    for empleado in empleados:
                        monto_comision=0
                        leads = self.env['crm.lead'].search([('user_id','=',empleados.user_id.id),('active','=',True),('fecha_ganada','>=',fecha_actual),('fecha_ganada','<=',fecha_fin)])
                        monto_ganado= sum(leads.mapped("planned_revenue"))
                        comision_tabla=self.env['comision'].search([('cargo_id','=',cargo),('valor_min','<=',monto_ganado),('valor_max','>=',monto_ganado)],limit=1)
                        if comision_tabla>0:
                            monto_comision=comision_tabla.comision*monto_ganado + comision_tabla.bono

                        listaComision.append({'empleado_id':empleado.id,'comision':monto_comision})


                if tipo_comision.logica=='supervisor':

                    for empleado in empleados:
                        monto_comision=0
                        leads = self.env['crm.lead'].search([('supervisor','=',empleados.user_id.id),('active','=',True),('fecha_ganada','>=',fecha_actual),('fecha_ganada','<=',fecha_fin)])
                        monto_ganado= sum(leads.mapped("planned_revenue"))
                        comision_tabla=self.env['comision'].search([('cargo_id','=',cargo),('valor_min','<=',monto_ganado),('valor_max','>=',monto_ganado)],limit=1)
                        if comision_tabla>0:
                            monto_comision=comision_tabla.comision*monto_ganado + comision_tabla.bono

                        listaComision.append({'empleado_id':empleado.id,'comision':monto_comision})

                if tipo_comision.logica=='jefe' or tipo_comision.logica=='gerente':

                    for empleado in empleados:
                        monto_comision=0
                        leads = self.env['crm.lead'].search([('fecha_ganada','>=',fecha_actual),('fecha_ganada','<=',fecha_fin)])
                        monto_ganado= sum(leads.mapped("planned_revenue"))
                        comision_tabla=self.env['comision'].search([('cargo_id','=',cargo),('valor_min','<=',monto_ganado),('valor_max','>=',monto_ganado)],limit=1)
                        if comision_tabla>0:
                            monto_comision=comision_tabla.comision*monto_ganado + comision_tabla.bono

                        listaComision.append({'empleado_id':empleado.id,'comision':monto_comision})


        comision=self.env['hr.payslip.input.type'].search([('code','=','COMI')])

        for empleado in listaComision:
            dct={
            'date':  hoy  ,
            'input_type_id': comision   ,
            'employee_id':empleado['empleado_id']  ,
            'amount':empleado['comision']   ,

            }
            comision=self.env['hr.input'].create(dct)






# -*- coding:utf-8 -*-

from odoo import api, models, fields,_
from datetime import date, timedelta
import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning, ValidationError

class entryworkwizard(models.TransientModel):
    _name = 'wizard.entry'
    _description = 'Entradas de Trabajo'


    #name = fields.Many2one('hr.employee',string='Empleado', domain=compute_employee, required=True)
    date_start = fields.Date('Fecha Inicio', required=True)
    date_end = fields.Date('Fecha Corte', required=True, default = date.today())
    
    def generar_work_entry(self):
        
        date_start = fields.Datetime.to_datetime(self.date_start)
        date_stop = datetime.datetime.combine(fields.Datetime.to_datetime(self.date_end), datetime.datetime.max.time())

        
        obj_entrywork=self.env['hr.work.entry'].search([('date_start','>=',self.date_start),('date_stop','<=',self.date_end)])
        if len(obj_entrywork)>0:
            obj_entrywork.unlink()
        obj_contract=self.env['hr.contract'].search([])
        lista=[]
        for contrato in obj_contract:
            valor=contrato._get_work_entries_values(date_start,date_stop)
            self.env['hr.work.entry'].create(valor)
        

    def generar_alimentacion(self):
        
        date_start = fields.Datetime.to_datetime(self.date_start)
        date_stop = datetime.datetime.combine(fields.Datetime.to_datetime(self.date_end), datetime.datetime.max.time())

        
        obj_entrywork=self.env['hr.work.entry'].search([('date_start','>=',self.date_start),('date_stop','<=',self.date_end)])
        if len(obj_entrywork)>0:
            obj_entrywork.unlink()
        obj_contract=self.env['hr.contract'].search([])
        lista=[]
        for contrato in obj_contract:




            valor=contrato._get_work_entries_values(date_start,date_stop)
            self.env['hr.work.entry'].create(valor)


            comision=self.env['hr.payslip.input.type'].search([('code','=','DALI')])
            for linea in valor:
                dct={
                'date':  linea['date_start']  ,
                'input_type_id': comision.id   ,
                'employee_id':contrato.employee_id.id  ,
                'amount':2  ,

                }

                input_anteriores=self.env['hr.input'].search([('employee_id','=',contrato.employee_id.id),('date','=',linea['date_start'].date())])
                if len(input_anteriores)==0:
                    comision_input=self.env['hr.input'].create(dct)
                else:
                    pass
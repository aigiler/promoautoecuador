# -*- coding: utf-8 -*-
{
    'name': 'gzl_employee',
    'version': '1.0',
    'description': 'Modificaciones en Empleados',
    'depends': ['hr','hr_payroll'],
    'data': [
            'security/ir.model.access.csv',

            'data/data_groups.xml',
            'data/data_age.xml',

            'views/hr_employee_view.xml',
            'views/hr_payslip_view.xml',
            'views/ir_attachment_view.xml',
            'views/res_bank_view.xml',
            
            'wizard/report_thirteenth_salary_view.xml',
            'wizard/report_fourteenth_salary_view.xml',
            'wizard/report_payment_file_view.xml',
            'wizard/calculo_comision_view.xml',
            'wizard/report_vacations_view.xml'
    ],
    'qweb': [],
    'demo': [],
    'installable': True,
    'auto_install': True,
}

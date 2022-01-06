# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Reportes',
    'version': '1.0',
    'category': 'Reportes',
    'summary': 'Reportes Adjudicaciones',
    'description': """
===========================================================================
 """,
    'website': 'https://odoo.com/',
    'depends': [
                'gzl_account','bi_account_cheque',
                ],
    'update_xml': [],
    'data': [

            'views/menu_view.xml',

			'views/fields_view.xml',
        
            'security/ir.model.access.csv',

            'wizard/gzl_reporte_anticipo_view.xml',
            'report/reporte_anticipo_template.xml',
            'report/reporte_anticipo.xml',
            'wizard/report_entregable_hito.xml',

            
             ],
    'installable': True,
    'auto_install': False,
    
    
}


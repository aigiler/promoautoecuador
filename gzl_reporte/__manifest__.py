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
            'data/data_grupo.xml',
            
            'security/ir.model.access.csv',

            'views/menu_view.xml',
			'views/fields_view.xml',
            'wizard/carta_finalizacion_wizard.xml',
            'wizard/congelamiento_wizard.xml',
            'wizard/contrato_adendum_wizard.xml',
            'wizard/hoja_ruta_wizard.xml',
            'wizard/politicas_credito_wizard.xml',
            'wizard/reporte_grupos.xml',
            'wizard/reporte_adjudicados.xml',
            'wizard/reporte_estado_de_cuenta_wizard.xml',
            'wizard/reporte_trazabilidad_pagos.xml',
            'wizard/politicas_credito_wizard.xml',



            ],
    'installable': True,
    'auto_install': False,


}


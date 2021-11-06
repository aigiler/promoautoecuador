# -*- coding: utf-8 -*-
{
    'name': 'gzl_fact_electronica',
    'version': '1.0',
    'category': 'Facturación Electrónica',
    'description': 'Facturación Electrónica',
    'depends': ['l10n_ec_tree','product','mail'],
    'data': [
        #'data/secuencias.xml',
        'data/data_ats.xml',
        'data/data_producto.xml',
        'data/data_payment_method.xml',
        'data/ats.country.csv',
        'data/account.tax.group.csv',
        'data/inventario_servicios_data_factura.xml',
        'data/inventario_servicios_data_guia_remision.xml',
        'data/inventario_servicios_data_nota_credito.xml',
        'data/inventario_servicios_data_nota_debito.xml',
        'data/inventario_servicios_data_retencion.xml',
        'data/ir_cron_data.xml',
        'data/ir_config_parameter_data.xml',
        'data/data_email.xml',
        
        'security/ir.model.access.csv',

        'views/ats_view.xml',
        'views/account_move_view.xml',
        'views/establecimiento_view.xml',
        'views/res_company_view.xml',
        'views/res_partner_view.xml',
        'views/account_journal_view.xml',
        'views/account_retention_view.xml',
        'views/account_move_nd_view.xml',
        'views/account_guia_remision_view.xml',
        'views/account_move_reversal.xml',
        'views/inventario_servicios_view.xml',
        'views/bitacora_consumo_servicios_view.xml',
        'views/l10n_latam_identification_type_view.xml',

        'wizard/wizard_ats_view.xml',
        'wizard/wizard_import_documents_view.xml',
        'wizard/layout_documents.xml',
        'wizard/report_retention.xml',
        'wizard/agregar_retencion.xml',


        
    ],
    'qweb': [],
    'demo': [],
    'installable': True,
    'auto_install': True,
}

{
    "name" : "gzl_adjudicacion",
    "version" : "0.1",
    'depends' :['base','mail','portal','base_setup'],
    "author" : "Yadira Quimis Gizlo",
    "description" : """
    product
                    """,
    "website" : "http://www.gizlocorp.com",
    "category" : "Generic Modules",
   
    "data" : [   
                    'data/data_grupo_adjudicacion.xml',
                    'data/data_tipo_contrato.xml',
                    'data/data_secuencia.xml',
                    'data/data_calificacion_cliente_parametros.xml',
                    'data/data_configuracion_adicional.xml',




                    'security/ir.model.access.csv',

                    'views/menu_view.xml',
                    'views/adjudicado_view.xml',
                    'views/tipo_contrato_view.xml',
                    'views/concesionario_view.xml',
                    'views/grupo_adjudicado_view.xml',
                    'views/entrega_vehiculo_view.xml',
                    'views/asamblea_view.xml',
                    'views/contrato_view.xml',
                    'views/res_config_settings_views.xml',
                    'views/configuracion_adicional.xml',
                    ],
    
    'installable': True,
    'auto_install': False,
}




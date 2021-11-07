{
    "name" : "gzl_adjudicacion",
    "version" : "0.1",
    'depends' :['base'
                ],
    "author" : "Yadira Quimis Gizlo",
    "description" : """
    product
                    """,
    "website" : "http://www.gizlocorp.com",
    "category" : "Generic Modules",
   
    "data" : [   
                   'data/data_grupo_adjudicacion.xml',

                      
                    'security/ir.model.access.csv',


                   'data/data_tipo_contrato.xml',
                   'views/menu_view.xml',
                   'views/adjudicado_view.xml',
                   'views/tipo_contrato_view.xml',
                   'views/concesionario_view.xml',
                   'views/grupo_adjudicado_view.xml',
                   
                    ],
    
    'installable': True,
    'auto_install': False,
}




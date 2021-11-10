{
    "name" : "gzl_crm",
    "version" : "0.1",
    'depends' :['crm','sale',
                ],
    "author" : "Yadira Quimis Gizlo",
    "description" : """
    Heredado de CRM
                    """,
    "website" : "http://www.gizlocorp.com",
    "category" : "Generic Modules",
   
    "data" : [   
                "security/ir.model.access.csv",

                "views/crm_lead_view.xml",  
                   
                    ],
    
    'installable': True,
    'auto_install': False,
}




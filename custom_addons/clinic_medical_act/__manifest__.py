# -*- coding: utf-8 -*-
{
    'name': 'Clinic Medical Acts',
    'version': '1.0.0',
    'category': 'Healthcare',
    'summary': 'Gestion des actes médicaux pour clinique',
    'description': """
        Module de gestion des actes médicaux
        =====================================
        ...
    """,
    'author': 'Clinic Management Team',
    'website': 'https://www.clinique.dz',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'product',
        'clinic_patient',
        'point_of_sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/medical_act_categories.xml',
        'views/product_template_views.xml',
        'views/clinic_medical_act_line_views.xml',
        # 'views/clinic_medical_act_reports.xml',  # Désactivé temporairement pour debug
        'views/clinic_doctor_views.xml',
        'views/res_partner_views.xml',
        'views/clinic_medical_act_menus.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

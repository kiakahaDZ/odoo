# -*- coding: utf-8 -*-
{
    'name': 'Clinic Dashboard',
    'version': '1.0.0',
    'category': 'Healthcare/Reporting',
    'summary': 'Tableau de bord de gestion',
    'description': """
        Dashboard Clinique
        ===================
        Fournit une vue d'ensemble de l'activité.
    """,
    'author': 'Clinic Management Team',
    'license': 'LGPL-3',  # Ajout de la licence
    'depends': [
        'base',
        'clinic_patient',
        'clinic_medical_act',
        'clinic_reception',
        'clinic_validation',
        'clinic_reports',
    ],
    'data': [
        'views/dashboard_action.xml',
    ],
    'installable': True,
    'auto_install': False,
}

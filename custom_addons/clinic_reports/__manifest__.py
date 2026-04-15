# -*- coding: utf-8 -*-
{
    'name': 'Clinic Reports',
    'version': '1.0.0',
    'category': 'Healthcare/Reporting',
    'summary': 'Rapports et Statistiques Clinique',
    'description': """
        Module de Rapports
        ===================
        
        Fournit des rapports statistiques sur:
        * Revenus par médecin (calcul des parts)
        * Actes par type et service
        * Fréquentation patient
        * Rapports financiers journaliers
    """,
    'author': 'Clinic Management Team',
    'license': 'LGPL-3',  # Ajout de la licence
    'depends': [
        'clinic_medical_act',
        'clinic_pos',
        'clinic_reception',
        'clinic_validation',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/clinic_reports_menus.xml',
    ],
    'installable': True,
    'auto_install': False,
}

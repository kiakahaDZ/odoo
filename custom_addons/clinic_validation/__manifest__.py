# -*- coding: utf-8 -*-
{
    'name': 'Clinic Validation',
    'version': '1.0.0',
    'category': 'Healthcare',
    'summary': 'Validation des actes médicaux (Labo & Imagerie)',
    'description': """
        Module de Validation des Actes
        ===============================
        
        Fonctionnalités principales:
        * Liste des actes payés en attente de réalisation
        * Validation par service (Laboratoire, Imagerie)
        * Historique des validations
        * Interface dédiée pour techniciens
        
        Statuts gérés:
        - Payé → En cours → Réalisé
        
        Services supportés:
        - Laboratoire (analyses)
        - Imagerie médicale (radio, écho, scanner, IRM)
    """,
    'author': 'Clinic Management Team',
    'website': 'https://www.clinique.dz',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'clinic_patient',
        'clinic_medical_act',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/clinic_validation_views.xml',
        'views/clinic_validation_menus.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

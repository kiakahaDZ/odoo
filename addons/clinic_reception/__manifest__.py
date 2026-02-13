# -*- coding: utf-8 -*-
{
    'name': 'Clinic Reception',
    'version': '1.0.0',
    'category': 'Healthcare',
    'summary': 'Module de réception pour clinique',
    'description': """
        Module de Réception Clinique
        =============================
        
        Fonctionnalités principales:
        * Enregistrement rapide des patients
        * Sélection des actes médicaux demandés
        * Génération de tickets pour la caisse
        * Suivi du statut des patients
        * Interface optimisée pour la réception
        
        Statuts gérés:
        - En attente
        - Payé
        - En cours
        - Validé
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
        'data/reception_sequence.xml',
        'views/clinic_reception_views.xml',
        'views/clinic_reception_line_views.xml',
        # 'views/clinic_reception_reports.xml',  # Désactivé temporairement pour debug
        'views/clinic_reception_menus.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

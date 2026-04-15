# -*- coding: utf-8 -*-
{
    'name': 'Clinic POS (Caisse Médicale)',
    'version': '1.0.0',
    'category': 'Healthcare/Point of Sale',
    'summary': 'Caisse médicale adaptée pour clinique',
    'description': """
        Caisse Médicale (POS Adapté)
        =============================
        
        Fonctionnalités principales:
        * Adaptation du module POS pour usage médical
        * Obligation de sélectionner un patient
        * Limitation aux actes médicaux uniquement
        * Association des paiements aux dossiers patients
        * Génération de reçus/factures médicaux
        * Modes de paiement: Espèces, Carte bancaire
        
        Ce module étend le Point of Sale standard d'Odoo
        pour l'adapter aux besoins d'une caisse médicale.
    """,
    'author': 'Clinic Management Team',
    'website': 'https://www.clinique.dz',
    'license': 'LGPL-3',
    'depends': [
        'point_of_sale',
        'clinic_patient',
        'clinic_medical_act',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_config_views.xml',
        'views/pos_order_views.xml',
        # 'views/pos_order_reports.xml',  # Désactivé temporairement pour debug
        'views/clinic_pos_menus.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

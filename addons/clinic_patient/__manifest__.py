# -*- coding: utf-8 -*-
{
    'name': 'Clinic Patient Management',
    'version': '1.0.0',
    'category': 'Healthcare',
    'summary': 'Gestion des patients pour clinique médicale',
    'description': """
        Module de gestion des patients pour clinique
        =============================================
        
        بسم الله الرحمن الرحيم
        
        Fonctionnalités principales:
        * Enregistrement et gestion des patients
        * Numéro de dossier patient unique
        * Historique des actes médicaux
        * Recherche rapide et avancée
        * Fiche patient complète
        * Interface moderne avec mascotte Fennec (renard algérien)
        
        Développé pour le système de gestion de clinique en Algérie
        مع تحيات فريق التطوير الجزائري
    """,
    'author': 'Clinic Management Team - الجزائر',
    'website': 'https://www.clinique.dz',
    'license': 'LGPL-3',
    
    # Images
    'images': [
        'static/description/icon.png',
        'static/description/banner.png',
    ],
    
    # Icons
    'icon': '/clinic_patient/static/description/icon.png',
    
    # Assets
    'assets': {},
    
    'depends': [
        'base',
        'contacts',
        'mail',
        'product',
        'account',
        'stock',
    ],
    
    'data': [
        'security/clinic_patient_security.xml',
        'security/ir.model.access.csv',
        'data/patient_sequence.xml',
        'views/clinic_patient_views.xml',
        'views/clinic_visit_views.xml',
        'wizard/clinic_payment_wizard_views.xml',
        'views/clinic_act_line_form.xml',
        'views/clinic_act_views.xml',
        'views/clinic_patient_menus.xml',
        'data/clinic_user_setup.xml',
        'data/consultation_products.xml',
        'data/demo_data.xml',
    ],
    
    'banner': 'static/description/banner.png',
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'support': 'support@clinique.dz',
    'live_test_url': 'https://demo.clinique.dz',
    'price': 0.00,
    'currency': 'DZD',
}
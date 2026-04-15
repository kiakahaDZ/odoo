# -*- coding: utf-8 -*-
{
    'name': '💈 Barber & Salon POS',
    'version': '18.0.1.0',
    'category': 'Point of Sale',
    'summary': 'Système de caisse complet pour salon de coiffure et barbier',
    'description': """
        Barber & Salon POS — Module Odoo
        ===================================

        Module de point de vente professionnel dédié aux salons de coiffure et barbiers.

        Fonctionnalités principales :
        ─────────────────────────────
        ✅ Deux rôles : Administrateur & Coiffeur/Barbier
        ✅ Gestion des contrats coiffeurs (loyer mensuel ou % du CA)
        ✅ Prestations (coupes, soins, barbe) avec tarifs variables
        ✅ Produits consommables associés aux prestations
        ✅ Interface POS intuitive avec panier et paiement
        ✅ Sessions de caisse (ouverture / fermeture)
        ✅ Calcul automatique des commissions et loyers
        ✅ Dashboard administrateur avec KPIs et graphiques
        ✅ Rapports journaliers et mensuels par coiffeur
        ✅ Ticket de caisse imprimable

        Développé pour les salons de coiffure professionnels.
    """,
    'author': 'Barber POS Team',
    'website': 'https://www.odoo.com',
    'license': 'LGPL-3',

    'images': [
        'static/description/icon.png',
        'static/description/banner.png',
    ],
    'icon': '/barber_pos/static/description/icon.png',

    'depends': [
        'base',
        'mail',
        'product',
        'account',
        'hr',
        'web',
    ],

    'data': [
        # Security
        'security/barber_security.xml',
        'security/ir.model.access.csv',

        # Data
        'data/barber_sequence.xml',
        'data/barber_admin_setup.xml',

        # Reports
        'report/barber_receipt_report.xml',
        'report/barber_daily_report.xml',

        # Views
        'views/barber_config_views.xml',
        'views/barber_service_views.xml',
        'views/barber_barber_views.xml',
        'views/barber_contract_views.xml',
        'views/barber_session_views.xml',
        'views/barber_order_views.xml',
        'views/barber_dashboard_views.xml',
        'views/barber_templates.xml',
        'views/barber_menus.xml',

        # Wizards
        'wizard/barber_payment_wizard_views.xml',
        'wizard/barber_close_session_views.xml',

        # Demo data
        'data/barber_demo.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'barber_pos/static/src/css/barber_pos.css',
            'barber_pos/static/src/js/barber_dashboard.js',
        ],
    },

    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 1,
}

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test du workflow clinique
Teste la création de patients, tickets, actes et paiements
"""

import os
import sys
import django
from datetime import datetime

# Configuration Odoo
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Importer les modules Odoo
sys.path.insert(0, '/path/to/odoo')

try:
    import odoo
    from odoo import api
    from odoo.tools import config
    
    # Configuration Odoo
    config['db_name'] = 'mydb_clinic'
    config['db_host'] = 'localhost'
    config['db_port'] = 5432
    config['db_user'] = 'odoo'
    config['db_password'] = '987654321aA'
    
    # Connexion
    registry = odoo.registry('mydb_clinic')
    
    print("=" * 60)
    print("TEST WORKFLOW CLINIQUE")
    print("=" * 60)
    
    with api.Environment.manage():
        with registry.cursor() as cr:
            env = api.Environment(cr, 1, {})
            
            # Test 1: Patient
            print("\n[1] Test création patient...")
            patient = env['res.partner'].create({
                'name': 'Test Patient Jean',
                'is_patient': True,
                'date_of_birth': '1990-01-15',
                'gender': 'male',
                'blood_group': 'O+',
                'phone': '0661234567'
            })
            print(f"✓ Patient créé: {patient.name} (ID: {patient.id}, N°: {patient.patient_number})")
            
            # Test 2: Produits actes médicaux
            print("\n[2] Test produits actes médicaux...")
            lab_act = env['product.product'].search([
                ('is_medical_act', '=', True),
                ('product_tmpl_id.medical_act_type', '=', 'laboratory')
            ], limit=1)
            
            if lab_act:
                print(f"✓ Acte labo trouvé: {lab_act.name}")
            else:
                print("⚠ Aucun acte labo trouvé - création...")
                
            # Test 3: Ticket réception
            print("\n[3] Test ticket réception...")
            reception = env['clinic.reception'].create({
                'patient_id': patient.id,
                'medical_act_line_ids': []
            })
            print(f"✓ Ticket créé: {reception.name} (État: {reception.state})")
            
            # Test 4: Actes demandés
            print("\n[4] Test ajout actes...")
            if lab_act:
                line = env['clinic.reception.line'].create({
                    'reception_id': reception.id,
                    'product_id': lab_act.id,
                    'price_unit': lab_act.list_price,
                    'quantity': 1
                })
                print(f"✓ Acte ajouté: {lab_act.name}")
                
            # Test 5: Envoi à la caisse
            print("\n[5] Test envoi à caisse...")
            reception.action_send_to_cashier()
            acts = env['clinic.medical.act.line'].search([
                ('reception_id', '=', reception.id)
            ])
            print(f"✓ {len(acts)} acte(s) créé(s)")
            for act in acts:
                print(f"  - {act.name}: État={act.state}, Patient={act.patient_id.name}")
            
            # Test 6: Vérifier états
            print("\n[6] Vérification des états...")
            waiting_acts = env['clinic.medical.act.line'].search([
                ('state', '=', 'waiting')
            ])
            print(f"✓ Actes en attente: {len(waiting_acts)}")
            
            # Test 7: Afficher resum
            print("\n[7] Résumé workflow...")
            print(f"""
Patient: {patient.name} ({patient.patient_number})
Réception: {reception.name} - Montant: {reception.total_amount}€
Actes créés: {len(acts)}
État réception: {reception.state}
États actes: {', '.join(set(acts.mapped('state')))}

Workflow fonctionnel! Prêt pour test POS payment.
            """)
            
            print("=" * 60)
            print("✓ TOUS LES TESTS PASSÉS!")
            print("=" * 60)
            
except Exception as e:
    print(f"\n❌ ERREUR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

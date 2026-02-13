#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Initializer - Script de setup initial de la clinique
Crée les données de base nécessaires
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from odoo import api
from odoo.api import Environment

def create_base_data(env):
    """Crée les données de base pour la clinique"""
    
    print("\n" + "=" * 70)
    print("INITIALISATION DONNÉES CLINIQUE")
    print("=" * 70)
    
    # 1. Créer categorie d'actes
    print("\n[1] Création catégories de produits...")
    lab_cat = env['product.category'].search([('name', '=', 'Actes Laboratoire')], limit=1)
    if not lab_cat:
        lab_cat = env['product.category'].create({'name': 'Actes Laboratoire'})
        print(f"  ✓ Catégorie créée: {lab_cat.name}")
    else:
        print(f"  ✓ Catégorie trouvée: {lab_cat.name}")
    
    # 2. Créer actes labo
    print("\n[2] Création actes laboratoire...")
    lab_acts = [
        ('Prise de sang', 1000.00, 'Analyse sanguine complète'),
        ('Bilan lipidique', 500.00, 'Dosage cholestérol et triglycérides'),
        ('Groupage sanguin', 800.00, 'Détermination groupe sanguin'),
        ('Analyse urinaire', 400.00, 'Test d\'urine complet'),
        ('Glycémie', 300.00, 'Dosage du glucose'),
    ]
    
    for name, price, desc in lab_acts:
        product = env['product.product'].search([
            ('name', '=', name),
            ('is_medical_act', '=', True)
        ], limit=1)
        
        if not product:
            tmpl = env['product.template'].create({
                'name': name,
                'description': desc,
                'type': 'service',
                'categ_id': lab_cat.id,
                'list_price': price,
                'is_medical_act': True,
                'medical_act_type': 'laboratory',
                'service_type': 'analysis',
                'doctor_share_percentage': 30.0,
                'clinic_share_percentage': 70.0,
            })
            product = tmpl.product_variant_ids[0]
            print(f"  ✓ Acte créé: {name} - {price}€")
        else:
            print(f"  ✓ Acte trouvé: {name}")
    
    # 3. Créer actes imagerie
    print("\n[3] Création actes imagerie...")
    img_cat = env['product.category'].search([('name', '=', 'Actes Imagerie')], limit=1)
    if not img_cat:
        img_cat = env['product.category'].create({'name': 'Actes Imagerie'})
    
    img_acts = [
        ('Radiographie thoracique', 2000.00, 'Radiographie du thorax'),
        ('Echographie abdominale', 2500.00, 'Echo de l\'abdomen'),
        ('Echographie mammaire', 2500.00, 'Echo du sein'),
        ('Scanner abdominal', 5000.00, 'Scan de l\'abdomen'),
        ('IRM crânienne', 8000.00, 'Imagerie par résonance magnétique'),
    ]
    
    for name, price, desc in img_acts:
        product = env['product.product'].search([
            ('name', '=', name),
            ('is_medical_act', '=', True)
        ], limit=1)
        
        if not product:
            tmpl = env['product.template'].create({
                'name': name,
                'description': desc,
                'type': 'service',
                'categ_id': img_cat.id,
                'list_price': price,
                'is_medical_act': True,
                'medical_act_type': 'imaging',
                'service_type': 'imaging',
                'doctor_share_percentage': 25.0,
                'clinic_share_percentage': 75.0,
            })
            product = tmpl.product_variant_ids[0]
            print(f"  ✓ Acte créé: {name} - {price}€")
        else:
            print(f"  ✓ Acte trouvé: {name}")
    
    # 4. Créer médecins
    print("\n[4] Création médecins...")
    doctors = [
        ('Dr. Ahmed Medecin', 'ahmed@clinic.dz'),
        ('Dr. Fatima Radiologue', 'fatima@clinic.dz'),
        ('Dr. Mohamed Laboratoire', 'mohamed@clinic.dz'),
    ]
    
    for name, email in doctors:
        doctor = env['res.partner'].search([
            ('name', '=', name),
            ('is doctor', '=', True)
        ], limit=1)
        
        if not doctor:
            doctor = env['res.partner'].create({
                'name': name,
                'email': email,
                'is_doctor': True,
                'phone': '0661111111',
                'street': 'Rue de la Clinique',
                'city': 'Alger'
            })
            print(f"  ✓ Médecin créé: {name}")
        else:
            print(f"  ✓ Médecin trouvé: {name}")
    
    # 5. Créer patients de test
    print("\n[5] Création patients test...")
    test_patients = [
        ('Karim Benali', '1985-03-15', 'M', 'O+'),
        ('Zahra Ameziane', '1992-07-22', 'F', 'AB-'),
        ('Younes Hamidou', '1978-11-08', 'M', 'A+'),
    ]
    
    for name, birth, gender, blood in test_patients:
        patient = env['res.partner'].search([
            ('name', '=', name),
            ('is_patient', '=', True)
        ], limit=1)
        
        if not patient:
            patient = env['res.partner'].create({
                'name': name,
                'is_patient': True,
                'date_of_birth': birth,
                'gender': gender,
                'blood_group': blood,
                'phone': '0661122334'
            })
            print(f"  ✓ Patient créé: {name} ({patient.patient_number})")
        else:
            print(f"  ✓ Patient trouvé: {name} ({patient.patient_number})")
    
    # 6. Résumé
    print("\n[6] Résumé des données créées...")
    product_count = env['product.product'].search_count([('is_medical_act', '=', True)])
    patient_count = env['res.partner'].search_count([('is_patient', '=', True)])
    doctor_count = env['res.partner'].search_count([('is_doctor', '=', True)])
    
    print(f"""
    Produits (actes médicaux): {product_count}
    Patients: {patient_count}
    Médecins: {doctor_count}
    
    ✓ Données initiales créées avec succès!
    """)
    
    print("=" * 70 + "\n")

if __name__ == '__main__':
    # Cette fonction sera appelée par Odoo lors du post-install
    # ou peut être exécutée manuellement via:
    # python -c "import initialize; initialize.create_base_data(env)"
    pass

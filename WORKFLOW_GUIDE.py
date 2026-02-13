#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'initialisation des données de démonstration pour la clinique
"""

import os
import sys
import django

# Ajustez le chemin selon votre installation
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'odoo.settings')

def setup_demo_data():
    """Initialise les données de démonstration"""
    from odoo import api
    from odoo.cli import main as odoo_main
    
    print("\n" + "="*60)
    print("INITIALISATION DES DONNÉES DE DÉMONSTRATION - CLINIQUE")
    print("="*60 + "\n")
    
    print("""
FLUX DE TRAVAIL COMPLET:
========================

1. RÉSUMÉ DU WORKFLOW
   Patient → Réception → Actes Médicaux → POS (Caisse) → Validation (Labo/Imagerie)

2. ÉTAPES DÉTAILLÉES:

   ÉTAPE 1 - RÉCEPTIONNISTE REÇOIT LE PATIENT
   ├─ Aller à: Réception → Réception
   ├─ Créer un nouveau ticket:
   │  ├─ Patient: Sélectionner ou créer un patient
   │  ├─ Date: Automatique
   │  └─ État: Brouillon
   
   ÉTAPE 2 - AJOUTER LES ACTES MÉDICAUX DEMANDÉS
   ├─ Dans le ticket, ajouter les actes demandés:
   │  ├─ Acte Médical: Sélectionner un acte (ex: Analyse de sang)
   │  ├─ Quantité: 1
   │  └─ Prix: Automatique
   
   ÉTAPE 3 - ENVOYER À LA CAISSE
   ├─ Cliquer sur "Envoyer à la Caisse"
   ├─ Cela crée les actes médicaux (clinic.medical.act.line)
   ├─ État des actes: 'En Attente' (waiting)
   └─ État du ticket: 'En Attente Caisse' (waiting)
   
   ÉTAPE 4 - CAISSIER EFFECTUE LE PAIEMENT
   ├─ Aller à: POS → Caisse
   ├─ Créer une commande:
   │  ├─ Patient: Sélectionner le même patient
   │  ├─ Ajouter les produits médicaux
   │  └─ Payer la commande
   └─ Cela marque les actes comme payés (state='paid')
   
   ÉTAPE 5 - CONSULTER LES ACTES PAYÉS
   ├─ Les actes payés s'affichent maintenant:
   │  ├─ Si laboratoire: Réception → Validation → Laboratoire
   │  └─ Si imagerie: Réception → Validation → Imagerie
   └─ Labo peut valider les résultats
   
   ÉTAPE 6 - VALIDATION DES RÉSULTATS
   ├─ Aller à: Réception → Validation → Laboratoire ou Imagerie
   ├─ Sélectionner un acte en cours
   ├─ Ajouter les notes/résultats
   └─ Cliquer sur "Valider"

3. DONNÉES NÉCESSAIRES:
   
   Les données suivantes doivent être créées/vérifiées:
   
   a) Patients:
      - Évaluation professionnelle → Patients
      - Au moins 2-3 patients de test
   
   b) Produits Médicaux (Actes):
      - Ventes → Produits
      - Créer des produits avec:
        ├─ Nom: Analyse de sang, Radiographie, etc.
        ├─ Type d'acte: Laboratoire ou Imagerie
        ├─ Service: Sélectionner le service
        └─ Prix: Définir le prix
   
   c) Médecins (Optionnel):
      - Réception → Médecins
      - Associer à chaque acte
   
   d) POS Configuration:
      - Ventes → Configuration → Caisse
      - Créer une caisse pour:
        ├─ Cocher: "Est une caisse médicale"
        └─ Configurer les actes acceptés

4. NOTES IMPORTANTES:

   - Les actes créés dans la réception n'apparaissent au POS que si:
     a) Le patient est sélectionné dans la commande POS
     b) Les produits sont des actes médicaux (is_medical_act=True)
   
   - Les actes n'apparaissent dans Validation que si:
     a) Ils ont le type "laboratoire" ou "imagerie"
     b) Ils ont l'état "waiting", "paid" ou "in_progress"
   
   - Le workflow complet nécessite:
     a) Réception → crée clinic.reception.line
     b) Envoi à caisse → crée clinic.medical.act.line (state='waiting')
     c) Paiement POS → marque clinic.medical.act.line (state='paid')
     d) Validation → met clinic.medical.act.line (state='done')

5. DÉPANNAGE:

   Q: Les actes n'apparaissent pas dans Laboratoire/Imagerie?
   R: Vérifiez que:
      - Le type d'acte est bien "laboratoire" ou "imagerie"
      - L'acte a l'état "waiting", "paid" ou "in_progress"
      - Filtre appliqué: cocher les bons filtres
   
   Q: Les actes n'apparaissent pas au POS?
   R: Vérifiez que:
      - Le patient est sélectionné dans la commande POS
      - Le produit est un acte médical (is_medical_act=True)
      - La caisse POS est configurée comme "caisse médicale"
   
   Q: Le bouton "Voir Actes Créés" ne montre rien?
   R: C'est normal si aucun acte n'a été créé encore. 
      Allez à: Réception → Actes Médicaux pour voir tous les actes.

""")
    
    print("="*60)
    print("Pour commencer: Allez à Réception → Réception")
    print("="*60 + "\n")

if __name__ == '__main__':
    setup_demo_data()

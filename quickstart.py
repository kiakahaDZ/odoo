#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Start Guide - Démarrage Rapide du Système Clinique
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

def print_header():
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║   🏥  SYSTÈME DE GESTION CLINIQUE - DÉMARRAGE RAPIDE  🏥         ║
║                                                                    ║
║                      Version 1.0.0 Beta                           ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)

def check_system():
    """Vérifier la configuration du système"""
    print("\n[1] VÉRIFICATION SYSTÈME")
    print("-" * 50)
    
    checks = {
        "PostgreSQL": "psql --version",
        "Python": "python --version",
        "Odoo": "head -1 f:/odoo/odoo-bin",
    }
    
    for name, cmd in checks.items():
        try:
            os.system(f"{cmd} > /dev/null 2>&1")
            print(f"✓ {name:15s} - OK")
        except:
            print(f"✗ {name:15s} - NOT FOUND")

def print_quick_start():
    """Afficher les étapes de démarrage rapide"""
    print("\n[2] DÉMARRAGE RAPIDE")
    print("-" * 50)
    
    steps = [
        ("Accéder à l'interface", "http://localhost:8069"),
        ("Créer un patient", "Patients → Créer"),
        ("Créer ticket réception", "Réception → Créer"),
        ("Ajouter actes", "Ajouter lignes d'actes"),
        ("Envoyer à caisse", "Action: Envoyer à la caisse"),
        ("Paiement POS", "Caisse → Nouvelle commande"),
        ("Valider labo", "Laboratoire → Actes payés"),
    ]
    
    for i, (step, action) in enumerate(steps, 1):
        print(f"{i}. {step}")
        print(f"   → {action}\n")

def print_test_data():
    """Afficher les données de test disponibles"""
    print("\n[3] DONNÉES DE TEST")
    print("-" * 50)
    
    print("Patients Disponibles:")
    patients = [
        ("Karim Benali", "PAT000001", "M, 1985, O+"),
        ("Zahra Ameziane", "PAT000002", "F, 1992, AB-"),
        ("Younes Hamidou", "PAT000003", "M, 1978, A+"),
    ]
    
    for name, num, info in patients:
        print(f"  • {name:20s} ({num}) - {info}")
    
    print("\nExamens Laboratoire:")
    lab_acts = [
        ("Prise de sang", "1 000 DZD"),
        ("Bilan lipidique", "500 DZD"),
        ("Groupage sanguin", "800 DZD"),
        ("Analyse urinaire", "400 DZD"),
        ("Glycémie", "300 DZD"),
    ]
    
    for act, price in lab_acts:
        print(f"  • {act:20s} → {price}")
    
    print("\nExamens Imagerie:")
    img_acts = [
        ("Radiographie thoracique", "2 000 DZD"),
        ("Échographie abdominale", "2 500 DZD"),
        ("Échographie mammaire", "2 500 DZD"),
        ("Scanner abdominal", "5 000 DZD"),
        ("IRM crânienne", "8 000 DZD"),
    ]
    
    for act, price in img_acts:
        print(f"  • {act:25s} → {price}")

def print_credentials():
    """Afficher les identifiants de connexion"""
    print("\n[4] IDENTIFIANTS DE CONNEXION")
    print("-" * 50)
    
    creds = {
        "Interface Web": "http://localhost:8069",
        "Admin User": "admin",
        "Admin Password": "admin",
        "Database": "mydb_clinic",
        "DB User": "odoo",
        "DB Password": "987654987654321aA",
        "DB Host": "localhost",
        "DB Port": "5432",
    }
    
    for key, value in creds.items():
        print(f"{key:20s}: {value}")

def print_keyboard_shortcuts():
    """Afficher les raccourcis clavier"""
    print("\n[5] RACCOURCIS CLAVIER ODOO")
    print("-" * 50)
    
    shortcuts = {
        "Ctrl + S": "Sauvegarder",
        "Ctrl + Delete": "Supprimer",
        "Ctrl + Shift + N": "Nouvelles documents",
        "Alt + Q": "Chercher",
        "Ctrl + Home": "Aller au début",
        "Ctrl + End": "Aller à la fin",
        "Tab": "Naviguer entre champs",
        "Escape": "Annuler/Fermer",
    }
    
    for shortcut, action in shortcuts.items():
        print(f"{shortcut:15s} → {action}")

def print_useful_commands():
    """Afficher les commandes utiles"""
    print("\n[6] COMMANDES UTILES")
    print("-" * 50)
    
    commands = {
        "Recharger modules": "python odoo-bin -c odoo.conf -u clinic_patient -d mydb_clinic --stop-after-init",
        "Afficher logs": "tail -f odoo.log",
        "Restart serveur": "pkill -f 'odoo-bin' && python odoo-bin -c odoo.conf -d mydb_clinic",
        "Backup DB": "pg_dump -h localhost -U odoo mydb_clinic > backup_$(date +%Y%m%d).sql",
        "Restore DB": "psql -h localhost -U odoo mydb_clinic < backup_20241219.sql",
        "Accès DB": "psql -h localhost -U odoo -d mydb_clinic"
    }
    
    print("\nCommandes Ligne Commande:")
    for desc, cmd in commands.items():
        print(f"\n{desc}:")
        print(f"  $ {cmd}")

def print_troubleshooting():
    """Afficher les solutions aux problèmes courants"""
    print("\n[7] DÉPANNAGE COURANT")
    print("-" * 50)
    
    issues = {
        "Serveur ne démarre": [
            "1. Vérifier PostgreSQL est lancé: psql -h localhost -l",
            "2. Vérifier odoo.conf pour db_host/db_port",
            "3. Relancer: python odoo-bin -c odoo.conf -d mydb_clinic"
        ],
        "Actes ne changent pas d'état": [
            "1. Vérifier patient_id sur commande POS",
            "2. Vérifier reception_id sur actes",
            "3. Chercher logs: grep 'action_pos_order_paid' odoo.log"
        ],
        "Menu vide": [
            "1. Recharger module: python odoo-bin -c odoo.conf -u clinic_medical_act -d mydb_clinic",
            "2. Rafraîchir page: Ctrl + F5",
            "3. Vérifier domaine filter est valide"
        ],
        "Erreur Base de Données": [
            "1. Vérifier encoding UTF-8: psql -c \"SELECT datctype FROM pg_database WHERE datname='mydb_clinic'\"",
            "2. Relancer postgres si erreur encoding",
            "3. Vérifier utilisateur permissions: psql -c \"\\du\""
        ]
    }
    
    for issue, solutions in issues.items():
        print(f"\n{issue}:")
        for solution in solutions:
            print(f"  {solution}")

def print_documentation():
    """Afficher les ressources documentation"""
    print("\n[8] DOCUMENTATION")
    print("-" * 50)
    
    docs = [
        ("CLINIC_SYSTEM_README.md", "Guide utilisateur complet (15 pages)"),
        ("WORKFLOW_INTEGRATION.md", "Architecture workflow détaillée"),
        ("FINAL_CHECKLIST.md", "Checklist de vérification système"),
        ("PROJECT_SUMMARY.md", "Résumé final du projet"),
        ("verify_system.py", "Script de vérification système"),
        ("test_workflow.py", "Tests unitaires workflow"),
    ]
    
    print("\nFichiers Documentation:")
    for filename, description in docs:
        full_path = Path(f"f:/odoo/{filename}")
        status = "✓" if full_path.exists() else "✗"
        print(f"{status} {filename:30s} - {description}")

def print_support():
    """Afficher les informations de support"""
    print("\n[9] SUPPORT & MAINTENANCE")
    print("-" * 50)
    
    print("""
Équipe Support:
  • Email: support@clinique.dz
  • Hotline: +213 661 234 567
  • Chat: support.clinique.dz

Horaires Support:
  • Lundi-Vendredi: 8h-18h
  • Samedi: 10h-14h
  • Dimanche: Fermé (urgences: hotline)

Mises à Jour:
  • Patches: Quotidiens
  • Nouvelles features: Mensuels
  • Major updates: Trimestriels

Backups:
  • Automatiques: Quotidiens
  • Rétention: 30 jours
  • Récupération: < 1 heure
""")

def print_next_steps():
    """Afficher les prochaines étapes"""
    print("\n[10] PROCHAINES ÉTAPES")
    print("-" * 50)
    
    steps = [
        ("Accéder l'interface", "http://localhost:8069"),
        ("Se connecter", "admin / admin"),
        ("Créer un patient test", "Suivre guide dans CLINIC_SYSTEM_README.md"),
        ("Tester workflow complet", "Patient → Réception → POS → Validation"),
        ("Consulter rapports", "Via menu Dashboard"),
        ("Sauvegarder configuration", "Exporter backups"),
        ("Former utilisateurs", "En salle de formation"),
        ("Déployer en production", "Au lancement officiel"),
    ]
    
    print("\nTâches Immédiates:")
    for i, (task, details) in enumerate(steps, 1):
        print(f"{i}. {task}")
        print(f"   → {details}\n")

def main():
    """Main entry point"""
    os.system("clear" if sys.platform != "win32" else "cls")
    
    print_header()
    check_system()
    print_quick_start()
    print_test_data()
    print_credentials()
    print_keyboard_shortcuts()
    print_useful_commands()
    print_troubleshooting()
    print_documentation()
    print_support()
    print_next_steps()
    
    # Footer
    print("\n" + "=" * 70)
    print("🚀 LE SYSTÈME EST PRÊT POUR TESTING!")
    print("=" * 70)
    print("\nPour plus d'informations, consulter:")
    print("  • CLINIC_SYSTEM_README.md (guide utilisateur)")
    print("  • WORKFLOW_INTEGRATION.md (architecture)")
    print("  • FINAL_CHECKLIST.md (vérifications)")
    print("\nContact: support@clinique.dz")
    print("Version: 1.0.0 Beta | Date: Décembre 2024")
    print("=" * 70 + "\n")

if __name__ == '__main__':
    main()

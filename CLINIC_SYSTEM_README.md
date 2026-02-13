# Système de Gestion de Clinique - Odoo 19.0

## 🏥 Vue d'ensemble

Système de gestion complet pour une clinique médicale incluant:
- **Gestion des patients** (dossiers, historique, documents)
- **Réception et tickets** (prise de rendez-vous, demandes d'actes)
- **Actes médicaux** (laboratoire, imagerie, consultations)
- **Caisse POS** (paiement commode et sécurisé)
- **Validation** (laboratoire et imagerie)
- **Rapports et dashboard** (statistiques et suivi)

## 📋 Architecture Système

### Base de Données
- **Système**: PostgreSQL 18.1
- **Hôte**: localhost
- **Port**: 5432
- **Base**: mydb_clinic
- **Utilisateur**: odoo
- **Mot de passe**: 987654321aA

### Serveur Odoo
- **Version**: 19.0
- **URL**: http://localhost:8069
- **Python**: 3.11
- **Admin Password**: admin

### Modules Installés

| Module | Rôle | Status |
|--------|------|--------|
| clinic_patient | Gestion patients | ✅ Active |
| clinic_reception | Tickets réception | ✅ Active |
| clinic_medical_act | Actes médicaux | ✅ Active |
| clinic_pos | Caisse (POS) | ✅ Active |
| clinic_validation | Validation Labo/Radio | ✅ Active |
| clinic_reports | Rapports | ✅ Active |
| clinic_dashboard | Tableau de bord | ✅ Active |

## 🔄 Workflow du Patient

```
ÉTAPE 1: Création Patient
└─→ res.partner (is_patient=True)
    • Numéro dossier auto-généré
    • Données personnelles (age, groupe sanguin, etc)

ÉTAPE 2: Ticket Réception
└─→ clinic.reception
    • Patient sélectionné
    • Actes demandés ajoutés (via clinic.reception.line)
    • Montant total calculé

ÉTAPE 3: Création Actes Médicaux
└─→ clinic.medical.act.line (state='waiting')
    • Action: action_send_to_cashier()
    • Crée les actes en état 'waiting'

ÉTAPE 4: Paiement Caisse
└─→ pos.order (payment confirmed)
    • Patient patient_id
    • Articales à actes médicaux
    • Action: action_pos_order_paid()
    • Transition: state 'waiting' → 'paid'

ÉTAPE 5: Validation Laboratoire/Imagerie
└─→ clinic.medical.act.line (state='paid')
    • Filtrées par medical_act_type
    • Actions: 
      - action_set_in_progress() (state='in_progress')
      - action_validate() (state='done')

ÉTAPE 6: Rapports et Facturation
└─→ clinic_reports & clinic_dashboard
    • Statistiques d'activité
    • Recettes collectées
    • Actes par médecin/type
```

## 📊 Modèles de Données

### clinic.patient (extend res.partner)
```
Fields:
  • is_patient: Boolean
  • patient_number: Char (unique) - auto-généré via séquence
  • date_of_birth: Date
  • age: Integer (computed)
  • gender: Selection (male/female)
  • blood_group: Selection (O+, O-, A+, A-, B+, B-, AB+, AB-)
```

### clinic.reception
```
Fields:
  • name: Char (numéro ticket)
  • reception_date: Datetime (auto: now)
  • patient_id: Many2one(res.partner)
  • medical_act_line_ids: One2many(clinic.reception.line)
  • state: Selection (draft, waiting, paid, in_progress, done, cancelled)
  • total_amount: Monetary (computed)
  
Methods:
  • action_send_to_cashier() - crée actes et envoie à caisse
  • action_mark_paid() - mark reception as paid
  • action_cancel() - annul reception
```

### clinic.medical.act.line
```
Fields:
  • name: Char (référence unique)
  • date: Datetime
  • patient_id: Many2one(res.partner)
  • product_id: Many2one(product.product)
  • medical_act_type: Selection (laboratory, imaging) - from product
  • service_type: Selection (analysis, imaging, consultation)
  • state: Selection (draft, waiting, paid, in_progress, done, cancelled)
  • price_unit: Monetary
  • quantity: Integer
  • price_total: Monetary (computed)
  • reception_id: Many2one(clinic.reception)
  • pos_order_id: Many2one(pos.order)
  • payment_date: Datetime
  • validated_by: Many2one(res.users)
  • validation_date: Datetime
  • doctor_share_amount: Monetary (computed)
  • clinic_share_amount: Monetary (computed)

Methods:
  • action_set_paid() - mark as paid (waiting→paid)
  • action_set_in_progress() - start processing (paid→in_progress)
  • action_validate() - finalize (in_progress→done)
  • action_cancel() - cancel act
```

### product.template (extended)
```
New Fields:
  • is_medical_act: Boolean
  • medical_act_type: Selection (laboratory, imaging)
  • service_type: Selection (analysis, imaging, consultation)
  • doctor_share_percentage: Float
  • clinic_share_percentage: Float
  • requires_validation: Boolean
```

## 🎯 Menus Utilisateur

### Clinique (Root Menu)
```
├── 📋 Patients
│   ├── Vue liste de tous les patients enregistrés
│   ├── Créer nouveau patient
│   └── Historique des actes
│
├── 🏥 Réception
│   ├── Tickets de Réception (Vue Kanban/List/Form)
│   └── Actes Médicaux (Vue List/Kanban)
│
├── 💰 Caisse (POS)
│   └── Commandes POS avec patients
│
├── 🧪 Laboratoire
│   └── Actes en attente/en cours de validation
│
├── 📸 Imagerie
│   └── Examens radiologiques en attente de validation
│
├── 📊 Rapports
│   └── Statistiques et bilans
│
└── 📈 Dashboard
    └── Vue d'ensemble de l'activité
```

## 🔐 Sécurité et Accès

### Groupes d'Utilisation
- **clinic_patient_user**: Accès patients
- **clinic_receptionist**: Réception
- **clinic_cashier**: Caisse/POS
- **clinic_technician**: Laboratoire
- **clinic_radiologist**: Imagerie
- **clinic_manager**: Administration complète

### Permissions à la Ligne
```
clinic.medical.act.line:
  • read: Voir les actes
  • write: Modifier statut
  • create: Créer actes (reception uniquement)
  • delete: Admin uniquement
```

## 🚀 Utilisation Quotidienne

### Créer un Patient
1. Menu Clinique → Patients
2. Créer nouveau
3. Nom, date naissance, groupe sanguin
4. Sauvegarder (numéro dossier auto-généré)

### Enregistrer Visite
1. Réception → Tickets
2. Créer nouveau ticket
3. Sélectionner patient
4. Ajouter actes demandés
5. Ajuster quantités/prix
6. "Envoyer à la caisse"

### Payer à la Caisse
1. Caisse (POS) → Commandes
2. Sélectionner patient
3. Ajouter articles/actes
4. Valider paiement
   ↓ (Actes passent automatiquement à 'paid')

### Valider Laboratoire
1. Laboratoire → Actes payés
2. Sélectionner acte
3. "Marquer En Cours" → "Valider"
4. Acte marqué comme 'done'

## 🔍 Recherche et Filtrage

### Filtres Standardisés
- **Par état**: En attente, Payés, Terminés, Annulés
- **Par type**: Laboratoire vs Imagerie
- **Par patient**: Liste/Kanban groupée
- **Par date**: Derniers actes, mois en cours
- **Par médecin**: Actes d'un médecin spécifique

### Vues Disponibles
- **Kanban**: Groupée par état
- **List**: Tableau avec tri/filtre
- **Form**: Détail complet avec workflow
- **Graph/Pivot**: Analyses statistiques

## 📲 API/ORM Utilisation

### Créer patient
```python
patient = env['res.partner'].create({
    'name': 'Ahmed Ali',
    'is_patient': True,
    'date_of_birth': '1990-01-15',
    'gender': 'male',
    'blood_group': 'A+',
    'phone': '0661111111'
})
# patient.patient_number = 'PAT000001' (auto)
```

### Créer ticket réception
```python
# Ajouter actes
act_lines = []
for product_id in [101, 102]:
    act_lines.append((0, 0, {
        'product_id': product_id,
        'price_unit': 1000,
        'quantity': 1
    }))

reception = env['clinic.reception'].create({
    'patient_id': patient.id,
    'medical_act_line_ids': act_lines
})
```

### Envoyer à caisse
```python
reception.action_send_to_cashier()
# Crée clinic.medical.act.line records avec state='waiting'
```

### Paiement POS
```python
# Quand pos ordre est payé (action_pos_order_paid()):
# - Recherche actes waiting pour ce patient
# - Transition: waiting → paid
# - Sauvegarder payment_date et pos_order_id
```

### Valider acte
```python
act = env['clinic.medical.act.line'].browse(123)
act.action_set_in_progress()  # waiting → in_progress
act.action_validate()  # in_progress → done
```

## 📈 Rapports et Statistiques

### Disponibles
- Actes par jour/mois
- Répartition Labo vs Imagerie
- Recettes totales
- Charge par médecin
- Délai moyen de validation

### À Développer
- Rapport patient détaillé
- Factures mensuelles par médecin
- Courbe de charge
- Analyse performances

## 🐛 Dépannage

### Le serveur ne démarre pas
```bash
# Vérifier logs
cat odoo.log

# Vérifier PostgreSQL
psql -h localhost -U odoo -d mydb_clinic

# Relancer
python odoo-bin -c odoo.conf -d mydb_clinic
```

### Base de données introuvable
```bash
# Vérifier odoo.conf
cat odoo.conf | grep db_

# Créer base si nécessaire
sudo -u postgres createdb mydb_clinic
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE mydb_clinic TO odoo;"
```

### Actes ne passent pas en 'paid'
1. Vérifier que pos_order.action_pos_order_paid() est appelé
2. Vérifier patient_id sur la commande POS
3. Vérifier que les actes ont reception_id
4. Logs: `grep -i "action_pos_order_paid" odoo.log`

### Menu Laboratoire vide
1. Créer acte médical avec medical_act_type='laboratory'
2. Passer acte à état 'paid'
3. Vérifier filtre: `[('medical_act_type', '=', 'laboratory'), ('state', 'in', ['paid', 'in_progress', 'done'])]`

## 📦 Données d'Exemple

### Produits Prédéfinis
**Laboratoire** (10 actes)
- Prise de sang: 1000 DZD
- Bilan lipidique: 500 DZD
- Groupage sanguin: 800 DZD
- Analyse urinaire: 400 DZD
- Glycémie: 300 DZD

**Imagerie** (6 actes)
- Radiographie: 2000 DZD
- Échographie abdominale: 2500 DZD
- Échographie sein: 2500 DZD
- Scanner: 5000 DZD
- IRM crânienne: 8000 DZD

### Patients de Test
- Karim Benali (O+, M, 1985)
- Zahra Ameziane (AB-, F, 1992)
- Younes Hamidou (A+, M, 1978)

## 🔄 Maintenance

### Backups Quotidiens
```bash
# Dump PostgreSQL
pg_dump -h localhost -U odoo mydb_clinic > backup_$(date +%Y%m%d).sql

# Filestore Odoo
tar -czf filestore_$(date +%Y%m%d).tar.gz addons/*/
```

### Mise à Jour Modules
```bash
# Après modification code
python odoo-bin -c odoo.conf -u clinic_patient,clinic_reception -d mydb_clinic --stop-after-init
```

### Nettoyage Données
```bash
# Supprimer test data (en SQL)
DELETE FROM clinic_medical_act_line WHERE create_date < NOW() - INTERVAL '7 days' AND state='cancelled';
```

## 📚 Documentation Supplémentaire

- **WORKFLOW_INTEGRATION.md**: Architecture workflow détaillée
- **verify_system.py**: Script de vérification système
- **test_workflow.py**: Tests unitaires workflow
- **odoo.conf**: Configuration serveur
- **README.md**: Informations générales Odoo

## 👥 Support et Maintenance

**Développeur**: Équipe de Gestion Clinique
**Contact**: support@clinique.dz
**Version**: 1.0.0
**Dernière mise à jour**: Décembre 2024

---

**⚠️ Important**: Ce système gère des données médicales sensibles. Assurez-vous:
1. ✅ Sauvegardes régulières (quotidiennes minimum)
2. ✅ Accès sécurisé (VPN, SSL, authentification 2FA)
3. ✅ Conformité RGPD (si applicable)
4. ✅ Logs d'audit actifs
5. ✅ Formation utilisateurs appropriée

---

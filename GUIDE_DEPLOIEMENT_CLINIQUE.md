# 📋 GUIDE DE DÉPLOIEMENT RAPIDE - Modules Clinique Odoo 19

**Date**: 5 février 2026  
**Version Odoo**: 19.0.0

---

## 🚀 ÉTAPES DE DÉPLOIEMENT (SIMPLIFIÉES)

### **ÉTAPE 1: Activation de l'Environnement Virtuel**
```bash
cd f:\odoo
# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1
```

### **ÉTAPE 2: Vérifier les Modules via Interface Web**

1. **Ouvrir Odoo**:
   - URL: `http://localhost:8069`
   - Login en tant qu'administrateur

2. **Menu Apps**:
   - Cliquer sur "Apps" (en haut à gauche)
   - Enlever le filtre "Installed"

3. **Mettre à jour les modules**:
   ```
   clinic_patient     ← Mettre à jour
   clinic_medical_act ← Mettre à jour
   clinic_reception   ← Mettre à jour
   clinic_pos         ← Mettre à jour
   clinic_validation  ← Mettre à jour
   clinic_reports     ← Mettre à jour
   clinic_dashboard   ← Mettre à jour
   ```

4. **Sélectionner et Cliquer "Upgrade"** pour chaque module

### **ÉTAPE 3: Naviguer dans les Modules Après Mise à Jour**

#### Menu Principal "Clinique":
- ✅ **Patients** - Gestion des patients
- ✅ **Actes** - Suivi des actes médicaux  
- ✅ **Réception** - Tickets de réception
- ✅ **Caisse** - Point of sale médical
- ✅ **Laboratoire** - Validation analyses
- ✅ **Imagerie** - Validation examens
- ✅ **Rapports** - Statistiques (gestionnaires)
- ✅ **Configuration** - Médecins et actes

---

## 📊 VUES DISPONIBLES PAR MODULE

### **clinic_patient** - Liste des Patients
- **Vue Kanban**: Affichage visuel des patients par cartes
- **Vue Liste**: Tableau avec tous les patients
- **Vue Formulaire**: Fiche patient détaillée
- **Vue Graphique**: Statistiques (sexe × statut)
- **Vue Pivot**: Analyse multidimensionnelle

**Filtres Disponibles**:
- Homme / Femme
- Actifs / Inactifs
- Avec/Sans assurance
- Avec/Sans allergies

---

### **clinic_medical_act** - Actes Médicaux
- **Vue Kanban**: Actes groupés par état
- **Vue Liste**: Tous les actes avec couleurs de statut
- **Vue Formulaire**: Détails acte + workflow
- **Vues Graphiques** (3 types):
  - Actes par type
  - Revenus par médecin
  - Distribution par état

---

### **clinic_reception** - Tickets de Réception
- **Vue Kanban**: Tickets groupés par état
- **Vue Liste**: Tous les tickets avec infos patient
- **Vue Formulaire**: Ticket complet avec actes
- **Vue Graphique**: État des réceptions (Pie chart)

---

### **clinic_pos** - Caisse Médicale
- Utilise les vues POS standards d'Odoo
- **Nouveau**: Champ patient obligatoire
- **Nouveau**: Graphiques revenus caisse

---

### **clinic_validation** - Validation Actes
#### Pour Laboratoire:
- Vue Kanban (par état)
- Vue Liste
- Vue Formulaire (avec résultats)
- Vue Graphique

#### Pour Imagerie:
- Vue Kanban (par état)
- Vue Liste
- Vue Formulaire (avec résultats)
- Vue Graphique

---

### **clinic_reports** - Rapports
5 rapports statistiques disponibles (accès gestionnaires):
1. Analyse des Actes
2. Honoraires Médecins
3. Chiffre d'Affaires
4. Fréquentation Patients
5. Par Type de Service

---

### **clinic_dashboard** - Tableau de Bord
- Vue graphique des actes payés
- Accessible pour gestionnaires uniquement

---

## 🔐 RÔLES ET PERMISSIONS

### **Réceptionniste** (`group_clinic_receptionist`)
- ✅ Voir Patients
- ✅ Créer Patients
- ✅ Créer Réception
- ❌ Pas d'accès Caisse
- ❌ Pas d'accès Validation

### **Caissier** (`group_clinic_cashier`)
- ✅ Voir Caisse (POS)
- ✅ Valider paiements
- ❌ Pas d'accès Patients
- ❌ Pas d'accès Validation

### **Technicien Labo** (`group_clinic_lab_tech`)
- ✅ Voir Actes Laboratoire
- ✅ Valider Analyses
- ❌ Pas d'accès Imagerie
- ❌ Pas d'accès Rapports

### **Technicien Imagerie** (`group_clinic_imaging_tech`)
- ✅ Voir Actes Imagerie
- ✅ Valider Examens
- ❌ Pas d'accès Labo
- ❌ Pas d'accès Rapports

### **Gestionnaire** (`group_clinic_manager`)
- ✅ **ACCÈS TOTAL** à tous les modules
- ✅ Voir tous les rapports
- ✅ Dashboard
- ✅ Configuration

---

## ⚠️ PROBLÈMES COURANTS ET SOLUTIONS

### **Erreur: "Module not found"**
- Solution: Vérifier que tous les modules sont dans `/f:/odoo/addons/`

### **Erreur: "Champ n'existe pas"**
- Solution: Le module dépendant n'est pas installé
- Vérifier l'ordre d'installation: `clinic_patient` d'abord

### **Menu "Clinique" ne s'affiche pas**
- Solution: Aller dans Apps, mettre à jour `clinic_patient`

### **Pas de graphiques visibles**
- Solution: Cliquer sur "Accueil" puis revenir au menu
- Ou: Actualiser la page (F5)

---

## 🔧 CONFIGURATION INITIALE RECOMMANDÉE

### **1. Créer des Médecins** (in clinic_medical_act > Configuration > Médecins)
- Ajouter nom, spécialité
- Définir part médecin / part clinique (%)

### **2. Créer des Actes Médicaux** (in clinic_medical_act > Configuration > Actes)
- Consultation généraliste
- Consultation spécialiste (Cardiologie, etc.)
- Analyses laboratoire
- Examens imagerie (Échographie, Scanner, etc.)

### **3. Créer des Patients** (in Patients)
- N° dossier généré automatiquement
- Remplir: nom, date naissance, sexe, tél

### **4. Configurer Caisse** (in clinic_pos)
- Méthodes de paiement (Espèces, Carte)
- Sessions caisse

---

## 📝 FLUX D'UTILISATION COMPLET

### **Exemple: Patient consultation généralisée**

1. **Réceptionniste**:
   - Menu > Patients
   - Créer ou sélectionner patient
   - Menu > Réception
   - Créer ticket de réception
   - Sélectionner actes (ex: Consultation généraliste)

2. **Caissier**:
   - Menu > Caisse
   - Générer facture
   - Patient paie (Espèces/Carte)
   - Générer reçu

3. **Médecin** (selon acte):
   - Si besoin analyses: Technicien Labo valide
   - Si besoin imagerie: Technicien Imagerie valide

4. **Gestionnaire**:
   - Menu > Rapports
   - Voir chiffre d'affaires
   - Voir honoraires médecins
   - Dashboard d'activité

---

## 🔄 MIS À JOUR FUTURE

Pour ajouter des vues graphiques supplémentaires après stabilisation:

1. Ajouter les fichiers XML dans `/views/`
2. Mettre à jour `__manifest__.py` (section `data`)
3. Aller dans Apps > Mettre à jour le module
4. Rafraîchir le navigateur

---

## 📞 SUPPORT

**Vérifier**:
- ✅ Tous les modules sont en statut "Installed"
- ✅ Utilisateurs ont les bons rôles
- ✅ Base de données PostgreSQL active
- ✅ Python 3.11 avec venv activé

---

**Fin du Guide de Déploiement Rapide**

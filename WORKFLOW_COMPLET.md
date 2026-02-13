# 🏥 GUIDE COMPLET DU WORKFLOW - SYSTÈME DE GESTION DE CLINIQUE

## 📋 Vue d'ensemble

Le système de gestion de clinique utilise un workflow complet qui relie:
- **Réception** (enregistrement des patients)
- **Actes Médicaux** (demande d'actes)
- **Caisse/POS** (paiement)
- **Validation** (laboratoire et imagerie)

---

## 🔄 FLUX DE TRAVAIL COMPLET

```
Patient arrive
     ↓
Réceptionniste crée Ticket Réception
     ↓
Ajoute Actes Médicaux Demandés (Réception > Ligne)
     ↓
Clique "Envoyer à la Caisse"
     ↓
Crée Actes Médicaux (state=waiting)
     ↓
Caissier crée Commande POS avec actes
     ↓
Paiement via POS
     ↓
Actes marqués comme Payés (state=paid)
     ↓
Actes visibles dans Laboratoire/Imagerie
     ↓
Labo/Imagerie valide les résultats
     ↓
Actes marqués comme Réalisés (state=done)
```

---

## 📝 ÉTAPES DÉTAILLÉES

### ✅ ÉTAPE 1: Accueil du Patient (Réceptionniste)

1. Aller à: **Clinique → Réception → Réception**
2. Créer un nouveau ticket:
   - **Patient**: Sélectionner un patient existant ou en créer un
   - **Date de Réception**: Automatique (date/heure actuelle)
   - **Réceptionniste**: Automatique (utilisateur actif)
   - **État**: Brouillon (draft)

### ✅ ÉTAPE 2: Ajouter les Actes Médicaux Demandés

1. Dans le ticket de réception, scrollez jusqu'à "Actes Médicaux Demandés"
2. Cliquez sur "Ajouter une ligne"
3. Remplissez chaque ligne:
   - **Acte Médical**: Sélectionner un acte (ex: Analyse de sang, Radiographie)
   - **Type**: Automatique (laboratoire/imagerie)
   - **Service**: Automatique d'après le produit
   - **Médecin**: Automatique d'après le produit
   - **Quantité**: 1 (généralement)
   - **Prix Unitaire**: Automatique du catalogue produit
   - **Total**: Calculé automatiquement

4. Répétez pour tous les actes demandés

### ✅ ÉTAPE 3: Envoyer à la Caisse

1. après avoir ajouté tous les actes, cliquez sur **"Envoyer à la Caisse"**
2. Cela crée les actes médicaux (clinic.medical.act.line) avec:
   - État: **En Attente** (waiting)
   - Référence de réception: Lien automatique
   - Notes: "Ticket de réception: [numéro]"

3. L'état du ticket devient **"En Attente Caisse"** (waiting)
4. Notification de succès: "Ticket envoyé à la caisse avec succès!"

### ✅ ÉTAPE 4: Paiement à la Caisse (Caissier)

1. Aller à: **Ventes → Point de Vente → Caisse**
2. Créer une nouvelle commande:
   - **Patient**: Sélectionner le **MÊME patient** que le ticket
   - **Ajouter les produits**: Les actes médicaux créés
   - **Prix**: Automatiques
3. Effectuer le paiement (argent, carte, etc.)
4. Cliquer sur "Valider la commande"

**À ce moment:**
- Les actes médicaux sont marqués comme **Payés** (state=paid)
- `payment_date` est rempli automatiquement

### ✅ ÉTAPE 5: Voir les Actes Créés depuis une Réception

1. Dans le ticket de réception, cliquez sur **"Voir Actes Créés"**
2. Cela affiche tous les actes créés à partir de ce ticket
3. Vous pouvez voir:
   - État actuel (en attente, payé, en cours, réalisé)
   - Montants
   - Dates de paiement
   - Médecin assigné

### ✅ ÉTAPE 6: Validation en Laboratoire (Labo/Imagerie)

**Pour les ACTES LABORATOIRE:**
1. Aller à: **Clinique → Réception → Validation → Laboratoire**
2. Vous voyez les actes en attente ou payés
3. Vous pouvez:
   - **Cliquer sur un acte** pour voir les détails
   - **Ajouter des notes** (résultats, observations)
   - **Marquer comme En Cours** (en_progress)
   - **Valider** (done) quand les résultats sont prêts

**Pour les ACTES IMAGERIE:**
1. Aller à: **Clinique → Réception → Validation → Imagerie**
2. Même processus que le laboratoire
3. Vous pouvez ajouter les images/clichés en notes

---

## 🔧 CONFIGURATION REQUISE

### 1. Créer des Patients

1. Aller à: **Évaluation professionnelle → Partenaires → Patients**
2. Cliquer sur "NOUVEAU"
3. Remplir:
   - **Nom**: Nom du patient
   - **Profession**: Son rôle (patient, médecin, etc.)
   - **Cocher**: "Est un patient"
   - **Numéro de Dossier**: Automatique ou manuel
   - **Âge**: Date de naissance → Âge calculé
4. **Sauvegarder**

### 2. Créer des Actes Médicaux (Produits)

1. Aller à: **Ventes → Produits → Produits**
2. Cliquer sur "NOUVEAU"
3. Remplir:
   - **Nom du Produit**: "Analyse de sang", "Radiographie thorax", etc.
   - **Type de Produit**: "Service" ou "Bien"
   - **Prix**: Définir le prix
   - **Onglet Clinique**:
     - **Est un acte médical**: ✅ Cocher
     - **Type d'acte**: Laboratoire ou Imagerie
     - **Service**: Sélectionner (Cardiologie, Radiologie, etc.)
     - **Médecin**: Sélectionner un médecin (optionnel)
     - **Partage Médecin (%)**: % de commission du médecin
4. **Sauvegarder**

### 3. Configurer la Caisse POS

1. Aller à: **Ventes → Configuration → Caisse (Positions de caisse)**
2. Créer ou éditer une caisse:
   - **Nom**: "Caisse Clinique"
   - **Onglet Clinique**:
     - **Est une caisse médicale**: ✅ Cocher
     - **Demander le patient**: ✅ Cocher
3. **Sauvegarder**

---

## ⚠️ POINTS IMPORTANTS

### 1. Les actes n'apparaissent pas au POS
**Causes possibles:**
- ❌ Patient non sélectionné dans la commande POS
- ❌ Produit n'est pas un acte médical (not is_medical_act)
- ❌ POS non configurée comme "caisse médicale"

**Solution:** Vérifiez les 3 points ci-dessus

### 2. Les actes n'apparaissent pas dans Validation
**Causes possibles:**
- ❌ Type d'acte pas "laboratoire" ou "imagerie"
- ❌ État de l'acte ne pas dans ['waiting', 'paid', 'in_progress']
- ❌ Filtre actif cache les actes

**Solution:** 
1. Allez à: Climatisation → Réception → Actes Médicaux
2. Vérifiez le type et l'état de l'acte

### 3. Un acte est bloqué/en mauvais état
**Solution:**
1. Allez à: **Clinique → Réception → Actes Médicaux**
2. Trouvez l'acte problématique
3. Cliquez pour éditer
4. Utilisez les boutons pour changer l'état
5. Nettoyez les données si nécessaire

---

## 📊 STATUTS DISPONIBLES

### 1. État du Ticket de Réception
| État | Description |
|------|-------------|
| **Draft** (Brouillon) | Ticket en cours de création |
| **Waiting** (En attente) | En attente de paiement à la caisse |
| **Paid** (Payé) | Paiement effectué |
| **In Progress** (En cours) | Actes en cours de traitement |
| **Done** (Terminé) | Tous les actes sont réalisés |
| **Cancelled** (Annulé) | Ticket annulé |

### 2. État de l'Acte Médical
| État | Description |
|------|-------------|
| **Draft** (Brouillon) | Acte créé mais non validé |
| **Waiting** (En attente) | Acte en attente de paiement |
| **Paid** (Payé) | Acte payé, prêt pour validation |
| **In Progress** (En cours) | Labo/Imagerie en traitement |
| **Done** (Réalisé) | Acte validé et complet |
| **Cancelled** (Annulé) | Acte annulé |

---

## 🎯 SCÉNARIOS COURANTS

### Scénario 1: Patient pour Analyse de Sang + Radiographie

```
1. Réceptionniste crée ticket réception
2. Ajoute 2 actes:
   - Analyse de sang (labo)
   - Radiographie (imagerie)
3. Envoie à la caisse (crée 2 actes médicaux, state=waiting)
4. Caissier paie via POS
5. Les 2 actes deviennent visibles:
   - Dans Laboratoire (analyse de sang)
   - Dans Imagerie (radiographie)
6. Labo valide l'analyse
7. Imagerie valide la radiographie
```

### Scénario 2: Paiement Partiel ou Groupé

```
1. Réceptionniste crée ticket réception
2. Ajoute 3 actes à 100 DA chacun (total 300 DA)
3. Envoie à la caisse
4. Caissier peut:
   a) Payer les 3 actes ensemble (300 DA)
   b) Payer acte par acte (100 DA × 3)
5. Chaque acte payé sera marqué individuellement
```

---

## 🔐 SÉCURITÉ & PERMISSIONS

Les rôles suivants sont définis:

| Rôle | Permissions |
|------|------------|
| **Réceptionniste** | Créer/éditer tickets de réception |
| **Caissier** | Créer/finaliser commandes POS |
| **Laborantin** | Valider actes de laboratoire |
| **Radiologue** | Valider actes d'imagerie |
| **Médecin** | Consulter les dossiers patients |
| **Administrateur** | Accès complet |

---

## 📞 SUPPORT & DÉPANNAGE

### Commandes Utiles (Terminal)

Pour recharger les modules après modifications:
```bash
python odoo-bin -c odoo.conf -d mydb_clinic -i clinic_reception,clinic_medical_act,clinic_validation --stop-after-init
```

### Fichiers Importants

- Configuration: `/odoo/odoo.conf`
- Modules clinic: `/odoo/addons/clinic_*/`
- Données de test: Via l'interface Odoo

---

**Version:** 1.0  
**Date:** 9 février 2026  
**Auteur:** Équipe de Développement Clinique

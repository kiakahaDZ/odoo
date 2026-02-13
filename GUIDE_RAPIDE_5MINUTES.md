# ⚡ GUIDE RAPIDE - MISE À JOUR MODULES CLINIQUE

**Durée totale**: ~15 minutes

---

## 🎯 AVANT DE COMMENCER

✅ Assurez-vous d'avoir:
- [ ] Accès administrateur à Odoo
- [ ] L'URL: `http://localhost:8069`
- [ ] Sauvegarde de base de données (IMPORTANT!)

---

## 🚀 ÉTAPE 1: SAUVEGARDER (2 min)

```bash
# Terminal PowerShell en tant qu'administrateur
cd f:\odoo

# Créer une sauvegarde
pg_dump odoo > backup_clinique_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql

# Ou via Odoo Web:
# Menu → Paramètres → Téléchargements (en bas à gauche)
# → Télécharger une sauvegarde de la base de données
```

---

## 📝 ÉTAPE 2: METTRE À JOUR LES MODULES (5 min)

### Option A: Via Interface Web ⭐ RECOMMANDÉ

1. **Se connecter**: http://localhost:8069
2. **Aller à**: Menu ☰ → Applications
3. **Chercher**: `clinic` dans la barre recherche
4. **Modifier** chaque module:
   - [ ] clinic_patient
   - [ ] clinic_medical_act
   - [ ] clinic_reception
   - [ ] clinic_pos
   - [ ] clinic_validation
   - [ ] clinic_reports
   - [ ] clinic_dashboard

5. **Pour chaque module**:
   - Cliquer dessus
   - Cliquer sur **"Mettre à jour"** (flèche circulaire)
   - Attendre le chargement (~5-10 sec par module)

### Option B: Via Terminal

```bash
# Terminal: Activer l'environnement virtuel
cd f:\odoo
.\venv\Scripts\Activate.ps1

# Mettre à jour tous les modules
python odoo-bin -c f:\odoo\odoo.conf `
    -u clinic_patient,clinic_medical_act,clinic_reception,clinic_pos,clinic_validation,clinic_reports,clinic_dashboard `
    --workers=0 --stop-after-init

# Attendre la fin (message: "Update Info saved")
```

---

## ✅ ÉTAPE 3: VÉRIFIER (5 min)

### Vérification Visuelle

1. **Rafraîchir** Odoo: `F5`
2. **Menu Clinique** visible? 
   - Cliquer sur le 🏥 **"Clinique"** en haut à gauche
3. **Tous les menus visibles?**
   ```
   ✓ Tableau de Bord
   ✓ Patients
   ✓ Actes
   ✓ Réception
   ✓ Caisse
   ✓ Laboratoire
   ✓ Imagerie
   ✓ Rapports
   ✓ Configuration
   ```

4. **Cliquer sur Patients** et tester:
   - [ ] Vue Kanban (cartes) - Cliquer sur l'icône `☰`
   - [ ] Vue Liste (tableau) - Cliquer sur l'icône `≡`
   - [ ] Vue Graphique - Cliquer sur l'icône 📊
   - [ ] Fonction Recherche - Tester filtres

### Vérification Console (Optionnel)

Appuyer sur `F12` (Outils de développement):
- Console: Pas d'erreurs rouges
- Réseau: Pas d'erreurs 500

---

## 🎓 ÉTAPE 4: EXPLORER LES NOUVELLES VUES (3 min)

### Par Module:

**Patients** → Cliquer sur chaque icône:
- 📋 = Liste
- 🃏 = Kanban (cartes colorées)
- 📝 = Détail
- 📊 = Graphique (nouveau!)
- 🔄 = Tableau croisé (nouveau!)
- 🔍 = Recherche (améliorée!)

**Actes Médicaux** → Mêmes vues + Graphiques supplémentaires

**Réception** → Ajout d'un Graphique par état

**Caisse** → Graphiques revenus caisse (nouveau!)

**Labo/Imagerie** → Kanban par état (nouveau!)

**Rapports** → 5 rapports statistiques disponibles (nouveau!)

---

## ⚠️ EN CAS DE PROBLÈME

### Erreur: "Module Not Found"
```bash
# Vider le cache
cd f:\odoo
rm -r addons/*/__pycache__/
# Relancer Odoo
```

### Erreur: "View Error"
```
→ Aller dans: Paramètres → Gestion des Modules
→ Chercher le module problématique
→ Cliquer sur "Réinstaller"
```

### Erreur: "Database Lock"
```
→ Attendre 2-3 minutes
→ Rafraîchir la page
→ Réessayer
```

### Erreur: "Access Denied"
```
→ Vérifier que vous êtes en tant que Gestionnaire
→ Menu ☰ → Paramètres → Utilisateurs
→ Sélectionner votre utilisateur
→ Vérifier les groupes:
   ✓ group_clinic_manager (au minimum)
```

---

## 📊 APRÈS LA MISE À JOUR

### Actions Recommandées:

1. **Créer un Patient de Test**
   - Menu → Patients
   - Bouton "+ Créer"
   - Remplir les champs
   - Cliquer "Enregistrer"

2. **Consulter le Tableau de Bord**
   - Menu → Tableau de Bord
   - Observer le graphique de revenus

3. **Générer un Rapport**
   - Menu → Rapports
   - Cliquer sur "Analyse des Actes"
   - Observer le graphique

4. **Tester les Filtres**
   - Patients → Recherche
   - Cliquer sur "Homme" ou "Femme"
   - Observer le filtrage

---

## 📚 DOCUMENTATION COMPLÈTE

Pour plus de détails, consulter:
- `DIAGNOSTIC_COMPLET_MODULES_CLINIQUE.md` - Analyse technique
- `DOCUMENT_AMELIORATIONS_CLINIQUE_ODOO19.md` - Documentation complète
- `GUIDE_MISE_A_JOUR_APRES_CORRECTIONS.md` - Guide détaillé

---

## ✅ CHECKLIST FINALE

- [ ] Base de données sauvegardée
- [ ] Tous les modules mis à jour
- [ ] Page Odoo rafraîchie
- [ ] Menu Clinique visible
- [ ] Tous les sous-menus présents
- [ ] Vues testées (Kanban, Graph, etc.)
- [ ] Recherche fonctionnelle
- [ ] Pas d'erreurs console

---

## 🎉 C'EST BON!

Vous pouvez maintenant utiliser les modules clinique améliorés avec:
- ✅ 20+ vues disponibles
- ✅ 9 graphiques
- ✅ 5 rapports
- ✅ Recherches avancées
- ✅ Tableaux croisés

**Profitez de votre système enrichi!** 🚀

---

**Questions?** Consulter les fichiers de documentation ou relancer le processus.

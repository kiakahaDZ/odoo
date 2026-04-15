# 🚀 Transférer Odoo Clinic System sur un autre PC

Ce guide explique comment déplacer votre installation Docker complète vers un nouvel ordinateur.

## Option 1 : Méthode Standard (Recommandée)
*Utilisez cette méthode si le nouveau PC a accès à Internet.*

1. **Copiez le dossier complet** `F:\odoo` sur une clé USB.
2. **Sur le nouveau PC** : Installez [Docker Desktop](https://www.docker.com/products/docker-desktop/).
3. **Branchez la clé USB** et copiez le dossier `odoo` sur le disque dur (ex: `C:\odoo`).
4. **Ouvrez un terminal** dans ce dossier et lancez :
   ```powershell
   docker-compose up -d
   ```
   *Docker téléchargera automatiquement Odoo 18 et PostgreSQL, puis installera vos modules.*

---

## Option 2 : Méthode Export d'Image (Installation hors-ligne)
*Utilisez cette méthode si le nouveau PC n'a pas Internet ou si vous voulez exactement la même image.*

### 1. Sur le PC Source (Votre PC actuel)
Exportez l'image personnalisée que nous avons construite :
```powershell
# Créer le fichier de l'image
docker save odoo_odoo > odoo_clinic_image.tar
```

### 2. Transférez les fichiers
Copiez ces éléments sur votre clé USB :
- Le dossier `custom_addons`
- Le fichier `docker-compose.yml`
- Le fichier `odoo.conf`
- Le fichier `odoo_clinic_image.tar` (que vous venez de créer)

### 3. Sur le PC de Destination
1. Copiez les fichiers dans un dossier (ex: `C:\odoo`).
2. Ouvrez un terminal dans ce dossier.
3. **Importez l'image** :
   ```powershell
   docker load < odoo_clinic_image.tar
   ```
4. **Lancez le système** :
   ```powershell
   docker-compose up -d
   ```

---

## 💾 Comment transférer les DONNÉES (Base de données) ?
Si vous avez déjà commencé à entrer des vrais patients et que vous voulez les transférer :

1. **Sur le PC Source** (pendant qu'Odoo tourne) :
   ```powershell
   docker exec -t odoo-db-1 pg_dumpall -c -U odoo > backup_total.sql
   ```
2. **Sur le nouveau PC** (après avoir lancé `docker-compose up -d`) :
   ```powershell
   cat backup_total.sql | docker exec -i odoo-db-1 psql -U odoo
   ```

---

## ✅ Checklist de vérification
- [ ] Docker Desktop est bien lancé sur le nouveau PC.
- [ ] Le port `8069` n'est pas utilisé par un autre logiciel.
- [ ] Vous avez bien copié le dossier `custom_addons`.

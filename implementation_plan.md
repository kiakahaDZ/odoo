# Module POS Salon de Coiffure / Barbier — `barber_pos`

## Objectif

Créer un module Odoo complet et autonome simulant un système POS (Point de Vente) dédié aux salons de coiffure et barbiers. Il intègre la gestion des rôles, les contrats coiffeurs (loyer mensuel ou pourcentage), les prestations à tarifs variables, les produits consommables, et un tableau de bord analytique.

---

## Architecture du Module

```
f:\odoo\addons\barber_pos\
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── main.py                        ← Route pour l'interface POS web
├── data/
│   ├── barber_sequence.xml            ← Séquences (commandes, contrats)
│   ├── barber_products_data.xml       ← Produits/services de démo
│   └── barber_demo.xml                ← Données de démonstration
├── models/
│   ├── __init__.py
│   ├── barber_config.py               ← Configuration du salon
│   ├── barber_barber.py               ← Coiffeurs/Barbiers (employés)
│   ├── barber_contract.py             ← Contrats (loyer mensuel / %)
│   ├── barber_service.py              ← Prestations & tarifs
│   ├── barber_product.py              ← Produits consommables utilisés
│   ├── barber_session.py              ← Session POS (ouverture/fermeture)
│   ├── barber_order.py                ← Commandes/tickets
│   └── barber_order_line.py           ← Lignes de commande
├── report/
│   ├── barber_receipt_report.xml      ← Layout ticket de caisse
│   └── barber_daily_report.xml        ← Rapport journalier/mensuel
├── security/
│   ├── barber_security.xml            ← Groupes & règles d'accès
│   └── ir.model.access.csv
├── static/
│   ├── description/
│   │   ├── icon.png
│   │   └── banner.png
│   └── src/
│       ├── css/
│       │   └── barber_pos.css         ← Styles interface POS
│       └── js/
│           └── barber_pos.js          ← Logique POS côté client
├── views/
│   ├── barber_config_views.xml        ← Config salon
│   ├── barber_barber_views.xml        ← Gestion coiffeurs
│   ├── barber_contract_views.xml      ← Gestion contrats
│   ├── barber_service_views.xml       ← Gestion prestations
│   ├── barber_session_views.xml       ← Sessions POS
│   ├── barber_order_views.xml         ← Commandes & tickets
│   ├── barber_dashboard_views.xml     ← Dashboard KPIs
│   └── barber_menus.xml               ← Menu principal
└── wizard/
    ├── __init__.py
    ├── barber_payment_wizard.py       ← Wizard paiement
    ├── barber_payment_wizard_views.xml
    ├── barber_close_session_wizard.py ← Fermeture de session
    └── barber_close_session_views.xml
```

---

## Modèles de données

### `barber.config` — Configuration du Salon
| Champ | Type | Description |
|---|---|---|
| name | Char | Nom du salon |
| address | Char | Adresse |
| phone | Char | Téléphone |
| currency_id | Many2one | Devise |
| tax_rate | Float | Taux de TVA (%) |
| receipt_header | Text | En-tête du ticket |
| receipt_footer | Text | Pied de ticket |
| logo | Binary | Logo du salon |

### `barber.barber` — Coiffeurs
| Champ | Type | Description |
|---|---|---|
| name | Char | Nom complet |
| code | Char | Code unique (SEQ) |
| user_id | Many2one(res.users) | Compte utilisateur Odoo |
| phone | Char | Téléphone |
| email | Char | Email |
| photo | Binary | Photo |
| contract_ids | One2many | Contrats associés |
| active_contract_id | Many2one | Contrat actif |
| state | Selection | active / inactive |
| total_revenue | Float | (compute) CA total |
| commission_due | Float | (compute) Commission due |

### `barber.contract` — Contrats Coiffeurs
| Champ | Type | Description |
|---|---|---|
| barber_id | Many2one | Coiffeur concerné |
| contract_type | Selection | `rent` = Loyer mensuel / `percentage` = Pourcentage actes |
| monthly_rent | Float | Montant loyer mensuel (si type=rent) |
| percentage | Float | % du CA (si type=percentage) |
| date_start | Date | Début du contrat |
| date_end | Date | Fin du contrat (optionnel) |
| state | Selection | draft / active / expired |

### `barber.service` — Prestations
| Champ | Type | Description |
|---|---|---|
| name | Char | Libellé de la prestation |
| code | Char | Code court |
| category_id | Many2one | Catégorie (coiffure, barbe, soin…) |
| price | Float | Prix standard |
| duration | Integer | Durée estimée (minutes) |
| product_line_ids | One2many | Produits consommés |
| active | Boolean | Actif/Inactif |
| image | Binary | Icône |

### `barber.service.product` — Produits consommés par prestation
| Champ | Type | Description |
|---|---|---|
| service_id | Many2one | Prestation parente |
| product_id | Many2one(product.product) | Produit Odoo |
| qty | Float | Quantité utilisée |

### `barber.session` — Sessions POS
| Champ | Type | Description |
|---|---|---|
| name | Char | Nom session (SEQ) |
| barber_id | Many2one | Coiffeur de la session |
| date_open | Datetime | Heure ouverture |
| date_close | Datetime | Heure fermeture |
| state | Selection | open / closing / closed |
| order_ids | One2many | Commandes de la session |
| total_revenue | Float | (compute) CA session |
| cash_in | Float | Montant caisse ouverture |
| cash_out | Float | Montant caisse fermeture |

### `barber.order` — Commandes / Tickets
| Champ | Type | Description |
|---|---|---|
| name | Char | Numéro ticket (SEQ) |
| session_id | Many2one | Session POS |
| barber_id | Many2one | Coiffeur |
| date_order | Datetime | Date/heure |
| order_line_ids | One2many | Lignes |
| amount_total | Float | (compute) Total |
| payment_method | Selection | cash / card / mobile |
| state | Selection | draft / paid / cancelled |
| note | Text | Remarques |

### `barber.order.line` — Lignes de commande
| Champ | Type | Description |
|---|---|---|
| order_id | Many2one | Commande parente |
| service_id | Many2one | Prestation choisie |
| qty | Float | Quantité |
| unit_price | Float | Prix unitaire (override possible) |
| discount | Float | Remise % |
| subtotal | Float | (compute) Sous-total |

---

## Rôles et Permissions

| Groupe | Accès |
|---|---|
| `barber_pos.group_barber_manager` | Accès complet : config, contrats, rapports, toutes sessions |
| `barber_pos.group_barber_user` | Accès limité : ses sessions POS, ses commandes, ses gains |

---

## Fonctionnalités clés

### ✅ Phase 1 — Foundation (Modèles + Sécurité)
- [ ] `__manifest__.py`, `__init__.py`
- [ ] Modèles: barber, contract, service, session, order, order_line
- [ ] Séquences: commandes, sessions
- [ ] Sécurité: groupes, règles d'accès

### ✅ Phase 2 — Vues Backend
- [ ] Formulaires et listes: Coiffeurs, Contrats, Prestations
- [ ] Vue Session POS (tableau de bord coiffeur)
- [ ] Vue Commandes & tickets
- [ ] Menus complets (Admin vs Coiffeur)

### ✅ Phase 3 — Interface POS
- [ ] Page POS interactive (sélection prestation → panier → paiement)
- [ ] Calcul automatique commissions
- [ ] Ticket de caisse imprimable

### ✅ Phase 4 — Dashboard & Rapports
- [ ] Dashboard Admin: KPIs, graphiques CA, commissions dues
- [ ] Rapport journalier par coiffeur
- [ ] Rapport mensuel: loyers vs pourcentages

### ✅ Phase 5 — Données de démo & Polish

---

## Plan de vérification

1. Installer le module dans Odoo (`-i barber_pos`)
2. Tester les rôles: login Admin vs login Coiffeur
3. Créer une prestation, ouvrir une session, enregistrer une commande, payer
4. Vérifier le calcul de commission (% et loyer)
5. Générer le rapport journalier

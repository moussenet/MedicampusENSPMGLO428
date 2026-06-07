# MediCampus — Plateforme de Gestion des Visites Médicales

<div align="center">

![Django](https://img.shields.io/badge/Django-4.2-0A1931?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.14-1A4A8A?style=for-the-badge&logo=python&logoColor=white)
![MariaDB](https://img.shields.io/badge/MariaDB-10.x-1B8A5A?style=for-the-badge&logo=mariadb&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)

**Plateforme web de gestion des visites médicales pour l'ENSPM Maroua**

*Cours GLO428 — Génie Logiciel · Université de Maroua · 2025–2026*

</div>

---

## Table des matières

- [Présentation](#présentation)
- [Fonctionnalités](#fonctionnalités)
- [Stack technique](#stack-technique)
- [Architecture du projet](#architecture-du-projet)
- [Modèle de données](#modèle-de-données)
- [Installation](#installation)
- [Configuration](#configuration)
- [Lancement](#lancement)
- [Comptes de test](#comptes-de-test)
- [Structure des dossiers](#structure-des-dossiers)
- [Contributeurs](#contributeurs)

---

## Présentation

MediCampus centralise l'organisation des visites médicales annuelles des étudiants de l'ENSPM. Elle couvre l'intégralité du processus : planification des périodes, prise de rendez-vous en ligne, saisie des résultats médicaux par le personnel soignant, consultation des résultats par les étudiants et génération de rapports pour l'administration.

---

## Fonctionnalités

### Super-administrateur
- Création des comptes administrateur et médecin
- Activation / désactivation des comptes
- Génération de codes de validation ENSPM

### Administrateur
- Création et gestion des périodes de visite médicale
- Attribution d'un médecin et d'un département à chaque période
- Génération automatique des créneaux horaires (1h par créneau)
- Import des listes d'étudiants par fichier CSV
- Tableau de bord : statistiques présents / absents / aptes / inaptes
- Consultation des rapports médicaux soumis par le personnel médical

### Personnel médical
- Consultation des rendez-vous du jour (filtrés par période assignée)
- Validation de la présence des étudiants (présent / absent)
- Saisie des résultats médicaux :
  - Constantes : tension artérielle, poids, taille, IMC (calculé automatiquement), glycémie
  - Tests rapides (TDR) : paludisme, typhoïde, VIH
  - Analyses : selles, urinaire
  - Observations et recommandations
  - Statut d'aptitude : apte / apte avec réserves / inapte temporaire / inapte
- Soumission d'un rapport général à l'administrateur en fin de période

### Étudiant
- Consultation des périodes disponibles pour son département
- Prise de rendez-vous en ligne avec choix du créneau
- Annulation d'un rendez-vous confirmé
- Consultation des résultats médicaux
- Réception de notifications : confirmation RDV, rappels, résultats disponibles

---

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| Backend | Django 4.2 — Python 3.14 |
| Base de données | MariaDB 10.x (XAMPP) |
| ORM | Django ORM — MySQLdb |
| Frontend | Bootstrap 5.3 — DM Sans — Bootstrap Icons |
| Authentification | Django Auth — EmailBackend personnalisé |
| Serveur de développement | WSGIServer Django — port 8000 |
| Environnement | Python venv — Windows 10 — XAMPP |

---

## Architecture du projet

L'application suit le patron MVT (Modèle-Vue-Template) de Django, organisée en 5 modules indépendants :

```
medicampus/
├── accounts/        # Authentification, rôles, dashboards par profil
├── periodes/        # Gestion des périodes et créneaux de visite
├── rendezvous/      # Prise de RDV et validation des présences
├── resultats/       # Saisie médicale et rapports
├── notifications/   # Alertes et rappels aux étudiants
└── medicampus/      # Configuration globale (settings, urls, wsgi)
```

### Flux principal

```
Administrateur
    │
    ├─► Crée une période de visite (département + médecin + dates)
    │       └─► Créneaux générés automatiquement
    │
    ├─► Importe la liste des étudiants (CSV)
    │
Étudiant
    ├─► Consulte les périodes disponibles pour son département
    ├─► Choisit un créneau et confirme son RDV
    │       └─► Notification de confirmation générée
    │
Personnel médical (le jour J)
    ├─► Consulte les RDV du jour
    ├─► Valide la présence (présent / absent)
    ├─► Saisit les résultats médicaux
    │       └─► Notification "résultat disponible" envoyée à l'étudiant
    └─► Soumet un rapport général à l'administrateur
    │
Étudiant
    └─► Consulte et télécharge ses résultats
```

---

## Modèle de données

```
accounts_user
    │ 1
    │ ├─────────────────────────────────────────┐
    │ ▼ (medecin)                               │ (etudiant / cree_par)
periodes_visite                            rendezvous
    │ 1                                         │
    │                                           │
    ▼ N                                         │
creneaux ◄─────────────────────────────────────┘
                                                │
                                                ▼
                                      resultats_medicaux
                                                │
                                                ▼
                                      rapports_medicaux

accounts_user ──► notifications
```

### Tables principales

| Table | Description |
|-------|-------------|
| `accounts_user` | Tous les utilisateurs (rôles : superadmin, admin, medecin, etudiant) |
| `periodes_visite` | Périodes de visite avec médecin et département assignés |
| `creneaux` | Créneaux horaires générés automatiquement par période |
| `rendezvous` | RDV étudiant/créneau avec statut de présence |
| `resultats_medicaux` | Résultats complets : constantes, TDR, analyses, aptitude |
| `rapports_medicaux` | Rapport synthétique du médecin à l'administrateur |
| `notifications` | Alertes générées automatiquement par les événements |
| `codes_validation_enspm` | Codes pour valider la création de comptes administrateur |

---

## Installation

### Prérequis

- Python 3.10+
- XAMPP (MariaDB + phpMyAdmin)
- Git

### Étapes

**1. Cloner le dépôt**

```bash
git clone https://github.com/<organisation>/MedicampusENSPMGLO428.git
cd MedicampusENSPMGLO428
```

**2. Créer et activer l'environnement virtuel**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

**3. Installer les dépendances**

```bash
pip install django==4.2 mysqlclient pillow python-decouple
```

**4. Créer la base de données**

Démarrer XAMPP (MySQL), puis dans phpMyAdmin :

```sql
CREATE DATABASE medicampus_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```

**5. Créer un utilisateur dédié (recommandé)**

```sql
CREATE USER 'medicampus_user'@'localhost' IDENTIFIED BY 'votre_mot_de_passe';
GRANT SELECT, INSERT, UPDATE, DELETE ON medicampus_db.* TO 'medicampus_user'@'localhost';
FLUSH PRIVILEGES;
```

---

## Configuration

**1. Copier le fichier d'exemple**

```bash
cp .env.example .env
```

**2. Remplir le fichier `.env`**

```env
SECRET_KEY=remplacer_par_une_cle_secrete_longue
DEBUG=True
DB_NAME=medicampus_db
DB_USER=medicampus_user
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=3306
```

**3. Appliquer les migrations**

```bash
cd medicampus
python manage.py migrate
```

**4. Créer le super-administrateur**

```bash
python manage.py createsuperuser
```

**5. Collecter les fichiers statiques**

```bash
python manage.py collectstatic
```

---

## Lancement

```bash
python manage.py runserver
```

Accéder à l'application : [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Comptes de test

| Rôle | Email | Mot de passe |
|------|-------|--------------|
| Super-admin | superadmin@medicampus.cm | (défini à la création) |
| Administrateur | admin@enspm.cm | (défini par le superadmin) |
| Médecin | medecin@enspm.cm | (défini par le superadmin) |
| Étudiant | etudiant@gmail.com | (auto-inscription) |

> Les étudiants s'inscrivent eux-mêmes via `/accounts/register/`

---

## Structure des dossiers

```
medicampus/
│
├── accounts/
│   ├── models.py          # Modèle User personnalisé (AbstractUser)
│   ├── views.py           # Login, register, dashboards par rôle
│   ├── urls.py
│   ├── forms.py
│   ├── backends.py        # Authentification par email
│   └── templates/accounts/
│       ├── base.html
│       ├── login.html
│       ├── register.html
│       ├── superadmin_dashboard.html
│       ├── admin_dashboard.html
│       ├── medecin_dashboard.html
│       └── etudiant_dashboard.html
│
├── periodes/
│   ├── models.py          # PeriodeVisite, Creneau, EtudiantImporte
│   ├── views.py           # CRUD périodes, import CSV
│   ├── forms.py
│   ├── urls.py
│   └── templates/periodes/
│       ├── liste.html
│       ├── form.html
│       ├── detail.html
│       └── import_csv.html
│
├── rendezvous/
│   ├── models.py          # RendezVous
│   ├── views.py           # Prise RDV, validation présence
│   ├── urls.py
│   └── templates/rendezvous/
│       ├── periodes_disponibles.html
│       ├── confirmer_rdv.html
│       └── mes_rendezvous.html
│
├── resultats/
│   ├── models.py          # ResultatMedical, RapportMedical
│   ├── views.py           # Saisie résultats, rapport général
│   ├── forms.py
│   ├── urls.py
│   └── templates/resultats/
│       ├── rdv_du_jour.html
│       ├── saisir_resultat.html
│       ├── rapport_general.html
│       └── detail_etudiant.html
│
├── notifications/
│   ├── models.py          # Notification
│   └── views.py
│
├── medicampus/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── static/                # Fichiers statiques sources
├── staticfiles/           # Fichiers statiques collectés
├── media/                 # Uploads
├── manage.py
└── .env.example
```

---

## Contributeurs

| Nom | Rôle |
|-----|------|
| Eneta Moussa Christophe Le Jollec | Architecture, authentification, backend |
| Terdam Valentin | Administration, périodes |
| superadmin | creation compte admin, personnel medical |

---

## Licence

Projet académique — ENSPM Maroua · GLO428 · 2025–2026

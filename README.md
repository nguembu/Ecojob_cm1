
# 🌱 EcoJob CM

> **Une plateforme web RESTful pour connecter les jeunes du Cameroun aux opportunités d'emplois verts.**

---

## 📘 Présentation

**EcoJob CM** est une application web backend (API REST) développée avec **Django** et **Django REST Framework**, qui permet de :

- Créer et gérer des **offres d’emploi dans le domaine de l’économie verte** (recruteurs)
- Enregistrer des **collectes de déchets** (collecteurs)
- Consulter les **types de déchets disponibles** (acheteurs)
- Authentifier les utilisateurs avec **JWT** (via SimpleJWT)

Le projet s'inscrit dans un contexte de **valorisation des déchets** et de **lutte contre le chômage des jeunes au Cameroun**.

---

## 🚀 Fonctionnalités principales

### 🔐 Authentification
- Inscription par rôle (recruteur, collecteur, acheteur)
- Connexion via JWT token (SimpleJWT)
- Vue `/api/user/me/` pour récupérer les infos du user connecté

### 🧑‍💼 Recruteur
- Création / modification / suppression d'offres d’emploi (`JobOffer`)
- Filtres sur `location`, `contract_type`, `company`
- Affichage de toutes les candidatures reçues (à venir)

### 🚮 Collecteur (à venir)
- Enregistrement de collectes (`WasteCollect`)
- Visualisation des statistiques : quantité (kg), durée, revenu

### 🛒 Acheteur (à venir)
- Consultation des déchets disponibles
- Contact ou commande aux collecteurs

---

## 🛠️ Stack technique

| Composant       | Technologie                      |
|-----------------|----------------------------------|
| Backend         | Django 4.x, Django REST          |
| Authentification| JWT via SimpleJWT                |
| Base de données | SQLite (dev) / PostgreSQL (prod) |
| Documentation   | Swagger via drf-yasg             |
| Hébergement     | Render (ou Heroku)               |


---

## 📦 Installation locale (Linux / Ubuntu)

```bash
# 1. Cloner le dépôt
git clone https://github.com/nguembu/Ecojob_cm1.git
cd Ecojob_cm1
git checkout `nom_branche`  # Branche de travail

# 2. Créer et activer un environnement virtuel
python3 -m venv env
source env/bin/activate

# 3. Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt  # S'il existe
# Sinon :
pip install django djangorestframework djangorestframework-simplejwt drf-yasg

# 4. Appliquer les migrations
python manage.py makemigrations
python manage.py migrate

# 5. Créer un super utilisateur
python manage.py createsuperuser

# 6. Lancer le serveur
python manage.py runserver
```

---

## 📡 Endpoints de l’API (principaux)

| Méthode | URL                        | Description                            |
|---------|----------------------------|----------------------------------------|
| `POST`  | `/api/token/`              | Obtenir un JWT token (login)           |
| `POST`  | `/api/register/`           | Enregistrer un nouvel utilisateur      |
| `GET`   | `/api/user/me/`            | Infos du user connecté                 |
| `GET`   | `/api/offers/`             | Liste des offres d’emploi              |
| `POST`  | `/api/offers/`             | Créer une offre (recruteur uniquement) |
| `PUT`   | `/api/offers/<id>/`        | Modifier une offre                     |
| `DELETE`| `/api/offers/<id>/`        | Supprimer une offre                    |

---

## 📚 Swagger / Documentation API

Accès à la documentation interactive via Swagger :
```
http://localhost:8000/swagger/
```

---

## 🧪 Tests (à venir)

Tu peux exécuter les tests automatisés avec :

```bash
python manage.py test
```

---

## 👨‍💻 Équipe de développement

| Nom                     | Rôle                                            |
|-------------------------|-------------------------------------------------|
| **John NGUEMBU**        | Chef de projet / Fullstack                      |
| **Alain NGUEUDJANG**    | Développeur Backend (JobOffer API)              |
| **Ronel MAAMOC**        | Développeur Backend (Collecte, Paiement, Tests) |

---

## 📌 Roadmap

- [ ] Authentification JWT
- [x] API CRUD `JobOffer` (recruteur)
- [ ] API Collecte (collecteur)
- [ ] API Paiement / Statistiques
- [ ] Système de notification / chat
- [ ] Déploiement Render / Heroku

---

## 🔐 Sécurité

- Authentification JWT (access / refresh)
- Permissions par rôle (`IsRecruiter`, `IsCollector`, etc.)
- Données protégées en production via HTTPS

---

## 📄 Licence

Ce projet est sous licence MIT – voir le fichier `LICENSE` pour plus d'informations.

---

## ✉️ Contact

> Pour toute question, bug ou contribution :

- 📧 jaures.nguembu@facsciences-uy1.cm
- 📧 gildas.ngueudjang@facsciences-uy1.cm
- 📧 ronel.maamoc@facsciences-uy1.cm
- 💼 https://github.com/nguembu/Ecojob_cm1

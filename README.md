# FINOR - Backend de Gestion d'Investissements

FINOR est une plateforme de gestion d'investissements permettant la collecte de fonds, le suivi des dépenses par rubriques et l'analyse de l'impact des investissements.

## 🚀 Technologies utilisées

- **FastAPI** : Framework web Python moderne et performant.
- **PostgreSQL** : Base de données relationnelle.
- **SQLAlchemy (Async)** : ORM pour les interactions asynchrones avec la base de données.
- **Alembic** : Gestion des migrations de base de données.
- **Pydantic V2** : Validation de données et gestion des schémas.
- **JWT (JSON Web Tokens)** : Authentification sécurisée des trésoriers.
- **Pytest** : Suite de tests unitaires complets.

## 🛠️ Installation et Configuration

### 1. Cloner le projet
```bash
git clone https://github.com/PIO-VIA/FINOR_BACKEND.git
cd FINOR_BACKEND
```

### 2. Créer un environnement virtuel
```bash
python -m venv venv
source venv/bin/activate  # Sur Linux/macOS
# ou
.\venv\Scripts\activate   # Sur Windows
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement
Créez un fichier `.env` à la racine (utilisez `.env.example` comme modèle) :
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/finor_db
SECRET_KEY=votre_cle_secrete_tres_longue
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 5. Lancer les migrations
```bash
alembic upgrade head
```

### 6. Initialiser le compte Trésorier
```bash
python seed.py
```
*Identifiants par défaut : `admin@finor.com` / `admin123`*

## 🏃 Lancement de l'application

```bash
uvicorn app.main:app --reload
```
L'API sera accessible sur `http://localhost:8000`.
La documentation interactive (Swagger) est disponible sur `http://localhost:8000/docs`.

## 🧪 Tests

Pour lancer la suite de tests unitaires :
```bash
pytest
```

## 📖 Architecture de l'API

### Format des Réponses
Toutes les réponses suivent un format standardisé :
```json
{
  "code": 200,
  "message": "Description de l'action",
  "data": { ... }
}
```

### Rôles et Accès
- **Trésorier** : Accès complet via authentification JWT. Peut gérer les rubriques, valider les investissements, enregistrer les dépenses et transferts.
- **Investisseur** : Accès via son code personnel `INV-XXXX`. Peut déclarer des investissements, voir son historique et son impact.

## 📂 Structure du Projet

- `app/` : Code source de l'application.
  - `models/` : Modèles SQLAlchemy.
  - `schemas/` : Modèles Pydantic pour la validation.
  - `crud/` : Logique d'accès aux données.
  - `routers/` : Points d'entrée de l'API (Endpoints).
  - `dependencies/` : Dépendances FastAPI (Auth, DB).
- `alembic/` : Migrations de base de données.
- `tests/` : Suite de tests unitaires.
- `seed.py` : Script d'initialisation des données.

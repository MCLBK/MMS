# MMS Express

Plateforme SaaS intelligente de gestion, d'attribution et de suivi des livraisons en temps réel.

## Fonctionnalités principales

- **Gestion des commandes** — Création, suivi, machine à états avec 21 statuts et transitions validées
- **Attribution IA** — Scoring multicritère (7 facteurs) pour assigner automatiquement le meilleur livreur
- **Suivi GPS temps réel** — Carte Leaflet avec positions live, WebSocket pour mises à jour instantanées
- **Prédictions IA** — Estimation délais, prévision volumes, zones chaudes, analyse de risques
- **Assistant IA** — Chatbot opérateur (Ollama local + fallback templates) pour aide à la décision
- **Analytics** — Tableaux de bord, KPIs, graphiques (Recharts), tendances et répartitions
- **Multi-tenant** — Isolation par entreprise, RBAC 4 rôles (super_admin, company_admin, courier, customer)
- **Notifications temps réel** — WebSocket + système de notifications in-app
- **Audit trail** — Journalisation complète des actions pour traçabilité
- **Application mobile** — React Native CLI pour les livreurs (Android/iOS)

## Architecture

| Composant | Technologie | Dossier |
|-----------|------------|---------|
| Frontend Web | Next.js 14, React 18, TypeScript, Tailwind CSS | `frontend-web/` |
| Application Mobile | React Native CLI 0.75, TypeScript | `mobile/` |
| Backend API | Python 3.11+, FastAPI, SQLAlchemy 2.0 async | `backend/` |
| Base de données | PostgreSQL 16 | Docker |
| Cache / Sessions | Redis 7 | Docker |
| IA locale | Ollama (llama3.2:3b) | Optionnel |
| Reverse proxy | Nginx (production) | `infrastructure/` |

## Stack technique détaillée

### Backend (11 modules)
- **Auth** — JWT + refresh tokens, Argon2 password hashing
- **Users** — CRUD utilisateurs, profils
- **Companies** — Gestion multi-tenant
- **Delivery** — Commandes, items, state machine, attribution auto
- **Couriers** — Profils livreurs, statuts, positions
- **Notifications** — Système de notifications in-app
- **Analytics** — Dashboard stats, KPIs, séries temporelles
- **Tracking** — GPS historique, positions live
- **Audit** — Journal d'audit complet
- **AI** — Scoring v2, prédictions, assistant chatbot
- **WebSocket** — Temps réel (notifications, tracking, commandes)

### Frontend Web
- **Design System** — Outfit + DM Sans, palette Navy/Orange/Teal
- **Composants UI** — Modal, DataTable, StatCard, Select, Tabs, Textarea, Badge, Button, Card
- **React Query** — Data fetching avec cache et refetch automatique
- **Zustand** — State management (auth)
- **Recharts** — Graphiques (Line, Pie, Bar) chargés dynamiquement
- **Leaflet** — Carte GPS (import dynamique, SSR disabled)

### Sécurité
- Rate limiting (100 req/min par IP)
- Security headers (X-Frame-Options, CSP, XSS Protection, etc.)
- CORS configuré
- JWT avec expiration courte en production

## Prérequis

- **Node.js** 20+
- **Python** 3.11+
- **Docker** et **Docker Compose**
- **PostgreSQL** 16+ (ou via Docker)
- **Redis** 7+ (ou via Docker)

## Démarrage rapide

### 1. Cloner et configurer

```bash
git clone <repo-url> mms-express
cd mms-express

# Configurer les variables d'environnement
cp backend/.env.example backend/.env
cp frontend-web/.env.example frontend-web/.env.local
```

### 2. Lancer avec Docker Compose (développement)

```bash
docker-compose up -d
```

Cela démarre PostgreSQL, Redis et le backend API avec hot reload.

### 3. Frontend Web

```bash
cd frontend-web
npm install
npm run dev
```

Accessible sur `http://localhost:3000`

### 4. Backend seul (sans Docker)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"
alembic upgrade head
python -m src.main
```

API : `http://localhost:8000`
Documentation Swagger : `http://localhost:8000/docs`

### 5. Application Mobile

```bash
cd mobile
npm install

# Android
npx react-native run-android

# iOS (macOS uniquement)
cd ios && pod install && cd ..
npx react-native run-ios
```

## Déploiement production

```bash
# Configurer les secrets
cp backend/.env.production backend/.env
# Modifier SECRET_KEY, FIRST_ADMIN_PASSWORD, CORS_ORIGINS, etc.

# Lancer la stack complète
docker-compose -f docker-compose.prod.yml up -d --build
```

La stack production inclut :
- **Nginx** reverse proxy (port 80) avec headers sécurité
- **Backend** FastAPI (2 workers uvloop)
- **Frontend** Next.js standalone
- **PostgreSQL** avec persistance
- **Redis** avec persistence AOF

## Tests

```bash
cd backend
pip install -e ".[dev]"
pytest -v
```

## Endpoints API principaux

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/auth/login` | Authentification |
| POST | `/api/auth/refresh` | Rafraîchir le token |
| GET | `/api/companies/{id}/orders` | Lister les commandes |
| POST | `/api/companies/{id}/orders` | Créer une commande |
| POST | `/api/companies/{id}/orders/{id}/transition` | Changer le statut |
| POST | `/api/companies/{id}/orders/{id}/assign` | Attribution auto IA |
| GET | `/api/companies/{id}/couriers` | Lister les livreurs |
| GET | `/api/companies/{id}/analytics/dashboard` | Stats dashboard |
| GET | `/api/companies/{id}/tracking/live` | Positions GPS live |
| POST | `/api/companies/{id}/ai/scoring` | Scoring IA livreurs |
| POST | `/api/companies/{id}/ai/predict-time` | Prédiction délai |
| GET | `/api/companies/{id}/ai/forecast` | Prévision volume |
| GET | `/api/companies/{id}/ai/hot-zones` | Zones chaudes |
| POST | `/api/companies/{id}/ai/chat` | Assistant IA |
| WS | `/ws/notifications` | Notifications temps réel |
| WS | `/ws/tracking` | GPS temps réel |
| WS | `/ws/order/{id}` | Suivi commande live |

## Structure du projet

```
mms-express/
├── backend/                 # API FastAPI
│   ├── src/
│   │   ├── ai/              # IA : scoring, prédictions, assistant
│   │   ├── analytics/       # Service analytics
│   │   ├── auth/            # Authentification JWT
│   │   ├── companies/       # Gestion entreprises
│   │   ├── core/            # Config, sécurité, dépendances
│   │   ├── couriers/        # Gestion livreurs
│   │   ├── database/        # Models, session, migrations
│   │   ├── delivery/        # Commandes, attribution, state machine
│   │   ├── guards/          # RBAC, tenant isolation
│   │   ├── middlewares/     # Rate limiting, sécurité
│   │   ├── notifications/   # Système notifications
│   │   ├── tracking/        # GPS tracking
│   │   ├── users/           # Gestion utilisateurs
│   │   ├── websockets/      # Temps réel WS
│   │   └── main.py          # Point d'entrée FastAPI
│   └── tests/               # Tests unitaires et intégration
├── frontend-web/            # Application Next.js 14
│   └── src/
│       ├── app/             # Pages (App Router)
│       ├── components/ui/   # Design system
│       ├── hooks/           # React Query hooks
│       ├── services/        # Client API
│       ├── store/           # Zustand auth
│       ├── types/           # TypeScript types
│       └── constants/       # Labels, variantes
├── mobile/                  # React Native CLI
│   └── src/
│       ├── screens/         # Écrans
│       ├── navigation/      # React Navigation
│       ├── services/        # API client
│       ├── store/           # Zustand auth
│       └── theme/           # Design system mobile
├── infrastructure/          # Docker, Nginx
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
├── docker-compose.yml       # Développement
└── docker-compose.prod.yml  # Production
```

## Compte admin par défaut

- **Email** : admin@mmsexpress.com
- **Mot de passe** : Admin123!

> Changez ces identifiants immédiatement en production.

## Licence

Projet privé — Tous droits réservés.

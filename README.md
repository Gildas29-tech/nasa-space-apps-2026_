# FieldShift - Plateforme d'analyse agricole intelligente

> **Comprendre son exploitation. Anticiper les risques. Adapter ses cultures.**

FieldShift est une application web progressive (PWA) qui centralise des données satellitaires, climatiques et agricoles pour les transformer en informations compréhensibles et en recommandations d'aide à la décision pour les exploitants agricoles.

## 🌟 Fonctionnalités principales

| Module | Description |
|--------|-------------|
| **AgriTwin** | Gestion des exploitations : création, délimitation parcellaire sur carte, caractéristiques culturales |
| **HarvestVision** | Surveillance végétale via NDVI (Sentinel-2, Landsat) avec séries temporelles et comparaisons |
| **FarmGuardian** | Détection automatique des risques : déficit pluviométrique, sécheresse, stress hydrique, gel |
| **WaterWise** | Analyse des ressources en eau : précipitations, humidité des sols (SMAP), bilan hydrique |
| **CropShift** | Comparaison multi-cultures selon adéquation pédoclimatique, planification rotations |
| **Global Farm Resilience** | Génération de diagnostics complets exportables en PDF |

## 🏗️ Architecture technique

```
┌─────────────────┐     ┌─────────────────┐     ┌────────────────────────────┐
│   Frontend      │────▶│   Backend       │────▶│   Sources de données       │
│   (React+Vite)  │     │   (FastAPI)     │     │   NASA POWER, Sentinel-2,  │
│   PWA + Leaflet │     │   Python 3.11+  │     │   Landsat, SMAP, GAEZ,     │
│   Recharts      │     │   Pandas/NumPy  │     │   GPM, SRTM, GLDAS         │
└─────────────────┘     └─────────────────┘     └────────────────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Supabase      │
                       │   (PostgreSQL)  │
                       │   Auth + Storage│
                       └─────────────────┘
```

### Frontend
- **React 18** + **Vite** + **JavaScript** (pas de TypeScript)
- **React Router** pour la navigation
- **Leaflet** + **React-Leaflet** pour les cartes interactives
- **Recharts** pour les graphiques
- **PWA** : installation, cache offline, sync background

### Backend
- **FastAPI** (Python 3.11+)
- **HTTPX** pour appels API externes asynchrones
- **Pandas/NumPy** pour traitements numériques
- **GeoPandas/Rasterio** pour données géospatiales
- **Scikit-learn** pour modèles prédictifs futurs

### Sources de données
| Source | Type | Utilisation |
|--------|------|-------------|
| NASA POWER | API REST | Température, précipitations, rayonnement, humidité |
| ESA Sentinel-2 | Catalogue géospatial | NDVI haute résolution (10m) |
| NASA Landsat | Catalogue géospatial | NDVI historique (30m) |
| NASA SMAP | API REST | Humidité des sols |
| NASA GPM IMERG | API REST | Précipitations satellitaires |
| FAO GAEZ | Portail scientifique | Aptitude des terres, potentiel cultural |
| NASA SRTM | API REST | Modèle numérique de terrain |
| NASA GLDAS | API REST | Variables hydrologiques |

## 🚀 Démarrage rapide

### Prérequis
- Node.js 18+ et npm
- Python 3.11+
- (Optionnel) Compte Supabase pour la persistance

### Installation Frontend
```bash
cd frontend
npm install
npm run dev
```
L'application sera accessible sur http://localhost:5173

### Installation Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Éditer .env avec vos clés API si nécessaire
uvicorn app.main:app --reload
```
L'API sera accessible sur http://localhost:8000
Documentation Swagger : http://localhost:8000/docs

### Variables d'environnement Backend (.env)
```env
# NASA POWER - Pas de clé requise pour usage de base
NASA_POWER_BASE_URL=https://power.larc.nasa.gov/api/temporal/daily/point

# Supabase (optionnel)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

# Sentinel Hub (optionnel - pour vraies images satellitaires)
SENTINEL_HUB_CLIENT_ID=your-id
SENTINEL_HUB_CLIENT_SECRET=your-secret
```

## 📁 Structure du projet

```
FieldShift/
├── frontend/                 # Application React PWA
│   ├── public/              # Assets statiques, manifest PWA
│   ├── src/
│   │   ├── components/      # Composants réutilisables (Layout, etc.)
│   │   ├── pages/           # Pages (Home, Dashboard, Farms, Monitoring, Crops, Reports, Settings)
│   │   ├── App.jsx          # Routes principales
│   │   ├── main.jsx         # Point d'entrée
│   │   └── index.css        # Design system (CSS variables)
│   ├── package.json
│   └── vite.config.js       # Config Vite + PWA plugin
│
├── backend/                  # API FastAPI
│   ├── app/
│   │   ├── api/             # Routes API par module
│   │   │   ├── health.py    # Health checks
│   │   │   ├── farms.py     # CRUD exploitations
│   │   │   ├── climate.py   # NASA POWER integration
│   │   │   ├── vegetation.py # NDVI, Sentinel-2
│   │   │   ├── crops.py     # Comparaison cultures, rotations
│   │   │   └── reports.py   # Génération rapports PDF
│   │   ├── config.py        # Configuration Pydantic
│   │   └── main.py          # App FastAPI + lifespan
│   ├── requirements.txt
│   └── .env.example
│
└── README.md
```

## 🎨 Design System

Le design suit les principes du cahier des charges :
- **Couleur primaire** : Vert profond `#1B4D2E` (agriculture, fiabilité)
- **Fond** : Blanc cassé `#F5F8F5` (confort lecture)
- **Typographie** : Inter (lisibilité, professionnalisme)
- **Approche** : Mobile-first, accessible, épuré

### Thème sombre
Support natif via `prefers-color-scheme` et toggle manuel.

## 📱 PWA - Installation

L'application peut être installée :
- **Desktop** : Chrome/Edge "Installer l'application"
- **Mobile** : "Ajouter à l'écran d'accueil"
- **Fonctionne hors ligne** : Consultation données cachées, sync à la reconnexion

## 🔬 Principes scientifiques

1. **Transparence** : Chaque indicateur cite source, unité, période, résolution, confiance
2. **Humilité** : Estimations satellitaires ≠ mesures terrain directes
3. **Pas de diagnostic automatique** : Baisse NDVI = signal, pas maladie
4. **Harmonisation** : Pas de mélange données résolutions/périodes différentes sans traitement
5. **Contexte local** : Recommandations adaptées à la zone géographique
6. **Validation humaine** : Décisions importantes = expertise agronome

## 🗺️ Portée internationale

- Coordonnées géographiques mondiales (WGS84)
- Unités métriques/imperiales configurables
- Sources NASA/ESA/FAO à couverture globale
- Calendriers agricoles par hémisphère
- Pas de dépendance services exclusivement américains

## 🧪 Tests

```bash
# Frontend
cd frontend
npm run lint

# Backend
cd backend
pytest  # (à configurer)
```

## 📦 Build Production

```bash
# Frontend
cd frontend
npm run build
# Sortie dans dist/

# Backend
cd backend
# Utiliser uvicorn avec workers en production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🛣️ Roadmap (Post-MVP)

### Phase 1 - MVP ✅ (en cours)
- [x] Page d'accueil professionnelle
- [x] Dashboard avec indicateurs climatiques
- [x] Gestion exploitations + carte Leaflet
- [x] API NASA POWER (températures, précipitations)
- [x] NDVI mock + série temporelle
- [x] Comparaison cultures avec scoring
- [x] Génération rapports (structure)
- [x] PWA installable

### Phase 2 - Données réelles
- [ ] Intégration Sentinel Hub / Google Earth Engine pour vraies images NDVI
- [ ] NASA SMAP humidité sols
- [ ] NASA GPM IMERG précipitations
- [ ] FAO GAEZ potentiel cultural

### Phase 3 - Intelligence avancée
- [ ] Modèles prédictifs rendements (scikit-learn)
- [ ] Simulation scénarios climatiques
- [ ] Notifications push alertes
- [ ] Mode collaboratif coopératives

### Phase 4 - Écosystème
- [ ] API publique pour partenaires
- [ ] Intégration données locales (chambres agriculture, météo nationale)
- [ ] Application mobile native (Capacitor)

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit (`git commit -m 'Ajout nouvelle fonctionnalité'`)
4. Push (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrir une Pull Request

## 📄 Licence

Projet privé - Tous droits réservés.

## 📞 Contact

- **Support** : support@fieldshift.app
- **Documentation** : docs.fieldshift.app
- **Auteur** : Équipe FieldShift

---

*FieldShift ne doit pas seulement montrer la situation d'une exploitation. Il doit aider à comprendre ce qui se passe, pourquoi cela se produit et quelles décisions peuvent être envisagées.*
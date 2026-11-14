import { Link } from 'react-router-dom'
import {
  MapPin,
  Eye,
  Leaf,
  AlertTriangle,
  Droplets,
  RefreshCw,
  FileText,
  ArrowRight,
  CheckCircle,
  Globe,
  Shield,
  Zap
} from 'lucide-react'
import './Home.css'

const features = [
  {
    icon: MapPin,
    title: 'AgriTwin - Gestion des exploitations',
    description: 'Créez et délimitez vos parcelles sur une carte interactive. Enregistrez la superficie, le type de culture et les informations sur le sol.',
  },
  {
    icon: Eye,
    title: 'HarvestVision - Surveillance végétale',
    description: 'Suivez l\'évolution de la végétation via les indices NDVI issus d\'images satellitaires Sentinel-2 et Landsat. Comparez différentes périodes.',
  },
  {
    icon: AlertTriangle,
    title: 'FarmGuardian - Détection des risques',
    description: 'Identifiez automatiquement les déficits de précipitations, sécheresses, excès de pluie, stress hydrique et dégradations végétales.',
  },
  {
    icon: Droplets,
    title: 'WaterWise - Ressources en eau',
    description: 'Analysez les précipitations, l\'humidité des sols (NASA SMAP) et les périodes sèches pour anticiper les risques hydriques.',
  },
  {
    icon: Leaf,
    title: 'CropShift - Comparaison cultures',
    description: 'Comparez l\'adéquation de plusieurs cultures selon vos conditions climatiques, pédologiques et les risques identifiés.',
  },
  {
    icon: FileText,
    title: 'Global Farm Resilience - Diagnostics',
    description: 'Générez des rapports complets de diagnostic et de plan d\'adaptation, exportables en PDF avec sources et niveaux de confiance.',
  },
]

const benefits = [
  { icon: Globe, title: 'Portée internationale', text: 'Fonctionne dans tous les pays avec des sources de données mondiales (NASA, ESA, FAO).' },
  { icon: Shield, title: 'Données scientifiques', text: 'Basé sur des sources ouvertes documentées : NASA POWER, Sentinel-2, Landsat, FAO GAEZ, SRTM.' },
  { icon: Zap, title: 'Application progressive (PWA)', text: 'Installable sur mobile et desktop, fonctionne hors connexion pour la consultation des données locales.' },
  { icon: CheckCircle, title: 'Transparence scientifique', text: 'Chaque indicateur cite sa source, son unité, sa période, sa résolution et son niveau de confiance.' },
]

export default function Home() {
  return (
    <div className="home-page">
      <header className="hero">
        <div className="hero-content">
          <div className="hero-badge">
            <span className="badge badge-success">Version 2.0 - MVP</span>
          </div>
          <h1 className="hero-title">
            FieldShift
            <br />
            <span className="hero-title-accent">Comprendre son exploitation.</span>
            <br />
            <span className="hero-title-accent">Anticiper les risques.</span>
            <br />
            <span className="hero-title-accent">Adapter ses cultures.</span>
          </h1>
          <p className="hero-subtitle">
            Plateforme intelligente d\'analyse agricole et d\'adaptation climatique grâce aux données satellitaires et environnementales.
          </p>
          <div className="hero-actions">
            <Link to="/dashboard" className="btn btn-primary btn-lg">
              Accéder à l'application
              <ArrowRight size={20} aria-hidden="true" />
            </Link>
            <Link to="/farms" className="btn btn-secondary btn-lg">
              Découvrir les fonctionnalités
            </Link>
          </div>
          <div className="hero-trust">
            <div className="trust-item">
              <CheckCircle size={16} aria-hidden="true" />
              <span>Données NASA & ESA officielles</span>
            </div>
            <div className="trust-item">
              <CheckCircle size={16} aria-hidden="true" />
              <span>Open source & transparente</span>
            </div>
            <div className="trust-item">
              <CheckCircle size={16} aria-hidden="true" />
              <span>Conçue pour l\'agriculteur</span>
            </div>
          </div>
        </div>
        <div className="hero-visual" aria-hidden="true">
          <div className="map-preview">
            <div className="map-layer map-base"></div>
            <div className="map-layer map-ndvi"></div>
            <div className="map-layer map-parcel"></div>
            <div className="map-markers">
              <div className="map-marker" style={{ top: '35%', left: '45%' }}></div>
              <div className="map-marker" style={{ top: '60%', left: '70%' }}></div>
              <div className="map-marker" style={{ top: '25%', left: '75%' }}></div>
            </div>
            <div className="map-legend">
              <div className="legend-item">
                <span className="legend-color ndvi"></span>
                <span>NDVI élevé</span>
              </div>
              <div className="legend-item">
                <span className="legend-color parcel"></span>
                <span>Parcelle</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <section className="features" aria-labelledby="features-title">
        <div className="container">
          <header className="section-header">
            <h2 id="features-title">Fonctionnalités principales</h2>
            <p>Six modules intégrés pour une vision complète de votre exploitation</p>
          </header>
          <div className="features-grid">
            {features.map((feature, index) => (
              <article key={index} className="feature-card">
                <div className="feature-icon">
                  <feature.icon size={24} aria-hidden="true" />
                </div>
                <h3 className="feature-title">{feature.title}</h3>
                <p className="feature-description">{feature.description}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="benefits" aria-labelledby="benefits-title">
        <div className="container">
          <header className="section-header">
            <h2 id="benefits-title">Pourquoi choisir FieldShift ?</h2>
            <p>Une plateforme conçue pour la rigueur scientifique et la simplicité d\'usage</p>
          </header>
          <div className="benefits-grid">
            {benefits.map((benefit, index) => (
              <article key={index} className="benefit-card">
                <div className="benefit-icon">
                  <benefit.icon size={24} aria-hidden="true" />
                </div>
                <h3 className="benefit-title">{benefit.title}</h3>
                <p className="benefit-text">{benefit.text}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="data-sources" aria-labelledby="sources-title">
        <div className="container">
          <header className="section-header">
            <h2 id="sources-title">Sources de données utilisées</h2>
            <p>Des sources ouvertes, documentées et internationalement reconnues</p>
          </header>
          <div className="sources-grid">
            <div className="source-card">
              <h3>NASA POWER</h3>
              <p>Température, précipitations, humidité, rayonnement solaire</p>
              <span className="source-tag">API directe</span>
            </div>
            <div className="source-card">
              <h3>ESA Sentinel-2</h3>
              <p>Images multispectrales 10m - Surveillance végétation détaillée</p>
              <span className="source-tag">Catalogue géospatial</span>
            </div>
            <div className="source-card">
              <h3>NASA Landsat</h3>
              <p>Images multispectrales 30m - Historique long terme</p>
              <span className="source-tag">Catalogue géospatial</span>
            </div>
            <div className="source-card">
              <h3>NASA SMAP</h3>
              <p>Humidité de surface et du sol - Analyse hydrique</p>
              <span className="source-tag">API directe</span>
            </div>
            <div className="source-card">
              <h3>NASA GPM IMERG</h3>
              <p>Précipitations satellitaires - Surveillance pluies</p>
              <span className="source-tag">API directe</span>
            </div>
            <div className="source-card">
              <h3>FAO GAEZ</h3>
              <p>Aptitude des terres et potentiel agricole - Comparaison cultures</p>
              <span className="source-tag">Portail scientifique</span>
            </div>
            <div className="source-card">
              <h3>NASA SRTM</h3>
              <p>Élévation et relief - Analyse du terrain</p>
              <span className="source-tag">API directe</span>
            </div>
            <div className="source-card">
              <h3>NASA GLDAS</h3>
              <p>Variables hydrologiques et terrestres - Contexte environnemental</p>
              <span className="source-tag">API directe</span>
            </div>
          </div>
        </div>
      </section>

      <footer className="footer">
        <div className="container">
          <p>FieldShift - Plateforme d\'analyse agricole intelligente</p>
          <p className="footer-note">
            Les analyses constituent une aide à la décision et non une prescription agronomique définitive.
            Validation humaine recommandée pour les décisions importantes.
          </p>
        </div>
      </footer>
    </div>
  )
}
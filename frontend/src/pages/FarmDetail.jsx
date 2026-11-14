import { useState, useEffect, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { MapContainer, TileLayer, Polygon, Marker, Popup, useMap } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import {
  ArrowLeft,
  MapPin,
  Leaf,
  Calendar,
  AlertTriangle,
  Sun,
  CloudRain,
  Droplets,
  TrendingUp,
  TrendingDown,
  Download,
  Edit,
  MoreVertical,
  RefreshCw
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import './FarmDetail.css'

const mockFarm = {
  id: 1,
  name: 'Exploitation Demo',
  region: 'Nouvelle-Aquitaine, France',
  coordinates: { lat: 45.75, lng: -0.63 },
  area: 42.5,
  crop: 'Blé tendre',
  soilType: 'Argilo-calcaire',
  createdAt: '2024-03-15',
  lastAnalysis: '2025-01-15',
  status: 'active',
  alerts: 2,
  parcelCoords: [
    [45.748, -0.635],
    [45.752, -0.635],
    [45.752, -0.625],
    [45.748, -0.625],
    [45.748, -0.635],
  ],
}

const mockClimateData = [
  { month: 'Jan', temp: 8.2, rain: 65, ndvi: 0.32 },
  { month: 'Fév', temp: 9.1, rain: 52, ndvi: 0.35 },
  { month: 'Mar', temp: 12.5, rain: 48, ndvi: 0.48 },
  { month: 'Avr', temp: 15.8, rain: 58, ndvi: 0.62 },
  { month: 'Mai', temp: 19.2, rain: 72, ndvi: 0.75 },
  { month: 'Juin', temp: 22.8, rain: 55, ndvi: 0.81 },
  { month: 'Juil', temp: 25.4, rain: 42, ndvi: 0.78 },
  { month: 'Aoû', temp: 25.1, rain: 48, ndvi: 0.72 },
  { month: 'Sep', temp: 21.5, rain: 62, ndvi: 0.65 },
  { month: 'Oct', temp: 16.8, rain: 78, ndvi: 0.52 },
  { month: 'Nov', temp: 11.2, rain: 71, ndvi: 0.41 },
  { month: 'Déc', temp: 8.5, rain: 68, ndvi: 0.34 },
]

const mockIndicators = [
  { label: 'Température moyenne', value: '12.4°C', trend: '+0.8°C', trendType: 'up', unit: 'vs norme 30 ans', icon: Sun },
  { label: 'Cumul précipitations', value: '687 mm', trend: '-12%', trendType: 'down', unit: 'vs moyenne 30 ans', icon: CloudRain },
  { label: 'Humidité sol surface', value: '0.28 m³/m³', trend: 'Stable', trendType: 'neutral', unit: 'NASA SMAP', icon: Droplets },
  { label: 'NDVI moyen', value: '0.68', trend: '+0.04', trendType: 'up', unit: 'vs mois précédent', icon: Leaf },
]

const mockAlerts = [
  { id: 1, type: 'warning', title: 'Déficit pluviométrique', description: 'Cumul sur 30 jours inférieur de 35% à la normale saisonnière', date: '2025-01-15', confidence: 85, action: 'Surveiller l\'humidité du sol, envisager irrigation si disponible' },
  { id: 2, type: 'info', title: 'Températures élevées', description: '5 jours consécutifs > 30°C prévus selon modèles météo', date: '2025-01-14', confidence: 78, action: 'Éviter travaux au champ aux heures les plus chaudes' },
]

function MapComponent({ center, zoom, parcelCoords, readOnly = true }) {
  const mapRef = useRef(null)

  return (
    <MapContainer
      ref={mapRef}
      center={center}
      zoom={zoom}
      scrollWheelZoom={!readOnly}
      style={{ width: '100%', height: '100%' }}
      className="farm-map"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <Polygon
        positions={parcelCoords}
        color="#1B4D2E"
        fillColor="#4CAF50"
        fillOpacity={0.2}
        weight={2}
        dashArray="8, 4"
      />
      <Marker position={center}>
        <Popup>
          <strong>{mockFarm.name}</strong><br />
          {mockFarm.area} ha • {mockFarm.crop}
        </Popup>
      </Marker>
    </MapContainer>
  )
}

function MapFullScreen({ farm }) {
  const [mapCenter, setMapCenter] = useState([farm.coordinates.lat, farm.coordinates.lng])
  const [mapZoom, setMapZoom] = useState(14)

  const map = useMap()
  useEffect(() => {
    map.setView(mapCenter, mapZoom)
  }, [mapCenter, mapZoom, map])

  return null
}

export default function FarmDetail() {
  const { id } = useParams()
  const [activeTab, setActiveTab] = useState('overview')
  const [mapView, setMapView] = useState(false)

  const tabs = [
    { id: 'overview', label: 'Vue d\'ensemble', icon: MapPin },
    { id: 'climate', label: 'Climat', icon: Sun },
    { id: 'vegetation', label: 'Végétation', icon: Leaf },
    { id: 'risks', label: 'Risques', icon: AlertTriangle },
    { id: 'water', label: 'Eau', icon: Droplets },
  ]

  return (
    <div className="farm-detail">
      <div className="farm-header">
        <Link to="/farms" className="btn btn-ghost">
          <ArrowLeft size={18} aria-hidden="true" />
          Retour
        </Link>
        <div className="farm-header-info">
          <div className="farm-status">
            <span className={`status-badge ${mockFarm.status}`}>
              {mockFarm.status === 'active' ? 'Active' : 'Attention'}
            </span>
            {mockFarm.alerts > 0 && (
              <span className="alert-count">
                <AlertTriangle size={14} aria-hidden="true" />
                {mockFarm.alerts} alerte{mockFarm.alerts > 1 ? 's' : ''}
              </span>
            )}
          </div>
          <h1>{mockFarm.name}</h1>
          <p className="farm-location">
            <MapPin size={16} aria-hidden="true" />
            {mockFarm.region} • {mockFarm.area} ha • {mockFarm.crop}
          </p>
        </div>
        <div className="farm-header-actions">
          <button className="btn btn-secondary">
            <Edit size={18} aria-hidden="true" />
            Modifier
          </button>
          <button className="btn btn-primary">
            <Download size={18} aria-hidden="true" />
            Générer rapport
          </button>
        </div>
      </div>

      <div className="farm-tabs" role="tablist">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            role="tab"
            aria-selected={activeTab === tab.id}
            aria-controls={`${tab.id}-panel`}
            className={`tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <tab.icon size={16} aria-hidden="true" />
            {tab.label}
          </button>
        ))}
      </div>

      <div className="farm-content">
        {activeTab === 'overview' && (
          <div id="overview-panel" role="tabpanel">
            <div className="overview-grid">
              <section className="map-section card" aria-labelledby="map-title">
                <header className="card-header">
                  <h2 id="map-title">Localisation de la parcelle</h2>
                  <button className="btn btn-ghost btn-sm" onClick={() => setMapView(true)}>
                    <RefreshCw size={14} aria-hidden="true" />
                    Plein écran
                  </button>
                </header>
                <div className="card-body map-container">
                  <MapComponent
                    center={[mockFarm.coordinates.lat, mockFarm.coordinates.lng]}
                    zoom={14}
                    parcelCoords={mockFarm.parcelCoords}
                  />
                </div>
              </section>

              <section className="info-section card" aria-labelledby="info-title">
                <header className="card-header">
                  <h2 id="info-title">Informations de l'exploitation</h2>
                </header>
                <div className="card-body">
                  <dl className="info-list">
                    <div>
                      <dt>Nom</dt>
                      <dd>{mockFarm.name}</dd>
                    </div>
                    <div>
                      <dt>Région</dt>
                      <dd>{mockFarm.region}</dd>
                    </div>
                    <div>
                      <dt>Coordonnées</dt>
                      <dd>{mockFarm.coordinates.lat.toFixed(4)}°, {mockFarm.coordinates.lng.toFixed(4)}°</dd>
                    </div>
                    <div>
                      <dt>Superficie</dt>
                      <dd>{mockFarm.area} ha</dd>
                    </div>
                    <div>
                      <dt>Culture principale</dt>
                      <dd>{mockFarm.crop}</dd>
                    </div>
                    <div>
                      <dt>Type de sol</dt>
                      <dd>{mockFarm.soilType}</dd>
                    </div>
                    <div>
                      <dt>Date de création</dt>
                      <dd>{new Date(mockFarm.createdAt).toLocaleDateString('fr-FR')}</dd>
                    </div>
                    <div>
                      <dt>Dernière analyse</dt>
                      <dd>{new Date(mockFarm.lastAnalysis).toLocaleDateString('fr-FR')}</dd>
                    </div>
                  </dl>
                </div>
              </section>
            </div>

            <section className="indicators-section card" aria-labelledby="indicators-title">
              <header className="card-header">
                <h2 id="indicators-title">Indicateurs clés</h2>
              </header>
              <div className="card-body">
                <div className="indicators-grid">
                  {mockIndicators.map((indicator, index) => (
                    <article key={index} className="indicator-card">
                      <div className="indicator-icon">
                        <indicator.icon size={20} aria-hidden="true" />
                      </div>
                      <div className="indicator-content">
                        <p className="indicator-label">{indicator.label}</p>
                        <div className="indicator-value-row">
                          <span className="indicator-value">{indicator.value}</span>
                          <span className={`indicator-trend ${indicator.trendType}`}>
                            {indicator.trendType !== 'neutral' && (
                              indicator.trendType === 'up' ? <TrendingUp size={14} /> : <TrendingDown size={14} />
                            )}
                            {indicator.trend}
                          </span>
                        </div>
                        <p className="indicator-unit">{indicator.unit}</p>
                      </div>
                    </article>
                  ))}
                </div>
              </div>
            </section>
          </div>
        )}

        {activeTab === 'climate' && (
          <div id="climate-panel" role="tabpanel">
            <section className="chart-section card" aria-labelledby="climate-chart-title">
              <header className="card-header">
                <h2 id="climate-chart-title">Évolution climatique sur 12 mois</h2>
              </header>
              <div className="card-body">
                <div className="chart-container" style={{ height: 380 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={mockClimateData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                      <defs>
                        <linearGradient id="tempGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.3}/>
                          <stop offset="95%" stopColor="#F59E0B" stopOpacity={0}/>
                        </linearGradient>
                        <linearGradient id="rainGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
                          <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={getComputedStyle(document.documentElement).getPropertyValue('--color-border-light').trim() || '#E5EBE6'} />
                      <XAxis dataKey="month" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                      <YAxis orientation="left" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                      <YAxis yAxisId="right" orientation="right" domain={[0, 1]} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={(v) => v.toFixed(1)} />
                      <Tooltip />
                      <Area type="monotone" dataKey="temp" stroke="#F59E0B" strokeWidth={2} fillOpacity={1} fill="url(#tempGradient)" name="Température (°C)" />
                      <Area type="monotone" dataKey="rain" stroke="#3B82F6" strokeWidth={2} fillOpacity={1} fill="url(#rainGradient)" name="Précipitations (mm)" />
                      <Line type="monotone" dataKey="ndvi" stroke="#4CAF50" strokeWidth={2} dot={false} yAxisId="right" name="NDVI" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </section>

            <div className="climate-summary">
              <article className="summary-card card">
                <div className="card-body">
                  <h3>Températures</h3>
                  <div className="summary-stats">
                    <div><strong>Moyenne:</strong> 12.4°C</div>
                    <div><strong>Max:</strong> 25.4°C (Juil)</div>
                    <div><strong>Min:</strong> 8.2°C (Jan)</div>
                    <div><strong>Écart norme:</strong> +0.8°C</div>
                  </div>
                  <p className="summary-source">Source: NASA POWER • Résolution: 0.5° • Période: 2024</p>
                </div>
              </article>
              <article className="summary-card card">
                <div className="card-body">
                  <h3>Précipitations</h3>
                  <div className="summary-stats">
                    <div><strong>Cumul annuel:</strong> 687 mm</div>
                    <div><strong>Mois le plus humide:</strong> Oct (78 mm)</div>
                    <div><strong>Mois le plus sec:</strong> Juil (42 mm)</div>
                    <div><strong>Écart norme:</strong> -12%</div>
                  </div>
                  <p className="summary-source">Source: NASA POWER / GPM IMERG • Résolution: 0.1° • Période: 2024</p>
                </div>
              </article>
            </div>
          </div>
        )}

        {activeTab === 'vegetation' && (
          <div id="vegetation-panel" role="tabpanel">
            <section className="card" aria-labelledby="veg-map-title">
              <header className="card-header">
                <h2 id="veg-map-title">Carte NDVI - Sentinel-2</h2>
                <div className="veg-controls">
                  <select className="input" style={{ width: 'auto', minWidth: '180px' }}>
                    <option>Dernière image disponible</option>
                    <option>Il y a 1 mois</option>
                    <option>Il y a 3 mois</option>
                    <option>Même période 2023</option>
                  </select>
                </div>
              </header>
              <div className="card-body map-container" style={{ height: 400 }}>
                <MapComponent
                  center={[mockFarm.coordinates.lat, mockFarm.coordinates.lng]}
                  zoom={14}
                  parcelCoords={mockFarm.parcelCoords}
                />
                <div className="ndvi-overlay">
                  <div className="ndvi-legend">
                    <div className="legend-gradient"></div>
                    <div className="legend-labels">
                      <span>0.1</span>
                      <span>0.3</span>
                      <span>0.5</span>
                      <span>0.7</span>
                      <span>0.9</span>
                    </div>
                    <p className="legend-note">NDVI - Données Sentinel-2 (10m)</p>
                  </div>
                </div>
              </div>
            </section>

            <div className="veg-analysis">
              <article className="card">
                <div className="card-body">
                  <h3>Analyse de la végétation</h3>
                  <div className="analysis-grid">
                    <div>
                      <h4>NDVI moyen actuel: 0.68</h4>
                      <p>Végétation vigoureuse, en phase de croissance active. Légère augmentation par rapport au mois précédent (+0.04).</p>
                    </div>
                    <div>
                      <h4>Hétérogénéité spatiale: Faible</h4>
                      <p>La parcelle présente une couverture végétale uniforme. Aucune zone de stress détectée par imagerie satellitaire.</p>
                    </div>
                    <div>
                      <h4>Comparaison année précédente</h4>
                      <p>NDVI supérieur de +0.08 à la même période 2023. Conditions plus favorables cette année.</p>
                    </div>
                  </div>
                </div>
              </article>
            </div>
          </div>
        )}

        {activeTab === 'risks' && (
          <div id="risks-panel" role="tabpanel">
            <section className="card" aria-labelledby="risks-title">
              <header className="card-header">
                <h2 id="risks-title">Alertes et risques détectés</h2>
              </header>
              <div className="card-body">
                {mockAlerts.map((alert) => (
                  <article key={alert.id} className={`alert-detail alert-${alert.type}`}>
                    <div className="alert-detail-header">
                      <div className="alert-detail-icon">
                        {alert.type === 'warning' && <AlertTriangle size={24} />}
                        {alert.type === 'info' && <Sun size={24} />}
                      </div>
                      <div>
                        <h3>{alert.title}</h3>
                        <div className="alert-meta">
                          <span className="alert-confidence">{alert.confidence}% confiance</span>
                          <time dateTime={alert.date}>{new Date(alert.date).toLocaleDateString('fr-FR')}</time>
                        </div>
                      </div>
                      <span className={`badge ${alert.type === 'warning' ? 'badge-warning' : 'badge-info'}`}>
                        {alert.type === 'warning' ? 'Attention' : 'Information'}
                      </span>
                    </div>
                    <p className="alert-description">{alert.description}</p>
                    <div className="alert-action">
                      <strong>Action recommandée:</strong> {alert.action}
                    </div>
                    <div className="alert-sources">
                      <strong>Sources:</strong> NASA POWER (températures), GPM IMERG (précipitations), Modèles météo ECMWF
                    </div>
                  </article>
                ))}

                <article className="alert-detail alert-success">
                  <div className="alert-detail-header">
                    <div className="alert-detail-icon">
                      <TrendingUp size={24} />
                    </div>
                    <div>
                      <h3>Végétation vigoureuse</h3>
                      <div className="alert-meta">
                        <span className="alert-confidence">92% confiance</span>
                        <time dateTime="2025-01-10">10 janvier 2025</time>
                      </div>
                    </div>
                    <span className="badge badge-success">Favorable</span>
                  </div>
                  <p className="alert-description">NDVI supérieur à la moyenne sur 90% de la parcelle. Aucune anomalie détectée.</p>
                  <div className="alert-action">
                    <strong>Action:</strong> Continuer la surveillance hebdomadaire. Pas d'intervention nécessaire.
                  </div>
                </article>
              </div>
            </section>
          </div>
        )}

        {activeTab === 'water' && (
          <div id="water-panel" role="tabpanel">
            <section className="card" aria-labelledby="water-title">
              <header className="card-header">
                <h2 id="water-title">Analyse des ressources en eau</h2>
              </header>
              <div className="card-body">
                <div className="water-grid">
                  <article className="water-card">
                    <h3>Humidité du sol (SMAP)</h3>
                    <div className="water-value">0.28 m³/m³</div>
                    <p>Surface (0-5 cm) - Donnée du 14 janvier 2025</p>
                    <div className="water-bar">
                      <div className="water-bar-fill" style={{ width: '55%' }}></div>
                    </div>
                    <span className="water-status">Niveau modéré</span>
                  </article>
                  <article className="water-card">
                    <h3>Précipitations 30 jours</h3>
                    <div className="water-value">28 mm</div>
                    <p>Déficit de 35% vs normale saisonnière</p>
                    <div className="water-bar">
                      <div className="water-bar-fill warning" style={{ width: '65%' }}></div>
                    </div>
                    <span className="water-status warning">Surveillance</span>
                  </article>
                  <article className="water-card">
                    <h3>Jours sans pluie</h3>
                    <div className="water-value">12</div>
                    <p>Consécutifs - Prévision: 5 jours supplémentaires</p>
                    <div className="water-bar">
                      <div className="water-bar-fill warning" style={{ width: '70%' }}></div>
                    </div>
                    <span className="water-status warning">Attention</span>
                  </article>
                </div>
              </div>
            </section>

            <section className="card" aria-labelledby="water-history-title">
              <header className="card-header">
                <h2 id="water-history-title">Historique hydrique</h2>
              </header>
              <div className="card-body">
                <div className="chart-container" style={{ height: 280 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={mockClimateData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="month" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                      <Tooltip />
                      <Line type="monotone" dataKey="rain" stroke="#3B82F6" strokeWidth={2} dot={{ r: 4 }} name="Précipitations (mm)" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                <p className="chart-source">Source: NASA POWER / GPM IMERG • Estimations satellitaires, non mesures locales</p>
              </div>
            </section>
          </div>
        )}
      </div>

      {mapView && (
        <div className="map-modal-overlay" onClick={() => setMapView(false)}>
          <div className="map-modal" onClick={(e) => e.stopPropagation()}>
            <header className="map-modal-header">
              <h2>Carte interactive - {mockFarm.name}</h2>
              <button className="icon-btn" onClick={() => setMapView(false)} aria-label="Fermer">
                <MoreVertical size={20} style={{ transform: 'rotate(90deg)' }} />
              </button>
            </header>
            <div className="map-modal-body">
              <MapComponent
                center={[mockFarm.coordinates.lat, mockFarm.coordinates.lng]}
                zoom={14}
                parcelCoords={mockFarm.parcelCoords}
                readOnly={false}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
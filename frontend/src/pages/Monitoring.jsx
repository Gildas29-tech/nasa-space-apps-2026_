import { useState } from 'react'
import {
  Calendar,
  ChevronLeft,
  ChevronRight,
  Download,
  RefreshCw,
  Eye,
  AlertTriangle,
  CheckCircle,
  MapPin,
  Layers,
  MoreVertical
} from 'lucide-react'
import { MapContainer, TileLayer, Polygon, useMap } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import './Monitoring.css'

const mockFarm = {
  name: 'Exploitation Demo',
  coordinates: { lat: 45.75, lng: -0.63 },
  parcelCoords: [
    [45.748, -0.635],
    [45.752, -0.635],
    [45.752, -0.625],
    [45.748, -0.625],
    [45.748, -0.635],
  ],
}

const ndviHistory = [
  { date: '2024-01-15', ndvi: 0.32, cloudCover: 15 },
  { date: '2024-02-15', ndvi: 0.35, cloudCover: 10 },
  { date: '2024-03-15', ndvi: 0.48, cloudCover: 5 },
  { date: '2024-04-15', ndvi: 0.62, cloudCover: 20 },
  { date: '2024-05-15', ndvi: 0.75, cloudCover: 8 },
  { date: '2024-06-15', ndvi: 0.81, cloudCover: 12 },
  { date: '2024-07-15', ndvi: 0.78, cloudCover: 30 },
  { date: '2024-08-15', ndvi: 0.72, cloudCover: 25 },
  { date: '2024-09-15', ndvi: 0.65, cloudCover: 18 },
  { date: '2024-10-15', ndvi: 0.52, cloudCover: 10 },
  { date: '2024-11-15', ndvi: 0.41, cloudCover: 22 },
  { date: '2024-12-15', ndvi: 0.34, cloudCover: 15 },
  { date: '2025-01-15', ndvi: 0.38, cloudCover: 8 },
]

const sentinelDates = [
  '2025-01-10', '2025-01-05', '2024-12-31', '2024-12-26',
  '2024-12-21', '2024-12-16', '2024-12-11', '2024-12-06',
]

export default function Monitoring() {
  const [activeView, setActiveView] = useState('timeseries')
  const [selectedDate, setSelectedDate] = useState(sentinelDates[0])
  const [compareDate, setCompareDate] = useState(null)

  const currentNDVI = ndviHistory.find(d => d.date === selectedDate)?.ndvi || 0
  const previousNDVI = ndviHistory[ndviHistory.findIndex(d => d.date === selectedDate) - 1]?.ndvi || 0
  const ndviChange = currentNDVI - previousNDVI

  return (
    <div className="monitoring">
      <div className="page-header">
        <div>
          <h1>Surveillance végétale</h1>
          <p className="page-subtitle">Suivez l'évolution de la végétation via les indices NDVI (Sentinel-2 / Landsat)</p>
        </div>
        <div className="header-actions">
          <button className="btn btn-secondary">
            <RefreshCw size={18} aria-hidden="true" />
            Actualiser
          </button>
          <button className="btn btn-primary">
            <Download size={18} aria-hidden="true" />
            Exporter données
          </button>
        </div>
      </div>

      <div className="monitoring-toolbar">
        <div className="farm-selector">
          <MapPin size={18} aria-hidden="true" />
          <select className="input" style={{ width: 'auto', minWidth: '250px' }}>
            <option value="1" selected>{mockFarm.name}</option>
            <option value="2">Domaine du Soleil</option>
            <option value="3">Ferme des Vallons</option>
          </select>
        </div>

        <div className="view-tabs" role="tablist">
          <button
            role="tab"
            aria-selected={activeView === 'timeseries'}
            className={`view-tab ${activeView === 'timeseries' ? 'active' : ''}`}
            onClick={() => setActiveView('timeseries')}
          >
            <Layers size={16} aria-hidden="true" />
            Série temporelle
          </button>
          <button
            role="tab"
            aria-selected={activeView === 'map'}
            className={`view-tab ${activeView === 'map' ? 'active' : ''}`}
            onClick={() => setActiveView('map')}
          >
            <MapPin size={16} aria-hidden="true" />
            Carte NDVI
          </button>
          <button
            role="tab"
            aria-selected={activeView === 'compare'}
            className={`view-tab ${activeView === 'compare' ? 'active' : ''}`}
            onClick={() => setActiveView('compare')}
          >
            <Eye size={16} aria-hidden="true" />
            Comparaison
          </button>
        </div>
      </div>

      <div className="monitoring-content">
        {activeView === 'timeseries' && (
          <section className="timeseries-view" aria-labelledby="ts-title">
            <div className="timeseries-header">
              <h2 id="ts-title">Évolution du NDVI</h2>
              <div className="date-nav">
                <button className="icon-btn" aria-label="Période précédente">
                  <ChevronLeft size={18} />
                </button>
                <select
                  className="input"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  style={{ width: 'auto', minWidth: '160px' }}
                  aria-label="Sélectionner une date"
                >
                  {ndviHistory.map((d) => (
                    <option key={d.date} value={d.date}>
                      {new Date(d.date).toLocaleDateString('fr-FR', { month: 'short', year: 'numeric' })} (NDVI: {d.ndvi.toFixed(2)})
                    </option>
                  ))}
                </select>
                <button className="icon-btn" aria-label="Période suivante">
                  <ChevronRight size={18} />
                </button>
              </div>
            </div>

            <div className="timeseries-grid">
              <div className="timeseries-main">
                <div className="ndvi-summary-cards">
                  <article className="summary-card">
                    <div className="summary-value">{currentNDVI.toFixed(2)}</div>
                    <div className="summary-label">NDVI actuel</div>
                    <div className={`summary-trend ${ndviChange >= 0 ? 'positive' : 'negative'}`}>
                      {ndviChange >= 0 ? '+' : ''}{ndviChange.toFixed(2)} vs période précédente
                    </div>
                  </article>
                  <article className="summary-card">
                    <div className="summary-value">{ndviHistory[ndviHistory.length - 1].ndvi.toFixed(2)}</div>
                    <div className="summary-label">Moyenne annuelle</div>
                    <div className="summary-trend neutral">Évolution saisonnière normale</div>
                  </article>
                  <article className="summary-card">
                    <div className="summary-value">{Math.max(...ndviHistory.map(d => d.ndvi)).toFixed(2)}</div>
                    <div className="summary-label">Pic annuel</div>
                    <div className="summary-trend neutral">Juin ({ndviHistory.find(d => d.ndvi === Math.max(...ndviHistory.map(d => d.ndvi)))?.date.slice(5,7)})</div>
                  </article>
                </div>

                <div className="chart-card card">
                  <div className="card-body">
                    <div className="chart-container" style={{ height: 350 }}>
                      <ResponsiveContainer width="100%" height="100%">
                        <import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts' />
                        <AreaChart data={ndviHistory} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                          <defs>
                            <linearGradient id="ndviGradient" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#4CAF50" stopOpacity={0.3}/>
                              <stop offset="95%" stopColor="#4CAF50" stopOpacity={0}/>
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} />
                          <XAxis dataKey="date" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={(v) => new Date(v).toLocaleDateString('fr-FR', { month: 'short' })} />
                          <YAxis domain={[0, 1]} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={(v) => v.toFixed(1)} />
                          <Tooltip
                            formatter={(value) => [value.toFixed(3), 'NDVI']}
                            labelFormatter={(v) => new Date(v).toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })}
                          />
                          <Area type="monotone" dataKey="ndvi" stroke="#4CAF50" strokeWidth={2} fillOpacity={1} fill="url(#ndviGradient)" />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                    <p className="chart-source">Source: ESA Sentinel-2 (10m) / NASA Landsat (30m) • Couverture nuageuse indiquée par point</p>
                  </div>
                </div>
              </div>

              <aside className="timeseries-sidebar">
                <section className="card" aria-labelledby="available-title">
                  <header className="card-header">
                    <h3 id="available-title">Images disponibles</h3>
                  </header>
                  <div className="card-body">
                    <ul className="image-list">
                      {sentinelDates.map((date) => (
                        <li key={date} className={selectedDate === date ? 'active' : ''}>
                          <button
                            className="image-item"
                            onClick={() => setSelectedDate(date)}
                            aria-pressed={selectedDate === date}
                          >
                            <span className="image-date">{new Date(date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })}</span>
                            <span className="image-source">Sentinel-2</span>
                            <span className={`image-cloud ${getCloudClass(ndviHistory.find(d => d.date === date)?.cloudCover || 0)}`}>
                              ☁ {ndviHistory.find(d => d.date === date)?.cloudCover || 0}%
                            </span>
                          </button>
                        </li>
                      ))}
                    </ul>
                  </div>
                </section>

                <section className="card" aria-labelledby="interpret-title">
                  <header className="card-header">
                    <h3 id="interpret-title">Interprétation</h3>
                  </header>
                  <div className="card-body">
                    <div className="interpretation">
                      <p><strong>NDVI {currentNDVI.toFixed(2)}</strong> - Végétation <strong>{getNDVIStatus(currentNDVI)}</strong></p>
                      <p>{getNDVIDescription(currentNDVI, ndviChange)}</p>
                      <div className="interpretation-note">
                        <CheckCircle size={14} aria-hidden="true" />
                        <span>Une variation du NDVI ne constitue pas un diagnostic de maladie ou carence. C'est un signal nécessitant une vérification terrain.</span>
                      </div>
                    </div>
                  </div>
                </section>
              </aside>
            </div>
          </section>
        )}

        {activeView === 'map' && (
          <section className="map-view" aria-labelledby="map-title">
            <div className="map-controls">
              <div className="map-date-selector">
                <label htmlFor="map-date" className="label">Date de l'image</label>
                <select
                  id="map-date"
                  className="input"
                  value={selectedDate}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  style={{ width: 'auto', minWidth: '200px' }}
                >
                  {sentinelDates.map((d) => (
                    <option key={d} value={d}>{new Date(d).toLocaleDateString('fr-FR')}</option>
                  ))}
                </select>
              </div>
              <div className="map-legend-inline">
                <span>NDVI:</span>
                <div className="legend-gradient-mini"></div>
                <span>-0.1 → 1.0</span>
              </div>
            </div>
            <div className="map-container-large">
              <MapContainer
                center={[mockFarm.coordinates.lat, mockFarm.coordinates.lng]}
                zoom={14}
                scrollWheelZoom={true}
                style={{ width: '100%', height: '100%' }}
              >
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <Polygon
                  positions={mockFarm.parcelCoords}
                  color="#1B4D2E"
                  fillColor="#4CAF50"
                  fillOpacity={0.15}
                  weight={2}
                  dashArray="8, 4"
                />
              </MapContainer>
              <div className="ndvi-map-overlay">
                <div className="ndvi-legend-full">
                  <div className="legend-title">NDVI - {new Date(selectedDate).toLocaleDateString('fr-FR')}</div>
                  <div className="legend-gradient-full"></div>
                  <div className="legend-labels-full">
                    <span>Faible (-0.1)</span>
                    <span>Moyen (0.3)</span>
                    <span>Élevé (0.6)</span>
                    <span>Très élevé (0.9)</span>
                  </div>
                  <p className="legend-disclaimer">Simulation - Données réelles via API Sentinel Hub / Google Earth Engine</p>
                </div>
              </div>
            </div>
          </section>
        )}

        {activeView === 'compare' && (
          <section className="compare-view" aria-labelledby="compare-title">
            <div className="compare-controls">
              <h2 id="compare-title">Comparaison de périodes</h2>
              <div className="compare-date-pickers">
                <div className="date-picker">
                  <label htmlFor="compare-date-1" className="label">Période A</label>
                  <select
                    id="compare-date-1"
                    className="input"
                    value={selectedDate}
                    onChange={(e) => setSelectedDate(e.target.value)}
                  >
                    {ndviHistory.map((d) => (
                      <option key={d.date} value={d.date}>{new Date(d.date).toLocaleDateString('fr-FR', { month: 'short', year: 'numeric' })}</option>
                    ))}
                  </select>
                </div>
                <div className="date-picker">
                  <label htmlFor="compare-date-2" className="label">Période B</label>
                  <select
                    id="compare-date-2"
                    className="input"
                    value={compareDate || ''}
                    onChange={(e) => setCompareDate(e.target.value || null)}
                  >
                    <option value="">Sélectionner...</option>
                    {ndviHistory.map((d) => (
                      <option key={d.date} value={d.date}>{new Date(d.date).toLocaleDateString('fr-FR', { month: 'short', year: 'numeric' })}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {compareDate && (
              <div className="compare-results">
                <div className="compare-card">
                  <h3>Période A: {new Date(selectedDate).toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })}</h3>
                  <div className="compare-ndvi">{ndviHistory.find(d => d.date === selectedDate)?.ndvi.toFixed(3) || 'N/A'}</div>
                </div>
                <div className="compare-card">
                  <h3>Période B: {new Date(compareDate).toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })}</h3>
                  <div className="compare-ndvi">{ndviHistory.find(d => d.date === compareDate)?.ndvi.toFixed(3) || 'N/A'}</div>
                </div>
                <div className="compare-card diff">
                  <h3>Différence</h3>
                  <div className={`compare-ndvi ${(ndviHistory.find(d => d.date === selectedDate)?.ndvi || 0) - (ndviHistory.find(d => d.date === compareDate)?.ndvi || 0) >= 0 ? 'positive' : 'negative'}`}>
                    {(ndviHistory.find(d => d.date === selectedDate)?.ndvi || 0) - (ndviHistory.find(d => d.date === compareDate)?.ndvi || 0) >= 0 ? '+' : ''}
                    {((ndviHistory.find(d => d.date === selectedDate)?.ndvi || 0) - (ndviHistory.find(d => d.date === compareDate)?.ndvi || 0)).toFixed(3)}
                  </div>
                </div>
              </div>
            )}

            <div className="compare-chart card">
              <div className="card-body">
                <div className="chart-container" style={{ height: 300 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={ndviHistory} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="date" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={(v) => new Date(v).toLocaleDateString('fr-FR', { month: 'short' })} />
                      <YAxis domain={[0, 1]} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={(v) => v.toFixed(1)} />
                      <Tooltip />
                      <Line type="monotone" dataKey="ndvi" stroke="#4CAF50" strokeWidth={2} dot={{ r: 4 }} name="NDVI" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                <p className="chart-source">Sélectionnez deux périodes ci-dessus pour comparer leurs valeurs NDVI</p>
              </div>
            </div>
          </section>
        )}
      </div>
    </div>
  )
}

function getCloudClass(cover) {
  if (cover < 10) return 'low'
  if (cover < 30) return 'medium'
  return 'high'
}

function getNDVIStatus(ndvi) {
  if (ndvi < 0.2) return 'très faible'
  if (ndvi < 0.4) return 'faible'
  if (ndvi < 0.6) return 'modérée'
  if (ndvi < 0.8) return 'vigoureuse'
  return 'très vigoureuse'
}

function getNDVIDescription(ndvi, change) {
  if (ndvi < 0.3) return 'Végétation très clairsemée ou sol nu. Vérifier l\'état des cultures ou la période de jachère.'
  if (ndvi < 0.5) return 'Végétation en développement ou culture à stade précoce. Surveillance de la croissance recommandée.'
  if (ndvi < 0.7) return 'Bonne couverture végétale. Culture en croissance active.'
  return 'Excellente vigueur végétative. Culture dense et en bonne santé.'
}
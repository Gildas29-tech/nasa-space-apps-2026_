import { useState } from 'react'
import {
  Plus,
  Search,
  Filter,
  Sun,
  CloudRain,
  Droplets,
  Leaf,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Info,
  ChevronRight,
  RefreshCw,
  Download,
  BarChart2,
  RotateCcw
} from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import './Crops.css'

const mockCrops = [
  { id: 'wheat', name: 'Blé tendre', icon: '🌾', season: 'Hiver', waterNeed: 'Moyen', tempOptimal: '15-25°C', frostTolerance: 'Forte', growthDays: 240 },
  { id: 'barley', name: 'Orge', icon: '🌾', season: 'Hiver/Printemps', waterNeed: 'Faible à moyen', tempOptimal: '12-22°C', frostTolerance: 'Moyenne', growthDays: 180 },
  { id: 'maize', name: 'Maïs', icon: '🌽', season: 'Été', waterNeed: 'Élevé', tempOptimal: '20-30°C', frostTolerance: 'Nulle', growthDays: 150 },
  { id: 'sunflower', name: 'Tournesol', icon: '🌻', season: 'Été', waterNeed: 'Moyen', tempOptimal: '20-28°C', frostTolerance: 'Faible', growthDays: 120 },
  { id: 'rapeseed', name: 'Colza', icon: '🌱', season: 'Hiver', waterNeed: 'Moyen à élevé', tempOptimal: '10-20°C', frostTolerance: 'Forte', growthDays: 300 },
  { id: 'soybean', name: 'Soja', icon: '🫘', season: 'Été', waterNeed: 'Moyen à élevé', tempOptimal: '20-30°C', frostTolerance: 'Nulle', growthDays: 130 },
  { id: 'sorghum', name: 'Sorgho', icon: '🌾', season: 'Été', waterNeed: 'Faible', tempOptimal: '25-35°C', frostTolerance: 'Nulle', growthDays: 120 },
  { id: 'pea', name: 'Pois protéagineux', icon: '🫛', season: 'Hiver/Printemps', waterNeed: 'Faible à moyen', tempOptimal: '10-20°C', frostTolerance: 'Moyenne', growthDays: 180 },
]

const mockFarm = {
  id: 1,
  name: 'Exploitation Demo',
  region: 'Nouvelle-Aquitaine, France',
  coordinates: { lat: 45.75, lng: -0.63 },
  area: 42.5,
  soilType: 'Argilo-calcaire',
  soilPH: 7.2,
  soilTexture: 'Argilo-limoneux',
  waterCapacity: 'Moyenne',
  climateZone: 'Océanique tempéré',
  avgTemp: 12.4,
  annualRain: 687,
  frostDays: 45,
  growingSeason: 'Avr-Oct',
}

const cropScores = [
  { crop: 'Blé tendre', score: 92, suitability: 'Très adapté', details: { temp: 95, water: 88, soil: 90, frost: 95 } },
  { crop: 'Orge', score: 88, suitability: 'Très adapté', details: { temp: 90, water: 92, soil: 85, frost: 85 } },
  { crop: 'Tournesol', score: 85, suitability: 'Bien adapté', details: { temp: 88, water: 85, soil: 82, frost: 70 } },
  { crop: 'Maïs', score: 72, suitability: 'Adapté avec irrigation', details: { temp: 75, water: 60, soil: 78, frost: 40 } },
  { crop: 'Colza', score: 89, suitability: 'Très adapté', details: { temp: 92, water: 80, soil: 95, frost: 90 } },
  { crop: 'Soja', score: 68, suitability: 'Peu adapté', details: { temp: 65, water: 70, soil: 75, frost: 30 } },
  { crop: 'Sorgho', score: 75, suitability: 'Adapté', details: { temp: 85, water: 90, soil: 70, frost: 35 } },
  { crop: 'Pois', score: 82, suitability: 'Bien adapté', details: { temp: 85, water: 88, soil: 80, frost: 80 } },
]

const selectedCrops = ['wheat', 'barley', 'sunflower']

export default function Crops() {
  const [activeTab, setActiveTab] = useState('compare')
  const [searchTerm, setSearchTerm] = useState('')
  const [showAddModal, setShowAddModal] = useState(false)

  const tabs = [
    { id: 'compare', label: 'Comparer cultures', icon: BarChart2 },
    { id: 'rotation', label: 'Rotations', icon: RotateCcw },
    { id: 'catalog', label: 'Catalogue', icon: Leaf },
  ]

  const filteredCrops = mockCrops.filter(c =>
    c.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getScoreColor = (score) => {
    if (score >= 85) return 'var(--color-primary)'
    if (score >= 70) return 'var(--color-warning)'
    return 'var(--color-danger)'
  }

  const getSuitabilityBadge = (suitability) => {
    if (suitability.includes('Très')) return 'badge-success'
    if (suitability.includes('Bien')) return 'badge-info'
    if (suitability.includes('Adapté')) return 'badge-warning'
    return 'badge-danger'
  }

  return (
    <div className="crops">
      <div className="page-header">
        <div>
          <h1>Cultures et rotations</h1>
          <p className="page-subtitle">Comparez l'adéquation des cultures selon vos conditions pédoclimatiques</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
          <Plus size={18} aria-hidden="true" />
          Ajouter culture
        </button>
      </div>

      <div className="farm-context card">
        <div className="card-body">
          <h3>Contexte de l'exploitation: {mockFarm.name}</h3>
          <div className="context-grid">
            <div className="context-item">
              <Sun size={16} aria-hidden="true" />
              <div>
                <span className="context-label">Température moyenne</span>
                <span className="context-value">{mockFarm.avgTemp}°C</span>
              </div>
            </div>
            <div className="context-item">
              <CloudRain size={16} aria-hidden="true" />
              <div>
                <span className="context-label">Précipitations annuelles</span>
                <span className="context-value">{mockFarm.annualRain} mm</span>
              </div>
            </div>
            <div className="context-item">
              <Droplets size={16} aria-hidden="true" />
              <div>
                <span className="context-label">Capacité de rétention</span>
                <span className="context-value">{mockFarm.waterCapacity}</span>
              </div>
            </div>
            <div className="context-item">
              <Leaf size={16} aria-hidden="true" />
              <div>
                <span className="context-label">Type de sol</span>
                <span className="context-value">{mockFarm.soilType} (pH {mockFarm.soilPH})</span>
              </div>
            </div>
            <div className="context-item">
              <AlertTriangle size={16} aria-hidden="true" />
              <div>
                <span className="context-label">Jours de gel/an</span>
                <span className="context-value">{mockFarm.frostDays}</span>
              </div>
            </div>
            <div className="context-item">
              <RotateCcw size={16} aria-hidden="true" />
              <div>
                <span className="context-label">Saison de croissance</span>
                <span className="context-value">{mockFarm.growingSeason}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="crops-tabs" role="tablist">
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

      {activeTab === 'compare' && (
        <div id="compare-panel" role="tabpanel" className="compare-view">
          <div className="compare-toolbar">
            <div className="search-box">
              <Search size={18} aria-hidden="true" />
              <input
                type="search"
                placeholder="Filtrer les cultures..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input"
                style={{ width: 'auto', minWidth: '250px' }}
              />
            </div>
            <div className="selected-crops">
              <span className="selected-label">Sélectionnées:</span>
              <div className="selected-chips">
                {selectedCrops.map((id) => {
                  const crop = mockCrops.find(c => c.id === id)
                  return crop && (
                    <span key={id} className="chip">
                      {crop.name}
                      <button className="chip-remove" onClick={() => {}} aria-label={`Retirer ${crop.name}`}>
                        <XCircle size={12} />
                      </button>
                    </span>
                  )
                })}
                <button className="chip add-chip" onClick={() => setShowAddModal(true)}>
                  <Plus size={14} />
                </button>
              </div>
            </div>
          </div>

          <div className="comparison-table-container">
            <table className="comparison-table">
              <thead>
                <tr>
                  <th>Culture</th>
                  <th>Score global</th>
                  <th>Adéquation</th>
                  <th>Température</th>
                  <th>Eau</th>
                  <th>Sol</th>
                  <th>Gel</th>
                  <th>Cycle</th>
                  <th>Besoins en eau</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {cropScores.map((item) => (
                  <tr key={item.crop} className={selectedCrops.some(id => mockCrops.find(c => c.name === item.crop)?.id === id) ? 'selected' : ''}>
                    <td>
                      <div className="crop-cell">
                        <span className="crop-icon">{mockCrops.find(c => c.name === item.crop)?.icon || '🌱'}</span>
                        <strong>{item.crop}</strong>
                      </div>
                    </td>
                    <td>
                      <div className="score-cell">
                        <div className="score-circle" style={{ '--score-color': getScoreColor(item.score) }}>
                          {item.score}
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className={`badge ${getSuitabilityBadge(item.suitability)}`}>{item.suitability}</span>
                    </td>
                    <td>
                      <div className="mini-bar" style={{ '--fill': `${item.details.temp}%`, '--color': getScoreColor(item.details.temp) }}></div>
                      <span>{item.details.temp}%</span>
                    </td>
                    <td>
                      <div className="mini-bar" style={{ '--fill': `${item.details.water}%`, '--color': getScoreColor(item.details.water) }}></div>
                      <span>{item.details.water}%</span>
                    </td>
                    <td>
                      <div className="mini-bar" style={{ '--fill': `${item.details.soil}%`, '--color': getScoreColor(item.details.soil) }}></div>
                      <span>{item.details.soil}%</span>
                    </td>
                    <td>
                      <div className="mini-bar" style={{ '--fill': `${item.details.frost}%`, '--color': getScoreColor(item.details.frost) }}></div>
                      <span>{item.details.frost}%</span>
                    </td>
                    <td>
                      <span className="cycle-badge">{mockCrops.find(c => c.name === item.crop)?.growthDays || 0} j</span>
                    </td>
                    <td>{mockCrops.find(c => c.name === item.crop)?.waterNeed || '-'}</td>
                    <td>
                      <button className="icon-btn" aria-label={`Détails ${item.crop}`}>
                        <Info size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="radar-chart-section card">
            <header className="card-header">
              <h2>Visualisation comparative (cultures sélectionnées)</h2>
            </header>
            <div className="card-body">
              <div className="chart-container" style={{ height: 350 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={cropScores.filter(c => selectedCrops.some(id => mockCrops.find(cc => cc.name === c.crop)?.id === id))} layout="vertical" margin={{ top: 10, right: 30, left: 80, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                    <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                    <YAxis type="category" dataKey="crop" width={100} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                    <Tooltip />
                    <Bar dataKey="details.temp" name="Température" fill="#F59E0B" radius={[0, 4, 4, 0]} />
                    <Bar dataKey="details.water" name="Eau" fill="#3B82F6" radius={[0, 4, 4, 0]} />
                    <Bar dataKey="details.soil" name="Sol" fill="#4CAF50" radius={[0, 4, 4, 0]} />
                    <Bar dataKey="details.frost" name="Gel" fill="#8B5CF6" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <p className="chart-source">Scores sur 100 basés sur l'adéquation pédoclimatique locale. Source: FAO GAEZ, règles agronomiques, données climatiques NASA POWER.</p>
            </div>
          </div>

          <div className="crop-details-grid">
            {selectedCrops.map((id) => {
              const crop = mockCrops.find(c => c.id === id)
              const scoreData = cropScores.find(c => c.crop === crop?.name)
              if (!crop || !scoreData) return null
              return (
                <article key={id} className="crop-detail-card card">
                  <header className="card-header">
                    <div className="crop-detail-header">
                      <span className="crop-icon-large">{crop.icon}</span>
                      <div>
                        <h3>{crop.name}</h3>
                        <span className={`badge ${getSuitabilityBadge(scoreData.suitability)}`}>{scoreData.suitability} • Score: {scoreData.score}/100</span>
                      </div>
                    </div>
                  </header>
                  <div className="card-body">
                    <div className="detail-grid">
                      <div className="detail-item">
                        <Sun size={16} aria-hidden="true" />
                        <div>
                          <span className="detail-label">Température optimale</span>
                          <span className="detail-value">{crop.tempOptimal}</span>
                        </div>
                      </div>
                      <div className="detail-item">
                        <Droplets size={16} aria-hidden="true" />
                        <div>
                          <span className="detail-label">Besoins en eau</span>
                          <span className="detail-value">{crop.waterNeed}</span>
                        </div>
                      </div>
                      <div className="detail-item">
                        <AlertTriangle size={16} aria-hidden="true" />
                        <div>
                          <span className="detail-label">Tolérance au gel</span>
                          <span className="detail-value">{crop.frostTolerance}</span>
                        </div>
                      </div>
                      <div className="detail-item">
                        <RotateCcw size={16} aria-hidden="true" />
                        <div>
                          <span className="detail-label">Durée du cycle</span>
                          <span className="detail-value">{crop.growthDays} jours</span>
                        </div>
                      </div>
                      <div className="detail-item">
                        <Leaf size={16} aria-hidden="true" />
                        <div>
                          <span className="detail-label">Saison</span>
                          <span className="detail-value">{crop.season}</span>
                        </div>
                      </div>
                    </div>
                    <div className="score-breakdown">
                      <h4>Détail des scores</h4>
                      <div className="score-bars">
                        {Object.entries(scoreData.details).map(([key, value]) => (
                          <div key={key} className="score-bar-row">
                            <span className="score-bar-label">{key === 'temp' ? 'Température' : key === 'water' ? 'Eau' : key === 'soil' ? 'Sol' : 'Gel'}</span>
                            <div className="score-bar-track">
                              <div className="score-bar-fill" style={{ width: `${value}%`, background: getScoreColor(value) }}></div>
                            </div>
                            <span className="score-bar-value">{value}%</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div className="crop-recommendations">
                      <h4>Recommandations</h4>
                      <ul>
                        {scoreData.score >= 85 && <li><CheckCircle size={14} /> Culture très bien adaptée aux conditions locales</li>}
                        {scoreData.details.water < 70 && <li><AlertTriangle size={14} /> Besoins en eau élevés - irrigation recommandée</li>}
                        {scoreData.details.frost < 50 && <li><AlertTriangle size={14} /> Sensible au gel - attention aux semis précoces</li>}
                        {scoreData.score < 70 && <li><Info size={14} /> Culture peu adaptée - envisager variétés tolérantes ou culture alternative</li>}
                      </ul>
                    </div>
                  </div>
                </article>
              )
            })}
          </div>
        </div>
      )}

      {activeTab === 'rotation' && (
        <div id="rotation-panel" role="tabpanel" className="rotation-view">
          <div className="rotation-header">
            <h2>Planification des rotations</h2>
            <p>Sélectionnez une séquence culturale sur 3-5 ans pour optimiser la fertilité et réduire les maladies</p>
          </div>
          <div className="rotation-builder card">
            <div className="card-body">
              <div className="rotation-years">
                {['Année 1', 'Année 2', 'Année 3', 'Année 4', 'Année 5'].map((year, i) => (
                  <div key={year} className="rotation-year">
                    <label className="year-label">{year}</label>
                    <select className="input rotation-select">
                      <option value="">— Choisir —</option>
                      {mockCrops.map(c => (
                        <option key={c.id} value={c.id}>{c.name}</option>
                      ))}
                    </select>
                    <div className="year-indicators">
                      <span className="indicator"><Sun size={12} /> N</span>
                      <span className="indicator"><Leaf size={12} /> C</span>
                      <span className="indicator"><Droplets size={12} /> -</span>
                    </div>
                  </div>
                ))}
              </div>
              <div className="rotation-analysis">
                <h3>Analyse de la rotation</h3>
                <div className="analysis-grid">
                  <div className="analysis-item good">
                    <CheckCircle size={20} />
                    <div>
                      <strong>Diversité culturale</strong>
                      <p>3 familles botaniques différentes sur 5 ans</p>
                    </div>
                  </div>
                  <div className="analysis-item good">
                    <CheckCircle size={20} />
                    <div>
                      <strong>Retour azoté</strong>
                      <p>Légumineuse (pois) incluse - apport azote</p>
                    </div>
                  </div>
                  <div className="analysis-item warning">
                    <AlertTriangle size={20} />
                    <div>
                      <strong>Risque maladies</strong>
                      <p>Blé et orge consécutifs - risque piétin-échaudage</p>
                    </div>
                  </div>
                  <div className="analysis-item good">
                    <CheckCircle size={20} />
                    <div>
                      <strong>Gestion eau</strong>
                      <p>Alternance cultures hiver/été favorable</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'catalog' && (
        <div id="catalog-panel" role="tabpanel" className="catalog-view">
          <div className="catalog-toolbar">
            <div className="search-box">
              <Search size={18} aria-hidden="true" />
              <input
                type="search"
                placeholder="Rechercher une culture..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input"
                style={{ width: 'auto', minWidth: '300px' }}
              />
            </div>
            <button className="btn btn-secondary">
              <Filter size={18} aria-hidden="true" />
              Filtres avancés
            </button>
          </div>

          <div className="catalog-grid">
            {filteredCrops.map((crop) => (
              <article key={crop.id} className="catalog-card card">
                <div className="catalog-card-header">
                  <span className="catalog-icon">{crop.icon}</span>
                  <div>
                    <h3>{crop.name}</h3>
                    <span className="catalog-season">{crop.season}</span>
                  </div>
                </div>
                <div className="catalog-card-body">
                  <div className="catalog-specs">
                    <div className="spec">
                      <Sun size={14} />
                      <span>{crop.tempOptimal}</span>
                    </div>
                    <div className="spec">
                      <Droplets size={14} />
                      <span>{crop.waterNeed}</span>
                    </div>
                    <div className="spec">
                      <AlertTriangle size={14} />
                      <span>Gel: {crop.frostTolerance}</span>
                    </div>
                    <div className="spec">
                      <RotateCcw size={14} />
                      <span>{crop.growthDays} j</span>
                    </div>
                  </div>
                  <div className="catalog-actions">
                    <button className="btn btn-secondary btn-sm">
                      <Plus size={14} />
                      Comparer
                    </button>
                    <button className="btn btn-ghost btn-sm">
                      <Info size={14} />
                      Fiche complète
                    </button>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </div>
      )}

      {showAddModal && (
        <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
          <div className="modal modal-lg" onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="add-crop-title">
            <header className="modal-header">
              <h2 id="add-crop-title">Ajouter une culture à la comparaison</h2>
              <button className="icon-btn" onClick={() => setShowAddModal(false)} aria-label="Fermer">
                <XCircle size={20} />
              </button>
            </header>
            <div className="modal-body">
              <p>Sélectionnez une culture à ajouter à votre comparaison:</p>
              <div className="crop-selector-grid">
                {mockCrops.filter(c => !selectedCrops.includes(c.id)).map((crop) => (
                  <button key={crop.id} className="crop-selector-card" onClick={() => {}}>
                    <span className="selector-icon">{crop.icon}</span>
                    <strong>{crop.name}</strong>
                    <span className="selector-meta">{crop.season} • {crop.waterNeed} • {crop.growthDays}j</span>
                  </button>
                ))}
              </div>
            </div>
            <footer className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setShowAddModal(false)}>Annuler</button>
            </footer>
          </div>
        </div>
      )}
    </div>
  )
}
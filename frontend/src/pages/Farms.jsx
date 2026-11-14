import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Plus,
  MapPin,
  Search,
  Filter,
  MoreVertical,
  Edit,
  Trash2,
  Eye,
  Leaf,
  Calendar,
  AlertTriangle
} from 'lucide-react'
import './Farms.css'

const mockFarms = [
  {
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
    alerts: 2
  },
  {
    id: 2,
    name: 'Domaine du Soleil',
    region: 'Occitanie, France',
    coordinates: { lat: 43.60, lng: 1.44 },
    area: 18.3,
    crop: 'Tournesol',
    soilType: 'Limoneux',
    createdAt: '2024-06-22',
    lastAnalysis: '2025-01-10',
    status: 'active',
    alerts: 0
  },
  {
    id: 3,
    name: 'Ferme des Vallons',
    region: 'Bretagne, France',
    coordinates: { lat: 48.11, lng: -1.67 },
    area: 65.0,
    crop: 'Maïs',
    soilType: 'Argileux',
    createdAt: '2023-11-08',
    lastAnalysis: '2024-12-20',
    status: 'warning',
    alerts: 3
  },
]

export default function Farms() {
  const [searchTerm, setSearchTerm] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newFarm, setNewFarm] = useState({ name: '', region: '', area: '', crop: '', soilType: '' })

  const filteredFarms = mockFarms.filter(farm =>
    farm.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    farm.region.toLowerCase().includes(searchTerm.toLowerCase()) ||
    farm.crop.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const handleCreateFarm = (e) => {
    e.preventDefault()
    // In real app, would call API
    console.log('Create farm:', newFarm)
    setShowCreateModal(false)
    setNewFarm({ name: '', region: '', area: '', crop: '', soilType: '' })
  }

  return (
    <div className="farms-page">
      <div className="page-header">
        <div>
          <h1>Mes exploitations</h1>
          <p className="page-subtitle">Gérez vos parcelles agricoles et suivez leurs analyses</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
          <Plus size={18} aria-hidden="true" />
          Nouvelle exploitation
        </button>
      </div>

      <div className="farms-toolbar">
        <div className="search-box">
          <Search size={18} aria-hidden="true" />
          <input
            type="search"
            placeholder="Rechercher une exploitation..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input"
            aria-label="Rechercher"
          />
        </div>
        <button className="btn btn-secondary">
          <Filter size={18} aria-hidden="true" />
          Filtres
        </button>
      </div>

      <div className="farms-grid">
        {filteredFarms.map((farm) => (
          <article key={farm.id} className="farm-card">
            <div className="farm-card-header">
              <div>
                <h2 className="farm-name">{farm.name}</h2>
                <p className="farm-location">
                  <MapPin size={14} aria-hidden="true" />
                  {farm.region}
                </p>
              </div>
              <span className={`status-badge ${farm.status}`}>
                {farm.status === 'active' ? 'Active' : 'Attention'}
              </span>
            </div>

            <div className="farm-meta">
              <div className="meta-item">
                <Leaf size={16} aria-hidden="true" />
                <span>{farm.crop}</span>
              </div>
              <div className="meta-item">
                <MapPin size={16} aria-hidden="true" />
                <span>{farm.area} ha</span>
              </div>
              <div className="meta-item">
                <Calendar size={16} aria-hidden="true" />
                <span>{farm.soilType}</span>
              </div>
            </div>

            <div className="farm-stats">
              <div className="stat">
                <span className="stat-value">{farm.alerts}</span>
                <span className="stat-label">
                  <AlertTriangle size={12} aria-hidden="true" />
                  Alertes
                </span>
              </div>
              <div className="stat">
                <span className="stat-value">
                  <Calendar size={12} aria-hidden="true" />
                </span>
                <span className="stat-label">Dernière analyse: {new Date(farm.lastAnalysis).toLocaleDateString('fr-FR')}</span>
              </div>
            </div>

            <div className="farm-actions">
              <Link to={`/farms/${farm.id}`} className="btn btn-secondary btn-sm">
                <Eye size={14} aria-hidden="true" />
                Voir détails
              </Link>
              <button className="btn btn-ghost btn-sm" aria-label="Plus d'options">
                <MoreVertical size={16} />
              </button>
            </div>
          </article>
        ))}
      </div>

      {filteredFarms.length === 0 && (
        <div className="empty-state">
          <MapPin size={64} className="empty-state-icon" aria-hidden="true" />
          <h3 className="empty-state-title">Aucune exploitation trouvée</h3>
          <p className="empty-state-text">
            {searchTerm ? 'Essayez de modifier vos termes de recherche.' : 'Commencez par créer votre première exploitation agricole.'}
          </p>
          {!searchTerm && (
            <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
              <Plus size={18} aria-hidden="true" />
              Créer une exploitation
            </button>
          )}
        </div>
      )}

      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="modal-title">
            <header className="modal-header">
              <h2 id="modal-title">Nouvelle exploitation</h2>
              <button className="icon-btn" onClick={() => setShowCreateModal(false)} aria-label="Fermer">
                <MoreVertical size={20} style={{ transform: 'rotate(90deg)' }} />
              </button>
            </header>
            <form onSubmit={handleCreateFarm} className="modal-body">
              <div className="form-group">
                <label htmlFor="farm-name" className="label">Nom de l'exploitation *</label>
                <input
                  type="text"
                  id="farm-name"
                  className="input"
                  placeholder="Ex: Domaine du Soleil"
                  value={newFarm.name}
                  onChange={(e) => setNewFarm({ ...newFarm, name: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label htmlFor="farm-region" className="label">Région / Pays *</label>
                <input
                  type="text"
                  id="farm-region"
                  className="input"
                  placeholder="Ex: Nouvelle-Aquitaine, France"
                  value={newFarm.region}
                  onChange={(e) => setNewFarm({ ...newFarm, region: e.target.value })}
                  required
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="farm-area" className="label">Superficie (ha) *</label>
                  <input
                    type="number"
                    id="farm-area"
                    className="input"
                    placeholder="42.5"
                    step="0.1"
                    min="0.1"
                    value={newFarm.area}
                    onChange={(e) => setNewFarm({ ...newFarm, area: e.target.value })}
                    required
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="farm-crop" className="label">Culture principale</label>
                  <input
                    type="text"
                    id="farm-crop"
                    className="input"
                    placeholder="Ex: Blé tendre"
                    value={newFarm.crop}
                    onChange={(e) => setNewFarm({ ...newFarm, crop: e.target.value })}
                  />
                </div>
              </div>
              <div className="form-group">
                <label htmlFor="farm-soil" className="label">Type de sol</label>
                <input
                  type="text"
                  id="farm-soil"
                  className="input"
                  placeholder="Ex: Argilo-calcaire"
                  value={newFarm.soilType}
                  onChange={(e) => setNewFarm({ ...newFarm, soilType: e.target.value })}
                />
              </div>
              <div className="form-help">
                <p>La localisation précise et la délimitation de la parcelle se feront sur la carte après création.</p>
              </div>
              <footer className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowCreateModal(false)}>
                  Annuler
                </button>
                <button type="submit" className="btn btn-primary">
                  <Plus size={18} aria-hidden="true" />
                  Créer l'exploitation
                </button>
              </footer>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
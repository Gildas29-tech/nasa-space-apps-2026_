import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  FileText,
  Download,
  Calendar,
  Clock,
  Eye,
  Edit,
  Trash2,
  Plus,
  Search,
  Filter,
  ChevronRight,
  AlertTriangle,
  CheckCircle,
  MapPin,
  Leaf,
  Droplets,
  Sun
} from 'lucide-react'
import './Reports.css'

const mockReports = [
  {
    id: 1,
    farmId: 1,
    farmName: 'Exploitation Demo',
    title: 'Diagnostic complet - Janvier 2025',
    type: 'full',
    status: 'completed',
    createdAt: '2025-01-15T10:30:00',
    period: '2024-01-01 à 2024-12-31',
    size: '2.4 MB',
    pages: 12,
    alerts: 2,
    indicators: 8,
  },
  {
    id: 2,
    farmId: 1,
    farmName: 'Exploitation Demo',
    title: 'Suivi végétale - Décembre 2024',
    type: 'vegetation',
    status: 'completed',
    createdAt: '2024-12-20T14:15:00',
    period: '2024-11-15 à 2024-12-15',
    size: '1.1 MB',
    pages: 6,
    alerts: 0,
    indicators: 4,
  },
  {
    id: 3,
    farmId: 2,
    farmName: 'Domaine du Soleil',
    title: 'Analyse climatique - Q4 2024',
    type: 'climate',
    status: 'completed',
    createdAt: '2024-12-10T09:00:00',
    period: '2024-10-01 à 2024-12-31',
    size: '1.8 MB',
    pages: 8,
    alerts: 1,
    indicators: 6,
  },
  {
    id: 4,
    farmId: 3,
    farmName: 'Ferme des Vallons',
    title: 'Comparaison cultures - Blé vs Orge',
    type: 'crop_comparison',
    status: 'completed',
    createdAt: '2024-11-28T16:45:00',
    period: 'Basé sur données 2024',
    size: '950 KB',
    pages: 5,
    alerts: 0,
    indicators: 5,
  },
  {
    id: 5,
    farmId: 1,
    farmName: 'Exploitation Demo',
    title: 'Diagnostic complet - Juillet 2024',
    type: 'full',
    status: 'completed',
    createdAt: '2024-07-15T11:20:00',
    period: '2024-01-01 à 2024-06-30',
    size: '2.1 MB',
    pages: 11,
    alerts: 1,
    indicators: 8,
  },
]

const reportTypes = {
  full: { label: 'Diagnostic complet', icon: FileText, color: 'var(--color-primary)' },
  climate: { label: 'Analyse climatique', icon: Sun, color: '#F59E0B' },
  vegetation: { label: 'Suivi végétale', icon: Leaf, color: '#4CAF50' },
  water: { label: 'Ressources en eau', icon: Droplets, color: '#3B82F6' },
  crop_comparison: { label: 'Comparaison cultures', icon: ChevronRight, color: '#8B5CF6' },
}

export default function Reports() {
  const [searchTerm, setSearchTerm] = useState('')
  const [typeFilter, setTypeFilter] = useState('all')
  const [farmFilter, setFarmFilter] = useState('all')
  const [showGenerateModal, setShowGenerateModal] = useState(false)
  const [generating, setGenerating] = useState(false)

  const filteredReports = mockReports.filter(report => {
    const matchesSearch = report.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         report.farmName.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = typeFilter === 'all' || report.type === typeFilter
    const matchesFarm = farmFilter === 'all' || report.farmId === parseInt(farmFilter)
    return matchesSearch && matchesType && matchesFarm
  })

  const handleGenerate = async (e) => {
    e.preventDefault()
    setGenerating(true)
    await new Promise(r => setTimeout(r, 2000))
    setGenerating(false)
    setShowGenerateModal(false)
    // In real app, would add to list
  }

  return (
    <div className="reports">
      <div className="page-header">
        <div>
          <h1>Rapports</h1>
          <p className="page-subtitle">Consultez, générez et exportez vos analyses agricoles</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowGenerateModal(true)}>
          <Plus size={18} aria-hidden="true" />
          Générer un rapport
        </button>
      </div>

      <div className="reports-toolbar">
        <div className="search-box">
          <Search size={18} aria-hidden="true" />
          <input
            type="search"
            placeholder="Rechercher un rapport..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input"
            style={{ width: 'auto', minWidth: '250px' }}
          />
        </div>
        <div className="filter-group">
          <select
            className="input"
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            style={{ width: 'auto', minWidth: '180px' }}
          >
            <option value="all">Tous les types</option>
            {Object.entries(reportTypes).map(([key, value]) => (
              <option key={key} value={key}>{value.label}</option>
            ))}
          </select>
          <select
            className="input"
            value={farmFilter}
            onChange={(e) => setFarmFilter(e.target.value)}
            style={{ width: 'auto', minWidth: '180px' }}
          >
            <option value="all">Toutes les exploitations</option>
            <option value="1">Exploitation Demo</option>
            <option value="2">Domaine du Soleil</option>
            <option value="3">Ferme des Vallons</option>
          </select>
        </div>
      </div>

      <div className="reports-grid">
        {filteredReports.map((report) => (
          <article key={report.id} className="report-card card">
            <div className="report-card-header">
              <div className="report-type-badge" style={{ background: reportTypes[report.type].color }}>
                <reportTypes[report.type].icon size={16} color="white" aria-hidden="true" />
              </div>
              <div>
                <h3 className="report-title">{report.title}</h3>
                <p className="report-farm">
                  <MapPin size={14} aria-hidden="true" />
                  {report.farmName}
                </p>
              </div>
            </div>

            <div className="report-meta">
              <div className="meta-item">
                <Calendar size={14} aria-hidden="true" />
                <span>{new Date(report.createdAt).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })}</span>
              </div>
              <div className="meta-item">
                <Clock size={14} aria-hidden="true" />
                <span>{new Date(report.createdAt).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}</span>
              </div>
              <div className="meta-item">
                <FileText size={14} aria-hidden="true" />
                <span>{report.pages} pages • {report.size}</span>
              </div>
              <div className="meta-item">
                <Leaf size={14} aria-hidden="true" />
                <span>Période: {report.period}</span>
              </div>
            </div>

            <div className="report-stats">
              <span className="stat">
                <AlertTriangle size={12} aria-hidden="true" />
                {report.alerts} alerte{report.alerts > 1 ? 's' : ''}
              </span>
              <span className="stat">
                <CheckCircle size={12} aria-hidden="true" />
                {report.indicators} indicateurs
              </span>
            </div>

            <footer className="report-actions">
              <button className="btn btn-primary btn-sm" onClick={() => {}}>
                <Download size={14} aria-hidden="true" />
                Télécharger PDF
              </button>
              <button className="btn btn-secondary btn-sm" onClick={() => {}}>
                <Eye size={14} aria-hidden="true" />
                Aperçu
              </button>
            </footer>
          </article>
        ))}
      </div>

      {filteredReports.length === 0 && (
        <div className="empty-state">
          <FileText size={64} className="empty-state-icon" aria-hidden="true" />
          <h3 className="empty-state-title">Aucun rapport trouvé</h3>
          <p className="empty-state-text">
            {searchTerm || typeFilter !== 'all' || farmFilter !== 'all'
              ? 'Essayez de modifier vos filtres de recherche.'
              : 'Générez votre premier rapport en cliquant sur le bouton ci-dessus.'}
          </p>
          {!searchTerm && typeFilter === 'all' && farmFilter === 'all' && (
            <button className="btn btn-primary" onClick={() => setShowGenerateModal(true)}>
              <Plus size={18} aria-hidden="true" />
              Générer un rapport
            </button>
          )}
        </div>
      )}

      {showGenerateModal && (
        <div className="modal-overlay" onClick={() => setShowGenerateModal(false)}>
          <div className="modal modal-lg" onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="generate-title">
            <header className="modal-header">
              <h2 id="generate-title">Générer un nouveau rapport</h2>
              <button className="icon-btn" onClick={() => setShowGenerateModal(false)} aria-label="Fermer">
                <ChevronRight size={20} style={{ transform: 'rotate(90deg)' }} />
              </button>
            </header>
            <form onSubmit={handleGenerate} className="modal-body">
              <div className="form-group">
                <label className="label">Exploitation *</label>
                <select className="input" required>
                  <option value="">Sélectionner...</option>
                  <option value="1">Exploitation Demo (42.5 ha - Blé tendre)</option>
                  <option value="2">Domaine du Soleil (18.3 ha - Tournesol)</option>
                  <option value="3">Ferme des Vallons (65 ha - Maïs)</option>
                </select>
              </div>

              <div className="form-group">
                <label className="label">Type de rapport *</label>
                <div className="report-type-options">
                  {Object.entries(reportTypes).map(([key, value]) => (
                    <label key={key} className="type-option">
                      <input type="radio" name="reportType" value={key} defaultChecked={key === 'full'} />
                      <div className="type-option-content" style={{ borderColor: value.color }}>
                        <value.icon size={20} style={{ color: value.color }} aria-hidden="true" />
                        <div>
                          <strong>{value.label}</strong>
                          <p>{getTypeDescription(key)}</p>
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="period-start" className="label">Date de début *</label>
                  <input type="date" id="period-start" className="input" required defaultValue="2024-01-01" />
                </div>
                <div className="form-group">
                  <label htmlFor="period-end" className="label">Date de fin *</label>
                  <input type="date" id="period-end" className="input" required defaultValue="2024-12-31" />
                </div>
              </div>

              <div className="form-group">
                <label className="label">Sections à inclure</label>
                <div className="checkbox-group">
                  <label className="checkbox-label">
                    <input type="checkbox" defaultChecked /> Résumé exécutif
                  </label>
                  <label className="checkbox-label">
                    <input type="checkbox" defaultChecked /> Conditions climatiques
                  </label>
                  <label className="checkbox-label">
                    <input type="checkbox" defaultChecked /> Indicateurs végétatifs (NDVI)
                  </label>
                  <label className="checkbox-label">
                    <input type="checkbox" defaultChecked /> Analyse des risques
                  </label>
                  <label className="checkbox-label">
                    <input type="checkbox" defaultChecked /> Ressources en eau
                  </label>
                  <label className="checkbox-label">
                    <input type="checkbox" /> Comparaison cultures
                  </label>
                  <label className="checkbox-label">
                    <input type="checkbox" /> Recommandations d'adaptation
                  </label>
                  <label className="checkbox-label">
                    <input type="checkbox" defaultChecked /> Limites et sources des données
                  </label>
                </div>
              </div>

              <div className="form-help">
                <p><strong>Note:</strong> La génération prend environ 30-60 secondes. Le PDF sera téléchargeable automatiquement une fois prêt.</p>
              </div>

              <footer className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowGenerateModal(false)}>
                  Annuler
                </button>
                <button type="submit" className="btn btn-primary" disabled={generating}>
                  {generating ? (
                    <>
                      <span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} aria-hidden="true" />
                      Génération en cours...
                    </>
                  ) : (
                    <>
                      <FileText size={18} aria-hidden="true" />
                      Générer le PDF
                    </>
                  )}
                </button>
              </footer>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

function getTypeDescription(type) {
  const descriptions = {
    full: 'Rapport complet incluant climat, végétation, eau, risques, cultures et recommandations',
    climate: 'Analyse détaillée des températures, précipitations et variables climatiques',
    vegetation: 'Évolution du NDVI, détection d\'anomalies, comparaison multi-périodes',
    water: 'Précipitations, humidité des sols, bilan hydrique, risques de sécheresse',
    crop_comparison: 'Évaluation comparative de plusieurs cultures selon l\'adéquation pédoclimatique',
  }
  return descriptions[type] || ''
}
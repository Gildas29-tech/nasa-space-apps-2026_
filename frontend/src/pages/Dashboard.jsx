import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  MapPin,
  Sun,
  CloudRain,
  Droplets,
  Leaf,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Calendar,
  Clock,
  ExternalLink,
  ChevronRight,
  RefreshCw
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import './Dashboard.css'

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

const mockAlerts = [
  { id: 1, type: 'warning', title: 'Déficit pluviométrique', description: 'Cumul sur 30 jours inférieur de 35% à la normale', date: '2025-01-15', confidence: 85 },
  { id: 2, type: 'info', title: 'Températures élevées', description: '5 jours consécutifs > 30°C prévus', date: '2025-01-14', confidence: 78 },
  { id: 3, type: 'success', title: 'Végétation vigoureuse', description: 'NDVI supérieur à la moyenne sur 90% de la parcelle', date: '2025-01-10', confidence: 92 },
]

const mockIndicators = [
  { label: 'Température moyenne', value: '12.4°C', trend: '+0.8°C', trendType: 'up', unit: 'vs norme', icon: Sun },
  { label: 'Cumul précipitations', value: '687 mm', trend: '-12%', trendType: 'down', unit: 'vs 30 ans', icon: CloudRain },
  { label: 'Humidité sol (surface)', value: '0.28 m³/m³', trend: 'Stable', trendType: 'neutral', unit: 'SMAP', icon: Droplets },
  { label: 'NDVI moyen actuel', value: '0.68', trend: '+0.04', trendType: 'up', unit: 'vs mois préc.', icon: Leaf },
]

export default function Dashboard() {
  const [activePeriod, setActivePeriod] = useState('12m')
  const [loading, setLoading] = useState(false)

  const handleRefresh = async () => {
    setLoading(true)
    await new Promise(r => setTimeout(r, 1000))
    setLoading(false)
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h1>Tableau de bord</h1>
          <p className="dashboard-subtitle">Exploitation Demo • Nouvelle-Aquitaine, France • Dernière mise à jour : 15 janvier 2025</p>
        </div>
        <div className="dashboard-actions">
          <select
            className="period-select"
            value={activePeriod}
            onChange={(e) => setActivePeriod(e.target.value)}
            aria-label="Période d'analyse"
          >
            <option value="1m">30 derniers jours</option>
            <option value="3m">3 derniers mois</option>
            <option value="6m">6 derniers mois</option>
            <option value="12m" selected>12 derniers mois</option>
          </select>
          <button className="btn btn-secondary" onClick={handleRefresh} disabled={loading}>
            <RefreshCw size={18} className={loading ? 'spinning' : ''} aria-hidden="true" />
            Actualiser
          </button>
        </div>
      </div>

      <section className="indicators-grid" aria-labelledby="indicators-title">
        <h2 id="indicators-title" className="sr-only">Indicateurs clés</h2>
        <div className="indicators">
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
      </section>

      <div className="dashboard-grid">
        <section className="chart-section" aria-labelledby="climate-title">
          <header className="chart-header">
            <h2 id="climate-title">Évolution climatique</h2>
            <div className="chart-legend">
              <span className="legend-item temp"><span className="legend-dot temp"></span>Température (°C)</span>
              <span className="legend-item rain"><span className="legend-dot rain"></span>Précipitations (mm)</span>
              <span className="legend-item ndvi"><span className="legend-dot ndvi"></span>NDVI</span>
            </div>
          </header>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={320}>
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
                  <linearGradient id="ndviGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#4CAF50" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#4CAF50" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke={getComputedStyle(document.documentElement).getPropertyValue('--color-border-light').trim() || '#E5EBE6'} vertical={false} />
                <XAxis
                  dataKey="month"
                  tick={{ fontSize: 11, fill: getComputedStyle(document.documentElement).getPropertyValue('--color-text-muted').trim() || '#7A8D7E' }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  orientation="left"
                  tick={{ fontSize: 11, fill: getComputedStyle(document.documentElement).getPropertyValue('--color-text-muted').trim() || '#7A8D7E' }}
                  axisLine={false}
                  tickLine={false}
                  domain={['auto', 'auto']}
                />
                <YAxis
                  yAxisId="right"
                  orientation="right"
                  domain={[0, 1]}
                  tick={{ fontSize: 11, fill: getComputedStyle(document.documentElement).getPropertyValue('--color-text-muted').trim() || '#7A8D7E' }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(v) => v.toFixed(1)}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--color-bg-elevated').trim() || '#FFFFFF',
                    border: `1px solid ${getComputedStyle(document.documentElement).getPropertyValue('--color-border-light').trim() || '#E5EBE6'}`,
                    borderRadius: '10px',
                    boxShadow: '0 4px 12px rgba(26, 46, 31, 0.08)'
                  }}
                  labelStyle={{ color: getComputedStyle(document.documentElement).getPropertyValue('--color-text').trim() || '#1A2E1F', fontWeight: 600 }}
                  itemStyle={{ fontSize: '12px' }}
                  formatter={(value, name) => {
                    if (name === 'temp') return [`${value}°C`, 'Température'];
                    if (name === 'rain') return [`${value} mm`, 'Précipitations'];
                    if (name === 'ndvi') return [value.toFixed(2), 'NDVI'];
                    return [value, name];
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="temp"
                  name="Température"
                  stroke="#F59E0B"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#tempGradient)"
                  yAxisId="left"
                />
                <Area
                  type="monotone"
                  dataKey="rain"
                  name="Précipitations"
                  stroke="#3B82F6"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#rainGradient)"
                  yAxisId="left"
                />
                <Line
                  type="monotone"
                  dataKey="ndvi"
                  name="NDVI"
                  stroke="#4CAF50"
                  strokeWidth={2}
                  dot={false}
                  yAxisId="right"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="alerts-section" aria-labelledby="alerts-title">
          <header className="section-header-row">
            <h2 id="alerts-title">Alertes récentes</h2>
            <Link to="/monitoring" className="btn btn-ghost btn-sm">
              Voir tout <ChevronRight size={14} />
            </Link>
          </header>
          <div className="alerts-list">
            {mockAlerts.map((alert) => (
              <article key={alert.id} className={`alert-item alert-${alert.type}`}>
                <div className="alert-icon">
                  {alert.type === 'warning' && <AlertTriangle size={20} />}
                  {alert.type === 'info' && <Sun size={20} />}
                  {alert.type === 'success' && <TrendingUp size={20} />}
                </div>
                <div className="alert-content">
                  <div className="alert-header-row">
                    <h3 className="alert-title">{alert.title}</h3>
                    <span className="alert-confidence">{alert.confidence}% confiance</span>
                  </div>
                  <p className="alert-description">{alert.description}</p>
                  <time className="alert-date" dateTime={alert.date}>
                    <Clock size={12} aria-hidden="true" />
                    {new Date(alert.date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })}
                  </time>
                </div>
              </article>
            ))}
          </div>
        </section>
      </div>

      <section className="quick-actions" aria-labelledby="actions-title">
        <h2 id="actions-title" className="sr-only">Actions rapides</h2>
        <div className="actions-grid">
          <Link to="/farms" className="action-card">
            <MapPin size={24} aria-hidden="true" />
            <h3>Mes exploitations</h3>
            <p>Gérer vos parcelles et cultures</p>
            <ChevronRight size={20} aria-hidden="true" />
          </Link>
          <Link to="/monitoring" className="action-card">
            <Leaf size={24} aria-hidden="true" />
            <h3>Surveillance végétale</h3>
            <p>Analyser l\'évolution du NDVI</p>
            <ChevronRight size={20} aria-hidden="true" />
          </Link>
          <Link to="/crops" className="action-card">
            <Droplets size={24} aria-hidden="true" />
            <h3>Comparer cultures</h3>
            <p>Évaluer l\'adéquation climatique</p>
            <ChevronRight size={20} aria-hidden="true" />
          </Link>
          <Link to="/reports" className="action-card">
            <ExternalLink size={24} aria-hidden="true" />
            <h3>Générer rapport</h3>
            <p>Diagnostic complet en PDF</p>
            <ChevronRight size={20} aria-hidden="true" />
          </Link>
        </div>
      </section>
    </div>
  )
}
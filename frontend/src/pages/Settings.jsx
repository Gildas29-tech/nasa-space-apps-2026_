import { useState } from 'react'
import {
  User,
  Bell,
  Shield,
  Globe,
  Palette,
  Database,
  Download,
  Trash2,
  LogOut,
  Key,
  Mail,
  Smartphone,
  Monitor,
  Save,
  AlertCircle
} from 'lucide-react'
import './Settings.css'

export default function Settings() {
  const [activeSection, setActiveSection] = useState('profile')
  const [darkMode, setDarkMode] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('darkMode')
      if (saved !== null) return JSON.parse(saved)
      return window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    return false
  })
  const [notifications, setNotifications] = useState({
    email: true,
    push: true,
    alerts: true,
    weekly: false,
    monthly: true,
  })
  const [units, setUnits] = useState('metric')
  const [language, setLanguage] = useState('fr')

  const sections = [
    { id: 'profile', label: 'Profil', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'preferences', label: 'Préférences', icon: Palette },
    { id: 'data', label: 'Données & Stockage', icon: Database },
    { id: 'security', label: 'Sécurité', icon: Shield },
    { id: 'about', label: 'À propos', icon: AlertCircle },
  ]

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode)
    localStorage.setItem('darkMode', JSON.stringify(darkMode))
  }, [darkMode])

  const handleSave = (section) => {
    // In real app, would save to backend
    console.log(`Saving ${section} settings`)
    alert('Paramètres enregistrés (simulation)')
  }

  return (
    <div className="settings">
      <div className="page-header">
        <h1>Paramètres</h1>
        <p className="page-subtitle">Configurez votre compte et vos préférences</p>
      </div>

      <div className="settings-layout">
        <nav className="settings-nav" aria-label="Sections des paramètres">
          <ul role="list">
            {sections.map((section) => (
              <li key={section.id}>
                <button
                  role="tab"
                  aria-selected={activeSection === section.id}
                  className={`nav-item ${activeSection === section.id ? 'active' : ''}`}
                  onClick={() => setActiveSection(section.id)}
                >
                  <section.icon size={20} aria-hidden="true" />
                  {section.label}
                </button>
              </li>
            ))}
          </ul>
        </nav>

        <div className="settings-content" role="tabpanel">
          {activeSection === 'profile' && (
            <section className="settings-section" aria-labelledby="profile-title">
              <header className="section-header">
                <h2 id="profile-title">Profil utilisateur</h2>
                <p>Gérez vos informations personnelles</p>
              </header>

              <div className="profile-card card">
                <div className="card-body">
                  <div className="profile-header">
                    <div className="avatar">
                      <User size={48} aria-hidden="true" />
                    </div>
                    <div>
                      <h3>Jean Dupont</h3>
                      <p className="profile-email">jean.dupont@exemple.fr</p>
                      <p className="profile-role">Agriculteur • Exploitation Demo</p>
                    </div>
                  </div>

                  <form className="profile-form" onSubmit={(e) => { e.preventDefault(); handleSave('profile') }}>
                    <div className="form-row">
                      <div className="form-group">
                        <label htmlFor="firstName" className="label">Prénom</label>
                        <input type="text" id="firstName" className="input" defaultValue="Jean" />
                      </div>
                      <div className="form-group">
                        <label htmlFor="lastName" className="label">Nom</label>
                        <input type="text" id="lastName" className="input" defaultValue="Dupont" />
                      </div>
                    </div>
                    <div className="form-group">
                      <label htmlFor="email" className="label">Email</label>
                      <input type="email" id="email" className="input" defaultValue="jean.dupont@exemple.fr" />
                    </div>
                    <div className="form-group">
                      <label htmlFor="phone" className="label">Téléphone</label>
                      <input type="tel" id="phone" className="input" placeholder="+33 6 00 00 00 00" />
                    </div>
                    <div className="form-group">
                      <label htmlFor="farmName" className="label">Nom de l'exploitation principale</label>
                      <input type="text" id="farmName" className="input" defaultValue="Exploitation Demo" />
                    </div>
                    <div className="form-group">
                      <label htmlFor="address" className="label">Adresse</label>
                      <textarea id="address" className="input" rows={3} placeholder="Adresse complète de l'exploitation" />
                    </div>
                    <footer className="form-footer">
                      <button type="submit" className="btn btn-primary">
                        <Save size={18} aria-hidden="true" />
                        Enregistrer les modifications
                      </button>
                    </footer>
                  </form>
                </div>
              </div>
            </section>
          )}

          {activeSection === 'notifications' && (
            <section className="settings-section" aria-labelledby="notifications-title">
              <header className="section-header">
                <h2 id="notifications-title">Notifications</h2>
                <p>Configurez comment et quand vous souhaitez être informé</p>
              </header>

              <div className="card">
                <div className="card-body">
                  <h3>Canal de notification</h3>
                  <div className="toggle-group">
                    <label className="toggle-label">
                      <input
                        type="checkbox"
                        checked={notifications.email}
                        onChange={(e) => setNotifications({ ...notifications, email: e.target.checked })}
                      />
                      <div>
                        <strong>Email</strong>
                        <p>Recevoir les alertes et rapports par email</p>
                      </div>
                    </label>
                    <label className="toggle-label">
                      <input
                        type="checkbox"
                        checked={notifications.push}
                        onChange={(e) => setNotifications({ ...notifications, push: e.target.checked })}
                      />
                      <div>
                        <strong>Push (mobile)</strong>
                        <p>Notifications sur l'application mobile</p>
                      </div>
                    </label>
                  </div>
                </div>
              </div>

              <div className="card" style={{ marginTop: 'var(--spacing-lg)' }}>
                <div className="card-body">
                  <h3>Types d'alertes</h3>
                  <div className="toggle-group">
                    <label className="toggle-label">
                      <input
                        type="checkbox"
                        checked={notifications.alerts}
                        onChange={(e) => setNotifications({ ...notifications, alerts: e.target.checked })}
                      />
                      <div>
                        <strong>Alertes immédiates</strong>
                        <p>Risques météorologiques, stress hydrique, anomalies végétatives</p>
                      </div>
                    </label>
                    <label className="toggle-label">
                      <input
                        type="checkbox"
                        checked={notifications.weekly}
                        onChange={(e) => setNotifications({ ...notifications, weekly: e.target.checked })}
                      />
                      <div>
                        <strong>Rapport hebdomadaire</strong>
                        <p>Synthèse des conditions de la semaine</p>
                      </div>
                    </label>
                    <label className="toggle-label">
                      <input
                        type="checkbox"
                        checked={notifications.monthly}
                        onChange={(e) => setNotifications({ ...notifications, monthly: e.target.checked })}
                      />
                      <div>
                        <strong>Rapport mensuel</strong>
                        <p>Analyse complète mensuelle avec recommandations</p>
                      </div>
                    </label>
                  </div>
                </div>
              </div>

              <footer className="form-footer" style={{ marginTop: 'var(--spacing-lg)' }}>
                <button className="btn btn-primary" onClick={() => handleSave('notifications')}>
                  <Save size={18} aria-hidden="true" />
                  Enregistrer
                </button>
              </footer>
            </section>
          )}

          {activeSection === 'preferences' && (
            <section className="settings-section" aria-labelledby="preferences-title">
              <header className="section-header">
                <h2 id="preferences-title">Préférences d'affichage</h2>
                <p>Personnalisez l'interface selon vos besoins</p>
              </header>

              <div className="card">
                <div className="card-body">
                  <h3>Thème</h3>
                  <div className="theme-options">
                    <label className="theme-option">
                      <input
                        type="radio"
                        name="theme"
                        checked={!darkMode}
                        onChange={() => setDarkMode(false)}
                      />
                      <div className="theme-preview light">
                        <div className="preview-header"></div>
                        <div className="preview-sidebar"></div>
                        <div className="preview-content"></div>
                      </div>
                      <span>Clair</span>
                    </label>
                    <label className="theme-option">
                      <input
                        type="radio"
                        name="theme"
                        checked={darkMode}
                        onChange={() => setDarkMode(true)}
                      />
                      <div className="theme-preview dark">
                        <div className="preview-header"></div>
                        <div className="preview-sidebar"></div>
                        <div className="preview-content"></div>
                      </div>
                      <span>Sombre</span>
                    </label>
                    <label className="theme-option">
                      <input
                        type="radio"
                        name="theme"
                        checked={false}
                        onChange={() => {
                          const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
                          setDarkMode(prefersDark)
                        }}
                      />
                      <div className="theme-preview auto">
                        <div className="preview-header"></div>
                        <div className="preview-sidebar"></div>
                        <div className="preview-content"></div>
                      </div>
                      <span>Système</span>
                    </label>
                  </div>
                </div>
              </div>

              <div className="card" style={{ marginTop: 'var(--spacing-lg)' }}>
                <div className="card-body">
                  <h3>Unités de mesure</h3>
                  <div className="radio-group">
                    <label className="radio-label">
                      <input
                        type="radio"
                        name="units"
                        value="metric"
                        checked={units === 'metric'}
                        onChange={(e) => setUnits(e.target.value)}
                      />
                      <span>Métrique (°C, mm, ha, m³/m³)</span>
                    </label>
                    <label className="radio-label">
                      <input
                        type="radio"
                        name="units"
                        value="imperial"
                        checked={units === 'imperial'}
                        onChange={(e) => setUnits(e.target.value)}
                      />
                      <span>Impérial (°F, in, ac, in³/in³)</span>
                    </label>
                  </div>
                </div>
              </div>

              <div className="card" style={{ marginTop: 'var(--spacing-lg)' }}>
                <div className="card-body">
                  <h3>Langue</h3>
                  <select
                    className="input"
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    style={{ width: 'auto', maxWidth: '200px' }}
                  >
                    <option value="fr">Français</option>
                    <option value="en">English</option>
                    <option value="es">Español</option>
                    <option value="pt">Português</option>
                  </select>
                </div>
              </div>

              <div className="card" style={{ marginTop: 'var(--spacing-lg)' }}>
                <div className="card-body">
                  <h3>Format de date</h3>
                  <select className="input" style={{ width: 'auto', maxWidth: '250px' }}>
                    <option>JJ/MM/AAAA (Français)</option>
                    <option>MM/JJ/AAAA (US)</option>
                    <option>AAAA-MM-JJ (ISO)</option>
                  </select>
                </div>
              </div>

              <footer className="form-footer" style={{ marginTop: 'var(--spacing-lg)' }}>
                <button className="btn btn-primary" onClick={() => handleSave('preferences')}>
                  <Save size={18} aria-hidden="true" />
                  Enregistrer
                </button>
              </footer>
            </section>
          )}

          {activeSection === 'data' && (
            <section className="settings-section" aria-labelledby="data-title">
              <header className="section-header">
                <h2 id="data-title">Données & Stockage</h2>
                <p>Gérez vos données locales et la synchronisation</p>
              </header>

              <div className="card">
                <div className="card-body">
                  <h3>Stockage local (PWA)</h3>
                  <div className="storage-info">
                    <div className="storage-bar">
                      <div className="storage-bar-fill" style={{ width: '45%' }}></div>
                    </div>
                    <div className="storage-stats">
                      <span>Utilisé: 12.4 MB</span>
                      <span>Disponible: ~50 MB</span>
                    </div>
                    <p className="storage-note">Données mises en cache: exploitations, rapports, images NDVI récentes</p>
                  </div>
                  <div className="storage-actions" style={{ marginTop: 'var(--spacing-md)' }}>
                    <button className="btn btn-secondary btn-sm" onClick={() => {}}>
                      <Download size={14} aria-hidden="true" />
                      Exporter mes données
                    </button>
                    <button className="btn btn-ghost btn-sm" onClick={() => {}}>
                      <Trash2 size={14} aria-hidden="true" />
                      Vider le cache
                    </button>
                  </div>
                </div>
              </div>

              <div className="card" style={{ marginTop: 'var(--spacing-lg)' }}>
                <div className="card-body">
                  <h3>Synchronisation Supabase</h3>
                  <div className="sync-status">
                    <div className="status-indicator disconnected"></div>
                    <div>
                      <strong>Non connecté</strong>
                      <p>Configurez vos identifiants Supabase pour activer la synchronisation cloud</p>
                    </div>
                  </div>
                  <div className="sync-config" style={{ marginTop: 'var(--spacing-md)' }}>
                    <div className="form-group">
                      <label htmlFor="supabase-url" className="label">URL Supabase</label>
                      <input type="url" id="supabase-url" className="input" placeholder="https://xxxx.supabase.co" />
                    </div>
                    <div className="form-group">
                      <label htmlFor="supabase-key" className="label">Clé anonyme (anon key)</label>
                      <input type="password" id="supabase-key" className="input" placeholder="eyJhbGciOiJIUzI1NiIs..." />
                    </div>
                    <button className="btn btn-primary btn-sm" onClick={() => {}}>
                      Tester la connexion
                    </button>
                  </div>
                </div>
              </div>

              <div className="card" style={{ marginTop: 'var(--spacing-lg)' }}>
                <div className="card-body">
                  <h3>Sources de données externes</h3>
                  <p>Statut des connexions API</p>
                  <div className="api-status">
                    <div className="api-item">
                      <span className="api-name">NASA POWER</span>
                      <span className="api-status-badge connected">Connecté</span>
                    </div>
                    <div className="api-item">
                      <span className="api-name">ESA Sentinel Hub</span>
                      <span className="api-status-badge pending">Clé requise</span>
                    </div>
                    <div className="api-item">
                      <span className="api-name">NASA GPM IMERG</span>
                      <span className="api-status-badge connected">Connecté</span>
                    </div>
                    <div className="api-item">
                      <span className="api-name">FAO GAEZ</span>
                      <span className="api-status-badge connected">Connecté</span>
                    </div>
                  </div>
                </div>
              </div>
            </section>
          )}

          {activeSection === 'security' && (
            <section className="settings-section" aria-labelledby="security-title">
              <header className="section-header">
                <h2 id="security-title">Sécurité</h2>
                <p>Gérez votre mot de passe et les sessions actives</p>
              </header>

              <div className="card">
                <div className="card-body">
                  <h3>Mot de passe</h3>
                  <form onSubmit={(e) => { e.preventDefault(); handleSave('security') }}>
                    <div className="form-group">
                      <label htmlFor="currentPassword" className="label">Mot de passe actuel</label>
                      <input type="password" id="currentPassword" className="input" />
                    </div>
                    <div className="form-row">
                      <div className="form-group">
                        <label htmlFor="newPassword" className="label">Nouveau mot de passe</label>
                        <input type="password" id="newPassword" className="input" />
                      </div>
                      <div className="form-group">
                        <label htmlFor="confirmPassword" className="label">Confirmer</label>
                        <input type="password" id="confirmPassword" className="input" />
                      </div>
                    </div>
                    <button type="submit" className="btn btn-primary">
                      <Key size={18} aria-hidden="true" />
                      Changer le mot de passe
                    </button>
                  </form>
                </div>
              </div>

              <div className="card" style={{ marginTop: 'var(--spacing-lg)' }}>
                <div className="card-body">
                  <h3>Authentification à deux facteurs (2FA)</h3>
                  <div className="toggle-label" style={{ flexDirection: 'row', alignItems: 'center' }}>
                    <input type="checkbox" />
                    <div>
                      <strong>Activer la 2FA</strong>
                      <p>Ajoutez une couche de sécurité avec une application d'authentification</p>
                    </div>
                    <button className="btn btn-secondary btn-sm" style={{ marginLeft: 'auto' }}>
                      Configurer
                    </button>
                  </div>
                </div>
              </div>

              <div className="card" style={{ marginTop: 'var(--spacing-lg)' }}>
                <div className="card-body">
                  <h3>Sessions actives</h3>
                  <div className="session-list">
                    <div className="session-item current">
                      <div className="session-info">
                        <div className="session-device">
                          <Monitor size={18} aria-hidden="true" />
                          <span>Navigateur Chrome sur Windows</span>
                        </div>
                        <div className="session-meta">Actuelle • Il y a 5 min • Paris, France</div>
                      </div>
                      <span className="badge badge-success">Active</span>
                    </div>
                    <div className="session-item">
                      <div className="session-info">
                        <div className="session-device">
                          <Smartphone size={18} aria-hidden="true" />
                          <span>Application mobile iOS</span>
                        </div>
                        <div className="session-meta">Il y a 2 jours • Lyon, France</div>
                      </div>
                      <button className="btn btn-ghost btn-sm">Révoquer</button>
                    </div>
                    <div className="session-item">
                      <div className="session-info">
                        <div className="session-device">
                          <Monitor size={18} aria-hidden="true" />
                          <span>Navigateur Safari sur Mac</span>
                        </div>
                        <div className="session-meta">Il y a 1 semaine • Bordeaux, France</div>
                      </div>
                      <button className="btn btn-ghost btn-sm">Révoquer</button>
                    </div>
                  </div>
                  <button className="btn btn-secondary btn-sm" style={{ marginTop: 'var(--spacing-md)' }}>
                    Révoquer toutes les autres sessions
                  </button>
                </div>
              </div>
            </section>
          )}

          {activeSection === 'about' && (
            <section className="settings-section" aria-labelledby="about-title">
              <header className="section-header">
                <h2 id="about-title">À propos de FieldShift</h2>
                <p>Informations sur l'application et mentions légales</p>
              </header>

              <div className="card">
                <div className="card-body text-center" style={{ padding: 'var(--spacing-xl)' }}>
                  <div className="app-logo" style={{ marginBottom: 'var(--spacing-lg)' }}>
                    <svg width="64" height="64" viewBox="0 0 32 32" fill="none">
                      <rect width="32" height="32" rx="8" fill="var(--color-primary)"/>
                      <path d="M8 20L14 14L18 16L24 8" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                      <circle cx="16" cy="16" r="6" stroke="white" strokeWidth="1.5"/>
                    </svg>
                  </div>
                  <h3 style={{ marginBottom: 'var(--spacing-xs)' }}>FieldShift</h3>
                  <p className="app-version">Version 2.0.0 (MVP)</p>
                  <p style={{ color: 'var(--color-text-secondary)', marginTop: 'var(--spacing-md)', maxWidth: '400px', margin: 'var(--spacing-md) auto 0' }}>
                    Plateforme intelligente d'analyse agricole et d'adaptation climatique grâce aux données satellitaires et environnementales.
                  </p>
                </div>
              </div>

              <div className="card" style={{ marginTop: 'var(--spacing-lg)' }}>
                <div className="card-body">
                  <h3>Sources de données</h3>
                  <ul className="data-sources-list">
                    <li><strong>NASA POWER</strong> - Données climatiques (température, précipitations, rayonnement)</li>
                    <li><strong>ESA Sentinel-2</strong> - Imagerie multispectrale haute résolution (10m)</li>
                    <li><strong>NASA Landsat</strong> - Imagerie multispectrale historique (30m)</li>
                    <li><strong>NASA SMAP</strong> - Humidité des sols</li>
                    <li><strong>NASA GPM IMERG</strong> - Précipitations satellitaires</li>
                    <li><strong>FAO GAEZ</strong> - Aptitude des terres et potentiel agricole</li>
                    <li><strong>NASA SRTM</strong> - Modèle numérique de terrain</li>
                    <li><strong>NASA GLDAS</strong> - Variables hydrologiques</li>
                  </ul>
                </div>
              </div>

              <div className="card" style={{ marginTop: 'var(--spacing-lg)' }}>
                <div className="card-body">
                  <h3>Technologies</h3>
                  <div className="tech-grid">
                    <span className="tech-tag">React 18</span>
                    <span className="tech-tag">Vite</span>
                    <span className="tech-tag">Leaflet</span>
                    <span className="tech-tag">Recharts</span>
                    <span className="tech-tag">FastAPI (Backend)</span>
                    <span className="tech-tag">Python</span>
                    <span className="tech-tag">Pandas/NumPy</span>
                    <span className="tech-tag">GeoPandas/Rasterio</span>
                    <span className="tech-tag">Supabase</span>
                    <span className="tech-tag">PWA</span>
                  </div>
                </div>
              </div>

              <div className="card" style={{ marginTop: 'var(--spacing-lg)' }}>
                <div className="card-body">
                  <h3>Liens utiles</h3>
                  <div className="links-grid">
                    <a href="#" className="link-item">
                      <Mail size={18} aria-hidden="true" />
                      <div>
                        <strong>Contact & Support</strong>
                        <p>support@fieldshift.app</p>
                      </div>
                    </a>
                    <a href="#" className="link-item">
                      <FileText size={18} aria-hidden="true" />
                      <div>
                        <strong>Documentation</strong>
                        <p>docs.fieldshift.app</p>
                      </div>
                    </a>
                    <a href="#" className="link-item">
                      <Shield size={18} aria-hidden="true" />
                      <div>
                        <strong>Politique de confidentialité</strong>
                        <p>privacy.fieldshift.app</p>
                      </div>
                    </a>
                    <a href="#" className="link-item">
                      <AlertCircle size={18} aria-hidden="true" />
                      <div>
                        <strong>Conditions d'utilisation</strong>
                        <p>terms.fieldshift.app</p>
                      </div>
                    </a>
                  </div>
                </div>
              </div>

              <div className="card" style={{ marginTop: 'var(--spacing-lg)' }}>
                <div className="card-body text-center">
                  <p style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>
                    FieldShift est un projet open source. Les analyses constituent une aide à la décision
                    et non une prescription agronomique définitive. Validation humaine recommandée
                    pour les décisions importantes.
                  </p>
                  <p style={{ color: 'var(--color-text-muted)', fontSize: '0.75rem', marginTop: 'var(--spacing-sm)' }}>
                    © 2025 FieldShift. Tous droits réservés.
                  </p>
                </div>
              </div>
            </section>
          )}
        </div>
      </div>
    </div>
  )
}
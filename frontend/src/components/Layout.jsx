import { Outlet, NavLink, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import {
  LayoutDashboard,
  MapPin,
  Eye,
  Leaf,
  FileText,
  Settings,
  Menu,
  X,
  ChevronLeft,
  ChevronRight,
  Sun,
  Moon,
  Bell,
  User,
  LogOut,
  HelpCircle,
  Globe
} from 'lucide-react'
import './Layout.css'

const navigation = [
  { path: '/dashboard', label: 'Vue d\'ensemble', icon: LayoutDashboard },
  { path: '/farms', label: 'Mes exploitations', icon: MapPin },
  { path: '/monitoring', label: 'Surveillance', icon: Eye },
  { path: '/crops', label: 'Cultures et rotations', icon: Leaf },
  { path: '/reports', label: 'Rapports', icon: FileText },
]

const secondaryNavigation = [
  { path: '/settings', label: 'Paramètres', icon: Settings },
  { path: '/help', label: 'Aide', icon: HelpCircle },
]

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [darkMode, setDarkMode] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('darkMode')
      if (saved !== null) return JSON.parse(saved)
      return window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    return false
  })
  const location = useLocation()

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode)
    localStorage.setItem('darkMode', JSON.stringify(darkMode))
  }, [darkMode])

  useEffect(() => {
    setSidebarOpen(false)
  }, [location.pathname])

  const currentFarm = { name: 'Exploitation Demo', region: 'Nouvelle-Aquitaine, France' }

  return (
    <div className="layout">
      <a href="#main-content" className="skip-link">Aller au contenu principal</a>

      <aside
        className={`sidebar ${sidebarOpen ? 'open' : ''} ${sidebarCollapsed ? 'collapsed' : ''}`}
        role="navigation"
        aria-label="Navigation principale"
      >
        <div className="sidebar-header">
          {!sidebarCollapsed && (
            <div className="logo">
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none" aria-hidden="true">
                <rect width="32" height="32" rx="8" fill="currentColor"/>
                <path d="M8 20L14 14L18 16L24 8" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                <circle cx="16" cy="16" r="6" stroke="white" strokeWidth="1.5"/>
              </svg>
              <span>FieldShift</span>
            </div>
          )}
          <button
            className="sidebar-toggle"
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            aria-label={sidebarCollapsed ? 'Étendre la barre latérale' : 'Réduire la barre latérale'}
            aria-expanded={!sidebarCollapsed}
          >
            {sidebarCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
          </button>
        </div>

        <nav className="sidebar-nav">
          <ul role="list">
            {navigation.map((item) => (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                  aria-current={location.pathname === item.path ? 'page' : undefined}
                >
                  <item.icon size={20} aria-hidden="true" />
                  {!sidebarCollapsed && <span>{item.label}</span>}
                </NavLink>
              </li>
            ))}
          </ul>

          <div className="sidebar-divider" />

          <ul role="list">
            {secondaryNavigation.map((item) => (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                >
                  <item.icon size={20} aria-hidden="true" />
                  {!sidebarCollapsed && <span>{item.label}</span>}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        {!sidebarCollapsed && (
          <div className="sidebar-footer">
            <div className="current-farm">
              <MapPin size={16} aria-hidden="true" />
              <div>
                <p className="farm-name">{currentFarm.name}</p>
                <p className="farm-region">{currentFarm.region}</p>
              </div>
            </div>
          </div>
        )}
      </aside>

      {sidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      <header className="header" role="banner">
        <button
          className="mobile-menu-btn"
          onClick={() => setSidebarOpen(true)}
          aria-label="Ouvrir le menu"
          aria-expanded={sidebarOpen}
          aria-controls="sidebar"
        >
          <Menu size={24} />
        </button>

        <div className="header-title">
          <h1 id="page-title">{getPageTitle(location.pathname)}</h1>
        </div>

        <div className="header-actions">
          <button
            className="icon-btn"
            onClick={() => setDarkMode(!darkMode)}
            aria-label={darkMode ? 'Mode clair' : 'Mode sombre'}
            aria-pressed={darkMode}
          >
            {darkMode ? <Sun size={20} /> : <Moon size={20} />}
          </button>

          <button className="icon-btn" aria-label="Notifications">
            <Bell size={20} />
            <span className="notification-badge">3</span>
          </button>

          <div className="user-menu">
            <button className="user-btn" aria-label="Menu utilisateur" aria-expanded="false" aria-haspopup="true">
              <User size={20} />
              {!sidebarCollapsed && <span>Utilisateur</span>}
            </button>
          </div>
        </div>
      </header>

      <main id="main-content" className="main" role="main" tabIndex={-1}>
        <Outlet />
      </main>
    </div>
  )
}

function getPageTitle(pathname) {
  const titles = {
    '/dashboard': 'Tableau de bord',
    '/farms': 'Mes exploitations',
    '/monitoring': 'Surveillance',
    '/crops': 'Cultures et rotations',
    '/reports': 'Rapports',
    '/settings': 'Paramètres',
  }

  for (const [path, title] of Object.entries(titles)) {
    if (pathname.startsWith(path)) return title
  }
  return 'FieldShift'
}
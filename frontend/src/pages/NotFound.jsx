import { Link } from 'react-router-dom'
import { Home, RotateCcw, Search } from 'lucide-react'
import './NotFound.css'

export default function NotFound() {
  return (
    <div className="not-found">
      <div className="not-found-content">
        <div className="error-code">404</div>
        <h1>Page introuvable</h1>
        <p>La page que vous recherchez n'existe pas ou a été déplacée.</p>
        <div className="not-found-actions">
          <Link to="/" className="btn btn-primary">
            <Home size={18} aria-hidden="true" />
            Retour à l'accueil
          </Link>
          <Link to="/dashboard" className="btn btn-secondary">
            <RotateCcw size={18} aria-hidden="true" />
            Tableau de bord
          </Link>
        </div>
        <div className="not-found-help">
          <p>Ou essayez de chercher :</p>
          <form className="search-form" onSubmit={(e) => { e.preventDefault(); window.location.href = '/dashboard'; }}>
            <Search size={18} aria-hidden="true" />
            <input type="search" placeholder="Rechercher dans FieldShift..." className="input" />
            <button type="submit" className="btn btn-ghost">Chercher</button>
          </form>
        </div>
      </div>
      <div className="not-found-illustration" aria-hidden="true">
        <svg viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="100" cy="100" r="90" stroke="currentColor" strokeWidth="2" strokeDasharray="8,4" opacity="0.3"/>
          <path d="M60 100L90 130L140 70" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" opacity="0.5"/>
          <circle cx="100" cy="100" r="30" stroke="currentColor" strokeWidth="1.5" opacity="0.3"/>
        </svg>
      </div>
    </div>
  )
}
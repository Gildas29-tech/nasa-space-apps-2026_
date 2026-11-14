import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import Farms from './pages/Farms'
import FarmDetail from './pages/FarmDetail'
import Monitoring from './pages/Monitoring'
import Crops from './pages/Crops'
import Reports from './pages/Reports'
import Settings from './pages/Settings'
import NotFound from './pages/NotFound'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="farms" element={<Farms />} />
        <Route path="farms/:id" element={<FarmDetail />} />
        <Route path="monitoring" element={<Monitoring />} />
        <Route path="crops" element={<Crops />} />
        <Route path="reports" element={<Reports />} />
        <Route path="settings" element={<Settings />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}

export default App
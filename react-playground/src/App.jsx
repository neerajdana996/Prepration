import { Routes, Route, Navigate, NavLink } from 'react-router-dom'
import ExperimentsPage from './pages/ExperimentsPage'
import MachineCodingPage from './pages/MachineCodingPage'
import RealAppPage from './pages/RealAppPage'
import Dashboard from './dashboard/Dashboard'
import './App.css'

const tabs = [
  { to: '/experiments', label: 'Experiments' },
  { to: '/machine-coding', label: 'Machine coding' },
  { to: '/real-app', label: 'Real app' },
  { to: '/dashboard', label: 'Dashboard' },
]

export default function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>React Playground</h1>
        <nav className="tabs">
          {tabs.map((t) => (
            <NavLink
              key={t.to}
              to={t.to}
              className={({ isActive }) => 'tab' + (isActive ? ' tab-active' : '')}
            >
              {t.label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main className="app-main">
        <Routes>
          <Route path="/" element={<Navigate to="/experiments" replace />} />
          <Route path="/experiments" element={<ExperimentsPage />} />
          <Route path="/machine-coding" element={<MachineCodingPage />} />
          <Route path="/real-app" element={<RealAppPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </main>
    </div>
  )
}

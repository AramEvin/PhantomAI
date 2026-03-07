import React from 'react'
import SearchBar from './components/ui/SearchBar'
import ResultsDashboard from './components/tools/ResultsDashboard'
import HistoryPanel from './components/ui/HistoryPanel'
import Header from './components/layout/Header'
import { useInvestigationStore } from './store/investigationStore'

export default function App() {
  const { investigation, isLoading, investigate } = useInvestigationStore()

  return (
    <div style={{ minHeight: '100vh', background: '#0a0a0f', color: '#e2e8f0', fontFamily: 'Inter, sans-serif' }}>
      <div style={{ position: 'fixed', inset: 0, pointerEvents: 'none', overflow: 'hidden', zIndex: 0 }}>
        <div style={{
          position: 'absolute', top: 0, left: '50%', transform: 'translateX(-50%)',
          width: 700, height: 300,
          background: 'radial-gradient(ellipse, rgba(124,58,237,0.1) 0%, transparent 70%)',
          borderRadius: '50%'
        }} />
      </div>

      <div style={{ position: 'relative', zIndex: 1, maxWidth: 1400, margin: '0 auto', padding: '2rem 1.5rem' }}>
        <Header />
        <SearchBar />

        {(investigation || isLoading) ? (
          <div style={{
            marginTop: '2rem',
            display: 'flex',
            gap: '1.5rem',
            alignItems: 'flex-start'
          }}>
            {/* Main results - takes all available space */}
            <div style={{ flex: 1, minWidth: 0 }}>
              <ResultsDashboard />
            </div>
            {/* Sidebar - fixed width */}
            <div style={{ width: 220, flexShrink: 0 }}>
              <HistoryPanel />
            </div>
          </div>
        ) : (
          <div style={{ marginTop: '5rem', textAlign: 'center' }}>
            <p style={{ color: '#475569', fontFamily: 'monospace', fontSize: 13, marginBottom: '1rem' }}>
              Try one of these examples:
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 8 }}>
              {['8.8.8.8', '1.1.1.1', 'github.com', 'google.com', 'cloudflare.com'].map(ex => (
                <button key={ex} onClick={() => investigate(ex)} style={{
                  padding: '8px 16px', background: '#12121a', border: '1px solid #1e1e2e',
                  borderRadius: 8, fontFamily: 'monospace', fontSize: 13, color: '#64748b',
                  cursor: 'pointer'
                }}
                  onMouseEnter={e => { (e.target as HTMLElement).style.color = '#a78bfa'; (e.target as HTMLElement).style.borderColor = '#6d28d9' }}
                  onMouseLeave={e => { (e.target as HTMLElement).style.color = '#64748b'; (e.target as HTMLElement).style.borderColor = '#1e1e2e' }}
                >{ex}</button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

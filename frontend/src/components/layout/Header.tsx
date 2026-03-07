import React from 'react'

export default function Header() {
  const tools = [
    { name: 'GeoIP',      icon: '🌍' },
    { name: 'DNS',        icon: '📡' },
    { name: 'WHOIS',      icon: '📋' },
    { name: 'SSL',        icon: '🔒' },
    { name: 'Subdomains', icon: '🔗' },
    { name: 'HTTP',       icon: '🌐' },
    { name: 'Shodan',     icon: '👁️' },
    { name: 'VirusTotal', icon: '🦠' },
    { name: 'Blacklist',  icon: '🚫' },
  ]

  return (
    <header style={{ textAlign: 'center', marginBottom: '3rem' }}>

      {/* Logo + Name */}
      <div style={{ display: 'inline-flex', alignItems: 'center', gap: 16, marginBottom: 12 }}>
        <img
          src="/phantom-logo.png"
          style={{ width: 72, height: 72, objectFit: 'contain', filter: 'drop-shadow(0 0 16px rgba(124,58,237,0.6))' }}
        />
        <div style={{ textAlign: 'left' }}>
          <h1 style={{ fontSize: 48, fontWeight: 800, margin: 0, letterSpacing: '-2px', lineHeight: 1 }}>
            <span style={{ color: '#fff' }}>Phantom</span>
            <span style={{ color: '#a78bfa' }}>AI</span>
          </h1>
          <p style={{ color: '#475569', fontFamily: 'monospace', fontSize: 12, margin: '4px 0 0', letterSpacing: 2 }}>
            OSINT INTELLIGENCE PLATFORM
          </p>
        </div>
      </div>

      {/* Divider */}
      <div style={{ width: '100%', height: 1, background: 'linear-gradient(90deg, transparent, #1e1e2e, #7c3aed33, #1e1e2e, transparent)', marginBottom: 20 }} />

      {/* Tool badges */}
      <div style={{ display: 'flex', justifyContent: 'center', flexWrap: 'wrap', gap: 8 }}>
        {tools.map(t => (
          <div key={t.name} style={{
            display: 'flex', alignItems: 'center', gap: 6,
            padding: '6px 14px',
            background: 'rgba(124,58,237,0.06)',
            border: '1px solid rgba(124,58,237,0.15)',
            borderRadius: 20,
            fontSize: 12, color: '#64748b',
            fontFamily: 'monospace',
            transition: 'all 0.2s',
          }}
            onMouseEnter={e => {
              (e.currentTarget as HTMLElement).style.background = 'rgba(124,58,237,0.15)'
              ;(e.currentTarget as HTMLElement).style.color = '#a78bfa'
              ;(e.currentTarget as HTMLElement).style.borderColor = 'rgba(124,58,237,0.4)'
            }}
            onMouseLeave={e => {
              (e.currentTarget as HTMLElement).style.background = 'rgba(124,58,237,0.06)'
              ;(e.currentTarget as HTMLElement).style.color = '#64748b'
              ;(e.currentTarget as HTMLElement).style.borderColor = 'rgba(124,58,237,0.15)'
            }}
          >
            <span style={{ fontSize: 14 }}>{t.icon}</span>
            {t.name}
          </div>
        ))}
      </div>
    </header>
  )
}

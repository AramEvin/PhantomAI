import React from 'react'

const TOOLS = [
  { id: 'geoip',         icon: '🌍', label: 'GeoIP' },
  { id: 'dns',           icon: '📡', label: 'DNS' },
  { id: 'whois',         icon: '📋', label: 'WHOIS' },
  { id: 'ssl',           icon: '🔒', label: 'SSL' },
  { id: 'subdomains',    icon: '🔗', label: 'Subdomains' },
  { id: 'http_headers',  icon: '🌐', label: 'HTTP Headers' },
  { id: 'shodan',        icon: '👁️', label: 'Shodan' },
  { id: 'virustotal',    icon: '🦠', label: 'VirusTotal' },
  { id: 'blacklist',     icon: '🚫', label: 'Blacklist' },
  { id: 'nmap',          icon: '🔬', label: 'Nmap' },
  { id: 'cve_lookup',    icon: '🛡', label: 'CVE Lookup' },
  { id: 'reverse_ip',    icon: '🔄', label: 'Reverse IP' },
  { id: 'whois_history', icon: '📅', label: 'WHOIS History' },
  { id: 'leakdb',        icon: '💧', label: 'Leak / Breach' },
  { id: 'bgp_asn',       icon: '🌐', label: 'BGP / ASN' },
]

export default function ScanProgress() {
  const [tick, setTick] = React.useState(0)

  React.useEffect(() => {
    const t = setInterval(() => setTick(x => x + 1), 400)
    return () => clearInterval(t)
  }, [])

  const dots = '.'.repeat((tick % 3) + 1).padEnd(3, ' ')

  return (
    <div style={{ background: '#12121a', border: '1px solid #1e1e2e', borderRadius: 12, padding: '24px' }}>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 18 }}>
        <div style={{
          width: 32, height: 32, borderRadius: '50%',
          border: '3px solid transparent',
          borderTopColor: '#a78bfa',
          borderRightColor: '#7c3aed',
          animation: 'spin 0.8s linear infinite',
          flexShrink: 0,
        }} />
        <style>{`@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}`}</style>
        <div>
          <div style={{ fontFamily: 'monospace', fontSize: 14, color: '#e2e8f0', fontWeight: 700 }}>
            Running {TOOLS.length} OSINT tools{dots}
          </div>
          <div style={{ fontFamily: 'monospace', fontSize: 11, color: '#475569', marginTop: 2 }}>
            GeoIP · DNS · WHOIS · SSL · Nmap · CVE · BGP/ASN · Breach Check · and more
          </div>
        </div>
      </div>

      {/* Animated progress bar */}
      <div style={{ height: 3, background: 'rgba(255,255,255,0.05)', borderRadius: 2, marginBottom: 18, overflow: 'hidden' }}>
        <div style={{
          height: '100%', width: '40%',
          background: 'linear-gradient(90deg, transparent, #7c3aed, #a78bfa, transparent)',
          borderRadius: 2,
          animation: 'slide 1.5s ease-in-out infinite',
        }} />
        <style>{`@keyframes slide{0%{transform:translateX(-200%)}100%{transform:translateX(400%)}}`}</style>
      </div>

      {/* Tool grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 5 }}>
        {TOOLS.map((t, i) => {
          // Stagger the "pulsing" animation so tools light up in sequence
          const phase = (tick + i * 2) % (TOOLS.length * 2)
          const isActive = phase < 3

          return (
            <div key={t.id} style={{
              display: 'flex', alignItems: 'center', gap: 6,
              padding: '6px 8px', borderRadius: 7,
              background: isActive ? 'rgba(124,58,237,0.12)' : 'rgba(0,0,0,0.2)',
              border: `1px solid ${isActive ? '#7c3aed50' : '#1e1e2e'}`,
              transition: 'all 0.2s',
            }}>
              <span style={{ fontSize: 12 }}>{t.icon}</span>
              <span style={{
                fontSize: 10, fontFamily: 'monospace',
                color: isActive ? '#a78bfa' : '#334155',
                transition: 'color 0.2s',
              }}>
                {t.label}
              </span>
              {isActive && (
                <span style={{ marginLeft: 'auto', fontSize: 9, color: '#7c3aed', fontFamily: 'monospace' }}>
                  ⟳
                </span>
              )}
            </div>
          )
        })}
      </div>

      {/* AI note */}
      <div style={{
        marginTop: 12, padding: '8px 12px', borderRadius: 8,
        background: 'rgba(124,58,237,0.06)',
        border: '1px solid #3b2d6e',
        display: 'flex', alignItems: 'center', gap: 8,
      }}>
        <span style={{ fontSize: 14 }}>🧠</span>
        <span style={{ fontSize: 11, fontFamily: 'monospace', color: '#7c3aed' }}>
          AI analysis (up to 11 providers) will run after all tools complete
        </span>
      </div>
    </div>
  )
}

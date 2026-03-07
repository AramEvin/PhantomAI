import React, { useEffect } from 'react'
import { useInvestigationStore } from '../../store/investigationStore'

const RISK_COLOR: Record<string, string> = {
  critical: '#ef4444', high: '#f97316', medium: '#f59e0b', low: '#10b981'
}

function timeAgo(ts: string): string {
  const diff = Date.now() - new Date(ts).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1) return 'just now'
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}

export default function HistoryPanel() {
  const { history, historyLoading, loadHistory, loadScan, deleteScan } = useInvestigationStore()

  useEffect(() => { loadHistory() }, [])

  if (historyLoading) {
    return (
      <div style={{ background: '#12121a', border: '1px solid #1e1e2e', borderRadius: 12, padding: 16 }}>
        <div style={{ fontSize: 11, fontFamily: 'monospace', color: '#334155' }}>Loading history...</div>
      </div>
    )
  }

  if (history.length === 0) {
    return (
      <div style={{ background: '#12121a', border: '1px solid #1e1e2e', borderRadius: 12, padding: 16 }}>
        <div style={{ fontSize: 11, fontFamily: 'monospace', color: '#334155', textAlign: 'center' }}>
          No scans yet
        </div>
      </div>
    )
  }

  return (
    <div style={{ background: '#12121a', border: '1px solid #1e1e2e', borderRadius: 12, padding: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
        <span style={{ fontSize: 11, fontFamily: 'monospace', color: '#475569', textTransform: 'uppercase', letterSpacing: 1 }}>
          🕐 Scan History
        </span>
        <span style={{ fontSize: 10, fontFamily: 'monospace', color: '#334155' }}>
          {history.length} scans
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        {history.map(scan => (
          <div key={scan.id} style={{
            borderRadius: 8, border: '1px solid #1e1e2e',
            overflow: 'hidden', transition: 'border-color 0.2s'
          }}
            onMouseEnter={e => (e.currentTarget.style.borderColor = '#2d2d3d')}
            onMouseLeave={e => (e.currentTarget.style.borderColor = '#1e1e2e')}
          >
            <button onClick={() => loadScan(scan.id)} style={{
              width: '100%', textAlign: 'left', padding: '8px 10px',
              background: 'none', border: 'none', cursor: 'pointer',
            }}
              onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.02)')}
              onMouseLeave={e => (e.currentTarget.style.background = 'none')}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontFamily: 'monospace', fontSize: 12, color: '#cbd5e1', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 130 }}>
                  {scan.target}
                </span>
                {scan.risk_level && (
                  <span style={{ fontSize: 10, fontFamily: 'monospace', fontWeight: 700, color: RISK_COLOR[scan.risk_level] || '#64748b', flexShrink: 0, marginLeft: 6 }}>
                    {scan.risk_level.toUpperCase()}
                  </span>
                )}
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 3 }}>
                <span style={{ fontSize: 10, fontFamily: 'monospace', color: '#334155' }}>
                  {scan.tools_success}/{scan.tools_run} tools
                </span>
                <span style={{ fontSize: 10, fontFamily: 'monospace', color: '#334155' }}>
                  {timeAgo(scan.timestamp)}
                </span>
              </div>
            </button>

            {/* Delete button */}
            <button onClick={() => deleteScan(scan.id)} style={{
              width: '100%', padding: '4px', background: 'none', border: 'none',
              borderTop: '1px solid #1e1e2e', cursor: 'pointer',
              fontSize: 10, fontFamily: 'monospace', color: '#334155',
              transition: 'color 0.2s'
            }}
              onMouseEnter={e => { (e.currentTarget as HTMLElement).style.color = '#ef4444'; (e.currentTarget as HTMLElement).style.background = 'rgba(239,68,68,0.05)' }}
              onMouseLeave={e => { (e.currentTarget as HTMLElement).style.color = '#334155'; (e.currentTarget as HTMLElement).style.background = 'none' }}
            >
              🗑 delete
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

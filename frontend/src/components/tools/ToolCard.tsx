import React, { useState } from 'react'
import { ToolResult } from '../../store/investigationStore'

interface Props { toolName: string; result: ToolResult }

const TOOL_META: Record<string, { icon: string; label: string; color: string }> = {
  geoip:        { icon: '🌍', label: 'GeoIP Location',  color: '#10b981' },
  dns:          { icon: '📡', label: 'DNS Records',      color: '#3b82f6' },
  whois:        { icon: '📋', label: 'WHOIS',            color: '#8b5cf6' },
  ssl:          { icon: '🔒', label: 'SSL Certificate',  color: '#f59e0b' },
  subdomains:   { icon: '🔗', label: 'Subdomains',       color: '#06b6d4' },
  http_headers: { icon: '🌐', label: 'HTTP Headers',     color: '#6366f1' },
  shodan:       { icon: '👁️',  label: 'Shodan',          color: '#ec4899' },
  virustotal:   { icon: '🦠', label: 'VirusTotal',       color: '#ef4444' },
  blacklist:    { icon: '🚫', label: 'Blacklist Check',  color: '#f97316' },
}

function renderValue(val: any, depth = 0): React.ReactNode {
  if (val === null || val === undefined) return <span style={{ color: '#334155' }}>null</span>
  if (typeof val === 'boolean') return <span style={{ color: val ? '#10b981' : '#ef4444' }}>{String(val)}</span>
  if (typeof val === 'number') return <span style={{ color: '#fbbf24' }}>{val}</span>
  if (typeof val === 'string') return <span style={{ color: '#cbd5e1' }}>{val}</span>

  if (Array.isArray(val)) {
    if (val.length === 0) return <span style={{ color: '#334155' }}>[ ]</span>
    if (val.every(v => typeof v === 'string' || typeof v === 'number')) {
      return (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 4 }}>
          {val.slice(0, 20).map((v, i) => (
            <span key={i} style={{ padding: '1px 8px', background: '#1e1e2e', borderRadius: 4, fontSize: 11, fontFamily: 'monospace', color: '#94a3b8' }}>{v}</span>
          ))}
          {val.length > 20 && <span style={{ color: '#475569', fontSize: 11 }}>+{val.length - 20} more</span>}
        </div>
      )
    }
    return (
      <div style={{ marginLeft: 12, marginTop: 4, borderLeft: '1px solid #1e1e2e', paddingLeft: 8 }}>
        {val.slice(0, 8).map((v, i) => <div key={i} style={{ marginBottom: 2 }}>{renderValue(v, depth + 1)}</div>)}
        {val.length > 8 && <span style={{ color: '#475569', fontSize: 11 }}>+{val.length - 8} more</span>}
      </div>
    )
  }

  if (typeof val === 'object') {
    if (depth > 3) return <span style={{ color: '#334155', fontSize: 11 }}>[...]</span>
    return (
      <div style={{ marginLeft: 8, marginTop: 4 }}>
        {Object.entries(val).slice(0, 20).map(([k, v]) => (
          <div key={k} style={{ display: 'flex', gap: 8, marginBottom: 5, fontSize: 12 }}>
            <span style={{ color: '#c4b5fd', fontFamily: 'monospace', flexShrink: 0, minWidth: 100 }}>{k}:</span>
            <div>{renderValue(v, depth + 1)}</div>
          </div>
        ))}
        {Object.keys(val).length > 20 && <span style={{ color: '#475569', fontSize: 11 }}>+{Object.keys(val).length - 20} more</span>}
      </div>
    )
  }
  return <span style={{ color: '#cbd5e1' }}>{String(val)}</span>
}

export default function ToolCard({ toolName, result }: Props) {
  const [expanded, setExpanded] = useState(false)
  const meta = TOOL_META[toolName] || { icon: '🔧', label: toolName, color: '#64748b' }
  const isSuccess = result.status === 'success'
  const isSkipped = result.data?.skipped

  return (
    <div style={{
      background: '#12121a',
      border: `1px solid ${expanded ? meta.color + '33' : '#1e1e2e'}`,
      borderLeft: `3px solid ${isSkipped ? '#334155' : isSuccess ? meta.color : '#ef4444'}`,
      borderRadius: 10,
      overflow: 'hidden',
      transition: 'border-color 0.2s',
    }}>
      <button
        onClick={() => setExpanded(!expanded)}
        style={{
          width: '100%', display: 'flex', alignItems: 'center', gap: 14,
          padding: '14px 18px', background: 'none', border: 'none',
          cursor: 'pointer', textAlign: 'left',
        }}
        onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.02)')}
        onMouseLeave={e => (e.currentTarget.style.background = 'none')}
      >
        {/* Icon */}
        <div style={{
          width: 40, height: 40, borderRadius: 10, flexShrink: 0,
          background: `${meta.color}15`,
          border: `1px solid ${meta.color}30`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 20,
        }}>
          {meta.icon}
        </div>

        {/* Label + status */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontWeight: 600, fontSize: 14, color: '#e2e8f0', marginBottom: 3 }}>
            {meta.label}
          </div>
          <div style={{ fontSize: 11, color: '#475569', fontFamily: 'monospace', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {isSkipped ? result.data?.reason || 'Skipped — API key not configured'
             : result.error ? result.error.slice(0, 80)
             : result.duration_ms ? `Completed in ${result.duration_ms}ms`
             : ''}
          </div>
        </div>

        {/* Status badge */}
        <div style={{
          padding: '3px 10px', borderRadius: 20, fontSize: 11, fontFamily: 'monospace', fontWeight: 600, flexShrink: 0,
          background: isSkipped ? 'rgba(51,65,85,0.3)' : isSuccess ? `${meta.color}15` : 'rgba(239,68,68,0.15)',
          color: isSkipped ? '#475569' : isSuccess ? meta.color : '#ef4444',
          border: `1px solid ${isSkipped ? '#1e293b' : isSuccess ? meta.color + '40' : '#ef444440'}`,
        }}>
          {isSkipped ? '⏭ skipped' : isSuccess ? '✓ done' : '✗ error'}
        </div>

        <span style={{ color: '#334155', fontSize: 12, flexShrink: 0 }}>{expanded ? '▲' : '▼'}</span>
      </button>

      {expanded && (
        <div style={{
          borderTop: `1px solid ${meta.color}20`,
          padding: '14px 18px',
          fontFamily: 'monospace', fontSize: 12,
          maxHeight: 400, overflowY: 'auto',
          lineHeight: 1.7,
          background: 'rgba(0,0,0,0.2)',
        }}>
          {isSkipped
            ? <span style={{ color: '#475569' }}>{result.data?.reason || 'Configure the API key in backend/.env to enable this tool.'}</span>
            : result.error
            ? <span style={{ color: '#ef4444' }}>{result.error}</span>
            : result.data
            ? renderValue(result.data)
            : <span style={{ color: '#334155' }}>No data returned</span>
          }
        </div>
      )}
    </div>
  )
}

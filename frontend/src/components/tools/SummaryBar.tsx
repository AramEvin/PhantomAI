import React from 'react'
import { Investigation } from '../../store/investigationStore'

interface Props { investigation: Investigation }

export default function SummaryBar({ investigation }: Props) {
  const failCount = investigation.tools_run - investigation.tools_success
  return (
    <div style={{
      background: '#12121a', border: '1px solid #1e1e2e', borderRadius: 12,
      padding: '14px 20px', display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 16
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <span style={{ fontFamily: 'monospace', fontSize: 18, fontWeight: 700, color: '#a78bfa' }}>
          {investigation.target}
        </span>
        <span style={{
          fontSize: 11, background: '#1e1e2e', color: '#64748b',
          padding: '2px 8px', borderRadius: 4, fontFamily: 'monospace'
        }}>
          {investigation.target_type.toUpperCase()}
        </span>
      </div>
      <div style={{ marginLeft: 'auto', display: 'flex', gap: 16, fontFamily: 'monospace', fontSize: 13 }}>
        <span style={{ color: '#10b981' }}>✓ {investigation.tools_success} passed</span>
        {failCount > 0 && <span style={{ color: '#ef4444' }}>✗ {failCount} failed</span>}
        <span style={{ color: '#475569' }}>⏱ {(investigation.duration_ms / 1000).toFixed(1)}s</span>
      </div>
    </div>
  )
}

import React from 'react'
import { useInvestigationStore } from '../../store/investigationStore'
import AIAnalysisCard from './AIAnalysisCard'
import ToolCard from './ToolCard'
import SummaryBar from './SummaryBar'
import ScanProgress from './ScanProgress'

const TOOL_ORDER = ['geoip', 'whois', 'dns', 'ssl', 'subdomains', 'http_headers', 'shodan', 'virustotal', 'blacklist']

export default function ResultsDashboard() {
  const { investigation, isLoading, error } = useInvestigationStore()

  if (isLoading) {
    return <ScanProgress />
  }

  if (error) {
    return (
      <div style={{ background: 'rgba(127,29,29,0.3)', border: '1px solid #7f1d1d', borderRadius: 12, padding: 24, textAlign: 'center' }}>
        <p style={{ color: '#fca5a5', fontFamily: 'monospace', fontSize: 14 }}>⚠ {error}</p>
      </div>
    )
  }

  if (!investigation) return null

  const tools = TOOL_ORDER.filter(t => investigation.results[t])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      <SummaryBar investigation={investigation} />

      {investigation.ai_analysis
        ? <AIAnalysisCard analysis={investigation.ai_analysis} />
        : (
          <div style={{ background: 'rgba(124,58,237,0.06)', border: '1px dashed #3b2d6e', borderRadius: 12, padding: '16px 20px', display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ fontSize: 24 }}>🧠</span>
            <div>
              <p style={{ color: '#7c3aed', fontWeight: 600, fontSize: 14, marginBottom: 2 }}>AI Analysis unavailable</p>
              <p style={{ color: '#475569', fontSize: 12, fontFamily: 'monospace' }}>
                Configure at least one AI key in <span style={{ color: '#a78bfa' }}>backend/.env</span>
              </p>
            </div>
          </div>
        )
      }

      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 4 }}>
        <h2 style={{ fontSize: 14, fontWeight: 700, color: '#94a3b8', fontFamily: 'monospace', textTransform: 'uppercase', letterSpacing: 2, margin: 0 }}>
          🔧 OSINT Tool Results
        </h2>
        <div style={{ flex: 1, height: 1, background: '#1e1e2e' }} />
        <span style={{ fontSize: 11, fontFamily: 'monospace', color: '#334155' }}>
          {investigation.tools_success}/{investigation.tools_run} tools
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {tools.map(toolName => (
          <ToolCard key={toolName} toolName={toolName} result={investigation.results[toolName]} />
        ))}
      </div>
    </div>
  )
}

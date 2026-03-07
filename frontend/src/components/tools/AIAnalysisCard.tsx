import React, { useState } from 'react'
import { AIAnalysis } from '../../store/investigationStore'

interface Props { analysis: AIAnalysis }

const RISK: Record<string, { color: string; bg: string; border: string; label: string }> = {
  low:      { color: '#10b981', bg: 'rgba(6,78,59,0.2)',  border: '#064e3b', label: '🟢 LOW RISK' },
  medium:   { color: '#f59e0b', bg: 'rgba(78,55,6,0.2)',  border: '#78350f', label: '🟡 MEDIUM RISK' },
  high:     { color: '#f97316', bg: 'rgba(78,30,6,0.2)',  border: '#7c2d12', label: '🟠 HIGH RISK' },
  critical: { color: '#ef4444', bg: 'rgba(78,6,6,0.2)',   border: '#7f1d1d', label: '🔴 CRITICAL' },
}

const PORT_RISK_COLORS: Record<string, string> = {
  low: '#10b981', medium: '#f59e0b', high: '#f97316', critical: '#ef4444'
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  const [open, setOpen] = useState(true)
  return (
    <div style={{ marginBottom: 12 }}>
      <button onClick={() => setOpen(!open)} style={{
        width: '100%', display: 'flex', alignItems: 'center', gap: 8,
        background: 'none', border: 'none', cursor: 'pointer',
        padding: '6px 0', marginBottom: open ? 8 : 0
      }}>
        <span style={{ fontSize: 11, fontFamily: 'monospace', color: '#475569', textTransform: 'uppercase', letterSpacing: 1 }}>{title}</span>
        <div style={{ flex: 1, height: 1, background: '#1e1e2e' }} />
        <span style={{ color: '#334155', fontSize: 10 }}>{open ? '▲' : '▼'}</span>
      </button>
      {open && children}
    </div>
  )
}

export default function AIAnalysisCard({ analysis }: Props) {
  const risk = RISK[analysis.risk_level] || RISK.low
  const score = Math.min(100, Math.max(0, analysis.risk_score))
  const infra = analysis.infrastructure || {}
  const surface = analysis.attack_surface || {}
  const portRisks = analysis.port_risks || []
  const threat = analysis.threat_intel || {}

  return (
    <div style={{ background: risk.bg, border: `1px solid ${risk.border}`, borderRadius: 12, overflow: 'hidden' }}>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '14px 20px', borderBottom: `1px solid ${risk.border}` }}>
        <h2 style={{ margin: 0, fontSize: 13, fontWeight: 700, color: '#94a3b8', fontFamily: 'monospace', textTransform: 'uppercase', letterSpacing: 2 }}>
          🧠 Intelligence Report
        </h2>
        <span style={{ padding: '4px 14px', borderRadius: 20, fontSize: 12, fontFamily: 'monospace', fontWeight: 700, color: risk.color, background: 'rgba(0,0,0,0.3)', border: `1px solid ${risk.border}` }}>
          {risk.label}
        </span>
      </div>

      <div style={{ padding: '16px 20px' }}>

        {/* Risk Score Bar */}
        <div style={{ marginBottom: 14 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 5 }}>
            <span style={{ fontSize: 11, fontFamily: 'monospace', color: '#475569', textTransform: 'uppercase', letterSpacing: 1 }}>Risk Score</span>
            <span style={{ fontSize: 13, fontFamily: 'monospace', fontWeight: 700, color: risk.color }}>{score}/100</span>
          </div>
          <div style={{ height: 6, background: 'rgba(0,0,0,0.4)', borderRadius: 3 }}>
            <div style={{ height: '100%', width: `${score}%`, background: risk.color, borderRadius: 3, boxShadow: `0 0 10px ${risk.color}60`, transition: 'width 1.2s ease' }} />
          </div>
        </div>

        {/* Summary */}
        <p style={{ color: '#cbd5e1', fontSize: 13, lineHeight: 1.75, marginBottom: 18, padding: '12px 16px', background: 'rgba(0,0,0,0.25)', borderRadius: 8, borderLeft: `3px solid ${risk.color}` }}>
          {analysis.summary}
        </p>

        {/* Infrastructure Fingerprint */}
        {Object.keys(infra).length > 0 && (
          <Section title="🏗 Infrastructure Fingerprint">
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 8 }}>
              {infra.hosting_provider && infra.hosting_provider !== "Unknown" && (
                <div style={{ background: 'rgba(0,0,0,0.2)', borderRadius: 8, padding: '8px 12px' }}>
                  <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#475569', marginBottom: 3 }}>HOSTING</div>
                  <div style={{ fontSize: 12, color: '#cbd5e1' }}>{infra.hosting_provider}</div>
                </div>
              )}
              {infra.server_type && (
                <div style={{ background: 'rgba(0,0,0,0.2)', borderRadius: 8, padding: '8px 12px' }}>
                  <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#475569', marginBottom: 3 }}>SERVER</div>
                  <div style={{ fontSize: 12, color: '#cbd5e1' }}>{infra.server_type}</div>
                </div>
              )}
              {infra.cloud_provider && infra.cloud_provider !== "Unknown" && (
                <div style={{ background: 'rgba(0,0,0,0.2)', borderRadius: 8, padding: '8px 12px' }}>
                  <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#475569', marginBottom: 3 }}>CDN/CLOUD</div>
                  <div style={{ fontSize: 12, color: '#a78bfa' }}>{infra.cloud_provider} {infra.cdn_detected ? '(CDN)' : ''}</div>
                </div>
              )}
            </div>
            {infra.fingerprint_notes?.length > 0 && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5 }}>
                {infra.fingerprint_notes.map((n: string, i: number) => (
                  <span key={i} style={{ padding: '2px 8px', background: 'rgba(124,58,237,0.15)', border: '1px solid rgba(124,58,237,0.2)', borderRadius: 4, fontSize: 11, fontFamily: 'monospace', color: '#a78bfa' }}>{n}</span>
                ))}
              </div>
            )}
          </Section>
        )}

        {/* Threat Intelligence */}
        {Object.keys(threat).length > 0 && (
          <Section title="🎯 Threat Intelligence">
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8, marginBottom: 8 }}>
              {threat.blacklist_status && (
                <div style={{ background: 'rgba(0,0,0,0.2)', borderRadius: 8, padding: '8px 12px', textAlign: 'center' }}>
                  <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#475569', marginBottom: 3 }}>BLACKLIST</div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: threat.blacklist_status === 'listed' ? '#ef4444' : '#10b981' }}>
                    {threat.blacklist_status === 'listed' ? `⚠ ${threat.blacklist_count} lists` : '✓ Clean'}
                  </div>
                </div>
              )}
              {threat.reputation_score !== undefined && (
                <div style={{ background: 'rgba(0,0,0,0.2)', borderRadius: 8, padding: '8px 12px', textAlign: 'center' }}>
                  <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#475569', marginBottom: 3 }}>REPUTATION</div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: threat.reputation_score >= 70 ? '#10b981' : threat.reputation_score >= 40 ? '#f59e0b' : '#ef4444' }}>
                    {threat.reputation_score}/100
                  </div>
                </div>
              )}
              {threat.malware_detected !== undefined && (
                <div style={{ background: 'rgba(0,0,0,0.2)', borderRadius: 8, padding: '8px 12px', textAlign: 'center' }}>
                  <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#475569', marginBottom: 3 }}>MALWARE</div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: threat.malware_detected ? '#ef4444' : '#10b981' }}>
                    {threat.malware_detected ? '⚠ Detected' : '✓ None'}
                  </div>
                </div>
              )}
            </div>
            {threat.threat_indicators?.length > 0 && (
              <div>
                {threat.threat_indicators.map((t: string, i: number) => (
                  <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 4, fontSize: 12, color: '#fca5a5' }}>
                    <span style={{ color: '#ef4444', flexShrink: 0 }}>⚠</span>{t}
                  </div>
                ))}
              </div>
            )}
          </Section>
        )}

        {/* Attack Surface */}
        {Object.keys(surface).length > 0 && (
          <Section title="🗺 Attack Surface">
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 8 }}>
              {surface.total_entry_points > 0 && (
                <div style={{ background: 'rgba(0,0,0,0.2)', borderRadius: 8, padding: '8px 12px' }}>
                  <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#475569', marginBottom: 3 }}>ENTRY POINTS</div>
                  <div style={{ fontSize: 18, fontWeight: 700, color: '#f59e0b' }}>{surface.total_entry_points}</div>
                </div>
              )}
              {surface.subdomains_count > 0 && (
                <div style={{ background: 'rgba(0,0,0,0.2)', borderRadius: 8, padding: '8px 12px' }}>
                  <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#475569', marginBottom: 3 }}>SUBDOMAINS</div>
                  <div style={{ fontSize: 18, fontWeight: 700, color: '#06b6d4' }}>{surface.subdomains_count}</div>
                </div>
              )}
            </div>
            {surface.critical_exposures?.length > 0 && (
              <div style={{ marginBottom: 8 }}>
                <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#ef4444', marginBottom: 5 }}>CRITICAL EXPOSURES</div>
                {surface.critical_exposures.map((e: string, i: number) => (
                  <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 4, fontSize: 12, color: '#fca5a5', alignItems: 'flex-start' }}>
                    <span style={{ color: '#ef4444', flexShrink: 0 }}>⚠</span>{e}
                  </div>
                ))}
              </div>
            )}
            {surface.ssl_issues?.length > 0 && (
              <div>
                <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#f59e0b', marginBottom: 5 }}>SSL/HEADER ISSUES</div>
                {surface.ssl_issues.slice(0, 5).map((s: string, i: number) => (
                  <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 3, fontSize: 12, color: '#fde68a' }}>
                    <span style={{ color: '#f59e0b', flexShrink: 0 }}>›</span>{s}
                  </div>
                ))}
              </div>
            )}
          </Section>
        )}

        {/* Port Risk Scoring */}
        {portRisks.length > 0 && (
          <Section title="🔌 Port & Service Risk">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              {portRisks.map((p: any, i: number) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '6px 10px', background: 'rgba(0,0,0,0.2)', borderRadius: 6, fontSize: 12 }}>
                  <span style={{ fontFamily: 'monospace', fontWeight: 700, color: '#a78bfa', minWidth: 40 }}>{p.port}</span>
                  <span style={{ color: '#64748b', flex: 1 }}>{p.note}</span>
                  <span style={{ padding: '1px 8px', borderRadius: 10, fontSize: 10, fontFamily: 'monospace', fontWeight: 700, background: `${PORT_RISK_COLORS[p.risk] || '#64748b'}20`, color: PORT_RISK_COLORS[p.risk] || '#64748b', border: `1px solid ${PORT_RISK_COLORS[p.risk] || '#64748b'}40` }}>
                    {p.risk.toUpperCase()}
                  </span>
                </div>
              ))}
            </div>
          </Section>
        )}

        {/* Key Findings + Recommendations */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginTop: 4 }}>
          {analysis.key_findings.length > 0 && (
            <Section title="🔍 Key Findings">
              {analysis.key_findings.map((f, i) => (
                <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 7, fontSize: 12, color: '#cbd5e1', alignItems: 'flex-start', lineHeight: 1.5 }}>
                  <span style={{ color: '#a78bfa', flexShrink: 0, marginTop: 2 }}>›</span>{f}
                </div>
              ))}
            </Section>
          )}
          {analysis.recommendations.length > 0 && (
            <Section title="✅ Recommendations">
              {analysis.recommendations.map((r, i) => (
                <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 7, fontSize: 12, color: '#cbd5e1', alignItems: 'flex-start', lineHeight: 1.5 }}>
                  <span style={{ color: '#10b981', flexShrink: 0, marginTop: 2 }}>✓</span>{r}
                </div>
              ))}
            </Section>
          )}
        </div>

        {/* Tags */}
        {analysis.tags.length > 0 && (
          <div style={{ marginTop: 10, display: 'flex', flexWrap: 'wrap', gap: 5 }}>
            {analysis.tags.map(tag => (
              <span key={tag} style={{ padding: '2px 10px', background: 'rgba(0,0,0,0.3)', color: '#475569', borderRadius: 20, fontSize: 11, fontFamily: 'monospace', border: '1px solid rgba(255,255,255,0.05)' }}>
                #{tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

import React, { useState } from 'react'

interface SeverityFinding {
  severity: 'critical' | 'medium' | 'ok'
  category: string
  title: string
  detail: string
  fix?: string | null
}

interface AIAnalysis {
  summary: string
  risk_level: string
  risk_score: number
  key_findings: string[]
  recommendations: string[]
  tags: string[]
  infrastructure: Record<string, any>
  attack_surface: Record<string, any>
  port_risks: Array<{ port: number; service: string; risk: string; note: string }>
  threat_intel: Record<string, any>
  severity_findings: SeverityFinding[]
}

const SEVERITY_CONFIG = {
  critical: { color: '#ef4444', bg: 'rgba(239,68,68,0.08)', border: 'rgba(239,68,68,0.25)', icon: '🔴', label: 'CRITICAL' },
  medium:   { color: '#f59e0b', bg: 'rgba(245,158,11,0.08)', border: 'rgba(245,158,11,0.25)', icon: '🟡', label: 'MEDIUM' },
  ok:       { color: '#10b981', bg: 'rgba(16,185,129,0.08)', border: 'rgba(16,185,129,0.25)', icon: '🟢', label: 'OK' },
}

const RISK_COLOR: Record<string, string> = {
  critical: '#ef4444', high: '#f97316', medium: '#f59e0b', low: '#10b981'
}

function FindingCard({ f }: { f: SeverityFinding }) {
  const [expanded, setExpanded] = useState(false)
  const cfg = SEVERITY_CONFIG[f.severity] || SEVERITY_CONFIG.ok
  const hasFix = f.fix && f.severity !== 'ok'

  return (
    <div style={{
      borderRadius: 10, border: `1px solid ${cfg.border}`,
      background: cfg.bg, overflow: 'hidden', transition: 'all 0.2s'
    }}>
      {/* Header row */}
      <div
        onClick={() => hasFix && setExpanded(!expanded)}
        style={{
          display: 'flex', alignItems: 'center', gap: 10,
          padding: '10px 14px',
          cursor: hasFix ? 'pointer' : 'default'
        }}
      >
        <span style={{ fontSize: 14 }}>{cfg.icon}</span>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            <span style={{
              fontSize: 10, fontFamily: 'monospace', fontWeight: 700,
              color: cfg.color, letterSpacing: 1
            }}>{cfg.label}</span>
            <span style={{
              fontSize: 10, fontFamily: 'monospace', color: '#475569',
              background: 'rgba(255,255,255,0.05)', padding: '1px 6px',
              borderRadius: 4, border: '1px solid #1e1e2e'
            }}>{f.category}</span>
          </div>
          <div style={{ fontSize: 13, color: '#e2e8f0', fontWeight: 600, marginTop: 2 }}>
            {f.title}
          </div>
          <div style={{ fontSize: 12, color: '#64748b', fontFamily: 'monospace', marginTop: 2 }}>
            {f.detail}
          </div>
        </div>
        {hasFix && (
          <span style={{ fontSize: 12, color: '#475569', flexShrink: 0 }}>
            {expanded ? '▲' : '▼'} Fix
          </span>
        )}
      </div>

      {/* Expanded fix section */}
      {expanded && hasFix && (
        <div style={{
          borderTop: `1px solid ${cfg.border}`,
          padding: '12px 14px',
          background: 'rgba(0,0,0,0.2)'
        }}>
          <div style={{
            fontSize: 11, fontFamily: 'monospace', color: '#94a3b8',
            textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8
          }}>
            🔧 Remediation Steps
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            {f.fix!.split('\n').map((step, i) => (
              <div key={i} style={{
                fontSize: 12, color: '#cbd5e1', fontFamily: 'monospace',
                paddingLeft: 8, borderLeft: `2px solid ${cfg.color}40`
              }}>
                {step}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default function AIAnalysisCard({ analysis }: { analysis: AIAnalysis }) {
  const [section, setSection] = useState<string | null>('findings')

  const riskColor = RISK_COLOR[analysis.risk_level] || '#64748b'
  const pct = analysis.risk_score

  // Group findings by severity
  const critical = (analysis.severity_findings || []).filter(f => f.severity === 'critical')
  const medium = (analysis.severity_findings || []).filter(f => f.severity === 'medium')
  const ok = (analysis.severity_findings || []).filter(f => f.severity === 'ok')

  const toggle = (s: string) => setSection(prev => prev === s ? null : s)

  return (
    <div style={{ background: '#12121a', border: '1px solid #1e1e2e', borderRadius: 12, overflow: 'hidden' }}>

      {/* ── Header ── */}
      <div style={{
        padding: '16px 20px',
        background: 'linear-gradient(135deg, rgba(124,58,237,0.15), rgba(0,0,0,0))',
        borderBottom: '1px solid #1e1e2e'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: 20 }}>🧠</span>
            <div>
              <div style={{ fontSize: 14, fontWeight: 700, color: '#e2e8f0' }}>AI Security Analysis</div>
              <div style={{ fontSize: 11, fontFamily: 'monospace', color: '#475569' }}>Multi-provider intelligence report</div>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            {/* Severity counts */}
            {critical.length > 0 && (
              <span style={{ fontSize: 11, fontFamily: 'monospace', fontWeight: 700, color: '#ef4444', background: 'rgba(239,68,68,0.1)', padding: '3px 8px', borderRadius: 6, border: '1px solid rgba(239,68,68,0.3)' }}>
                🔴 {critical.length} Critical
              </span>
            )}
            {medium.length > 0 && (
              <span style={{ fontSize: 11, fontFamily: 'monospace', fontWeight: 700, color: '#f59e0b', background: 'rgba(245,158,11,0.1)', padding: '3px 8px', borderRadius: 6, border: '1px solid rgba(245,158,11,0.3)' }}>
                🟡 {medium.length} Medium
              </span>
            )}
            {ok.length > 0 && (
              <span style={{ fontSize: 11, fontFamily: 'monospace', fontWeight: 700, color: '#10b981', background: 'rgba(16,185,129,0.1)', padding: '3px 8px', borderRadius: 6, border: '1px solid rgba(16,185,129,0.3)' }}>
                🟢 {ok.length} OK
              </span>
            )}
            {/* Risk badge */}
            <span style={{
              fontSize: 12, fontFamily: 'monospace', fontWeight: 700,
              color: riskColor, background: `${riskColor}15`,
              padding: '4px 12px', borderRadius: 8,
              border: `1px solid ${riskColor}40`,
              textTransform: 'uppercase', letterSpacing: 1
            }}>
              {analysis.risk_level}
            </span>
          </div>
        </div>

        {/* Risk score bar */}
        <div style={{ marginTop: 12 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
            <span style={{ fontSize: 11, fontFamily: 'monospace', color: '#475569' }}>Risk Score</span>
            <span style={{ fontSize: 11, fontFamily: 'monospace', color: riskColor, fontWeight: 700 }}>{pct}/100</span>
          </div>
          <div style={{ height: 6, background: 'rgba(255,255,255,0.05)', borderRadius: 3, overflow: 'hidden' }}>
            <div style={{
              height: '100%', width: `${pct}%`, borderRadius: 3,
              background: pct > 60 ? '#ef4444' : pct > 40 ? '#f59e0b' : pct > 20 ? '#f97316' : '#10b981',
              transition: 'width 0.8s ease', boxShadow: `0 0 8px ${riskColor}60`
            }} />
          </div>
        </div>

        {/* Summary */}
        <p style={{ marginTop: 12, fontSize: 13, color: '#94a3b8', lineHeight: 1.6, borderLeft: `3px solid ${riskColor}`, paddingLeft: 10 }}>
          {analysis.summary}
        </p>

        {/* Tags */}
        {analysis.tags?.length > 0 && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 10 }}>
            {analysis.tags.map(tag => (
              <span key={tag} style={{
                fontSize: 10, fontFamily: 'monospace', color: '#64748b',
                background: 'rgba(255,255,255,0.03)', padding: '2px 8px',
                borderRadius: 4, border: '1px solid #1e1e2e'
              }}>#{tag}</span>
            ))}
          </div>
        )}
      </div>

      {/* ── Section Tabs ── */}
      <div style={{ display: 'flex', borderBottom: '1px solid #1e1e2e', overflowX: 'auto' }}>
        {[
          { id: 'findings', label: '🎯 Findings', count: (analysis.severity_findings || []).length },
          { id: 'infrastructure', label: '🏗 Infrastructure' },
          { id: 'attack', label: '🗺 Attack Surface' },
          { id: 'ports', label: '🔌 Ports' },
          { id: 'threat', label: '🦠 Threat Intel' },
        ].map(tab => (
          <button key={tab.id} onClick={() => toggle(tab.id)} style={{
            padding: '10px 16px', background: 'none', border: 'none',
            borderBottom: section === tab.id ? '2px solid #7c3aed' : '2px solid transparent',
            color: section === tab.id ? '#a78bfa' : '#475569',
            fontFamily: 'monospace', fontSize: 12, cursor: 'pointer',
            whiteSpace: 'nowrap', transition: 'color 0.2s'
          }}>
            {tab.label}{tab.count ? ` (${tab.count})` : ''}
          </button>
        ))}
      </div>

      {/* ── Findings Section ── */}
      {section === 'findings' && (
        <div style={{ padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: 8 }}>
          {(analysis.severity_findings || []).length === 0 ? (
            <div style={{ textAlign: 'center', color: '#334155', fontFamily: 'monospace', fontSize: 13, padding: 20 }}>
              No findings available
            </div>
          ) : (
            <>
              {critical.length > 0 && (
                <>
                  <div style={{ fontSize: 11, fontFamily: 'monospace', color: '#ef4444', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 4 }}>
                    🔴 Critical — Immediate Action Required
                  </div>
                  {critical.map((f, i) => <FindingCard key={i} f={f} />)}
                </>
              )}
              {medium.length > 0 && (
                <>
                  <div style={{ fontSize: 11, fontFamily: 'monospace', color: '#f59e0b', textTransform: 'uppercase', letterSpacing: 1, marginTop: critical.length > 0 ? 12 : 0, marginBottom: 4 }}>
                    🟡 Medium — Should Be Fixed
                  </div>
                  {medium.map((f, i) => <FindingCard key={i} f={f} />)}
                </>
              )}
              {ok.length > 0 && (
                <>
                  <div style={{ fontSize: 11, fontFamily: 'monospace', color: '#10b981', textTransform: 'uppercase', letterSpacing: 1, marginTop: 12, marginBottom: 4 }}>
                    🟢 OK — Good Practices Detected
                  </div>
                  {ok.map((f, i) => <FindingCard key={i} f={f} />)}
                </>
              )}
            </>
          )}
        </div>
      )}

      {/* ── Infrastructure ── */}
      {section === 'infrastructure' && analysis.infrastructure && (
        <div style={{ padding: '16px 20px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
            {[
              { label: 'Hosting', value: analysis.infrastructure.hosting_provider },
              { label: 'Cloud', value: analysis.infrastructure.cloud_provider },
              { label: 'Server', value: analysis.infrastructure.server_type },
              { label: 'CDN', value: analysis.infrastructure.cdn_detected ? 'Detected' : 'Not detected' },
            ].map(item => item.value && (
              <div key={item.label} style={{ background: 'rgba(255,255,255,0.02)', borderRadius: 8, padding: '10px 12px', border: '1px solid #1e1e2e' }}>
                <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#475569', textTransform: 'uppercase', letterSpacing: 1 }}>{item.label}</div>
                <div style={{ fontSize: 13, color: '#cbd5e1', marginTop: 2 }}>{item.value}</div>
              </div>
            ))}
          </div>
          {analysis.infrastructure.fingerprint_notes?.length > 0 && (
            <div style={{ marginTop: 10, display: 'flex', flexDirection: 'column', gap: 4 }}>
              {analysis.infrastructure.fingerprint_notes.map((note: string, i: number) => (
                <div key={i} style={{ fontSize: 12, color: '#64748b', fontFamily: 'monospace', paddingLeft: 8, borderLeft: '2px solid #7c3aed40' }}>{note}</div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── Attack Surface ── */}
      {section === 'attack' && analysis.attack_surface && (
        <div style={{ padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: 10 }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
            <div style={{ background: 'rgba(255,255,255,0.02)', borderRadius: 8, padding: '10px 12px', border: '1px solid #1e1e2e', textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 700, color: '#a78bfa' }}>{analysis.attack_surface.total_entry_points || 0}</div>
              <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#475569' }}>Entry Points</div>
            </div>
            <div style={{ background: 'rgba(255,255,255,0.02)', borderRadius: 8, padding: '10px 12px', border: '1px solid #1e1e2e', textAlign: 'center' }}>
              <div style={{ fontSize: 24, fontWeight: 700, color: '#06b6d4' }}>{analysis.attack_surface.subdomains_count || 0}</div>
              <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#475569' }}>Subdomains</div>
            </div>
          </div>
          {analysis.attack_surface.exposed_services?.length > 0 && (
            <div>
              <div style={{ fontSize: 11, fontFamily: 'monospace', color: '#475569', marginBottom: 6 }}>EXPOSED SERVICES</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {analysis.attack_surface.exposed_services.map((s: string, i: number) => (
                  <span key={i} style={{ fontSize: 11, fontFamily: 'monospace', color: '#a78bfa', background: 'rgba(124,58,237,0.1)', padding: '2px 8px', borderRadius: 4, border: '1px solid rgba(124,58,237,0.2)' }}>{s}</span>
                ))}
              </div>
            </div>
          )}
          {analysis.attack_surface.critical_exposures?.length > 0 && (
            <div>
              <div style={{ fontSize: 11, fontFamily: 'monospace', color: '#ef4444', marginBottom: 6 }}>CRITICAL EXPOSURES</div>
              {analysis.attack_surface.critical_exposures.map((e: string, i: number) => (
                <div key={i} style={{ fontSize: 12, color: '#fca5a5', fontFamily: 'monospace', paddingLeft: 8, borderLeft: '2px solid #ef444440' }}>{e}</div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ── Ports ── */}
      {section === 'ports' && (
        <div style={{ padding: '16px 20px' }}>
          {(analysis.port_risks || []).length === 0 ? (
            <div style={{ textAlign: 'center', color: '#334155', fontFamily: 'monospace', fontSize: 13 }}>No port data available</div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {analysis.port_risks.map((p, i) => {
                const rc = RISK_COLOR[p.risk] || '#64748b'
                return (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '8px 12px', background: 'rgba(255,255,255,0.02)', borderRadius: 8, border: '1px solid #1e1e2e' }}>
                    <span style={{ fontFamily: 'monospace', fontSize: 13, color: '#a78bfa', minWidth: 50 }}>{p.port}</span>
                    <span style={{ fontFamily: 'monospace', fontSize: 12, color: '#94a3b8', flex: 1 }}>{p.service}</span>
                    <span style={{ fontSize: 10, fontFamily: 'monospace', fontWeight: 700, color: rc, background: `${rc}15`, padding: '2px 8px', borderRadius: 4, border: `1px solid ${rc}30`, textTransform: 'uppercase' }}>{p.risk}</span>
                    <span style={{ fontSize: 11, color: '#475569', maxWidth: 200, textAlign: 'right' }}>{p.note}</span>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}

      {/* ── Threat Intel ── */}
      {section === 'threat' && analysis.threat_intel && (
        <div style={{ padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: 10 }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8 }}>
            <div style={{ background: 'rgba(255,255,255,0.02)', borderRadius: 8, padding: '10px 12px', border: '1px solid #1e1e2e', textAlign: 'center' }}>
              <div style={{ fontSize: 18, fontWeight: 700, color: analysis.threat_intel.blacklist_status === 'clean' ? '#10b981' : '#ef4444' }}>
                {analysis.threat_intel.blacklist_status === 'clean' ? '✓ Clean' : '✗ Listed'}
              </div>
              <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#475569' }}>Blacklist</div>
            </div>
            <div style={{ background: 'rgba(255,255,255,0.02)', borderRadius: 8, padding: '10px 12px', border: '1px solid #1e1e2e', textAlign: 'center' }}>
              <div style={{ fontSize: 18, fontWeight: 700, color: '#a78bfa' }}>{analysis.threat_intel.reputation_score ?? 'N/A'}</div>
              <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#475569' }}>Reputation</div>
            </div>
            <div style={{ background: 'rgba(255,255,255,0.02)', borderRadius: 8, padding: '10px 12px', border: '1px solid #1e1e2e', textAlign: 'center' }}>
              <div style={{ fontSize: 18, fontWeight: 700, color: analysis.threat_intel.malware_detected ? '#ef4444' : '#10b981' }}>
                {analysis.threat_intel.malware_detected ? '⚠ Yes' : '✓ None'}
              </div>
              <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#475569' }}>Malware</div>
            </div>
          </div>
          {analysis.threat_intel.threat_indicators?.length > 0 && (
            <div>
              <div style={{ fontSize: 11, fontFamily: 'monospace', color: '#475569', marginBottom: 6 }}>THREAT INDICATORS</div>
              {analysis.threat_intel.threat_indicators.map((t: string, i: number) => (
                <div key={i} style={{ fontSize: 12, color: '#94a3b8', fontFamily: 'monospace', paddingLeft: 8, borderLeft: '2px solid #f59e0b40', marginBottom: 3 }}>{t}</div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

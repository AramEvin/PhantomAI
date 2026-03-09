import React, { useState } from 'react'

interface SeverityFinding {
  severity: 'critical' | 'medium' | 'ok'
  category: string
  title: string
  detail: string
  fix?: string
}

interface CVEFinding {
  software: string
  cve_id: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  cvss_score: number
  description: string
  fix: string
}

interface AIAnalysis {
  summary?: string
  risk_level?: string
  risk_score?: number
  key_findings?: string[]
  recommendations?: string[]
  tags?: string[]
  infrastructure?: Record<string, any>
  attack_surface?: Record<string, any>
  port_risks?: any[]
  threat_intel?: Record<string, any>
  severity_findings?: SeverityFinding[]
  cve_findings?: CVEFinding[]
}

interface Props { analysis: AIAnalysis }

const RISK_COLOR: Record<string, string> = {
  critical: '#ef4444', high: '#f97316', medium: '#eab308', low: '#22c55e'
}
const SEV_COLOR: Record<string, string> = {
  critical: '#ef4444', medium: '#eab308', ok: '#22c55e'
}
const SEV_BG: Record<string, string> = {
  critical: 'rgba(239,68,68,0.08)', medium: 'rgba(234,179,8,0.08)', ok: 'rgba(34,197,94,0.08)'
}
const SEV_BORDER: Record<string, string> = {
  critical: 'rgba(239,68,68,0.25)', medium: 'rgba(234,179,8,0.25)', ok: 'rgba(34,197,94,0.2)'
}
const SEV_ICON: Record<string, string> = { critical: '🔴', medium: '🟡', ok: '🟢' }
const CVE_COLOR: Record<string, string> = {
  critical: '#ef4444', high: '#f97316', medium: '#eab308', low: '#22c55e'
}
const CVSS_BAR: Record<string, string> = {
  critical: '#ef4444', high: '#f97316', medium: '#eab308', low: '#22c55e'
}

function RiskBadge({ level }: { level: string }) {
  const color = RISK_COLOR[level] || '#94a3b8'
  return (
    <span style={{
      background: `${color}22`, border: `1px solid ${color}55`,
      color, borderRadius: 6, padding: '2px 10px',
      fontSize: 11, fontFamily: 'monospace', fontWeight: 700, textTransform: 'uppercase'
    }}>{level}</span>
  )
}

function ScoreRing({ score }: { score: number }) {
  const color = score >= 80 ? '#ef4444' : score >= 60 ? '#f97316' : score >= 40 ? '#eab308' : '#22c55e'
  const r = 20, circ = 2 * Math.PI * r
  const dash = (score / 100) * circ
  return (
    <div style={{ position: 'relative', width: 56, height: 56, flexShrink: 0 }}>
      <svg width="56" height="56" style={{ transform: 'rotate(-90deg)' }}>
        <circle cx="28" cy="28" r={r} fill="none" stroke="#1e1e2e" strokeWidth="5" />
        <circle cx="28" cy="28" r={r} fill="none" stroke={color} strokeWidth="5"
          strokeDasharray={`${dash} ${circ}`} strokeLinecap="round" />
      </svg>
      <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <span style={{ fontSize: 13, fontWeight: 800, fontFamily: 'monospace', color }}>{score}</span>
      </div>
    </div>
  )
}

function FindingCard({ f }: { f: SeverityFinding }) {
  const [open, setOpen] = useState(false)
  const color = SEV_COLOR[f.severity]
  return (
    <div style={{
      background: SEV_BG[f.severity], border: `1px solid ${SEV_BORDER[f.severity]}`,
      borderRadius: 8, overflow: 'hidden', marginBottom: 6
    }}>
      <div onClick={() => setOpen(!open)} style={{
        padding: '10px 14px', cursor: 'pointer',
        display: 'flex', alignItems: 'center', gap: 10
      }}>
        <span style={{ fontSize: 13 }}>{SEV_ICON[f.severity]}</span>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: '#e2e8f0', fontFamily: 'monospace' }}>{f.title}</div>
          <div style={{ fontSize: 11, color: '#64748b', marginTop: 2 }}>{f.category} · {f.detail.slice(0, 80)}{f.detail.length > 80 ? '…' : ''}</div>
        </div>
        {f.fix && (
          <span style={{ fontSize: 10, color, fontFamily: 'monospace', flexShrink: 0 }}>
            {open ? '▲ hide' : '▼ fix'}
          </span>
        )}
      </div>
      {open && (
        <div style={{ padding: '0 14px 12px', borderTop: `1px solid ${SEV_BORDER[f.severity]}` }}>
          <p style={{ fontSize: 12, color: '#94a3b8', fontFamily: 'monospace', margin: '8px 0 6px' }}>{f.detail}</p>
          {f.fix && (
            <div style={{ background: 'rgba(0,0,0,0.3)', borderRadius: 6, padding: '8px 12px' }}>
              <div style={{ fontSize: 10, color: '#475569', fontFamily: 'monospace', marginBottom: 4, textTransform: 'uppercase' }}>
                🔧 Remediation
              </div>
              {f.fix.split('\n').map((line, i) => (
                <div key={i} style={{ fontSize: 12, color: '#a78bfa', fontFamily: 'monospace', lineHeight: 1.8 }}>{line}</div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function CVECard({ c }: { c: CVEFinding }) {
  const [open, setOpen] = useState(false)
  const color = CVE_COLOR[c.severity] || '#94a3b8'
  const barColor = CVSS_BAR[c.severity] || '#94a3b8'
  return (
    <div style={{
      background: `${color}0d`, border: `1px solid ${color}33`,
      borderRadius: 8, overflow: 'hidden', marginBottom: 6
    }}>
      <div onClick={() => setOpen(!open)} style={{
        padding: '10px 14px', cursor: 'pointer',
        display: 'flex', alignItems: 'center', gap: 10
      }}>
        {/* CVSS score circle */}
        <div style={{
          width: 38, height: 38, borderRadius: '50%', flexShrink: 0,
          background: `${color}22`, border: `2px solid ${color}55`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          flexDirection: 'column'
        }}>
          <span style={{ fontSize: 11, fontWeight: 800, fontFamily: 'monospace', color, lineHeight: 1 }}>
            {c.cvss_score.toFixed(1)}
          </span>
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            <span style={{ fontSize: 13, fontWeight: 700, fontFamily: 'monospace', color: '#e2e8f0' }}>{c.cve_id}</span>
            <span style={{
              fontSize: 10, fontFamily: 'monospace', color,
              background: `${color}22`, border: `1px solid ${color}44`,
              borderRadius: 4, padding: '1px 6px', textTransform: 'uppercase'
            }}>{c.severity}</span>
          </div>
          <div style={{ fontSize: 11, color: '#64748b', marginTop: 2 }}>
            {c.software} · {c.description.slice(0, 70)}{c.description.length > 70 ? '…' : ''}
          </div>
        </div>
        {/* CVSS bar */}
        <div style={{ width: 60, flexShrink: 0 }}>
          <div style={{ height: 4, background: '#1e1e2e', borderRadius: 2, overflow: 'hidden' }}>
            <div style={{ height: '100%', width: `${(c.cvss_score / 10) * 100}%`, background: barColor, borderRadius: 2 }} />
          </div>
          <div style={{ fontSize: 9, color: '#334155', fontFamily: 'monospace', textAlign: 'right', marginTop: 2 }}>
            {open ? '▲' : '▼'} details
          </div>
        </div>
      </div>
      {open && (
        <div style={{ padding: '0 14px 12px', borderTop: `1px solid ${color}22` }}>
          <p style={{ fontSize: 12, color: '#94a3b8', fontFamily: 'monospace', margin: '8px 0 8px' }}>{c.description}</p>
          <div style={{ background: 'rgba(0,0,0,0.3)', borderRadius: 6, padding: '8px 12px' }}>
            <div style={{ fontSize: 10, color: '#475569', fontFamily: 'monospace', marginBottom: 4, textTransform: 'uppercase' }}>
              🔧 Fix
            </div>
            <div style={{ fontSize: 12, color: '#a78bfa', fontFamily: 'monospace' }}>{c.fix}</div>
          </div>
        </div>
      )}
    </div>
  )
}

export default function AIAnalysisCard({ analysis }: Props) {
  const [tab, setTab] = useState<'findings' | 'cve' | 'infra' | 'attack' | 'ports' | 'threat'>('findings')

  const findings = analysis.severity_findings || []
  const cves = analysis.cve_findings || []
  const critical = findings.filter(f => f.severity === 'critical')
  const medium = findings.filter(f => f.severity === 'medium')
  const ok = findings.filter(f => f.severity === 'ok')

  const cveCritical = cves.filter(c => c.severity === 'critical' || c.severity === 'high')
  const cveMedLow = cves.filter(c => c.severity === 'medium' || c.severity === 'low')

  const TABS = [
    { id: 'findings', label: '🎯 Findings', count: findings.length },
    { id: 'cve',      label: '🛡 CVEs',     count: cves.length },
    { id: 'infra',    label: '🏗 Infra',    count: null },
    { id: 'attack',   label: '🗺 Attack',   count: null },
    { id: 'ports',    label: '🔌 Ports',    count: (analysis.port_risks || []).length },
    { id: 'threat',   label: '🦠 Threat',   count: null },
  ] as const

  return (
    <div style={{ background: '#12121a', border: '1px solid #1e1e2e', borderRadius: 12, overflow: 'hidden' }}>

      {/* Header */}
      <div style={{ padding: '14px 16px', borderBottom: '1px solid #1e1e2e', display: 'flex', alignItems: 'center', gap: 14, flexWrap: 'wrap' }}>
        <ScoreRing score={analysis.risk_score || 0} />
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <span style={{ fontFamily: 'monospace', fontSize: 14, fontWeight: 700, color: '#e2e8f0' }}>🧠 AI Analysis</span>
            <RiskBadge level={analysis.risk_level || 'low'} />
            {/* Provider count badge */}
            <span style={{ fontSize: 10, fontFamily: 'monospace', color: '#475569', marginLeft: 'auto' }}>
              up to 11 AI providers
            </span>
          </div>
          {analysis.summary && (
            <p style={{ fontSize: 12, color: '#64748b', fontFamily: 'monospace', lineHeight: 1.5, margin: 0 }}>
              {analysis.summary.slice(0, 200)}{(analysis.summary.length > 200) ? '…' : ''}
            </p>
          )}
        </div>
      </div>

      {/* Severity badges row */}
      <div style={{ padding: '8px 16px', borderBottom: '1px solid #1e1e2e', display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center' }}>
        {[
          { label: `🔴 ${critical.length} Critical`, color: '#ef4444' },
          { label: `🟡 ${medium.length} Medium`,   color: '#eab308' },
          { label: `🟢 ${ok.length} OK`,            color: '#22c55e' },
          { label: `🛡 ${cves.length} CVEs`,         color: cves.length > 0 ? '#f97316' : '#334155' },
        ].map(b => (
          <span key={b.label} style={{ fontSize: 11, fontFamily: 'monospace', color: b.color, fontWeight: 600 }}>
            {b.label}
          </span>
        ))}
        {analysis.tags?.slice(0, 4).map(tag => (
          <span key={tag} style={{
            fontSize: 10, fontFamily: 'monospace', color: '#334155',
            background: '#0f0f18', border: '1px solid #1e1e2e',
            borderRadius: 4, padding: '1px 6px'
          }}>{tag}</span>
        ))}
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', borderBottom: '1px solid #1e1e2e', overflowX: 'auto' }}>
        {TABS.map(t => (
          <button key={t.id} onClick={() => setTab(t.id as any)} style={{
            padding: '8px 14px', fontSize: 11, fontFamily: 'monospace', cursor: 'pointer',
            border: 'none', borderBottom: tab === t.id ? '2px solid #a78bfa' : '2px solid transparent',
            background: 'transparent', color: tab === t.id ? '#a78bfa' : '#475569',
            fontWeight: tab === t.id ? 700 : 400, whiteSpace: 'nowrap', display: 'flex', alignItems: 'center', gap: 4
          }}>
            {t.label}
            {t.count != null && t.count > 0 && (
              <span style={{
                fontSize: 9, background: tab === t.id ? '#a78bfa33' : '#1e1e2e',
                color: tab === t.id ? '#a78bfa' : '#475569',
                borderRadius: 8, padding: '0 5px', minWidth: 16, textAlign: 'center'
              }}>{t.count}</span>
            )}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div style={{ padding: 14, maxHeight: 480, overflowY: 'auto' }}>

        {/* ── Findings Tab ── */}
        {tab === 'findings' && (
          <div>
            {findings.length === 0 ? (
              <p style={{ color: '#334155', fontFamily: 'monospace', fontSize: 12, textAlign: 'center', padding: 20 }}>
                No findings — run a scan to generate AI analysis
              </p>
            ) : (
              <>
                {critical.length > 0 && (
                  <div style={{ marginBottom: 10 }}>
                    <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#ef4444', textTransform: 'uppercase', marginBottom: 6, letterSpacing: 1 }}>
                      🔴 Critical ({critical.length})
                    </div>
                    {critical.map((f, i) => <FindingCard key={i} f={f} />)}
                  </div>
                )}
                {medium.length > 0 && (
                  <div style={{ marginBottom: 10 }}>
                    <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#eab308', textTransform: 'uppercase', marginBottom: 6, letterSpacing: 1 }}>
                      🟡 Medium ({medium.length})
                    </div>
                    {medium.map((f, i) => <FindingCard key={i} f={f} />)}
                  </div>
                )}
                {ok.length > 0 && (
                  <div>
                    <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#22c55e', textTransform: 'uppercase', marginBottom: 6, letterSpacing: 1 }}>
                      🟢 OK ({ok.length})
                    </div>
                    {ok.map((f, i) => <FindingCard key={i} f={f} />)}
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* ── CVE Tab ── */}
        {tab === 'cve' && (
          <div>
            {cves.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '20px 0' }}>
                <span style={{ fontSize: 28 }}>🛡</span>
                <p style={{ color: '#22c55e', fontFamily: 'monospace', fontSize: 12, marginTop: 8 }}>
                  No known CVEs detected for identified software versions
                </p>
                <p style={{ color: '#334155', fontFamily: 'monospace', fontSize: 11, marginTop: 4 }}>
                  CVEs are detected when software version banners are found in scan data
                </p>
              </div>
            ) : (
              <>
                {cveCritical.length > 0 && (
                  <div style={{ marginBottom: 10 }}>
                    <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#ef4444', textTransform: 'uppercase', marginBottom: 6, letterSpacing: 1 }}>
                      ⚠ Critical / High ({cveCritical.length})
                    </div>
                    {cveCritical.map((c, i) => <CVECard key={i} c={c} />)}
                  </div>
                )}
                {cveMedLow.length > 0 && (
                  <div>
                    <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#eab308', textTransform: 'uppercase', marginBottom: 6, letterSpacing: 1 }}>
                      Medium / Low ({cveMedLow.length})
                    </div>
                    {cveMedLow.map((c, i) => <CVECard key={i} c={c} />)}
                  </div>
                )}
                <div style={{ marginTop: 10, padding: '8px 12px', background: 'rgba(234,179,8,0.05)', border: '1px solid rgba(234,179,8,0.15)', borderRadius: 6 }}>
                  <p style={{ fontSize: 10, fontFamily: 'monospace', color: '#64748b', margin: 0 }}>
                    ⚠ CVE data is AI-generated based on detected software versions. Always verify against the official NVD database at nvd.nist.gov
                  </p>
                </div>
              </>
            )}
          </div>
        )}

        {/* ── Infrastructure Tab ── */}
        {tab === 'infra' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {[
              { label: '🏢 Hosting Provider', value: analysis.infrastructure?.hosting_provider },
              { label: '🖥 Server Type',       value: analysis.infrastructure?.server_type },
              { label: '☁ Cloud Provider',    value: analysis.infrastructure?.cloud_provider },
              { label: '🌐 CDN Detected',      value: analysis.infrastructure?.cdn_detected ? 'Yes' : null },
            ].filter(i => i.value).map(item => (
              <div key={item.label} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: '#0f0f18', borderRadius: 6 }}>
                <span style={{ fontSize: 12, fontFamily: 'monospace', color: '#475569' }}>{item.label}</span>
                <span style={{ fontSize: 12, fontFamily: 'monospace', color: '#a78bfa' }}>{item.value}</span>
              </div>
            ))}
            {(analysis.infrastructure?.fingerprint_notes || []).length > 0 && (
              <div style={{ padding: '8px 12px', background: '#0f0f18', borderRadius: 6 }}>
                <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#334155', marginBottom: 6, textTransform: 'uppercase' }}>📋 Fingerprint Notes</div>
                {analysis.infrastructure.fingerprint_notes.map((n: string, i: number) => (
                  <div key={i} style={{ fontSize: 11, fontFamily: 'monospace', color: '#64748b', lineHeight: 1.8 }}>· {n}</div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── Attack Surface Tab ── */}
        {tab === 'attack' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {analysis.attack_surface?.critical_exposures?.length > 0 && (
              <div style={{ padding: '8px 12px', background: 'rgba(239,68,68,0.05)', border: '1px solid rgba(239,68,68,0.15)', borderRadius: 6 }}>
                <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#ef4444', marginBottom: 6, textTransform: 'uppercase' }}>⚠ Critical Exposures</div>
                {analysis.attack_surface.critical_exposures.map((e: string, i: number) => (
                  <div key={i} style={{ fontSize: 11, fontFamily: 'monospace', color: '#fca5a5', lineHeight: 1.8 }}>· {e}</div>
                ))}
              </div>
            )}
            {analysis.attack_surface?.exposed_services?.length > 0 && (
              <div style={{ padding: '8px 12px', background: '#0f0f18', borderRadius: 6 }}>
                <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#334155', marginBottom: 6, textTransform: 'uppercase' }}>🔌 Exposed Services</div>
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  {analysis.attack_surface.exposed_services.map((s: string, i: number) => (
                    <span key={i} style={{ fontSize: 11, fontFamily: 'monospace', color: '#a78bfa', background: '#1a1a2e', border: '1px solid #2d2d4e', borderRadius: 4, padding: '2px 8px' }}>{s}</span>
                  ))}
                </div>
              </div>
            )}
            {analysis.attack_surface?.ssl_issues?.length > 0 && (
              <div style={{ padding: '8px 12px', background: 'rgba(234,179,8,0.05)', border: '1px solid rgba(234,179,8,0.15)', borderRadius: 6 }}>
                <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#eab308', marginBottom: 6, textTransform: 'uppercase' }}>🔐 SSL Issues</div>
                {analysis.attack_surface.ssl_issues.map((s: string, i: number) => (
                  <div key={i} style={{ fontSize: 11, fontFamily: 'monospace', color: '#fde68a', lineHeight: 1.8 }}>· {s}</div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── Ports Tab ── */}
        {tab === 'ports' && (
          <div>
            {(analysis.port_risks || []).length === 0 ? (
              <p style={{ color: '#334155', fontFamily: 'monospace', fontSize: 12, textAlign: 'center', padding: 20 }}>No port data available</p>
            ) : (
              <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: 'monospace', fontSize: 12 }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #1e1e2e' }}>
                    {['Port', 'Service', 'Risk', 'Note'].map(h => (
                      <th key={h} style={{ textAlign: 'left', padding: '4px 10px', color: '#334155', fontSize: 10, textTransform: 'uppercase' }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {(analysis.port_risks || []).map((p: any, i: number) => {
                    const col = RISK_COLOR[p.risk] || '#94a3b8'
                    return (
                      <tr key={i} style={{ borderBottom: '1px solid #0f0f18' }}>
                        <td style={{ padding: '6px 10px', color: '#a78bfa', fontWeight: 700 }}>{p.port}</td>
                        <td style={{ padding: '6px 10px', color: '#94a3b8' }}>{p.service}</td>
                        <td style={{ padding: '6px 10px' }}>
                          <span style={{ color: col, background: `${col}22`, borderRadius: 4, padding: '1px 6px', fontSize: 10, textTransform: 'uppercase' }}>{p.risk}</span>
                        </td>
                        <td style={{ padding: '6px 10px', color: '#475569' }}>{p.note}</td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            )}
          </div>
        )}

        {/* ── Threat Intel Tab ── */}
        {tab === 'threat' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
              {[
                { label: '🚫 Blacklist Status', value: analysis.threat_intel?.blacklist_status, highlight: analysis.threat_intel?.blacklist_status === 'listed' },
                { label: '🔢 Blacklist Count',  value: analysis.threat_intel?.blacklist_count?.toString() },
                { label: '⭐ Reputation Score', value: analysis.threat_intel?.reputation_score?.toString() },
                { label: '🦠 Malware',          value: analysis.threat_intel?.malware_detected ? '⚠ Detected' : '✓ Clean', highlight: analysis.threat_intel?.malware_detected },
              ].filter(i => i.value != null).map(item => (
                <div key={item.label} style={{ padding: '8px 12px', background: '#0f0f18', borderRadius: 6 }}>
                  <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#334155', marginBottom: 2 }}>{item.label}</div>
                  <div style={{ fontSize: 13, fontFamily: 'monospace', fontWeight: 700, color: item.highlight ? '#ef4444' : '#a78bfa' }}>{item.value}</div>
                </div>
              ))}
            </div>
            {analysis.threat_intel?.threat_indicators?.length > 0 && (
              <div style={{ padding: '8px 12px', background: 'rgba(239,68,68,0.05)', border: '1px solid rgba(239,68,68,0.15)', borderRadius: 6 }}>
                <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#ef4444', marginBottom: 6, textTransform: 'uppercase' }}>⚠ Threat Indicators</div>
                {analysis.threat_intel.threat_indicators.map((t: string, i: number) => (
                  <div key={i} style={{ fontSize: 11, fontFamily: 'monospace', color: '#fca5a5', lineHeight: 1.8 }}>· {t}</div>
                ))}
              </div>
            )}
            {analysis.threat_intel?.abuse_history && (
              <div style={{ padding: '8px 12px', background: '#0f0f18', borderRadius: 6 }}>
                <div style={{ fontSize: 10, fontFamily: 'monospace', color: '#334155', marginBottom: 4, textTransform: 'uppercase' }}>📋 Abuse History</div>
                <div style={{ fontSize: 12, fontFamily: 'monospace', color: '#64748b' }}>{analysis.threat_intel.abuse_history}</div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

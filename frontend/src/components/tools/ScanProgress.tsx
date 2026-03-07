import React from 'react'

export default function ScanProgress() {
  return (
    <div style={{ background: '#12121a', border: '1px solid #1e1e2e', borderRadius: 12, padding: '32px 24px', textAlign: 'center' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 14, marginBottom: 20 }}>
        <img src="/phantom-logo.png" style={{ width: 36, height: 36, objectFit: 'contain', animation: 'spin 1.5s linear infinite' }} />
        <style>{`@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}`}</style>
        <span style={{ fontFamily: 'monospace', fontSize: 15, color: '#a78bfa', fontWeight: 600 }}>
          Scanning target...
        </span>
      </div>
      <div style={{ height: 4, background: 'rgba(255,255,255,0.05)', borderRadius: 2, overflow: 'hidden', maxWidth: 400, margin: '0 auto' }}>
        <div style={{
          height: '100%', width: '60%', borderRadius: 2,
          background: 'linear-gradient(90deg, #7c3aed, #a78bfa)',
          boxShadow: '0 0 8px rgba(167,139,250,0.5)',
          animation: 'slide 1.5s ease-in-out infinite'
        }} />
      </div>
      <style>{`@keyframes slide{0%{transform:translateX(-150%)}100%{transform:translateX(250%)}}`}</style>
      <p style={{ marginTop: 16, fontFamily: 'monospace', fontSize: 12, color: '#334155' }}>
        Running 9 OSINT tools + AI analysis...
      </p>
    </div>
  )
}

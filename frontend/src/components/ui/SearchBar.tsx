import React, { useState } from 'react'
import { useInvestigationStore } from '../../store/investigationStore'

export default function SearchBar() {
  const [input, setInput] = useState('')
  const { investigate, isLoading, clearResults } = useInvestigationStore()

  const handleSearch = () => {
    if (!input.trim() || isLoading) return
    investigate(input.trim())
  }

  return (
    <div style={{ maxWidth: 680, margin: '0 auto' }}>
      <div style={{
        display: 'flex', alignItems: 'center', background: '#12121a',
        border: '1px solid #1e1e2e', borderRadius: 12, overflow: 'hidden',
        transition: 'border-color 0.2s, box-shadow 0.2s',
        boxShadow: '0 0 0 0 transparent'
      }}
        onFocus={e => (e.currentTarget.style.boxShadow = '0 0 0 2px #7c3aed, 0 0 20px rgba(124,58,237,0.2)')}
        onBlur={e => (e.currentTarget.style.boxShadow = 'none')}
      >
        <span style={{ paddingLeft: 16, fontSize: 18 }}>🔍</span>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSearch()}
          placeholder="Enter IP or domain  (e.g. 8.8.8.8 or github.com)"
          disabled={isLoading}
          autoFocus
          style={{
            flex: 1, background: 'transparent', border: 'none', outline: 'none',
            padding: '14px 12px', fontFamily: 'monospace', fontSize: 14,
            color: '#e2e8f0', caretColor: '#a78bfa'
          }}
        />
        {input && (
          <button onClick={() => { setInput(''); clearResults() }} style={{
            background: 'none', border: 'none', color: '#475569', cursor: 'pointer',
            padding: '0 8px', fontSize: 16
          }}>✕</button>
        )}
        <button
          onClick={handleSearch}
          disabled={isLoading || !input.trim()}
          style={{
            margin: 8, padding: '10px 24px', background: isLoading || !input.trim() ? '#3b1f6e' : '#7c3aed',
            border: 'none', borderRadius: 8, color: '#fff', fontWeight: 600,
            fontSize: 14, cursor: isLoading || !input.trim() ? 'not-allowed' : 'pointer',
            opacity: isLoading || !input.trim() ? 0.5 : 1, whiteSpace: 'nowrap',
            transition: 'background 0.2s'
          }}
        >
          {isLoading ? '⏳ Scanning...' : '🔎 Investigate'}
        </button>
      </div>
    </div>
  )
}

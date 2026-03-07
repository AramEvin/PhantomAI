import { create } from 'zustand'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2)
}

export interface ToolResult {
  tool_name: string
  status: 'success' | 'error' | 'skipped' | 'loading'
  data?: any
  error?: string
  duration_ms?: number
}

export interface AIAnalysis {
  summary: string
  risk_level: 'low' | 'medium' | 'high' | 'critical'
  risk_score: number
  key_findings: string[]
  recommendations: string[]
  tags: string[]
  infrastructure: Record<string, any>
  attack_surface: Record<string, any>
  port_risks: Array<{ port: number; service: string; risk: string; note: string }>
  threat_intel: Record<string, any>
}

export interface Investigation {
  target: string
  target_type: 'ip' | 'domain'
  timestamp: string
  duration_ms: number
  tools_run: number
  tools_success: number
  results: Record<string, ToolResult>
  ai_analysis?: AIAnalysis
}

export interface ScanHistory {
  id: number
  target: string
  target_type: string
  timestamp: string
  duration_ms: number
  tools_run: number
  tools_success: number
  risk_level?: string
  risk_score?: number
}

interface Store {
  isLoading: boolean
  error: string | null
  investigation: Investigation | null
  history: ScanHistory[]
  historyLoading: boolean
  investigate: (t: string) => Promise<void>
  clearResults: () => void
  loadHistory: () => Promise<void>
  loadScan: (id: number) => Promise<void>
  deleteScan: (id: number) => Promise<void>
}

export const useInvestigationStore = create<Store>((set, get) => ({
  isLoading: false,
  error: null,
  investigation: null,
  history: [],
  historyLoading: false,

  investigate: async (target) => {
    set({ isLoading: true, error: null, investigation: null })
    try {
      const { data } = await axios.post<Investigation>(
        `${API_URL}/api/v1/investigate`,
        { target: target.trim().toLowerCase() }
      )
      set({ investigation: data, isLoading: false })
      get().loadHistory()
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Investigation failed'
      set({ error: msg, isLoading: false })
    }
  },

  clearResults: () => set({ investigation: null, error: null }),

  loadHistory: async () => {
    set({ historyLoading: true })
    try {
      const { data } = await axios.get<ScanHistory[]>(`${API_URL}/api/v1/history?limit=20`)
      set({ history: data, historyLoading: false })
    } catch {
      set({ historyLoading: false })
    }
  },

  loadScan: async (id) => {
    set({ isLoading: true, error: null })
    try {
      const { data } = await axios.get(`${API_URL}/api/v1/history/${id}`)
      set({ investigation: data, isLoading: false })
    } catch (err: any) {
      set({ error: err.message, isLoading: false })
    }
  },

  deleteScan: async (id) => {
    try {
      await axios.delete(`${API_URL}/api/v1/history/${id}`)
      set(s => ({ history: s.history.filter(h => h.id !== id) }))
    } catch {}
  },
}))

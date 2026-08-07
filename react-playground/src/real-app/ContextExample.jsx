import { createContext, useContext, useState, useMemo, useCallback } from 'react'

// ── Principal-level Context structure ────────────────────────────
// 1. One context per concern (don't cram unrelated state together).
// 2. A dedicated Provider that owns the state.
// 3. value wrapped in useMemo so a parent re-render doesn't hand every
//    consumer a NEW object reference (the re-render trap).
// 4. A custom hook that guards against use outside the Provider.
// ─────────────────────────────────────────────────────────────────
const ThemeContext = createContext(null)

function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('dark')
  const toggle = useCallback(
    () => setTheme((t) => (t === 'dark' ? 'light' : 'dark')),
    []
  )
  const value = useMemo(() => ({ theme, toggle }), [theme, toggle])
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}

function useTheme() {
  const ctx = useContext(ThemeContext)
  if (!ctx) throw new Error('useTheme must be used within <ThemeProvider>')
  return ctx
}

// A deep consumer — reads theme with no prop drilling.
function ThemedPanel() {
  const { theme, toggle } = useTheme()
  const dark = theme === 'dark'
  return (
    <div
      style={{
        padding: '1rem',
        borderRadius: 8,
        border: '1px solid var(--border)',
        background: dark ? '#1f2028' : '#faf9f7',
        color: dark ? '#f3f4f6' : '#08060d',
      }}
    >
      <p style={{ margin: 0 }}>Current theme: <strong>{theme}</strong></p>
      <button onClick={toggle} style={{ marginTop: '0.75rem' }}>Toggle theme</button>
    </div>
  )
}

export default function ContextExample() {
  return (
    <section className="card">
      <h2>Context · theme (low-frequency global)</h2>
      <ThemeProvider>
        <ThemedPanel />
      </ThemeProvider>
    </section>
  )
}

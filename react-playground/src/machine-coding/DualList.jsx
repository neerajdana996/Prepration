import { useState, useEffect, useCallback } from 'react'
import StudentRow from './StudentRow'

// ─────────────────────────────────────────────────────────────
// MOCK APIs (provided). Overlaps: R2 (Bob) identical in both;
// R3 (Carol) appears in both with different marks (91 vs 95).
// Dedupe decision: B is applied last, so B wins the conflict (Carol 95).
// ─────────────────────────────────────────────────────────────
const fetchStudentsA = () =>
  new Promise((resolve) =>
    setTimeout(() => resolve([
      { name: 'Alice', marks: 88, registrationId: 'R1' },
      { name: 'Bob',   marks: 73, registrationId: 'R2' },
      { name: 'Carol', marks: 91, registrationId: 'R3' },
    ]), 400)
  )

const fetchStudentsB = () =>
  new Promise((resolve) =>
    setTimeout(() => resolve([
      { name: 'Bob',   marks: 73, registrationId: 'R2' },
      { name: 'Dan',   marks: 65, registrationId: 'R4' },
      { name: 'Carol', marks: 95, registrationId: 'R3' },
    ]), 700)
  )

export default function DualList() {
  const [users, setUsers] = useState([])
  const [status, setStatus] = useState('loading') // 'loading' | 'ready' | 'error'

  useEffect(() => {
    let active = true
    const load = async () => {
      try {
        const [usersA, usersB] = await Promise.all([fetchStudentsA(), fetchStudentsB()])
        const byId = new Map();
        [...usersA, ...usersB].forEach((u) => byId.set(u.registrationId, u)) // B wins on conflict
        if (!active) return
        setUsers([...byId.values()].map((u) => ({ ...u, side: 'available', checked: false })))
        setStatus('ready')
      } catch {
        if (active) setStatus('error')
      }
    }
    load()
    return () => { active = false }
  }, [])

  // useCallback with [] deps → a STABLE reference, because the functional
  // updater means this handler never needs to close over `users`.
  // This stability is what lets React.memo(StudentRow) skip unchanged rows.
  const handleCheck = useCallback((registrationId) => {
    setUsers((prev) =>
      prev.map((u) => (u.registrationId === registrationId ? { ...u, checked: !u.checked } : u))
    )
  }, [])

  const move = useCallback((from, to, type) => {
    if (type === 'all') {
      setUsers((prev) =>
        prev.map((u) => ({ ...u, side: to, checked: false }))
      )
    } else {
      setUsers((prev) =>
        prev.map((u) => (u.side === from && u.checked ? { ...u, side: to, checked: false } : u))
      )
    }
  }, [])

  const renderPanel = (title, list) => (
    <div className="panel">
      <div className="panel-head"><span>{title}</span><span>{list.length}</span></div>
      <div className="panel-body">
        {list.length === 0 ? (
          <p className="empty">none</p>
        ) : (
          list.map((u) => (
            <StudentRow key={u.registrationId} student={u} onToggle={handleCheck} />
          ))
        )}
      </div>
    </div>
  )

  if (status === 'loading') {
    return (
      <section className="card">
        <h2>Machine-coding · dual-list transfer</h2>
        <p>Loading…</p>
      </section>
    )
  } 
  if (status === 'error') {
    return (
      <section className="card">
        <h2>Machine-coding · dual-list transfer</h2>
        <p>Couldn’t load students. Try again.</p>
      </section>
    )
  }

  const available = users.filter((u) => u.side === 'available')
  const selected  = users.filter((u) => u.side === 'selected')

  return (
    <section className="card">
      <h2>Machine-coding · dual-list transfer</h2>
      <div className="panels">
        {renderPanel('Available', available)}

        <div className="row" style={{ flexDirection: 'column', justifyContent: 'center' }}>
        <button
            aria-label="Move all students to Selected"
            disabled={!available.some((u) => u.checked)}
            onClick={() => move('available', 'selected', 'all')}
          >↩</button>
          <button
            aria-label="Move checked students to Selected"
            disabled={!available.some((u) => u.checked)}
            onClick={() => move('available', 'selected')}
          >→</button>
          <button
            aria-label="Move checked students back to Available"
            disabled={!selected.some((u) => u.checked)}
            onClick={() => move('selected', 'available')}
          >←</button>
        </div>

        {renderPanel('Selected', selected)}
      </div>
    </section>
  )
}

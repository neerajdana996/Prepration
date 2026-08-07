import { useState } from 'react'
import { useFetch } from './useFetch'

// Hits the running IoT server on :4000. Try:
//  • "page size +5" → new URL → old request is ABORTED, new one runs.
//  • "refetch" → forces a fresh request (bypasses the cache).
//  • go back to a size you already loaded → served from CACHE instantly.
export default function UseFetchDemo() {
  const [n, setN] = useState(5)
  const url = `http://localhost:4000/devices?page=1&pageSize=${n}`
  const { data, loading, error, refetch } = useFetch(url)

  return (
    <section className="card">
      <h2>Custom hook · useFetch (cache + AbortController)</h2>
      <div className="row" style={{ marginBottom: '0.75rem' }}>
        <button onClick={() => setN((x) => Math.min(x + 5, 30))}>page size +5</button>
        <button onClick={() => setN((x) => Math.max(x - 5, 5))}>page size −5</button>
        <button onClick={refetch}>refetch</button>
      </div>

      {loading ? (
        <p className="empty">loading…</p>
      ) : error ? (
        <p className="empty">error: {String(error.message)}</p>
      ) : (
        <ul style={{ margin: 0, paddingLeft: '1.1rem' }}>
          {data.devices.map((d) => (
            <li key={d.id}>{d.name} — {d.status} · cpu {d.cpu}</li>
          ))}
        </ul>
      )}
      <p style={{ opacity: 0.6, fontSize: '0.8rem', marginTop: '0.5rem' }}>url: {url}</p>
    </section>
  )
}

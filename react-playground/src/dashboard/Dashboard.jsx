import { useState, useEffect, useRef, memo } from 'react'
import { Provider } from 'react-redux'
import { useSearchParams } from 'react-router-dom'
import { dashboardStore } from './store'
import { useGetDevicesQuery } from './dashboardApi'
import { useConnectionStatus } from './useConnectionStatus'

const PAGE_SIZE = 20

const statusStyles = {
  online: ['var(--bg-success)', 'var(--text-success)'],
  offline: ['var(--bg-danger)', 'var(--text-danger)'],
  degraded: ['var(--bg-warning)', 'var(--text-warning)'],
}

function StatusPill({ status }) {
  const [bg, fg] = statusStyles[status] || statusStyles.online
  return <span className="pill" style={{ background: bg, color: fg }}>{status}</span>
}

function ConnBadge() {
  const conn = useConnectionStatus()
  const map = {
    live: ['var(--bg-success)', 'var(--text-success)', 'live'],
    connecting: ['var(--surface-1)', 'var(--text-muted)', 'connecting…'],
    disconnected: ['var(--bg-danger)', 'var(--text-danger)', 'disconnected'],
  }
  const [bg, fg, label] = map[conn] || map.connecting
  return <span className="pill" style={{ background: bg, color: fg }}>● {label}</span>
}

const DeviceRow = memo(function DeviceRow({ d }) {
  return (
    <tr>
      <td>{d.name}</td>
      <td>{d.site}</td>
      <td><StatusPill status={d.status} /></td>
      <td className="num">{d.cpu}</td>
      <td className="num">{d.temp}</td>
    </tr>
  )
})

function DevicesTable() {
  // Q3: filters live in the URL → shareable / bookmarkable / back-button works.
  const [params, setParams] = useSearchParams()
  const status = params.get('status') || 'all'
  const q = params.get('q') || ''

  const setFilter = (key, val) => {
    const next = new URLSearchParams(params)
    if (val && !(key === 'status' && val === 'all')) next.set(key, val)
    else next.delete(key)
    setParams(next, { replace: true })
  }

  const [page, setPage] = useState(1)
  useEffect(() => { setPage(1) }, [status, q]) // new filter → restart from page 1

  const { data, isLoading, isFetching, isError } = useGetDevicesQuery({
    page, pageSize: PAGE_SIZE, status, q,
  })

  const loaded = data?.devices.length ?? 0
  const total = data?.total ?? 0
  const hasMore = loaded < total

  // Q5/Q6: IntersectionObserver on a sentinel. rootMargin 500px = prefetch the
  // next page BEFORE the user reaches the bottom.
  const sentinelRef = useRef(null)
  useEffect(() => {
    const el = sentinelRef.current
    if (!el) return
    const io = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !isFetching) {
          setPage((p) => p + 1)
        }
      },
      { rootMargin: '0px 0px 500px 0px' }
    )
    io.observe(el)
    return () => io.disconnect()
  }, [hasMore, isFetching])

  return (
    <div>
      <div className="dash-toolbar">
        <input
          className="dash-input"
          placeholder="search name…"
          value={q}
          onChange={(e) => setFilter('q', e.target.value)}
        />
        <select className="dash-input" value={status} onChange={(e) => setFilter('status', e.target.value)}>
          <option value="all">all statuses</option>
          <option value="online">online</option>
          <option value="degraded">degraded</option>
          <option value="offline">offline</option>
        </select>
        <span style={{ marginLeft: 'auto' }}><ConnBadge /></span>
      </div>

      {isError ? (
        <p className="empty">Failed to load — is the server on :4000 running?</p>
      ) : isLoading ? (
        <p className="empty">Loading…</p>
      ) : (
        <>
          <table className="dash-table">
            <thead>
              <tr><th>device</th><th>site</th><th>status</th><th>cpu %</th><th>temp °C</th></tr>
            </thead>
            <tbody>
              {data.devices.map((d) => <DeviceRow key={d.id} d={d} />)}
            </tbody>
          </table>

          <div ref={sentinelRef} className="dash-sentinel">
            {hasMore ? (isFetching ? 'loading more…' : 'scroll for more') : `all ${total} devices loaded`}
          </div>
          <div className="dash-pager"><span>showing {loaded} of {total}</span></div>
        </>
      )}
    </div>
  )
}

export default function Dashboard() {
  return (
    <section className="card">
      <h2>IoT device dashboard · live + infinite scroll</h2>
      <Provider store={dashboardStore}>
        <DevicesTable />
      </Provider>
    </section>
  )
}

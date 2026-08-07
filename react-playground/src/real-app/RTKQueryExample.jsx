import { Provider } from 'react-redux'
import { store } from './redux/store'
import { useGetDevicesQuery } from './redux/devicesApi'

// Both widgets call the SAME query hook. RTK Query dedups: only ONE request
// fires, and both read the shared cache — proven by "served by request #N"
// showing the same number in both.
function DevicesWidget({ label }) {
  const { data, isLoading, isFetching, refetch } = useGetDevicesQuery()
  return (
    <div className="panel" style={{ marginBottom: '0.75rem' }}>
      <div className="panel-head">
        <span>{label}</span>
        <span>{isFetching ? 'fetching…' : 'idle'}</span>
      </div>
      {isLoading ? (
        <p className="empty">loading…</p>
      ) : (
        <>
          <p style={{ margin: '0 0 0.5rem', fontSize: '0.8rem', opacity: 0.7 }}>
            served by request #{data.servedByRequest}
          </p>
          {data.devices.map((d) => (
            <div className="student-row" key={d.id}>
              <span>{d.name}</span>
              <span className="student-marks">{d.status}</span>
            </div>
          ))}
          <button onClick={() => refetch()} style={{ marginTop: '0.5rem' }}>refetch</button>
        </>
      )}
    </div>
  )
}

export default function RTKQueryExample() {
  return (
    <section className="card">
      <h2>RTK Query · server state (cache · dedup · refetch)</h2>
      <Provider store={store}>
        <DevicesWidget label="Widget 1" />
        <DevicesWidget label="Widget 2" />
      </Provider>
    </section>
  )
}

import { useRef } from 'react'
import { Provider, useSelector, useDispatch } from 'react-redux'
import { store } from './redux/store'
import { incA, incB, selectA, selectB, selectTotal } from './redux/counterSlice'

// Components use the EXPORTED selectors — they never touch state shape directly.
function DisplayA() {
  const a = useSelector(selectA)
  const renders = useRef(0); renders.current++
  return (
    <div className="student-row">
      <span>counter A = <strong>{a}</strong></span>
      <span className="render-badge">rendered {renders.current}×</span>
    </div>
  )
}

function DisplayB() {
  const b = useSelector(selectB)
  const renders = useRef(0); renders.current++
  return (
    <div className="student-row">
      <span>counter B = <strong>{b}</strong></span>
      <span className="render-badge">rendered {renders.current}×</span>
    </div>
  )
}

// Uses the memoized derived selector. Re-renders when A or B changes (it depends
// on both) — but the computation is memoized, not re-run on unrelated updates.
function Total() {
  const total = useSelector(selectTotal)
  const renders = useRef(0); renders.current++
  return (
    <div className="student-row">
      <span>total (A + B) = <strong>{total}</strong></span>
      <span className="render-badge">rendered {renders.current}×</span>
    </div>
  )
}

function Controls() {
  const dispatch = useDispatch()
  return (
    <div className="row" style={{ marginTop: '0.75rem' }}>
      <button onClick={() => dispatch(incA())}>A +1</button>
      <button onClick={() => dispatch(incB())}>B +1</button>
    </div>
  )
}

export default function ReduxExample() {
  return (
    <section className="card">
      <h2>Redux Toolkit · exported + memoized selectors</h2>
      <Provider store={store}>
        <DisplayA />
        <DisplayB />
        <Total />
        <Controls />
      </Provider>
    </section>
  )
}

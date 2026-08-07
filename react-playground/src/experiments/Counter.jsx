import { useState } from 'react'

// First experiment: the simplest possible useState.
// Try: click the buttons and watch the value re-render.
export default function Counter() {
  const [count, setCount] = useState(0)

  return (
    <section className="card">
      <h2>useState · Counter</h2>
      <p className="value">{count}</p>
      <div className="row">
        <button onClick={() => setCount(c => c - 1)}>-1</button>
        <button onClick={() => setCount(c => c + 1)}>+1</button>
        <button onClick={() => setCount(0)}>reset</button>
      </div>
    </section>
  )
}

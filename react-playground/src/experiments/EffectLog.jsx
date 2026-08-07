import { useState, useEffect } from 'react'

// Watch the console. The question: in what ORDER do "effect" and "cleanup"
// fire on mount, and when count changes?
export default function EffectLog() {
  const [count, setCount] = useState(0)

  useEffect(() => {
    console.log('effect: ' + count)
    return () => console.log('cleanup: ' + count)
  }, [count])

  return (
    <section className="card">
      <h2>useEffect · effect &amp; cleanup order</h2>
      <p className="value">{count}</p>
      <div className="row">
        <button onClick={() => setCount(c => c + 1)}>+1</button>
      </div>
    </section>
  )
}

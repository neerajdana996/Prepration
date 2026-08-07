import Counter from '../experiments/Counter'
import EffectLog from '../experiments/EffectLog'
import UseFetchDemo from '../experiments/UseFetchDemo'
import AccessibleTree from '../experiments/AccessibleTree'

// Small, focused hook/JS tests. Add more experiments here.
export default function ExperimentsPage() {
  return (
    <>
      <Counter />
      <EffectLog />
      <UseFetchDemo />
      <AccessibleTree />
    </>
  )
}

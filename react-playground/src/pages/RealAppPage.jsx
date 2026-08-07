import ContextExample from '../real-app/ContextExample'
import ReduxExample from '../real-app/ReduxExample'
import RTKQueryExample from '../real-app/RTKQueryExample'

// Principal-level state management, built up one tool at a time:
//   ✅ Context (theme)   ✅ Redux Toolkit slice   ✅ RTK Query (server state)
export default function RealAppPage() {
  return (
    <>
      <ContextExample />
      <ReduxExample />
      <RTKQueryExample />
    </>
  )
}

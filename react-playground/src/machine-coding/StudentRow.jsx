import { memo, useRef } from 'react'

// A single row. Wrapped in React.memo so it re-renders ONLY when its own
// `student` or `onToggle` prop changes by reference.
function StudentRow({ student, onToggle }) {
  // Debug-only: count how many times THIS row renders, to prove memo works.
  // (Mutating a ref in render is a demo technique, not production code.)
  const renders = useRef(0)
  renders.current += 1

  return (
    <label className="student-row">
      <input
        type="checkbox"
        checked={!!student.checked}
        onChange={() => onToggle(student.registrationId)}
      />
      <span className="student-name">{student.name}</span>
      <span className="student-marks">{student.marks}</span>
      <span className="render-badge">rendered {renders.current}×</span>
    </label>
  )
}

export default memo(StudentRow)

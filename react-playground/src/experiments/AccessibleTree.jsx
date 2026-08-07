import { useState, useRef, useEffect } from 'react'

const DATA = [
  { id: 's1', label: 'Site SJC-01', children: [{ id: 'd1', label: 'device-1' }, { id: 'd2', label: 'device-2' }] },
  { id: 's2', label: 'Site BLR-02', children: [{ id: 'd3', label: 'device-3' }, { id: 'd4', label: 'device-4' }] },
]

// Flatten to the currently VISIBLE rows (respecting which parents are expanded).
function flatten(nodes, expanded, level = 1, out = []) {
  for (const n of nodes) {
    const hasChildren = !!n.children?.length
    out.push({ id: n.id, label: n.label, level, hasChildren })
    if (hasChildren && expanded.has(n.id)) flatten(n.children, expanded, level + 1, out)
  }
  return out
}

export default function AccessibleTree() {
  const [expanded, setExpanded] = useState(new Set(['s1']))
  const [selected, setSelected] = useState(null)
  const [focusId, setFocusId] = useState('s1') // roving tabindex target
  const refs = useRef({})

  const visible = flatten(DATA, expanded)

  // Move real DOM focus to whichever item is the roving target.
  useEffect(() => { refs.current[focusId]?.focus() }, [focusId])

  const toggle = (id) =>
    setExpanded((prev) => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })

  const onKeyDown = (e, node) => {
    const idx = visible.findIndex((v) => v.id === focusId)
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault(); if (idx < visible.length - 1) setFocusId(visible[idx + 1].id); break
      case 'ArrowUp':
        e.preventDefault(); if (idx > 0) setFocusId(visible[idx - 1].id); break
      case 'ArrowRight':
        e.preventDefault()
        if (node.hasChildren && !expanded.has(node.id)) toggle(node.id)          // expand
        else if (node.hasChildren) setFocusId(visible[idx + 1].id)               // or step into child
        break
      case 'ArrowLeft':
        e.preventDefault()
        if (node.hasChildren && expanded.has(node.id)) toggle(node.id)           // collapse
        else {                                                                    // or go to parent
          const parent = visible.slice(0, idx).reverse().find((v) => v.level < node.level)
          if (parent) setFocusId(parent.id)
        }
        break
      case 'Enter':
      case ' ':
        e.preventDefault(); node.hasChildren ? toggle(node.id) : setSelected(node.id); break
      default:
        break
    }
  }

  return (
    <section className="card">
      <h2>Accessible tree-view (ARIA + keyboard)</h2>
      <p style={{ fontSize: '0.8rem', opacity: 0.6, marginTop: 0 }}>
        Click a row, then use ↑ ↓ → ← and Enter/Space.
      </p>
      <ul role="tree" aria-label="Devices by site" style={{ listStyle: 'none', padding: 0, margin: 0 }}>
        {visible.map((node) => (
          <li
            key={node.id}
            role="treeitem"
            aria-level={node.level}
            aria-expanded={node.hasChildren ? expanded.has(node.id) : undefined}
            aria-selected={selected === node.id}
            tabIndex={focusId === node.id ? 0 : -1}
            ref={(el) => { refs.current[node.id] = el }}
            onKeyDown={(e) => onKeyDown(e, node)}
            onFocus={() => setFocusId(node.id)}
            onClick={() => {
              setFocusId(node.id)
              node.hasChildren ? toggle(node.id) : setSelected(node.id)
            }}
            style={{
              paddingLeft: node.level * 16 + 8,
              paddingTop: 6, paddingBottom: 6,
              cursor: 'pointer', outline: 'none', borderRadius: 6,
              background:
                selected === node.id ? 'var(--bg-accent)'
                : focusId === node.id ? 'var(--surface-2)'
                : 'transparent',
            }}
          >
            {node.hasChildren ? (expanded.has(node.id) ? '▾ ' : '▸ ') : '• '}{node.label}
          </li>
        ))}
      </ul>
    </section>
  )
}

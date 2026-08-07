// Deep clone — nested objects/arrays + circular refs. Run:
//   node round2/js-concepts/deep-clone.js

function deepClone(obj, seen = new WeakMap()) {
  if (obj == null || typeof obj !== 'object') return obj   // primitives/null → as-is
  if (seen.has(obj)) return seen.get(obj)                  // circular ref → return the clone we started

  const clone = Array.isArray(obj) ? [] : {}
  seen.set(obj, clone)                                     // record BEFORE recursing (handles cycles)

  for (const key in obj) {
    if (Object.hasOwn(obj, key)) {
      clone[key] = deepClone(obj[key], seen)
    }
  }
  return clone
}

// ─── tests ──────────────────────────────────────────────────────────────
const a = { x: 1, nested: { y: 2 }, list: [1, 2, { z: 3 }] }
a.self = a                                                 // circular reference

const c = deepClone(a)
console.log('nested is a copy: ', c.nested !== a.nested)   // true
console.log('deep copy:       ', c.list[2] !== a.list[2])  // true
console.log('circular kept:   ', c.self === c)             // true (points to the clone, not `a`)
console.log('values:          ', c.x, c.nested.y, c.list)  // 1 2 [ 1, 2, { z: 3 } ]

c.nested.y = 99                                            // mutate the clone...
console.log('original intact: ', a.nested.y)               // 2  (independent)

/**
 * deepClone(obj) — a fully independent DEEP copy. Mutating the clone must not
 * touch the original at any depth. Handles circular references.
 *
 *   const orig = { a: 1, nested: { b: 2 }, list: [3, 4] };
 *   const copy = deepClone(orig);
 *   copy.nested.b = 99; copy.list.push(5);
 *   orig.nested.b;  // still 2
 *   orig.list;      // still [3, 4]
 *
 * Why: {...obj} / Object.assign are SHALLOW — nested objects stay shared by reference.
 *
 * KEY LESSONS:
 *  - recursion; base case = primitives + null returned as-is (typeof null === "object"!)
 *  - Array.isArray(obj) ? [] : {}  for the right container
 *  - circular refs → a WeakMap of  original -> clone; register the clone BEFORE
 *    recursing, so a self-reference hit during the loop returns the in-progress clone
 *  - WeakMap (not Map) so it doesn't hold the originals alive
 */

// --- YOUR ATTEMPT ---


// --- SOLUTION ---
function deepClone(obj, seen = new WeakMap()) {
  if (obj === null || typeof obj !== "object") return obj;   // base case
  if (seen.has(obj)) return seen.get(obj);                   // already cloning → break the cycle
  const clone = Array.isArray(obj) ? [] : {};
  seen.set(obj, clone);                                      // register BEFORE recursing
  for (const key in obj) {
    if (Object.hasOwn(obj, key)) {
      clone[key] = deepClone(obj[key], seen);                // recurse on the VALUE
    }
  }
  return clone;
}
  


function deepC(obj,seen=new WeekMap()){
  if(obj==null || typeof obj !=="object") return obj;
  if(seen.has(obj)) return seen.get(obj)

  const clone = Array.isArray(obj)?[]:{};
  seen.set(obj,clone)
  for (let key in obj){
    if(Object.hasOwn(obj,key)){
      clone[key] = deepClone(obj[key],seen)
    }
  }
  return clone
}
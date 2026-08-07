// Promise utilities. Run: node round2/js-concepts/promise-utils.js

const delay = (ms, value) => new Promise((res) => setTimeout(() => res(value), ms))
const fail  = (ms, msg)   => new Promise((_, rej) => setTimeout(() => rej(new Error(msg)), ms))

// ─── 1. promiseAll — like Promise.all (reject on first error) ───────────
function promiseAll(promises) {
  return new Promise((resolve, reject) => {
    if (!promises || promises.length === 0) { resolve([]); return }
    const results = new Array(promises.length)
    let completed = 0
    for (let i = 0; i < promises.length; i++) {
      Promise.resolve(promises[i]).then(
        data => { results[i] = data; if (++completed === promises.length) resolve(results) },
        reject // first rejection rejects the whole thing
      )
    }
  })
}

// ─── 1b. allSettled — never rejects; reports each outcome ───────────────
function allSettled(promises) {
  return new Promise((resolve) => {
    if (!promises || promises.length === 0) { resolve([]); return }
    const results = new Array(promises.length)
    let completed = 0
    for (let i = 0; i < promises.length; i++) {
      Promise.resolve(promises[i])
        .then(value  => { results[i] = { status: 'fulfilled', value } })
        .catch(reason => { results[i] = { status: 'rejected', reason } })
        .finally(() => { if (++completed === promises.length) resolve(results) })
    }
  })
}

// ─── 2. retry(fn, times, delayMs) ───────────────────────────────────────
async function retry(fn, times, delayMs = 0) {
  let lastErr
  for (let attempt = 0; attempt <= times; attempt++) {
    try {
      return await fn()                 // success → return immediately
    } catch (e) {
      lastErr = e                       // remember it in case this was the last try
      if (attempt < times && delayMs) await delay(delayMs)
    }
  }
  throw lastErr                         // out of attempts → propagate the last error
}

// ─── 3. runWithConcurrency(tasks, limit) — worker-pool pattern ──────────
async function runWithConcurrency(tasks, limit) {
  const results = new Array(tasks.length)
  let next = 0                          // shared cursor: the next task to claim

  async function worker() {
    while (next < tasks.length) {
      const i = next++                  // claim an index (sync, so no two workers take the same one)
      results[i] = await tasks[i]()     // run it; store by index → order preserved
    }
  }

  // spin up `limit` workers; each drains the queue → never more than `limit` in flight
  const pool = Array.from({ length: Math.min(limit, tasks.length) }, worker)
  await Promise.all(pool)
  return results
}

// ─── tests ──────────────────────────────────────────────────────────────
;(async () => {
  console.log(await promiseAll([delay(30, 'a'), delay(10, 'b'), 'c']))         // [ 'a', 'b', 'c' ]
  try { await promiseAll([delay(20, 'x'), fail(10, 'boom')]) }
  catch (e) { console.log('all rejected:', e.message) }                        // all rejected: boom

  console.log(await allSettled([delay(20, 'ok'), fail(10, 'nope')]))
  // [ { status:'fulfilled', value:'ok' }, { status:'rejected', reason: Error: nope } ]

  let n = 0
  const flaky = () => { n++; return n < 3 ? Promise.reject(new Error('fail ' + n)) : Promise.resolve('ok on ' + n) }
  console.log(await retry(flaky, 5))                                           // ok on 3

  const task = (id, ms) => () => delay(ms, id)
  console.log(await runWithConcurrency([task(1, 30), task(2, 10), task(3, 20), task(4, 5)], 2)) // [ 1, 2, 3, 4 ]
})()

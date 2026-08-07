// EventEmitter v2 — each subscription is a Listener object carrying its own
// config (once now; extensible to priority, filter, ... later).
// eventMap: event -> Set<Listener>. A Listener IS the unsubscribe handle.

class Listener {
  constructor(event, cb, config = { once: false, priority: 0 }) {
    this.event = event
    this.cb = cb
    this.config = config
  }
}

class EventEmitter {
  constructor() {
    this.eventMap = new Map() // event -> Set<Listener>
  }

  // plumbing (done for you): create a Listener, register it, return a handle
  _add(event, cb, options) {
    if (!this.eventMap.has(event))
      this.eventMap.set(event, new Set())

    const listener = new Listener(event, cb, options)

    this.eventMap.get(event).add(listener)

    return { release: () => this.eventMap.get(event)?.delete(listener) }
  }

  subscribe(event, cb, options = {}) { return this._add(event, cb, { ...options, once: false }) }
  once(event, cb, options = {}) { return this._add(event, cb, { ...options, once: true }) }

  emit(event, ...args) {
    if (!this.eventMap.has(event)) return
    const listeners = this.eventMap.get(event);
    const ordered = [...listeners].sort((a, b) => b.config.priority - a.config.priority)  // stable → ties keep subscribe order
    
    for (const l of ordered) {
      const { cb, config: { once } } = l;
      cb.apply(this, args)
      if (once)
        listeners.delete(l)
    }
    // TODO:
    //   const listeners = this.eventMap.get(event); if none → return
    //   iterate a SNAPSHOT ([...listeners]) so removing during emit is safe
    //   for each: call listener.cb(...args); if listener.once → listeners.delete(listener)
  }
}

// ─── tests ──────────────────────────────────────────────────────────────
const em = new EventEmitter()
em.subscribe('msg', () => console.log('A (p1)'), { priority: 1 })
em.subscribe('msg', () => console.log('B (p5)'), { priority: 5 })
em.subscribe('msg', () => console.log('C (p0)'))          // default priority 0
em.emit('msg')
// B (p5)   ← highest first
// A (p1)
// C (p0)
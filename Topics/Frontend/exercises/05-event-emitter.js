/**
 * EventEmitter — a pub/sub object.
 *   on(event, listener)     register a listener
 *   emit(event, ...args)    call every listener for that event with args
 *   off(event, listener)    remove a specific listener
 *   once(event, listener)   fire once, then auto-remove
 *
 *   const bus = new EventEmitter();
 *   const greet = name => console.log("hi", name);
 *   bus.on("hello", greet);
 *   bus.emit("hello", "Sam");   // "hi Sam"
 *   bus.off("hello", greet);
 *   bus.emit("hello", "Sam");   // (nothing)
 *
 * KEY LESSONS:
 *  - Map of  event -> array of listeners
 *  - store {fn, config} objects so you can support per-listener flags like `once`
 *  - emit loops with an ARROW so listeners see `this` = the emitter
 *  - off uses filter + set (immutable REPLACE) → safe to remove during emit's loop
 *    (splice-in-place during forEach would skip the next listener)
 */

// --- YOUR ATTEMPT ---


// --- SOLUTION ---
class EventEmitter {
  constructor() {
    this.events = new Map();
  }
  on(event, listener) {
    if (!this.events.has(event)) this.events.set(event, []);
    this.events.get(event).push({ fn: listener, config: {} });
    return this;
  }
  once(event, listener) {
    if (!this.events.has(event)) this.events.set(event, []);
    this.events.get(event).push({ fn: listener, config: { once: true } });
    return this;
  }
  emit(event, ...args) {
    if (!this.events.has(event)) return;
    this.events.get(event).forEach(({ fn, config }) => {
      fn.apply(this, args);
      if (config.once) this.off(event, fn);
    });
  }
  off(event, listener) {
    if (!this.events.has(event)) return;
    this.events.set(event, this.events.get(event).filter(l => l.fn !== listener));
  }
}

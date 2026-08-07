// EventEmitter
//   subscribe(event, cb) -> returns { release() }   (unsubscribe)
//   emit(event, ...args)  -> call every subscriber with args
//   once(event, cb)       -> fire ONCE, then auto-unsubscribe
//
// You've built subscribe/emit/release twice — write them from memory,
// then add once(). Think about how once can REUSE subscribe.
class Event{
  
}
class EventEmitter {
  constructor() {
    this.eventMap = new Map()
    // TODO: an event -> array (or Map) of callbacks
  }

  subscribe(event, cb) {
    if(!this.eventMap.has(event))
      this.eventMap.set(event,[])
      this.eventMap.get(event).push(cb)
      return {
        release:()=>{
          this.eventMap.set(event,this.eventMap.get(event).filter(a=>a!=cb))
        }
      }
    // TODO: register cb under event; return { release: () => ... }
  }

  emit(event, ...args) {
    if(!this.eventMap.has(event))
    {
      console.log("No Subscribers")
      return 
    }
    const callBack = this.eventMap.get(event)
    for(let cb of callBack){
      cb.apply(this,args)
    }

    // TODO: call every cb registered for event with ...args
    //       (guard: no subscribers → just return)
  }

  once(event, cb) {
    const sub = this.subscribe(event, (...args) => {
      sub.release()     // unsubscribe myself first
      cb(...args)       // then fire the real callback
    })
    // TODO: subscribe a wrapper that releases itself, then calls cb
    //       hint: capture the subscription so the wrapper can release it
  }
}

// ─── tests ──────────────────────────────────────────────────────────────
const em = new EventEmitter()
const sub = em.subscribe('msg', (m) => console.log('sub:', m))
em.once('msg', (m) => console.log('once:', m))

em.emit('msg', 'hello')   // sub: hello   once: hello
em.emit('msg', 'world')   // sub: world          (once must NOT fire again)
sub.release()
em.emit('msg', 'bye')     // (nothing — both gone)

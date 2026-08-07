class EventEmitter {
    constructor() {
        this.eventRegistry = new Map()
      // store: event name → list of listeners
    }
    on(event, listener) {
       if (!this.eventRegistry.has(event)){
         this.eventRegistry.set(event,[])
       }
       this.eventRegistry.get(event).push({fn:listener,config:{}})
      // register listener for this event
    }
    emit(event, ...args) {
        if (!this.eventRegistry.has(event))
            return 
        const listeners = this.eventRegistry.get(event)
        listeners.forEach(({fn,config}) => {
            fn.apply(this, args)
            if(config.once){
                this.off(event, ln)
            }
        });
      // call every listener registered for this event, passing args
    }
    off(event, listener) {
        if (!this.eventRegistry.has(event)){
            return 
          }
          const list = this.eventRegistry.get(event).filter(ln=>ln.fn != listener)
          this.eventRegistry.set(event,list)
      // remove this specific listener from the event
    }
    once(event, listener){
        if (!this.eventRegistry.has(event)){
            this.eventRegistry.set(event,[])
          }
          this.eventRegistry.get(event).push({fn:listener,config:{once:true}})
    }
  }



  const orig = { a: 1, nested: { b: 2 }, list: [3, 4] };
const copy = deepClone(orig);


const deepClone = (obj,newObj={})=>{
    for (let key in obj){
        if (obj.hasOwnKey(key)){
            if (typeof key ==="object"){
                const keyValue = deepClone(obj[key],{}) 
                newObj[key] = keyValue[key]
            }else {
                newObj[key] = obj[key]
            }
        }
    }
    return newObj
}



class MyPromise {
    constructor(executor) {
      this.state = "pending";
      this.value = undefined;
      this.onFulfilledCallbacks = []
      this.onRejectedCallbacks = []
      const settle = (newState,value)=>{
        if(this.state !== "pending"){
            throw new Error("Promise already settled")
        }
        this.state = newState
        this.value = value
      }
      const resolve = (value) => {
        settle("fulfilled",value)
      };
      const reject = (reason) => {
        settle("rejected",reason)
      };

      const then = (onFulfilled,onRejected)=>{
        if(this.state === "pending"){
            this.onFulfilledCallbacks.push(onFulfilled)
            this.onRejectedCallbacks.push(onRejected)
        }
        else if(this.state === "fulfilled"){
            onFulfilled(this.value)
        }
        else{
            onRejected(this.value)
        }
        return new MyPromise((resolve,reject)=>{
            if(this.state === "pending"){
                this.onFulfilledCallbacks.push(()=>{
                    resolve(onFulfilled(this.value))
                })
                this.onRejectedCallbacks.push(()=>{
                    reject(onRejected(this.value))
                })
            }
            else if(this.state === "fulfilled"){
                resolve(onFulfilled(this.value))
            }
            else{
                reject(onRejected(this.value))
            }
        })
    }
  
      executor(resolve, reject)
  }
}
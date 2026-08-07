class LRUCache{
  constructor(config){
      this.capacity=config.capacity
      this.map = new Map()

      this.head = {key:null,value:null}
      this.tail = {key:null,value:null}

      //head --> tail
      this.head.next = this.tail
      //head <--tail
      this.tail.prev = this.head
  }

  // head -- node ---tail
  _remove(node){
      node.prev.next = node.next
      node.next.prev = node.prev
  }

// head -- node ---tail add newNode
  _addToFront(node){
      node.prev = this.head 
      node.next = this.head.next

      this.head.next.prev = node
      this.head.next = node
  }

  get(key){
      if(!this.map.has(key)) return -1

      const node = this.map.get(key)
      this._remove(node)
      this._addToFront(node)
      return node.value
  }

  put(key,value){
      if(this.map.has(key)){
          const node = this.map.get(key)
          node.value = value
          this._remove(node)
          this._addToFront(node)
          return
      }

      const node = {key,value}
      this._addToFront(node)
      this.map.set(key,node);

      if(this.map.size > this.capacity)  this._evict()
  }
  _evict(){
      const nodeToEvict = this.tail.prev;
      this.map.delete(nodeToEvict.key)
      this._remove(nodeToEvict)

  }
}

// ─── tests ──────────────────────────────────────────────────────────────
const c = new LRUCache({
  capacity:2
})
c.put(1, 'a')
c.put(2, 'b')
console.log(c.get(1)) // 'a'   (1 is now most-recent; 2 is now the LRU)
c.put(3, 'c')         // capacity 2 exceeded → evict key 2
console.log(c.get(2)) // -1    (evicted)
console.log(c.get(3)) // 'c'
c.put(4, 'd')         // evict key 1 (least-recent)
console.log(c.get(1)) // -1
console.log(c.get(3)) // 'c'
console.log(c.get(4)) // 'd'
class Broker {
  constructor() {
    this.topics=new Map()
  }

  createTopic(topic,numPartitions){
      if(this.topics.has(topic)) throw new Error("Topic Exists")
      
      this.topics.set(topic,new Array(numPartitions).fill([]))
      return this.topics.get(topic)
  }
  getTopic(topic){
    if(!this.topics.has(topic)) throw new Error("Topic Missing")
    return this.topics.get(topic)
  }
  numPartitions(name) {
    return this.getTopic(name).partitions.length;
  }
  append(name, partition, key, value) {
    if(!this.topics.has(topic)) throw new Error("Topic Missing")
    
    const log = this.getTopic(name).partition[partition];
    const offset = log.length;

    const record = {offset,key,value};
    log.push(record)
    return record

  }
  read(name,partition,fromOffset){
    this.getTopic(name).partition[partition].slice(fromOffset);
  }
}

function hashKey(key) {
   // generate HASH 
  let h = 2166136261 >>> 0; // FNV offset basis

   for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619) >>> 0; // FNV prime, keep unsigned 32-bit
  }
  return h >>> 0;
}


class Producer {
  constructor(broker){
    this.broker=broker;
    this.rrCount = 0 

  }
  partitionFor(topic,key){
    const n = this.broker.numPartitions(topic);
    if (!key) {
      const p = this.rrCounter % n;
      this.rrCounter++;
      return p;
    }
    return hashKey(key) %n
  }
  send({ topic, key, value }) {
    const partition = this.partitionFor(topic,key)
    const record = this.broker.append(topic, partition, key ?? null, value)
    return { topic, partition, offset: record.offset, key: key ?? null, value };
  }
}


class ConsumerGroup {
  constructor(broker, groupId, topic) {

  }
}
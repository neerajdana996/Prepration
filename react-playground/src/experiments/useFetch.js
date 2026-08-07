import { useEffect, useState } from 'react'

const CACHE_TTL = 60_000 // 60 seconds
const cache = new Map()
const inFlight = new Map()
const MAX_CACHE_ENTRIES = 100

function fetchOnce(url) {
  if (inFlight.has(url)) {
    return inFlight.get(url)
  }

  const request = fetch(url)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      return response.json()
    })
    .then(data => {
      writeCache(url, data)
      return data
    })
    .finally(() => {
      inFlight.delete(url)
    })

  inFlight.set(url, request)

  return request
}
function readCache(url) {
  const entry = cache.get(url)

  if (!entry) return undefined

  if (Date.now() >= entry.expiresAt) {
    cache.delete(url)
    return undefined
  }

  // Move this entry to the newest position.
  cache.delete(url)
  cache.set(url, entry)

  return entry.data
}

function writeCache(url, data) {
  cache.set(url, {
    data,
    expiresAt: Date.now() + CACHE_TTL,
  })

  if (cache.size > MAX_CACHE_ENTRIES) {
    const oldestUrl = cache.keys().next().value
    cache.delete(oldestUrl)
  }
}
export function useFetch(url) {
  const [data, setData] = useState(() => readCache(url) ?? null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [requestNumber, setRequestNumber] = useState(0)
  const refetch = useCallback(() => {
    cache.delete(url)
    setRequestNumber(number => number + 1)
  }, [url])
  useEffect(() => {
    const cachedData = readCache(url)

    if (cachedData) {
      setData(cachedData)
      setError(null)
      setLoading(false)
      return
    }
    setLoading(true)
    setError(null)
    let active = true

    fetchOnce(url)
      .then(rawData => {
        if (active) {
          setData(rawData)
        }
      })
      .catch(error => {
        if (active) {
          setError(error)
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false)
        }
      })
   

    return () => {
      active=false
    }
  }, [url, requestNumber])

  return { data, loading, error, refetch }
}




//isAnagram("anagram", "nagaram") → true
//isAnagram(̧"rat", "car")         → false

const isAnagram = (str1,str2)=>{
  if (str1.length !== str2.length) return false
  const freq= new Array(26).fill(0)
  const base = "a".charCodeAt(0)
  str1 = str1.split("").filter(ch => ch.match(/[a-z]/i)).join("").toLowerCase()
  str2 = str2.split("").filter(ch => ch.match(/[a-z]/i)).join("").toLowerCase()
  console.log(str1,str2)
  for (let ch in str1) freq[ch.charCodeAt(0) - base]++
  for (let ch in str2) {
    if(--freq[ch.charCodeAt(0) - base] <0)
      return false
  }

  return true

}

console.log(isAnagram("anagram", "nagaram"))
console.log(isAnagram("anag$$$ram", "naga#@#ram"))
console.log(isAnagram("rat", "car"))




function myNew (constructor, ...args) {
   const obj = {}
   obj.__proto__ = constructor.prototype
   console.log(args)
   const result = constructor.apply(obj,args)
   if(result !=null && typeof result !="object"){
    return result
   }
   return obj;
}


function myNew(Constructor, ...args) {
  const obj = Object.create(Constructor.prototype)   // steps 1 + 2
  const result = Constructor.apply(obj, args)         // step 3: run with this = obj
  return (result !== null && typeof result === 'object') ? result : obj  // step 4
}

const Person = function (name, age) {
  this.name = name
  this.age = age
}

Person.prototype.sayName = function(){
  console.log(`Hello ${this.name} who is ${this.age} old`)
}
const person = myNew(Person, "John", 30)
console.log(person.sayName())
// A resilient shared socket: one instance for the whole dashboard, and it
// auto-reconnects with exponential backoff if the server drops. Consumers attach
// listeners to this STABLE wrapper (an EventTarget), so their listeners survive
// reconnects even though the underlying WebSocket is swapped out.
class ReconnectingSocket extends EventTarget {
  constructor(url) {
    super()
    this.url = url
    this.retry = 0
    this.connect()
  }

  connect() {
    this.ws = new WebSocket(this.url)
    this.ws.addEventListener('open', () => {
      this.retry = 0
      this.dispatchEvent(new Event('open'))
    })
    this.ws.addEventListener('message', (e) => {
      this.dispatchEvent(new MessageEvent('message', { data: e.data }))
    })
    this.ws.addEventListener('close', () => {
      this.dispatchEvent(new Event('close'))
      this.scheduleReconnect()
    })
    this.ws.addEventListener('error', () => this.dispatchEvent(new Event('error')))
  }

  scheduleReconnect() {
    this.retry = Math.min(this.retry + 1, 6)
    const delay = Math.min(1000 * 2 ** this.retry, 10000) // backoff, capped at 10s
    setTimeout(() => this.connect(), delay)
  }

  get readyState() {
    return this.ws ? this.ws.readyState : WebSocket.CONNECTING
  }
}

let instance = null

export function getSocket() {
  if (!instance) instance = new ReconnectingSocket('ws://localhost:4000')
  return instance
}

import http from 'http'
import express from 'express'
import cors from 'cors'
import { WebSocketServer } from 'ws'
import { makeDevices, STATUSES } from './devices.js'

const app = express()
app.use(cors())

const devices = makeDevices(1000)

// ── REST: paginated + filtered list ──────────────────────────────
// GET /devices?page=1&pageSize=25&status=all&q=
app.get('/devices', (req, res) => {
  const page = parseInt(req.query.page, 10) || 1
  const pageSize = parseInt(req.query.pageSize, 10) || 25
  const status = req.query.status || 'all'
  const q = (req.query.q || '').toLowerCase()

  let filtered = devices
  if (status !== 'all') filtered = filtered.filter((d) => d.status === status)
  if (q) filtered = filtered.filter((d) => d.name.toLowerCase().includes(q))

  const total = filtered.length
  const start = (page - 1) * pageSize
  const items = filtered.slice(start, start + pageSize)
  res.json({ devices: items, total, page, pageSize })
})

const server = http.createServer(app)
const wss = new WebSocketServer({ server })

wss.on('connection', () => console.log('client connected — clients:', wss.clients.size))

// ── WebSocket: mutate ~15 devices every second, broadcast deltas ──
setInterval(() => {
  const changed = []
  for (let k = 0; k < 150; k++) {
    const d = devices[Math.floor(Math.random() * devices.length)]
    d.cpu = Math.max(0, Math.min(100, d.cpu + Math.round((Math.random() - 0.5) * 20)))
    d.temp = Math.max(0, Math.min(100, d.temp + Math.round((Math.random() - 0.5) * 10)))
    if (Math.random() < 0.1) d.status = STATUSES[Math.floor(Math.random() * STATUSES.length)]
    d.lastUpdated = Date.now()
    changed.push({ ...d })
  }
  const msg = JSON.stringify({ type: 'deltas', devices: changed })
  wss.clients.forEach((c) => { if (c.readyState === 1) c.send(msg) })
}, 1000)

server.listen(4000, () => console.log('IoT server → http://localhost:4000 (ws on same port)'))

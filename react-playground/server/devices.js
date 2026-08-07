export const SITES = [
  'SJC-01', 'BLR-02', 'AMS-03', 'NYC-04', 'LON-05',
  'TOK-06', 'SYD-07', 'FRA-08', 'SIN-09', 'DXB-10',
]
export const STATUSES = ['online', 'offline', 'degraded']

// Seed an in-memory dataset. This stands in for the "devices JSON file".
export function makeDevices(n = 1000) {
  const devices = []
  for (let i = 1; i <= n; i++) {
    devices.push({
      id: 'D' + String(i).padStart(4, '0'),
      name: 'device-' + i,
      site: SITES[i % SITES.length],
      status: 'online',
      cpu: 20 + (i % 50),
      temp: 30 + (i % 40),
      lastUpdated: Date.now(),
    })
  }
  return devices
}

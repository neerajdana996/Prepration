import { createApi, fakeBaseQuery } from '@reduxjs/toolkit/query/react'

const MOCK_DEVICES = [
  { id: 'D1', name: 'Sensor Alpha', status: 'online' },
  { id: 'D2', name: 'Gateway Beta', status: 'offline' },
  { id: 'D3', name: 'Pump Gamma', status: 'online' },
]

// Module-level counter to PROVE how many real fetches actually happened.
let requestCount = 0

// createApi generates the whole data-fetching layer: cache, hooks, loading/error
// flags, dedup, refetch. fakeBaseQuery + queryFn lets us mock without a real HTTP call.
export const devicesApi = createApi({
  reducerPath: 'devicesApi',
  baseQuery: fakeBaseQuery(),
  endpoints: (builder) => ({
    getDevices: builder.query({
      async queryFn() {
        requestCount += 1
        const served = requestCount
        await new Promise((r) => setTimeout(r, 800)) // simulate network latency
        return { data: { devices: MOCK_DEVICES, servedByRequest: served } }
      },
    }),
  }),
})

// RTK Query auto-generates the hook from the endpoint name.
export const { useGetDevicesQuery } = devicesApi

import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
import { getSocket } from './socket'

export const dashboardApi = createApi({
  reducerPath: 'dashboardApi',
  baseQuery: fetchBaseQuery({ baseUrl: 'http://localhost:4000' }),
  endpoints: (builder) => ({
    getDevices: builder.query({
      query: ({ page, pageSize, status, q }) =>
        `/devices?page=${page}&pageSize=${pageSize}&status=${status}&q=${encodeURIComponent(q)}`,

      // ── Infinite-scroll accumulation ─────────────────────────────
      // Ignore `page` in the cache key → every page for a given filter shares
      // ONE cache entry that we append to. Change the filter → new entry.
      serializeQueryArgs: ({ endpointName, queryArgs }) =>
        `${endpointName}(${queryArgs.status},${queryArgs.q})`,

      // Append the new page's devices (dedup by id), keep the latest total.
      merge: (currentCache, newData) => {
        const seen = new Set(currentCache.devices.map((d) => d.id))
        currentCache.devices.push(...newData.devices.filter((d) => !seen.has(d.id)))
        currentCache.total = newData.total
      },

      // Refetch (and thus merge) whenever the page number advances.
      forceRefetch: ({ currentArg, previousArg }) =>
        currentArg?.page !== previousArg?.page,

      // ── Live updates: patch the accumulated list in place ────────
      async onCacheEntryAdded(arg, { updateCachedData, cacheDataLoaded, cacheEntryRemoved }) {
        await cacheDataLoaded
        const socket = getSocket()
        const listener = (event) => {
          let msg
          try { msg = JSON.parse(event.data) } catch { return }
          if (msg.type !== 'deltas') return
          const byId = new Map(msg.devices.map((d) => [d.id, d]))
          updateCachedData((draft) => {
            draft.devices.forEach((d) => {
              const upd = byId.get(d.id)
              if (upd) Object.assign(d, upd)
            })
          })
        }
        socket.addEventListener('message', listener)
        await cacheEntryRemoved
        socket.removeEventListener('message', listener)
      },
    }),
  }),
})

export const { useGetDevicesQuery } = dashboardApi

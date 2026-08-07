import { configureStore } from '@reduxjs/toolkit'
import { dashboardApi } from './dashboardApi'

export const dashboardStore = configureStore({
  reducer: { [dashboardApi.reducerPath]: dashboardApi.reducer },
  middleware: (getDefault) => getDefault().concat(dashboardApi.middleware),
})

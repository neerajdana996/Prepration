import { configureStore } from '@reduxjs/toolkit'
import counterReducer from './counterSlice'
import { devicesApi } from './devicesApi'

// configureStore wires DevTools, thunk middleware, and good defaults automatically.
// RTK Query needs its reducer + middleware registered here.
export const store = configureStore({
  reducer: {
    counter: counterReducer,
    [devicesApi.reducerPath]: devicesApi.reducer,
  },
  middleware: (getDefault) => getDefault().concat(devicesApi.middleware),
})

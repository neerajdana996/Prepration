import { createSlice, createSelector } from '@reduxjs/toolkit'

// createSlice generates the action creators + reducer for you.
// The "mutations" below are safe: RTK uses Immer to produce immutable updates.
const counterSlice = createSlice({
  name: 'counter',
  initialState: { a: 0, b: 0 },
  reducers: {
    incA: (state) => { state.a += 1 },
    incB: (state) => { state.b += 1 },
  },
})

export const { incA, incB } = counterSlice.actions

// ── Dedicated selectors, colocated with the slice ──────────────────
// Components import THESE instead of reaching into state shape (s => s.counter.a).
// Benefit: the store structure is encapsulated here — if it changes, you fix it
// in one place, not in every component.
export const selectA = (state) => state.counter.a
export const selectB = (state) => state.counter.b

// A MEMOIZED derived selector (reselect, bundled with RTK). Recomputes only when
// a or b changes; for derived objects/arrays it also returns a STABLE reference,
// which prevents needless re-renders downstream.
export const selectTotal = createSelector([selectA, selectB], (a, b) => a + b)

export default counterSlice.reducer

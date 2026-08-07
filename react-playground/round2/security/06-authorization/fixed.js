// ✅ Authorization is enforced on the SERVER, on EVERY request. Client hiding is UX only.

app.post('/api/delete-all', requireAuth, requireRole('admin'), (req, res) => {
  // only reached if the server confirmed an authenticated admin
  // ...perform the action...
  res.json({ ok: true })
})

function requireAuth(req, res, next) {
  if (!req.user) return res.status(401).json({ error: 'unauthenticated' })
  next()
}

function requireRole(role) {
  return (req, res, next) => {
    if (req.user.role !== role) return res.status(403).json({ error: 'forbidden' })
    next()
  }
}

// Principle: the client is fully controllable — anyone can call your API directly,
// bypassing the UI. Validate + authorize on the server for every request.
// Client-side role checks are for UX (don't show what they can't use), NEVER for security.

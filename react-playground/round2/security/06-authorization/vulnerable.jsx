// ❌ Client HIDES the admin action based on role — but that's only UX, not security.
function Toolbar({ user }) {
  return (
    <div>
      {user.role === 'admin' && (
        <button onClick={() => fetch('/api/delete-all', { method: 'POST', credentials: 'include' })}>
          Delete all
        </button>
      )}
    </div>
  )
}

// The API endpoint has NO server-side authorization check, so a non-admin just
// calls it directly — the hidden button changed nothing:
//   fetch('/api/delete-all', { method: 'POST', credentials: 'include' })
//   curl -X POST https://app.com/api/delete-all --cookie "session=<their own session>"
//
// Anyone can inspect the network tab, see the endpoint, and hit it. The UI is not a gate.

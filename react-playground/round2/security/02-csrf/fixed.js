// ✅ Two layers stop CSRF.

// 1) SameSite cookie (set by the server). Cross-site requests do NOT include it,
//    so the forged form in vulnerable.html arrives UNAUTHENTICATED.
//      Set-Cookie: session=...; HttpOnly; Secure; SameSite=Lax

// 2) CSRF token: the server issues a random per-session token; the client echoes
//    it on every state-changing request; the server verifies it. evil.com cannot
//    read your token (same-origin policy), so it can't forge a valid request.
async function transfer(to, amount) {
  const csrf = document
    .querySelector('meta[name="csrf-token"]')      // server rendered this into the page
    .getAttribute('content')

  await fetch('/transfer', {
    method: 'POST',                                 // state changes use POST, never GET
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': csrf,                         // <-- the proof it came from our origin
    },
    body: JSON.stringify({ to, amount }),
  })
}

// Server: reject if X-CSRF-Token is missing or !== the session's token.
// Also validate the Origin/Referer header as a cheap extra check.

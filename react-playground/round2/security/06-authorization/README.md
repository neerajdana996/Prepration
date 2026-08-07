# 06 · Authorization (never trust the client)

**What:** client-side checks (hiding a button, disabling a field) are **UX, not security**. Anyone can read your JS, see the endpoints, and call the API directly.

## Before → after
- **Before** ([vulnerable.jsx](vulnerable.jsx)): React hides the admin button by role, but the endpoint has no check → `curl`/direct `fetch` bypasses it.
- **After** ([fixed.js](fixed.js)): server middleware **authenticates + authorizes every request** → `403` for non-admins.

See [diagram.svg](diagram.svg).

**Soundbite:** *"The client is fully controllable, so I enforce authz on the server for every request; UI hiding is only for UX — never a security boundary."*

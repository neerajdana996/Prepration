# 03 · Auth token storage

**What:** *where* you keep the session/JWT decides whether an XSS can steal it.

## Before → after
- **Before** ([vulnerable.js](vulnerable.js)): JWT in `localStorage` → any JS reads it → **one XSS = stolen token**.
- **After** ([fixed.js](fixed.js)): **HttpOnly + Secure + SameSite** cookie → JS can't read it; the browser sends it automatically.

See [diagram.svg](diagram.svg).

**Trade-off:** auto-sent cookies introduce **CSRF** → handled by `SameSite` (+ a CSRF token). See [02-csrf](../02-csrf/README.md).

**Soundbite:** *"Auth tokens go in HttpOnly cookies so XSS can't read them; `localStorage` is fine only for non-sensitive prefs like theme."*

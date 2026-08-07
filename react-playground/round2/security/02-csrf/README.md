# 02 · CSRF (Cross-Site Request Forgery)

**What:** a malicious site makes the victim's *logged-in* browser fire a state-changing request to your app. The browser auto-attaches the session cookie, so if you trust the cookie **alone**, the forged request succeeds.

## Before → after
- **Before** ([vulnerable.html](vulnerable.html)): the endpoint trusts the auto-sent session cookie, no token → `evil.com` auto-submits a form → the action runs.
- **After** ([fixed.js](fixed.js)):
  1. **`SameSite=Lax/Strict`** cookie → not sent on cross-site requests.
  2. **CSRF token** the client echoes and the server verifies (`evil.com` can't read it — same-origin policy).
  3. Use **POST** for state changes; check **Origin/Referer**.

See [diagram.svg](diagram.svg).

**Soundbite:** *"Cookies are auto-sent cross-site, so cookie-only auth is CSRF-able. SameSite blocks the cross-site cookie, and a CSRF token proves the request came from my own origin."*

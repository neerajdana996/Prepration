// ✅ Keep the session in an HttpOnly cookie set by the SERVER — JS cannot read it.
//      Set-Cookie: session=...; HttpOnly; Secure; SameSite=Lax
//
// HttpOnly  → document.cookie can't see it, so XSS can't exfiltrate it
// Secure    → only sent over HTTPS
// SameSite  → not sent on cross-site requests (mitigates the CSRF that auto-sent cookies invite)

// The browser attaches the cookie automatically — you never touch the token in JS:
fetch('/api', { credentials: 'include' })

// Trade-off you must state: auto-sent cookies → CSRF risk → SameSite (+ a CSRF token). See 02-csrf.
// Rule: HttpOnly + Secure + SameSite for AUTH. localStorage only for non-sensitive prefs (theme, etc.).

# Frontend Security — attacks, before/after, and fixes

A reference library. Each folder = one attack/principle with:
- `README.md` — what it is, the before→after, the fix
- `vulnerable.*` / `fixed.*` — code you can read (and mostly run)
- `diagram.svg` — before/after visual

| # | Topic | One-line |
|---|-------|----------|
| 01 | **XSS** | injected script runs in your page → escape output, sanitize HTML, CSP |
| 02 | **CSRF** | forged request from a logged-in browser → SameSite cookies + CSRF token |
| 03 | **Token storage** | JS-readable token stolen via XSS → HttpOnly + Secure + SameSite cookie |
| 04 | **Clickjacking** | your UI iframed over a decoy → X-Frame-Options / CSP frame-ancestors |
| 05 | **CSP** | defense-in-depth header that blocks inline/injected scripts |
| 06 | **Authorization** | never trust the client → re-check authz on the server |

**The umbrella principle:** prevent injection (escape + sanitize + CSP), protect the session (HttpOnly/SameSite + CSRF), and **never trust the client** — defense in depth, not one layer.

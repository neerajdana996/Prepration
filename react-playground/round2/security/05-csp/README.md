# 05 · Content-Security-Policy (CSP)

**What:** a browser-enforced **allow-list** of where scripts/styles/etc. may come from, and whether inline scripts run. It's your **defense-in-depth backstop against XSS**.

## Before → after
- **Before** ([vulnerable.html](vulnerable.html)): no CSP → injected inline `<script>` runs; scripts load from any origin.
- **After** ([fixed.html](fixed.html)): `Content-Security-Policy: default-src 'self'; script-src 'self'` → inline blocked, only same-origin scripts.

See [diagram.svg](diagram.svg).

**Notes:** deliver as an **HTTP header** (preferred over `<meta>`). For inline you truly need, use a **nonce or hash** — never `'unsafe-inline'`. `frame-ancestors` in the same policy also stops clickjacking (04).

**Soundbite:** *"CSP is my XSS backstop — `script-src 'self'` blocks inline and injected scripts even if sanitization misses something."*

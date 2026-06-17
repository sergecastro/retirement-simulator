# Lovable — Command Center session link (`?session=` → localStorage)

**Status:** ✅ Implemented & published by Lovable on 2026-06-17.

## Purpose
Let anyone open their saved Command Center on any device via a single link:
```
https://familyforecast.ai/command-center?session=TEMP-XXXXXXXX
```
The Command Center figures out *whose* results to show by reading `ff_session_id`
from the browser's localStorage. This change seeds that value from the URL so a
fresh phone/browser (e.g. a person who never filled the form on that device) can
still load their saved results.

## What Lovable does (in `CommandCenter.tsx`, on page mount)
Runs **before** the existing code that reads `ff_session_id`:
```tsx
useEffect(() => {
  const sid = new URLSearchParams(window.location.search).get('session');
  if (sid) {
    localStorage.setItem('ff_session_id', sid.trim().toUpperCase());
    window.history.replaceState({}, '', window.location.pathname); // clean the URL
  }
}, []);
```

### Why `.toUpperCase()`
The backend stores and looks up session ids in canonical **uppercase**
(`analysis_results.intake_id`, with `.strip().upper()` on both the Streamlit
write side and the Flask `/cc/summary` read side). Uppercasing here guarantees
the lookup matches.

## How the data flows after this
```
familyforecast.ai/command-center?session=TEMP-XXXX
  → save ff_session_id (uppercase) to localStorage
  → existing code calls POST /cc/summary { intake: { session_id } }
  → Flask reads analysis_results (keyed by session_id) → returns real numbers
```
`analysis_results` rows persist (no TTL), so the link keeps working after the
24-hour `pending_intake` record expires.

## Known follow-up (optional, not required for numbers to show)
The numbers on every tab come from `/cc/summary` and work with this change alone.
The **"Ask the AI advisor"** chat (`/cc/chat`) builds its context from the
*posted intake*, not from the session id — so for the chat to also know the
user's specifics, Lovable should additionally populate the page's intake state
from the session. Displayed numbers do **not** depend on this.

## Test
```
POST https://forcash-api.onrender.com/cc/summary
{"intake":{"session_id":"TEMP-XXXXXXXX"}}
→ { "requiresAnalysis": false, "data": { ...real numbers... } }
```

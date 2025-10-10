# Explain Visual — Zero‑touch Add‑On (Bookmarklet / Userscript)

This add‑on overlays a small **“? Explain Visual”** button on top of charts and tables *in your browser only* (no changes to your app). 
Clicking the button opens a modal with a structured, plain‑English explanation plus basic, real‑time stats for the visual.

Works on your **Streamlit** pages at `http://localhost:850*` and any other page that uses Plotly charts or Streamlit DataFrames.

---

## Why this is safe
- **Zero‑touch:** It never edits your repository or server files. It’s 100% client‑side.
- **Local only:** Runs in your browser. No network calls, no data leaves your machine.
- **Removable:** Disable the userscript or delete the bookmark to remove it instantly.

---

## Two ways to use it (choose one)

### Option A — Bookmarklet (quickest)
1) Open Chrome (or Edge). Create a new bookmark in the bookmarks bar.
2) Name: `Explain Visual`  
3) Paste the contents of `bookmarklet.txt` into the URL/Location field. Save.
4) Go to your running app (e.g., `http://localhost:8501`) and **click the bookmark**.
5) Small “?” buttons will appear on charts/tables. Click a “?” to open the explanation modal.

> Note: you must click the bookmark once per page load (it’s by design and keeps it stateless).

### Option B — Tampermonkey Userscript (auto‑inject on localhost)
1) Install the Tampermonkey browser extension (Chrome Web Store).
2) In Tampermonkey, create a new script and paste the contents of `explain_visual.user.js`. Save.
3) Make sure the script is **enabled**. Visit your app at `http://localhost:850*`.
4) You’ll see “?” buttons automatically without clicking anything.

---

## What it can explain today
- **Plotly charts** rendered by Streamlit (`.js-plotly-plot`): we compute per‑series min/max/first/last, trend, and growth rate when x‑values are numeric (e.g., years).
- **Streamlit DataFrames** (`div[data-testid="stDataFrame"]`): basic summary with column count and a short description.
- **Other visuals** (images, Altair/Vega) receive a **generic** explanation block for now.

> The code is modular; you can add more analyzers in `explain_visual.js` under the `analyze()` function.

---

## Files
- `explain_visual.js` — core injector & modal logic.
- `bookmarklet.txt` — ready‑to‑paste `javascript:(...)` URL for a bookmark.
- `explain_visual.user.js` — Tampermonkey version that auto‑runs on `http://localhost:850*`.
- `LICENSE` — MIT.

---

## Developer notes (safe sandboxing)
- This add‑on **does not** import external libraries.
- It **never** sends HTTP requests.
- It attaches buttons next to detected visuals and a single, reusable modal element.
- To remove everything, refresh the page or disable the userscript.

---

## Known limitations
- Some third‑party renderers (e.g., deeply shadow‑DOMed Altair/Vega) expose limited raw data. We fall back to generic explanations.
- Very large Plotly traces are summarized (basic stats only) to avoid blocking the UI.

---

## Uninstall
- Bookmarklet: delete the bookmark.
- Userscript: disable or delete the script from Tampermonkey.


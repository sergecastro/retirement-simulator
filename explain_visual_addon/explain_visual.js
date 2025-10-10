/* Explain Visual — core injector (no network, no dependencies)
 * Adds a small "?" button on Plotly charts and Streamlit tables.
 * Clicking opens a modal with a structured explanation and basic stats.
 * Safe: pure client‑side. */
(function () {
  if (window.__EXPLAIN_VISUAL_ACTIVE__) {
    console.warn("Explain Visual is already active.");
    return;
  }
  window.__EXPLAIN_VISUAL_ACTIVE__ = true;

  const CSS = `
  .ev-btn{
    position:absolute; top:6px; right:6px; z-index: 9999;
    padding:4px 8px; border-radius:999px; border:1px solid rgba(0,0,0,.15);
    background:#fff; font-weight:700; cursor:pointer; box-shadow:0 1px 4px rgba(0,0,0,.15);
  }
  .ev-btn:hover{ background:#f0f0f0 }
  .ev-modal-backdrop{
    position:fixed; inset:0; background:rgba(0,0,0,0.35); z-index:99998;
    display:flex; align-items:center; justify-content:center;
  }
  .ev-modal{
    width:min(900px, 90vw); max-height:85vh; overflow:auto;
    background:white; border-radius:14px; box-shadow:0 10px 40px rgba(0,0,0,.25);
    padding:20px 22px; position:relative; font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,"Helvetica Neue",Arial;
  }
  .ev-close{ position:absolute; top:10px; right:14px; font-size:20px; cursor:pointer; }
  .ev-h{ margin:0 0 6px 0; font-size:18px; }
  .ev-kv{ font-size:13px; line-height:1.45; margin:4px 0; }
  .ev-section{ border:1px solid #eee; border-radius:10px; padding:10px 12px; margin:10px 0; }
  .ev-badge{ display:inline-block; padding:2px 8px; border-radius:999px; background:#f6f6f6; margin-right:6px; font-size:12px; }
  .ev-list{ margin:6px 0 0 18px; }
  `;

  function injectStyles(){
    const id = "ev-styles";
    if (document.getElementById(id)) return;
    const style = document.createElement("style");
    style.id = id;
    style.textContent = CSS;
    document.head.appendChild(style);
  }

  function ensureModal(){
    let backdrop = document.getElementById("ev-backdrop");
    if (backdrop) return backdrop;
    backdrop = document.createElement("div");
    backdrop.id = "ev-backdrop";
    backdrop.className = "ev-modal-backdrop";
    backdrop.style.display = "none";
    const modal = document.createElement("div");
    modal.className = "ev-modal";
    const close = document.createElement("div");
    close.className = "ev-close";
    close.innerHTML = "&times;";
    close.onclick = () => (backdrop.style.display = "none");
    const content = document.createElement("div");
    content.id = "ev-content";
    modal.appendChild(close);
    modal.appendChild(content);
    backdrop.appendChild(modal);
    backdrop.addEventListener("click", e => {
      if (e.target === backdrop) backdrop.style.display = "none";
    });
    document.body.appendChild(backdrop);
    return backdrop;
  }

  function openModal(html){
    const backdrop = ensureModal();
    const content = document.getElementById("ev-content");
    content.innerHTML = html;
    backdrop.style.display = "flex";
  }

  function addButton(container, type){
    // Avoid duplicates
    if (container.querySelector(":scope > .ev-btn")) return;
    const btn = document.createElement("button");
    btn.className = "ev-btn";
    btn.title = "Explain Visual";
    btn.textContent = "?";
    btn.addEventListener("click", () => {
      const info = analyze(container, type);
      const html = render(info);
      openModal(html);
    });
    container.style.position = container.style.position || "relative";
    container.appendChild(btn);
  }

  // Utilities
  function isNumber(x){ return typeof x === "number" && isFinite(x); }
  function safeMin(arr){ return arr.length ? Math.min.apply(null, arr) : null; }
  function safeMax(arr){ return arr.length ? Math.max.apply(null, arr) : null; }
  function formatPct(x){ return isNumber(x) ? (x*100).toFixed(1) + "%" : "—"; }
  function formatNum(x){
    if (!isNumber(x)) return "—";
    const abs = Math.abs(x);
    if (abs >= 1e9) return (x/1e9).toFixed(2)+"B";
    if (abs >= 1e6) return (x/1e6).toFixed(2)+"M";
    if (abs >= 1e3) return (x/1e3).toFixed(2)+"k";
    return x.toLocaleString(undefined, { maximumFractionDigits: 2 });
  }
  function slope(x, y){
    // simple linear regression slope (least squares)
    const n = Math.min(x.length, y.length);
    if (n < 2) return null;
    let sx=0, sy=0, sxx=0, sxy=0;
    for (let i=0;i<n;i++){ sx+=x[i]; sy+=y[i]; sxx+=x[i]*x[i]; sxy+=x[i]*y[i]; }
    return (n*sxy - sx*sy) / (n*sxx - sx*sx || 1);
  }

  // Core analyzer
  function analyze(container, type){
    const info = {
      type, title: guessTitle(container),
      details: [], insights: [], examples: [],
      definitions: [], raw: {}
    };

    if (type === "plotly"){
      const gd = container; // .js-plotly-plot root
      const data = gd.data || (gd.__plotly && gd.__plotly.data) || [];
      const layout = gd.layout || (gd.__plotly && gd.__plotly.layout) || {};
      info.raw.dataCount = data.length;
      const traces = [];
      let globalMin = +Infinity, globalMax = -Infinity;

      data.forEach((tr, i) => {
        const xs = Array.isArray(tr.x) ? tr.x : [];
        const ys = Array.isArray(tr.y) ? tr.y : [];
        const n = Math.min(xs.length, ys.length);
        const ynums = ys.filter(isNumber);
        const ymin = safeMin(ynums);
        const ymax = safeMax(ynums);
        if (isNumber(ymin)) globalMin = Math.min(globalMin, ymin);
        if (isNumber(ymax)) globalMax = Math.max(globalMax, ymax);
        const first = isNumber(ys[0]) ? ys[0] : null;
        const last  = isNumber(ys[n-1]) ? ys[n-1] : null;
        let m = null;
        // If x is numeric, compute slope over real x; else use index
        const xnums = xs.every(isNumber) ? xs : [...Array(n)].map((_,k)=>k);
        if (n >= 2) m = slope(xnums, ynums.length===n?ynums:ys.filter(isNumber));
        const trend = (isNumber(first) && isNumber(last)) ? last - first : null;
        const growth = (isNumber(first) && first !== 0 && isNumber(last)) ? (last-first)/Math.abs(first) : null;
        traces.push({
          name: tr.name || `Series ${i+1}`,
          n, ymin, ymax, first, last, trend, growth
        });
      });

      info.details.push(`Chart type: Plotly (${data.length} trace${data.length===1?"":"s"}).`);
      if (isFinite(globalMin) && isFinite(globalMax)){
        info.details.push(`Y‑range observed: ${formatNum(globalMin)} → ${formatNum(globalMax)}.`);
      }

      // Key insights
      traces.forEach(t => {
        const parts = [];
        parts.push(`n=${t.n}`);
        if (isNumber(t.first) && isNumber(t.last)){
          parts.push(`first=${formatNum(t.first)}`);
          parts.push(`last=${formatNum(t.last)}`);
          if (isNumber(t.trend)) parts.push(`Δ=${formatNum(t.trend)}`);
          if (isNumber(t.growth)) parts.push(`growth=${formatPct(t.growth)}`);
        }
        info.insights.push(`<span class="ev-badge">${t.name}</span> ${parts.join(" · ")}`);
      });

      // Examples / guidance
      info.examples.push("Hover the chart to see exact values for any point; compare the first vs. last value to gauge overall trend.");
      info.examples.push("If the series represents yearly projections, a positive Δ and positive growth% indicate improvement over the period.");
      info.examples.push("Look for divergence between series to understand scenario differences (e.g., baseline vs. stress case).");

      info.definitions.push("Δ (Delta): change from the first to the last point in the series.");
      info.definitions.push("Growth%: (last − first) ÷ |first|.");
      info.definitions.push("Y‑range: minimum and maximum Y value observed across all traces.");

    } else if (type === "table"){
      // Streamlit DataFrame wrapper
      const cols = container.querySelectorAll('table thead th');
      const rows = container.querySelectorAll('table tbody tr');
      info.details.push(`Table with ${rows.length} rows × ${cols.length} columns.`);
      info.insights.push("Use column headers to sort/filter (if enabled in your UI).");
      info.examples.push("Export this table to CSV (if your app offers a download button) and pivot in Excel to explore.");
      info.definitions.push("Row: a single record/observation. Column: a variable/feature.");

    } else {
      // Generic fallback
      info.details.push("This appears to be a static visual (image) or a chart type I can't introspect directly.");
      info.insights.push("Use the caption, axes labels, and legends to interpret the visual.");
      info.examples.push("If this is a Monte Carlo band, compare the median path vs. percentile bands for risk context.");
      info.definitions.push("Legend: explains series colors/markers; Axis: scales used to position values.");
    }

    return info;
  }

  function guessTitle(node){
    // Walk up a few ancestors to find a nearby header/text used as title
    let el = node;
    for (let i=0; i<4 && el; i++){
      const heading = el.querySelector && el.querySelector("h1,h2,h3,h4,strong,b");
      if (heading && heading.textContent.trim().length > 0){
        return heading.textContent.trim();
      }
      el = el.parentElement;
    }
    return "This visual";
  }

  function render(info){
    const sections = [];
    sections.push(`<div class="ev-section"><div class="ev-h">What you’re looking at</div>
      <div class="ev-kv"><b>${{}}escapeHtml(info.title)} — ${ {}}info.details.join(" ")}</div></div>`.replace("${{}}","${").replace("${ {}}","${"));
    // (The above line is a trick to keep JS template literals intact when written by Python.)

    if (info.insights.length){
      sections.push(`<div class="ev-section"><div class="ev-h">Key takeaways (auto‑generated)</div>
        <ul class="ev-list">${{}}info.insights.map(x=>`<li>${{}}x</li>`).join("")}</ul></div>`.replace("${{}}","${").replace("${{}}","${"));
    }

    if (info.examples.length){
      sections.push(`<div class="ev-section"><div class="ev-h">How to use this visual</div>
        <ul class="ev-list">${{}}info.examples.map(x=>`<li>${{}}escapeHtml(x)</li>`).join("")}</ul></div>`.replace("${{}}","${").replace("${{}}","${"));
    }

    if (info.definitions.length){
      sections.push(`<div class="ev-section"><div class="ev-h">Definitions</div>
        <ul class="ev-list">${{}}info.definitions.map(x=>`<li>${{}}escapeHtml(x)</li>`).join("")}</ul></div>`.replace("${{}}","${").replace("${{}}","${"));
    }

    return sections.join("");
  }

  function escapeHtml(str){
    return String(str)
      .replace(/&/g,"&amp;")
      .replace(/</g,"&lt;")
      .replace(/>/g,"&gt;")
      .replace(/"/g,"&quot;")
      .replace(/'/g,"&#39;");
  }

  function scanAndAttach(){
    injectStyles();
    // Plotly charts inside Streamlit
    document.querySelectorAll(".js-plotly-plot").forEach(el => addButton(el, "plotly"));
    // Streamlit DataFrames (AgGrid and dataframe share data-testid, but button goes on container)
    document.querySelectorAll('div[data-testid="stDataFrame"]').forEach(el => addButton(el, "table"));
    // Fallback: big images (likely Matplotlib renders)
    document.querySelectorAll('img[src^="data:image/png"]').forEach(el => {
      const container = el.parentElement || el;
      addButton(container, "image");
    });
  }

  scanAndAttach();
  // Also observe for dynamically added charts
  const mo = new MutationObserver(() => scanAndAttach());
  mo.observe(document.body, { childList: true, subtree: true });
})();
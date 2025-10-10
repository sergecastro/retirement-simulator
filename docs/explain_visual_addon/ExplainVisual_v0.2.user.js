// ==UserScript==
// @name         Explain Visual v0.2 (Streamlit localhost)
// @namespace    explain-visual
// @version      0.2.0
// @description  Overlay '?' explain buttons on charts/tables; open modal with global + auto explanations.
// @match        http://localhost:850*/
// @grant        none
// ==/UserScript==

(function () {
  if (window.__EXPLAIN_VISUAL_ACTIVE__) return;
  window.__EXPLAIN_VISUAL_ACTIVE__ = true;

  const CSS = `
  .ev-btn{
    position:absolute; top:8px; right:8px; z-index: 2147483647;
    padding:5px 10px; border-radius:999px; border:1px solid rgba(0,0,0,.15);
    background:#fff; font-weight:700; cursor:pointer; box-shadow:0 1px 4px rgba(0,0,0,.18);
  }
  .ev-btn:hover{ background:#f3f3f3 }
  .ev-modal-backdrop{
    position:fixed; inset:0; background:rgba(0,0,0,0.35); z-index:2147483646;
    display:flex; align-items:center; justify-content:center;
  }
  .ev-modal{
    width:min(980px, 92vw); max-height:86vh; overflow:auto;
    background:white; border-radius:14px; box-shadow:0 10px 40px rgba(0,0,0,.25);
    padding:22px 24px; position:relative; font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,"Helvetica Neue",Arial;
  }
  .ev-close{ position:absolute; top:10px; right:14px; font-size:22px; cursor:pointer; }
  .ev-h{ margin:0 0 6px 0; font-size:18px; }
  .ev-kv{ font-size:13px; line-height:1.45; margin:4px 0; }
  .ev-section{ border:1px solid #eee; border-radius:10px; padding:10px 12px; margin:10px 0; }
  .ev-badge{ display:inline-block; padding:2px 8px; border-radius:999px; background:#f6f6f6; margin-right:6px; font-size:12px; }
  .ev-list{ margin:6px 0 0 18px; }
  `;

  const EXPLAINERS = [
    {
      pattern: /(Monte\s*Carlo|Simulation Analysis|Success Rate)/i,
      overview: [
        "This Monte Carlo view projects portfolio outcomes across many randomized return paths.",
        "The shaded bands (or multiple lines) show different percentiles; the median is the 50th percentile path.",
        "“Success rate” is the share of simulations where the plan avoids depletion by the end of the horizon."
      ],
      examples: [
        "Compare median vs. pessimistic paths to gauge sequence-of-returns risk.",
        "If success rate < 85–90%, consider lowering withdrawals, delaying retirement, or increasing savings."
      ],
      defs: [
        "Success rate: percentage of simulated paths that meet funding goals without running out of assets.",
        "Percentile band: range capturing a proportion of outcomes (e.g., 10th–90th)."
      ]
    },
    {
      pattern: /(Cash Flow Analysis|Sankey)/i,
      overview: [
        "This Sankey diagram shows how money moves from income sources to expenses, savings, and taxes.",
        "The width of each flow is proportional to the amount flowing through that category."
      ],
      examples: [
        "Identify the largest outflows and evaluate potential reductions (e.g., housing, discretionary).",
        "Track how additional income allocates across taxes, savings, and spending."
      ],
      defs: [
        "Sankey: a flow diagram where band thickness indicates magnitude.",
        "Net cash flow: income minus total outflows in a period."
      ]
    },
    {
      pattern: /(IRMAA|Medicare)/i,
      overview: [
        "IRMAA adds an income-related surcharge to Medicare premiums based on MAGI from two years prior.",
        "This visual compares projected MAGI to IRMAA thresholds over time."
      ],
      examples: [
        "Plan Roth conversions in years where projected MAGI is below thresholds to avoid surcharges.",
        "Watch spike years triggered by RMDs or realized gains and evaluate smoothing strategies."
      ],
      defs: [
        "MAGI: Modified Adjusted Gross Income used for IRMAA determination.",
        "RMD: Required Minimum Distribution that can raise MAGI in retirement."
      ]
    },
    {
      pattern: /(Financial Trajector|Projection|Net Worth|Portfolio)/i,
      overview: [
        "This trajectory shows how portfolio value/net worth evolves across years under baseline assumptions.",
        "Lines can represent scenarios (baseline vs. stress/optimistic) or account classes."
      ],
      examples: [
        "Check for dips around retirement transitions or major cash events (home purchase, college).",
        "Use scenario gaps to understand sensitivity to returns, savings rate, or spending changes."
      ],
      defs: [
        "Baseline: current assumptions for returns, inflation, savings, spending.",
        "Scenario: alternative set of assumptions for what-if analysis."
      ]
    },
    {
      pattern: /(Goal Achievement|Gauge)/i,
      overview: [
        "Goal gauges summarize progress vs. targets (e.g., retirement readiness, liquidity).",
        "Each gauge aggregates model outputs into a single score to indicate current status."
      ],
      examples: [
        "If the gauge is borderline, review drivers (savings, expenses, time horizon) and adjust.",
        "Use side panels for the underlying numbers to see which lever moves the score."
      ],
      defs: [
        "Gauge: a compact indicator showing status against a goal threshold.",
        "Target: predefined level for 'on track' vs. 'at risk'."
      ]
    },
    {
      pattern: /(Timeline)/i,
      overview: [
        "The timeline plots key family/financial events (retirement dates, college, inheritances).",
        "Use it to align cash flows and verify that high-cost periods are funded."
      ],
      examples: [
        "Drag or review event dates to see how shifting timing affects projections.",
        "Layer in one-time inflows (inheritance) vs. outflows (tuition) to stress test cash coverage."
      ],
      defs: [
        "Event: one-time change affecting income, expenses, or assets.",
        "Horizon: the total planning window used in projections."
      ]
    }
  ];

  function injectStyles(){
    if (document.getElementById("ev-styles")) return;
    const style = document.createElement("style");
    style.id = "ev-styles";
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
    backdrop.addEventListener("click", e => { if (e.target === backdrop) backdrop.style.display = "none"; });
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
    if (getComputedStyle(container).position === "static"){
      container.style.position = "relative";
    }
    container.appendChild(btn);
  }

  // Utilities
  const isNum = x => typeof x === "number" && isFinite(x);
  const safeMin = a => a.length ? Math.min.apply(null, a) : null;
  const safeMax = a => a.length ? Math.max.apply(null, a) : null;
  const pct = x => isNum(x) ? (x*100).toFixed(1) + "%" : "—";
  const num = x => {
    if (!isNum(x)) return "—";
    const abs = Math.abs(x);
    if (abs >= 1e9) return (x/1e9).toFixed(2)+"B";
    if (abs >= 1e6) return (x/1e6).toFixed(2)+"M";
    if (abs >= 1e3) return (x/1e3).toFixed(2)+"k";
    return x.toLocaleString(undefined, { maximumFractionDigits: 2 });
  };
  function slope(x, y){
    const n = Math.min(x.length, y.length);
    if (n < 2) return null;
    let sx=0, sy=0, sxx=0, sxy=0;
    for (let i=0;i<n;i++){ sx+=x[i]; sy+=y[i]; sxx+=x[i]*x[i]; sxy+=x[i]*y[i]; }
    return (n*sxy - sx*sy) / (n*sxx - sx*sx || 1);
  }

  function nearestTitle(node){
    let el = node;
    for (let i=0; i<6 && el; i++){
      const h = el.querySelector && el.querySelector("h1,h2,h3,h4,[data-testid='stHeader'],strong,b");
      if (h && h.textContent.trim()) return h.textContent.trim();
      el = el.parentElement;
    }
    return "This visual";
  }

  function pickSectionExplainer(title){
    for (const ex of EXPLAINERS){
      if (ex.pattern.test(title)) return ex;
    }
    return null;
  }

  function analyze(container, type){
    const info = { type, title: nearestTitle(container), details: [], insights: [], examples: [], definitions: [], raw:{} };

    // Section-aware explainer
    const ex = pickSectionExplainer(info.title);
    if (ex){
      info.details.push("Section-aware guidance applied.");
      info.examples.push(...ex.examples);
      info.definitions.push(...ex.defs);
      info.overview = ex.overview;
    }

    if (type === "plotly"){
      const gd = container; // .js-plotly-plot root
      const data = gd.data || (gd.__plotly && gd.__plotly.data) || [];
      info.details.push(`Plotly chart with ${data.length} trace${data.length===1?"":"s"}.`);
      let gmin = +Infinity, gmax = -Infinity;

      data.forEach((tr, i) => {
        const xs = Array.isArray(tr.x) ? tr.x : [];
        const ys = Array.isArray(tr.y) ? tr.y : [];
        const n = Math.min(xs.length, ys.length);
        const ynums = ys.filter(isNum);
        const ymin = safeMin(ynums), ymax = safeMax(ynums);
        if (isNum(ymin)) gmin = Math.min(gmin, ymin);
        if (isNum(ymax)) gmax = Math.max(gmax, ymax);
        const first = isNum(ys[0]) ? ys[0] : null;
        const last  = isNum(ys[n-1]) ? ys[n-1] : null;
        const xnums = xs.every(isNum) ? xs : [...Array(n)].map((_,k)=>k);
        const m = n >= 2 ? slope(xnums, ynums.length===n?ynums:ys.filter(isNum)) : null;
        const trend = (isNum(first) && isNum(last)) ? last - first : null;
        const growth = (isNum(first) && first !== 0 && isNum(last)) ? (last-first)/Math.abs(first) : null;
        info.insights.push(`<span class="ev-badge">${tr.name || "Series "+(i+1)}</span> n=${n}${isNum(first)&&isNum(last)?` · first=${num(first)} · last=${num(last)} · Δ=${num(trend)} · growth=${pct(growth)}`:""}`);
      });

      if (isFinite(gmin) && isFinite(gmax)) info.details.push(`Observed Y-range: ${num(gmin)} → ${num(gmax)}.`);

    } else if (type === "table"){
      const cols = container.querySelectorAll('table thead th');
      const rows = container.querySelectorAll('table tbody tr');
      info.details.push(`Table with ${rows.length} rows × ${cols.length} columns.`);
      info.examples.push("Sort by clicking headers; export to CSV if available, then pivot in Excel for deeper analysis.");
      info.definitions.push("Row: a single record. Column: a variable/feature.");

    } else {
      info.details.push("Static image or non-introspectable chart. Showing generic guidance.");
      info.examples.push("Use axes, legends, and captions to interpret overall trends and scenario differences.");
      info.definitions.push("Legend: explains series colors/markers. Axis: the scale used to position values.");
    }

    return info;
  }

  function render(info){
    function esc(s){ return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#39;"); }
    const sections = [];
    const details = info.details.join(" ");

    sections.push(`<div class="ev-section"><div class="ev-h">What you’re looking at</div>
      <div class="ev-kv"><b>${esc(info.title)}</b> — ${esc(details)}</div></div>`);

    if (info.overview && info.overview.length){
      sections.push(`<div class="ev-section"><div class="ev-h">Global overview</div>
        <ul class="ev-list">${info.overview.map(x=>`<li>${esc(x)}</li>`).join("")}</ul></div>`);
    }

    if (info.insights && info.insights.length){
      sections.push(`<div class="ev-section"><div class="ev-h">Key takeaways (auto-generated)</div>
        <ul class="ev-list">${info.insights.map(x=>`<li>${x}</li>`).join("")}</ul></div>`);
    }

    if (info.examples && info.examples.length){
      sections.push(`<div class="ev-section"><div class="ev-h">How to use this visual</div>
        <ul class="ev-list">${info.examples.map(x=>`<li>${esc(x)}</li>`).join("")}</ul></div>`);
    }

    if (info.definitions && info.definitions.length){
      sections.push(`<div class="ev-section"><div class="ev-h">Definitions</div>
        <ul class="ev-list">${info.definitions.map(x=>`<li>${esc(x)}</li>`).join("")}</ul></div>`);
    }

    return sections.join("");
  }

  function scanAndAttach(){
    injectStyles();

    // Plotly charts (Streamlit uses .js-plotly-plot). Ignore tiny tiles.
    document.querySelectorAll(".js-plotly-plot").forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.width < 180 || r.height < 120) return; // avoid micro metrics
      addButton(el, "plotly");
    });

    // Streamlit DataFrames
    document.querySelectorAll('div[data-testid="stDataFrame"]').forEach(el => addButton(el, "table"));

    // Fallback: large PNG renders (Matplotlib). Ignore tiny images/icons.
    document.querySelectorAll('img[src^="data:image/png"]').forEach(img => {
      const r = img.getBoundingClientRect();
      if (r.width < 300 || r.height < 180) return;
      addButton(img.parentElement || img, "image");
    });
  }

  scanAndAttach();
  const mo = new MutationObserver(() => scanAndAttach());
  mo.observe(document.body, { childList: true, subtree: true });
})();

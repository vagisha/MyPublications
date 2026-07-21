#!/usr/bin/env python3
"""Build the standalone publications web page from curated data.

Reads `data/publications_filtered.json` (produced by curate.py) and writes a
SINGLE self-contained HTML file to `site/index.html`: all CSS and JS are
inlined, charts are hand-rolled SVG (no CDN / external requests), so the file
works fully offline and can be shared or opened directly in a browser.

Usage:
  python -X utf8 scripts/build_site.py
  python -X utf8 scripts/build_site.py --in data/publications_filtered.json \
      --out site/index.html --name "Vagisha Sharma" \
      --subtitle "University of Washington" \
      --orcid https://orcid.org/0000-0003-1922-439X
"""
import argparse
import datetime
import json
import os

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__PAGE_TITLE__ — Publications</title>
<style>
  :root {
    --bg: #fafafa;
    --panel: #ffffff;
    --text: #1a1a2e;
    --muted: #6b7280;
    --border: #e5e7eb;
    --c1: #2563eb; /* blue */
    --c2: #db2777; /* pink */
    --c3: #16a34a; /* green */
    --c4: #ea580c; /* orange */
    --c5: #7c3aed; /* purple */
    --c6: #0891b2; /* teal */
    --c7: #ca8a04; /* amber */
    --shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.5;
  }
  .wrap { max-width: 1100px; margin: 0 auto; padding: 0 20px 60px; }

  header.hero {
    padding: 48px 20px 32px;
    text-align: center;
    background: linear-gradient(135deg, #eef2ff 0%, #fdf2f8 50%, #ecfeff 100%);
    border-bottom: 1px solid var(--border);
  }
  header.hero h1 { margin: 0 0 4px; font-size: 2.2rem; letter-spacing: -0.02em; }
  header.hero .subtitle { color: var(--muted); font-size: 1.05rem; margin-bottom: 18px; }
  .links a {
    display: inline-block;
    margin: 0 6px;
    padding: 7px 16px;
    border-radius: 999px;
    background: var(--panel);
    border: 1px solid var(--border);
    color: var(--c1);
    text-decoration: none;
    font-weight: 600;
    font-size: 0.9rem;
    box-shadow: var(--shadow);
  }
  .links a:hover { border-color: var(--c1); }

  .stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 14px;
    margin: -28px 0 36px;
  }
  .stat {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 16px;
    text-align: center;
    box-shadow: var(--shadow);
    border-top: 4px solid var(--accent, var(--c1));
  }
  .stat .num { font-size: 1.9rem; font-weight: 800; }
  .stat .label { color: var(--muted); font-size: 0.82rem; text-transform: uppercase; letter-spacing: .04em; }

  h2.section-title {
    font-size: 1.3rem;
    margin: 44px 0 16px;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--border);
  }

  .charts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(440px, 1fr));
    gap: 20px;
  }
  .chart-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px;
    box-shadow: var(--shadow);
  }
  .chart-card h3 { margin: 0 0 4px; font-size: 1rem; }
  .chart-card .chart-note { color: var(--muted); font-size: 0.78rem; margin-bottom: 10px; }
  .chart-card svg { width: 100%; height: auto; display: block; }
  .legend { display: flex; gap: 16px; font-size: 0.78rem; color: var(--muted); margin-top: 6px; flex-wrap: wrap; }
  .legend span.swatch { display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 4px; vertical-align: middle; }

  .table-controls {
    display: flex; gap: 10px; flex-wrap: wrap; align-items: center;
    margin-bottom: 12px;
  }
  .table-controls input[type=search], .table-controls select {
    padding: 9px 12px;
    border: 1px solid var(--border);
    border-radius: 8px;
    font-size: 0.92rem;
    background: var(--panel);
  }
  .table-controls input[type=search] { flex: 1; min-width: 220px; }
  .result-count { color: var(--muted); font-size: 0.85rem; margin-left: auto; }

  table.pubs {
    width: 100%;
    border-collapse: collapse;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: var(--shadow);
  }
  table.pubs th, table.pubs td {
    padding: 10px 12px;
    text-align: left;
    border-bottom: 1px solid var(--border);
    vertical-align: top;
    font-size: 0.92rem;
  }
  table.pubs th {
    background: #f8fafc;
    cursor: pointer;
    user-select: none;
    white-space: nowrap;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: .03em;
    color: var(--muted);
  }
  table.pubs th.sorted-desc::after { content: " ▼"; }
  table.pubs th.sorted-asc::after { content: " ▲"; }
  table.pubs tbody tr:hover { background: #fafbfc; }
  table.pubs td.title-cell a { color: var(--text); text-decoration: none; font-weight: 600; }
  table.pubs td.title-cell a:hover { color: var(--c1); text-decoration: underline; }
  table.pubs td.title-cell .venue { color: var(--muted); font-size: 0.82rem; display: block; margin-top: 2px; }
  .badge {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.82rem;
    background: #eef2ff;
    color: var(--c1);
  }
  .type-pill {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 0.76rem;
    background: #f1f5f9;
    color: var(--muted);
    white-space: nowrap;
  }
  .authors .you { font-weight: 700; }
  .authors .more-toggle {
    color: var(--c1);
    cursor: pointer;
    font-size: 0.85rem;
    text-decoration: underline;
  }

  footer {
    margin-top: 50px;
    padding-top: 20px;
    border-top: 1px solid var(--border);
    color: var(--muted);
    font-size: 0.82rem;
    text-align: center;
  }

  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #0f1117;
      --panel: #171923;
      --text: #e6e6ef;
      --muted: #9099a8;
      --border: #2a2d3a;
      --shadow: 0 1px 3px rgba(0,0,0,0.4);
    }
    header.hero { background: linear-gradient(135deg, #1a1b2e 0%, #2a1a24 50%, #0f2530 100%); }
    table.pubs th { background: #1c1f2b; }
    .badge { background: #1c2340; }
    .type-pill { background: #1c1f2b; }
  }
</style>
</head>
<body>
<div class="wrap">

<header class="hero">
  <h1>__PAGE_NAME__</h1>
  <div class="subtitle">__PAGE_SUBTITLE__</div>
  <div class="links">
    __LINKS_HTML__
  </div>
</header>

<div class="stats" id="stats"></div>

<h2 class="section-title">Citation &amp; Publication Trends</h2>
<div class="charts-grid" id="charts"></div>

<h2 class="section-title">Publications</h2>
<div class="table-controls">
  <input type="search" id="search" placeholder="Search title, author, or venue…">
  <select id="typeFilter"><option value="">All types</option></select>
  <span class="result-count" id="resultCount"></span>
</div>
<div style="overflow-x:auto;">
<table class="pubs" id="pubsTable">
  <thead>
    <tr>
      <th data-key="title">Title</th>
      <th data-key="authors">Authors</th>
      <th data-key="type">Type</th>
      <th data-key="year">Year</th>
      <th data-key="cited_by_count" class="sorted-desc">Citations</th>
    </tr>
  </thead>
  <tbody id="pubsBody"></tbody>
</table>
</div>

<footer>
  __FOOTER_HTML__
</footer>

</div>

<script id="pub-data" type="application/json">__DATA_JSON__</script>
<script>
(function() {
  "use strict";
  var YOU = __YOU_JSON__;
  var PUBS = JSON.parse(document.getElementById("pub-data").textContent);
  var PALETTE = ["#2563eb", "#db2777", "#16a34a", "#ea580c", "#7c3aed", "#0891b2", "#ca8a04"];

  /* ---------- derived stats ---------- */
  function hIndex(pubs) {
    var counts = pubs.map(function(p){ return p.cited_by_count; }).sort(function(a,b){ return b-a; });
    var h = 0;
    for (var i = 0; i < counts.length; i++) {
      if (counts[i] >= i + 1) h = i + 1; else break;
    }
    return h;
  }
  var totalPapers = PUBS.length;
  var totalCitations = PUBS.reduce(function(s,p){ return s + p.cited_by_count; }, 0);
  var years = PUBS.map(function(p){ return p.year; }).filter(Boolean);
  var minYear = Math.min.apply(null, years), maxYear = Math.max.apply(null, years);

  var statsEl = document.getElementById("stats");
  var stats = [
    {num: totalPapers, label: "Publications", accent: PALETTE[0]},
    {num: totalCitations.toLocaleString(), label: "Total citations", accent: PALETTE[1]},
    {num: hIndex(PUBS), label: "h-index", accent: PALETTE[2]},
    {num: (maxYear - minYear + 1) + " yrs", label: minYear + " – " + maxYear, accent: PALETTE[3]}
  ];
  stats.forEach(function(s) {
    var d = document.createElement("div");
    d.className = "stat";
    d.style.setProperty("--accent", s.accent);
    d.innerHTML = '<div class="num">' + s.num + '</div><div class="label">' + s.label + '</div>';
    statsEl.appendChild(d);
  });

  /* ---------- per-year aggregation ---------- */
  var citByYear = {}, pubByYear = {};
  PUBS.forEach(function(p) {
    if (p.year) pubByYear[p.year] = (pubByYear[p.year] || 0) + 1;
    Object.keys(p.counts_by_year || {}).forEach(function(y) {
      citByYear[y] = (citByYear[y] || 0) + p.counts_by_year[y];
    });
  });
  var citYears = Object.keys(citByYear).map(Number).sort(function(a,b){return a-b;});
  var pubYears = Object.keys(pubByYear).map(Number).sort(function(a,b){return a-b;});

  var citedTrackedSum = citYears.reduce(function(s,y){ return s + citByYear[y]; }, 0);
  var untrackedNote = totalCitations - citedTrackedSum;

  function cumulative(yearsArr, byYear) {
    var run = 0, out = [];
    yearsArr.forEach(function(y) { run += byYear[y]; out.push({year: y, value: run}); });
    return out;
  }
  var cumCitations = cumulative(citYears, citByYear);
  var cumPubs = cumulative(pubYears, pubByYear);

  /* ---------- SVG chart helpers ---------- */
  var NS = "http://www.w3.org/2000/svg";
  function svgEl(tag, attrs) {
    var el = document.createElementNS(NS, tag);
    for (var k in attrs) el.setAttribute(k, attrs[k]);
    return el;
  }
  function makeSvg(vbW, vbH) {
    return svgEl("svg", {viewBox: "0 0 " + vbW + " " + vbH, preserveAspectRatio: "xMidYMid meet"});
  }

  // Area/line chart: single series
  function areaChart(container, points, opts) {
    opts = opts || {};
    var W = 760, H = 300, padL = 55, padR = 20, padT = 16, padB = 34;
    var svg = makeSvg(W, H);
    var maxV = Math.max.apply(null, points.map(function(p){return p.value;})) || 1;
    var n = points.length;
    var xw = (W - padL - padR) / Math.max(n - 1, 1);
    function X(i) { return padL + i * xw; }
    function Y(v) { return H - padB - (v / maxV) * (H - padT - padB); }

    // gridlines + y labels
    for (var g = 0; g <= 4; g++) {
      var gv = (maxV / 4) * g;
      var gy = Y(gv);
      svg.appendChild(svgEl("line", {x1: padL, x2: W - padR, y1: gy, y2: gy, stroke: "var(--border)", "stroke-width": 1}));
      var lbl = svgEl("text", {x: padL - 8, y: gy + 4, "text-anchor": "end", "font-size": 11, fill: "var(--muted)"});
      lbl.textContent = Math.round(gv).toLocaleString();
      svg.appendChild(lbl);
    }
    // x labels (sparse)
    points.forEach(function(p, i) {
      if (n <= 10 || i % Math.ceil(n / 10) === 0 || i === n - 1) {
        var t = svgEl("text", {x: X(i), y: H - padB + 18, "text-anchor": "middle", "font-size": 11, fill: "var(--muted)"});
        t.textContent = p.year;
        svg.appendChild(t);
      }
    });

    var areaPts = points.map(function(p,i){ return X(i) + "," + Y(p.value); }).join(" ");
    var areaPath = "M " + X(0) + "," + Y(0) + " L " + areaPts + " L " + X(n-1) + "," + Y(0) + " Z";
    svg.appendChild(svgEl("path", {d: areaPath, fill: opts.color || PALETTE[0], "fill-opacity": 0.15, stroke: "none"}));

    var linePts = "M " + areaPts.replace(/ /g, " L ").replace("M L", "M");
    svg.appendChild(svgEl("path", {d: "M " + areaPts.split(" ").join(" L "), fill: "none", stroke: opts.color || PALETTE[0], "stroke-width": 2.5}));

    points.forEach(function(p, i) {
      var c = svgEl("circle", {cx: X(i), cy: Y(p.value), r: 3, fill: opts.color || PALETTE[0]});
      var title = svgEl("title", {}); title.textContent = p.year + ": " + p.value.toLocaleString();
      c.appendChild(title);
      svg.appendChild(c);
    });
    container.appendChild(svg);
  }

  // Dual-axis: bars (left axis) + cumulative line (right axis)
  function dualChart(container, byYearObj, yearsArr, cumSeries, opts) {
    opts = opts || {};
    var W = 760, H = 300, padL = 50, padR = 50, padT = 16, padB = 34;
    var svg = makeSvg(W, H);
    var n = yearsArr.length;
    var barVals = yearsArr.map(function(y){ return byYearObj[y]; });
    var maxBar = Math.max.apply(null, barVals) || 1;
    var maxCum = Math.max.apply(null, cumSeries.map(function(p){return p.value;})) || 1;
    var xw = (W - padL - padR) / n;
    function X(i) { return padL + i * xw + xw/2; }
    function YBar(v) { return H - padB - (v / maxBar) * (H - padT - padB); }
    function YCum(v) { return H - padB - (v / maxCum) * (H - padT - padB); }

    for (var g = 0; g <= 4; g++) {
      var gy = H - padB - (g/4) * (H - padT - padB);
      svg.appendChild(svgEl("line", {x1: padL, x2: W - padR, y1: gy, y2: gy, stroke: "var(--border)", "stroke-width": 1}));
    }
    // left axis labels (bar scale)
    for (g = 0; g <= 4; g++) {
      var gv = (maxBar/4)*g;
      var t = svgEl("text", {x: padL - 8, y: H - padB - (g/4)*(H-padT-padB) + 4, "text-anchor": "end", "font-size": 10, fill: opts.barColor});
      t.textContent = Math.round(gv);
      svg.appendChild(t);
    }
    // right axis labels (cumulative scale)
    for (g = 0; g <= 4; g++) {
      var gv2 = (maxCum/4)*g;
      var t2 = svgEl("text", {x: W - padR + 8, y: H - padB - (g/4)*(H-padT-padB) + 4, "text-anchor": "start", "font-size": 10, fill: opts.lineColor});
      t2.textContent = Math.round(gv2).toLocaleString();
      svg.appendChild(t2);
    }

    yearsArr.forEach(function(y, i) {
      var v = byYearObj[y];
      var bw = xw * 0.55;
      var bx = X(i) - bw/2;
      var by = YBar(v);
      var rect = svgEl("rect", {x: bx, y: by, width: bw, height: (H - padB) - by, fill: opts.barColor, rx: 2});
      var title = svgEl("title", {}); title.textContent = y + ": " + v + " that year";
      rect.appendChild(title);
      svg.appendChild(rect);
      if (n <= 10 || i % Math.ceil(n/10) === 0 || i === n-1) {
        var lbl = svgEl("text", {x: X(i), y: H - padB + 18, "text-anchor": "middle", "font-size": 11, fill: "var(--muted)"});
        lbl.textContent = y;
        svg.appendChild(lbl);
      }
    });

    var linePts = cumSeries.map(function(p,i){ return X(i) + "," + YCum(p.value); }).join(" L ");
    svg.appendChild(svgEl("path", {d: "M " + linePts, fill: "none", stroke: opts.lineColor, "stroke-width": 2.5}));
    cumSeries.forEach(function(p,i) {
      var c = svgEl("circle", {cx: X(i), cy: YCum(p.value), r: 3, fill: opts.lineColor});
      var title = svgEl("title", {}); title.textContent = p.year + ": " + p.value.toLocaleString() + " cumulative";
      c.appendChild(title);
      svg.appendChild(c);
    });

    container.appendChild(svg);
  }

  // Horizontal bar chart
  function hBarChart(container, items, opts) {
    opts = opts || {};
    var W = 760, rowH = 30, padL = 260, padR = 60, padT = 10, padB = 10;
    var H = padT + padB + items.length * rowH;
    var svg = makeSvg(W, H);
    var maxV = Math.max.apply(null, items.map(function(d){return d.value;})) || 1;
    items.forEach(function(d, i) {
      var y = padT + i * rowH;
      var bw = (d.value / maxV) * (W - padL - padR);
      var label = svgEl("text", {x: padL - 8, y: y + rowH/2 + 4, "text-anchor": "end", "font-size": 11, fill: "var(--text)"});
      label.textContent = d.label;
      svg.appendChild(label);
      var rect = svgEl("rect", {x: padL, y: y + 5, width: Math.max(bw,2), height: rowH - 10, fill: PALETTE[i % PALETTE.length], rx: 3});
      var title = svgEl("title", {}); title.textContent = d.fullLabel + " — " + d.value.toLocaleString() + " citations";
      rect.appendChild(title);
      svg.appendChild(rect);
      var val = svgEl("text", {x: padL + bw + 6, y: y + rowH/2 + 4, "font-size": 11, fill: "var(--muted)", "font-weight": "700"});
      val.textContent = d.value.toLocaleString();
      svg.appendChild(val);
    });
    container.appendChild(svg);
  }

  function chartCard(title, note) {
    var card = document.createElement("div");
    card.className = "chart-card";
    var h = document.createElement("h3"); h.textContent = title;
    card.appendChild(h);
    if (note) {
      var n = document.createElement("div"); n.className = "chart-note"; n.textContent = note;
      card.appendChild(n);
    }
    document.getElementById("charts").appendChild(card);
    return card;
  }

  var chartsEl = document.getElementById("charts");

  var c1 = chartCard("Cumulative citations over time",
    untrackedNote > 0 ? ("+" + untrackedNote + " earlier citations to pre-2012 papers aren't broken out by year by the data source and are excluded from this curve.") : "");
  areaChart(c1, cumCitations, {color: PALETTE[0]});

  var c2 = chartCard("Citations received per year", "Bars = citations received that year (left axis). Line = cumulative total (right axis).");
  dualChart(c2, citByYear, citYears, cumCitations, {barColor: PALETTE[1], lineColor: PALETTE[0]});
  var leg2 = document.createElement("div"); leg2.className = "legend";
  leg2.innerHTML = '<span><span class="swatch" style="background:'+PALETTE[1]+'"></span>Citations that year</span><span><span class="swatch" style="background:'+PALETTE[0]+'"></span>Cumulative</span>';
  c2.appendChild(leg2);

  var c3 = chartCard("Publications per year", "Bars = papers published that year (left axis). Line = cumulative paper count (right axis).");
  dualChart(c3, pubByYear, pubYears, cumPubs, {barColor: PALETTE[2], lineColor: PALETTE[4]});
  var leg3 = document.createElement("div"); leg3.className = "legend";
  leg3.innerHTML = '<span><span class="swatch" style="background:'+PALETTE[2]+'"></span>Papers that year</span><span><span class="swatch" style="background:'+PALETTE[4]+'"></span>Cumulative</span>';
  c3.appendChild(leg3);

  var top = PUBS.slice().sort(function(a,b){ return b.cited_by_count - a.cited_by_count; }).slice(0, 10);
  var c4 = chartCard("Top-cited papers", "");
  hBarChart(c4, top.map(function(p) {
    var lbl = p.title.length > 42 ? p.title.slice(0,40) + "…" : p.title;
    return {label: p.year + " · " + lbl, fullLabel: p.title, value: p.cited_by_count};
  }));

  /* ---------- publications table ---------- */
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function(c) {
      return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];
    });
  }

  function formatAuthors(authors) {
    var esc = authors.map(function(a) {
      var h = escapeHtml(a);
      return a === YOU ? '<span class="you">' + h + '</span>' : h;
    });
    if (authors.length <= 6) {
      return esc.join(", ");
    }
    var first = esc[0];
    var last = esc[esc.length - 1];
    var middle = esc.slice(1, -1);
    var visibleMiddle = middle.slice(0, 4);
    var hiddenMiddle = middle.slice(4);
    var uid = "a" + Math.random().toString(36).slice(2, 9);
    var collapsed = [first].concat(visibleMiddle).join(", ") +
      (hiddenMiddle.length ? ', <span class="more-toggle" data-target="' + uid + '">+' + hiddenMiddle.length + ' more</span>, ' : ", ") +
      last;
    var full = esc.join(", ");
    return '<span class="authors-collapsed">' + collapsed + '</span>' +
      '<span class="authors-full" id="' + uid + '" style="display:none">' + full + ' <span class="more-toggle" data-collapse="' + uid + '">show less</span></span>';
  }

  var types = Array.from(new Set(PUBS.map(function(p){ return p.type; }))).sort();
  var typeSelect = document.getElementById("typeFilter");
  types.forEach(function(t) {
    var o = document.createElement("option"); o.value = t; o.textContent = t;
    typeSelect.appendChild(o);
  });

  var sortKey = "cited_by_count", sortDir = -1;
  var searchEl = document.getElementById("search");
  var tbody = document.getElementById("pubsBody");
  var resultCount = document.getElementById("resultCount");

  function render() {
    var q = searchEl.value.trim().toLowerCase();
    var tf = typeSelect.value;
    var rows = PUBS.filter(function(p) {
      if (tf && p.type !== tf) return false;
      if (!q) return true;
      var hay = (p.title + " " + p.authors.join(" ") + " " + (p.venue||"")).toLowerCase();
      return hay.indexOf(q) !== -1;
    });
    rows.sort(function(a, b) {
      var av = a[sortKey], bv = b[sortKey];
      if (sortKey === "authors") { av = a.authors.join(", "); bv = b.authors.join(", "); }
      if (typeof av === "string") { av = av.toLowerCase(); bv = (bv||"").toLowerCase(); }
      if (av < bv) return -1 * sortDir;
      if (av > bv) return 1 * sortDir;
      return 0;
    });
    tbody.innerHTML = rows.map(function(p) {
      var doiUrl = p.doi ? ("https://doi.org/" + p.doi) : (p.landing_page_url || "");
      var titleHtml = doiUrl
        ? '<a href="' + escapeHtml(doiUrl) + '" target="_blank" rel="noopener">' + escapeHtml(p.title) + '</a>'
        : escapeHtml(p.title);
      return "<tr>" +
        '<td class="title-cell">' + titleHtml + (p.venue ? '<span class="venue">' + escapeHtml(p.venue) + '</span>' : '') + "</td>" +
        '<td class="authors">' + formatAuthors(p.authors) + "</td>" +
        '<td><span class="type-pill">' + escapeHtml(p.type) + "</span></td>" +
        "<td>" + (p.year || "") + "</td>" +
        '<td><span class="badge">' + p.cited_by_count.toLocaleString() + "</span></td>" +
        "</tr>";
    }).join("");
    resultCount.textContent = rows.length + " of " + PUBS.length + " publications";
  }

  document.querySelectorAll("table.pubs th[data-key]").forEach(function(th) {
    th.addEventListener("click", function() {
      var key = th.getAttribute("data-key");
      if (sortKey === key) { sortDir *= -1; } else { sortKey = key; sortDir = key === "cited_by_count" ? -1 : 1; }
      document.querySelectorAll("table.pubs th").forEach(function(h){ h.classList.remove("sorted-asc","sorted-desc"); });
      th.classList.add(sortDir === 1 ? "sorted-asc" : "sorted-desc");
      render();
    });
  });
  searchEl.addEventListener("input", render);
  typeSelect.addEventListener("change", render);
  tbody.addEventListener("click", function(e) {
    var t = e.target;
    if (t.classList.contains("more-toggle")) {
      if (t.dataset.target) {
        t.closest(".authors-collapsed").style.display = "none";
        document.getElementById(t.dataset.target).style.display = "inline";
      } else if (t.dataset.collapse) {
        document.getElementById(t.dataset.collapse).style.display = "none";
        document.getElementById(t.dataset.collapse).previousElementSibling.style.display = "inline";
      }
    }
  });

  render();
})();
</script>
</body>
</html>
"""


def build_links_html(links):
    parts = []
    for label, url in links:
        parts.append(f'<a href="{url}" target="_blank" rel="noopener">{label}</a>')
    return "\n    ".join(parts)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in", dest="inp", default="data/publications_filtered.json")
    ap.add_argument("--out", default="site/index.html")
    ap.add_argument("--name", default="Vagisha Sharma")
    ap.add_argument("--subtitle", default="University of Washington")
    ap.add_argument("--orcid", default="https://orcid.org/0000-0003-1922-439X")
    args = ap.parse_args()

    pubs = json.load(open(args.inp, encoding="utf-8"))

    # Trim to only the fields the page needs (keeps the embedded JSON small).
    slim = []
    for p in pubs:
        slim.append({
            "title": p["title"],
            "authors": p["authors"],
            "venue": p.get("venue"),
            "type": p.get("type"),
            "year": p.get("year"),
            "cited_by_count": p.get("cited_by_count", 0),
            "doi": p.get("doi"),
            "landing_page_url": p.get("landing_page_url"),
            "counts_by_year": p.get("counts_by_year", {}),
        })

    links = [("ORCID", args.orcid)]
    today = datetime.date.today().isoformat()
    footer_html = (
        f"Data from <a href=\"https://openalex.org\" target=\"_blank\" rel=\"noopener\">OpenAlex</a>, "
        f"keyed by ORCID <a href=\"{args.orcid}\" target=\"_blank\" rel=\"noopener\">{args.orcid.rsplit('/',1)[-1]}</a>. "
        f"Curated by hand — see this project's repository for the full pipeline and curation log. "
        f"Citation counts are as tracked by OpenAlex and may lag or differ slightly from Google Scholar. "
        f"Last updated {today}."
    )

    html = (HTML_TEMPLATE
            .replace("__PAGE_TITLE__", args.name)
            .replace("__PAGE_NAME__", args.name)
            .replace("__PAGE_SUBTITLE__", args.subtitle)
            .replace("__LINKS_HTML__", build_links_html(links))
            .replace("__FOOTER_HTML__", footer_html)
            .replace("__DATA_JSON__", json.dumps(slim, ensure_ascii=False))
            .replace("__YOU_JSON__", json.dumps(args.name)))

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(args.out) / 1024
    print(f"Wrote {args.out} ({size_kb:.1f} KB, {len(pubs)} publications).")


if __name__ == "__main__":
    main()

// Nomystria — diagram i symulator ścieżek przepisów (sciezki.html?id=x002-001). Bez zależności.
(function () {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const WYNIK = { ok: "ścieżka istnieje", luka: "luka: brak ścieżki", statut: "rozstrzyga statut" };
  const NW = 214, PAD = 8, LH = 15.5, GAPX = 64, GAPY = 52;

  const id = new URLSearchParams(location.search).get("id") || location.hash.slice(1) || "x002-001";
  let D, W, parent = {}, kids = {}, pos = {}, trasa = [], wybory = [], sciezki = [];

  // ---- struktura ----
  const dzieci = (w) => (w.odpowiedzi ? w.odpowiedzi.map((o) => [o.do, o.etykieta]) : w.dalej ? [[w.dalej, "dalej"]] : []);
  function wrap(t, max) {
    const out = [];
    let line = "";
    for (const word of String(t).split(/\s+/)) {
      if ((line + " " + word).trim().length > max) { if (line) out.push(line); line = word; } else line = (line + " " + word).trim();
    }
    if (line) out.push(line);
    return out;
  }
  const krotki = (w) => (w.typ === "wynik" ? w.tekst.split(/(?<=[.:;])\s/)[0] : w.tekst);

  function layout() {
    // „Drabina decyzji”: przy pytaniu z dwiema odpowiedziami, z których jedna kończy ścieżkę, wynik stoi obok
    // pytania (ten sam wiersz), a dalsza część schodzi w dół. W pozostałych przypadkach dzieci układamy pod rodzicem.
    const lines = {}, row = {}, col = {};
    for (const [k, w] of Object.entries(W)) {
      let l = wrap(krotki(w), 31);
      if (l.length > 5) { l = l.slice(0, 5); l[4] += " …"; }
      lines[k] = l;
    }
    const isLeaf = (k) => !kids[k].length;
    const place = (k, c, r) => {  // zwraca szerokość poddrzewa w kolumnach
      row[k] = r;
      const ch = kids[k].map(([x]) => x);
      if (!ch.length) { col[k] = c; return 1; }
      if (ch.length === 2 && ch.filter(isLeaf).length === 1) {
        const leaf = ch.find(isLeaf), dalej = ch.find((x) => !isLeaf(x));
        col[k] = c; col[leaf] = c + 1; row[leaf] = r;
        return Math.max(2, place(dalej, c, r + 1));
      }
      let cc = c;
      for (const x of ch) cc += place(x, cc, r + 1);
      col[k] = c;  // wyrównanie do lewej: oś drabiny zostaje prosta, rozgałęzienie idzie w prawo
      return cc - c;
    };
    const span = place(D.start, 0, 0);
    const maxR = Math.max(...Object.values(row));
    const hOf = (k) => lines[k].length * LH + 2 * PAD + 18;
    const rowH = [];
    for (let r = 0; r <= maxR; r++) rowH[r] = Math.max(...Object.keys(row).filter((k) => row[k] === r).map(hOf));
    let y = 10;
    const rowY = rowH.map((h) => { const v = y; y += h + GAPY; return v; });
    for (const k of Object.keys(W)) {
      pos[k] = { x: 10 + col[k] * (NW + GAPX), y: rowY[row[k]], h: hOf(k), lines: lines[k] };
    }
    return { width: span * (NW + GAPX) + 10, height: y - GAPY + 10 };
  }

  function drawSvg() {
    const { width, height } = layout();
    const svg = $("svg");
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.setAttribute("width", width);
    svg.setAttribute("height", height);
    let e = "", n = "", lab = "";
    for (const [k, ch] of Object.entries(kids)) {
      const a = pos[k];
      ch.forEach(([c, label]) => {
        const b = pos[c];
        let x1, y1, x2, y2, d, lx, ly;
        if (Math.abs(a.y - b.y) < 1) {  // obok: krawędź pozioma od prawej krawędzi pytania
          x1 = a.x + NW; y1 = a.y + Math.min(a.h, b.h) / 2; x2 = b.x; y2 = y1;
          d = `M${x1},${y1} L${x2},${y2}`; lx = (x1 + x2) / 2; ly = y1 - 6;
        } else {
          x1 = a.x + NW / 2; y1 = a.y + a.h; x2 = b.x + NW / 2; y2 = b.y;
          const my = (y1 + y2) / 2;
          d = `M${x1},${y1} C${x1},${my} ${x2},${my} ${x2},${y2}`;
          // etykieta tuż nad węzłem docelowym — przy wachlarzu odpowiedzi się nie nakładają
          lx = x2; ly = Math.abs(x1 - x2) < 1 ? my + 4 : y2 - 12;
        }
        e += `<path class="edge" data-e="${k}>${c}" d="${d}" marker-end="url(#arr)"/>`;
        if (label !== "dalej") {
          const txt = label.length > 30 ? label.slice(0, 29) + "…" : label;
          lab += `<g><rect class="elab-bg" x="${lx - txt.length * 3.1 - 4}" y="${ly - 11}" width="${txt.length * 6.2 + 8}" height="15" rx="3"/>` +
                 `<text class="elab" data-e="${k}>${c}" x="${lx}" y="${ly}" text-anchor="middle">${esc(txt)}</text></g>`;
        }
      });
    }
    for (const [k, p] of Object.entries(pos)) {
      const w = W[k];
      const cls = `node t-${w.typ}${w.wynik ? " w-" + w.wynik : ""}`;
      const tl = p.lines.map((l, i) => `<tspan x="${p.x + PAD}" dy="${i ? LH : 0}">${esc(l)}</tspan>`).join("");
      n += `<g class="${cls}" data-n="${k}" tabindex="0"><title>${esc(w.tekst)}</title>` +
           `<rect x="${p.x}" y="${p.y}" width="${NW}" height="${p.h}" rx="8"/>` +
           `<text x="${p.x + PAD}" y="${p.y + PAD + 11}">${tl}</text>` +
           `<text class="prz" x="${p.x + PAD}" y="${p.y + p.h - PAD}">${esc((w.przepisy || []).join(", "))}</text></g>`;
    }
    const defs = `<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--edge)"/></marker></defs>`;
    svg.innerHTML = `${defs}<g>${e}</g><g>${lab}</g><g>${n}</g>`;
  }

  // ---- symulator ----
  function pathTo(k) {
    const out = [];
    while (k) { out.unshift(k); k = parent[k]?.[0]; }
    return out;
  }
  function setTrasa(p) {
    trasa = p;
    wybory = p.slice(1).map((k) => parent[k][1]);
    renderSim();
  }
  function renderSim() {
    const cur = trasa[trasa.length - 1];
    const w = W[cur];
    document.querySelectorAll("#svg .node").forEach((g) => {
      g.classList.toggle("on", trasa.includes(g.dataset.n));
      g.classList.toggle("cur", g.dataset.n === cur && w.typ !== "wynik");
    });
    const onE = new Set(trasa.slice(1).map((k, i) => `${trasa[i]}>${k}`));
    document.querySelectorAll("#svg [data-e]").forEach((x) => x.classList.toggle("on", onE.has(x.dataset.e)));
    $("trasa").innerHTML = trasa.slice(0, -1).map((k, i) =>
      `<li>${esc(W[k].tekst.length > 70 ? W[k].tekst.slice(0, 68) + "…" : W[k].tekst)} → <b>${esc(wybory[i])}</b></li>`).join("");
    const cyt = (w.cytaty || []).map((c) => `<blockquote>„${esc(c)}”</blockquote>`).join("");
    let html = `<p class="prz">${esc((w.przepisy || []).join(", "))}</p>`;
    if (w.typ === "wynik") {
      html = `<div class="wynik w-${w.wynik}"><strong>${esc(WYNIK[w.wynik] || w.wynik)}</strong><p>${esc(w.tekst)}</p></div>` + html + cyt;
    } else {
      html = `<p class="q">${esc(w.tekst)}</p>` + html + cyt + `<div class="sc-odp">${
        kids[cur].map(([c, l]) => `<button type="button" data-go="${c}">${l === "dalej" ? "Dalej →" : esc(l)}</button>`).join("")}</div>`;
    }
    $("krok").innerHTML = html;
    const path = trasa.join(">");
    document.querySelectorAll("#lista tr").forEach((tr) => tr.classList.toggle("on", tr.dataset.p === path));
  }

  function wszystkie() {
    const out = [];
    const dfs = (k, acc) => {
      if (!kids[k].length) { out.push(acc.concat(k)); return; }
      kids[k].forEach(([c]) => dfs(c, acc.concat(k)));
    };
    dfs(D.start, []);
    sciezki = out;
    const cnt = { ok: 0, luka: 0, statut: 0 };
    $("lista").innerHTML = out.map((p, i) => {
      const end = W[p[p.length - 1]];
      cnt[end.wynik] = (cnt[end.wynik] || 0) + 1;
      const odp = p.slice(1).map((k) => parent[k][1]).filter((l) => l !== "dalej");
      const prz = [...new Set(p.flatMap((k) => W[k].przepisy || []))];
      return `<tr data-p="${p.join(">")}"><td class="num">${i + 1}</td><td>${esc(odp.join(" → "))}</td>` +
             `<td><span class="pill w-${end.wynik}">${esc(WYNIK[end.wynik])}</span></td><td>${esc(prz.join(", "))}</td></tr>`;
    }).join("");
    $("podsum").textContent = `(${out.length}: ${cnt.ok} istnieje, ${cnt.luka} luk, ${cnt.statut} statut)`;
  }

  // ---- zdarzenia ----
  $("krok").addEventListener("click", (e) => {
    const b = e.target.closest("button[data-go]");
    if (b) setTrasa(trasa.concat(b.dataset.go));
  });
  $("cofnij").addEventListener("click", () => { if (trasa.length > 1) setTrasa(trasa.slice(0, -1)); });
  $("restart").addEventListener("click", () => setTrasa([D.start]));
  $("svg").addEventListener("click", (e) => { const g = e.target.closest("[data-n]"); if (g) setTrasa(pathTo(g.dataset.n)); });
  $("svg").addEventListener("keydown", (e) => { if (e.key === "Enter") { const g = e.target.closest("[data-n]"); if (g) setTrasa(pathTo(g.dataset.n)); } });
  $("lista").addEventListener("click", (e) => { const tr = e.target.closest("tr[data-p]"); if (tr) setTrasa(tr.dataset.p.split(">")); });

  const WERSJA = document.querySelector('meta[name="wersja"]')?.content || "";
  fetch(`sciezki/${encodeURIComponent(id)}.json?v=${encodeURIComponent(WERSJA)}`)
    .then((r) => { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
    .then((d) => {
      D = d; W = d.wezly;
      for (const [k, w] of Object.entries(W)) {
        kids[k] = dzieci(w);
        kids[k].forEach(([c, l]) => (parent[c] = [k, l]));
      }
      document.title = `Nomystria — ścieżki ${d.id}`;
      $("tytul").textContent = `${d.id}: ${d.tytul}`;
      $("opis").textContent = d.opis;
      $("zrodlo").href = `https://github.com/michalasobczak/nomystria/blob/main/kontrole/${d.id.split("-")[0]}/sciezki/${d.id}.json`;
      $("powrot").href = "./#tylkoZnal=1";
      drawSvg();
      wszystkie();
      setTrasa([d.start]);
    })
    .catch((e) => { $("tytul").textContent = `Nie udało się wczytać diagramu ${id} (${e.message}).`; });
})();

// Nomystria — przeglądarka ustaw (S007). Bez zależności; dane z dane.json (skrypty/strona.py).
(function () {
  "use strict";

  const SYMBOL = { U: "●", J: "◆", P: "○", PZ: "◐" };
  const BR_OPIS = { U: "ujednolicone", J: "jednolite (tekst jednolity z Dz. U.)", P: "pierwotne", PZ: "pierwotne (zmieniana)" };
  const BR_ALL = "U,J,P,PZ";
  const KONTROLA_OPIS = { zgodny: "potwierdzone", rozbiezny: "rozbieżność", niezweryfikowany: "nie dało się potwierdzić", brak: "nie sprawdzano" };
  const KATEGORIA_OPIS = {
    sprzecznosc: "sprzeczność", niespojnosc: "niespójność", luka: "luka", wada: "wada legislacyjna",
    brak_sciezki_alternatywnej: "brak ścieżki alternatywnej", zaniechanie: "zaniechanie",
  };
  const DOMYSLNE_SORT = { k: "data", dir: -1 };
  const ADV = ["rokOd", "rokDo", "zmOd", "zmDo", "tj", "poTj", "kontrola"];

  const $ = (id) => document.getElementById(id);
  const el = {
    q: $("q"), tylkoZnal: $("tylkoZnal"), od1989: $("od1989"), rokOd: $("rokOd"), rokDo: $("rokDo"), zmOd: $("zmOd"), zmDo: $("zmDo"),
    tj: $("tj"), poTj: $("poTj"), kontrola: $("kontrola"),
    br: Array.from(document.querySelectorAll('input[name="br"]')),
    adv: $("zaawansowane"), advActive: $("advActive"),
    rows: $("wiersze"), summary: $("summary"), dialog: $("szczegoly"), dlg: $("szTresc"),
  };

  let DATA = [];
  let sort = { ...DOMYSLNE_SORT };

  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const norm = (s) => String(s ?? "").toLocaleLowerCase("pl").normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/ł/g, "l");
  const num = (v) => (v === "" || v === null || v === undefined || isNaN(+v) ? null : +v);
  const sortStr = (s) => s.k + (s.dir < 0 ? ":desc" : "");

  // ---- stan filtrów <-> adres URL (#q=...&br=U,P) ----
  function readState() {
    const st = { q: el.q.value.trim(), tylkoZnal: el.tylkoZnal.checked ? "1" : "", od1989: el.od1989.checked ? "1" : "", br: el.br.filter((c) => c.checked).map((c) => c.value).join(",") };
    for (const k of ADV) st[k] = el[k].value;
    return st;
  }
  function writeHash(st) {
    const p = new URLSearchParams();
    for (const [k, v] of Object.entries(st)) {
      if (k === "br" && v === BR_ALL) continue;
      if (v) p.set(k, v);
    }
    if (sortStr(sort) !== sortStr(DOMYSLNE_SORT)) p.set("sort", sortStr(sort));
    const h = p.toString();
    history.replaceState(null, "", h ? "#" + h : location.pathname + location.search);
  }
  function applyHash() {
    const p = new URLSearchParams(location.hash.slice(1));
    el.q.value = p.get("q") || "";
    el.tylkoZnal.checked = p.get("tylkoZnal") === "1";
    el.od1989.checked = p.get("od1989") === "1";
    for (const k of ADV) el[k].value = p.get(k) || "";
    const br = (p.get("br") || BR_ALL).split(",");
    el.br.forEach((c) => (c.checked = br.includes(c.value)));
    const s = (p.get("sort") || sortStr(DOMYSLNE_SORT)).split(":");
    sort = { k: s[0], dir: s[1] === "desc" ? -1 : 1 };
    // Zaawansowane rozwinięte, jeśli adres zawiera filtry zaawansowane.
    if (ADV.some((k) => p.get(k)) || p.get("br")) el.adv.open = true;
  }

  // ---- filtrowanie ----
  // Każdy filtr osobno, żeby liczyć opcje przy pozostałych filtrach (fasety).
  const FILTRY = {
    q: (u, st) => { const w = norm(st.q).split(/\s+/).filter(Boolean); return !w.length || w.every((x) => u._hay.includes(x)); },
    tylkoZnal: (u, st) => !st.tylkoZnal || u.znaleziska.length > 0,
    // uchwalona w 1989 r. lub później albo zmieniona ustawą ogłoszoną w 1989 r. lub później
    od1989: (u, st) => !st.od1989 || (u.rok ?? 0) >= 1989 || (u.rokZm ?? 0) >= 1989,
    br: (u, st) => (st.br ? st.br.split(",") : []).includes(u.br),
    rok: (u, st) => { const o = num(st.rokOd), d = num(st.rokDo); return (o === null || (u.rok ?? -1) >= o) && (d === null || (u.rok ?? 1e9) <= d); },
    zmian: (u, st) => { const o = num(st.zmOd), d = num(st.zmDo); return (o === null || (u.zmian ?? 0) >= o) && (d === null || (u.zmian ?? 0) <= d); },
    tj: (u, st) => !st.tj || (st.tj === "jest" ? !!u.tj : !u.tj),
    poTj: (u, st) => !st.poTj || (st.poTj === "1" ? u.poTj > 0 : !!u.tj && u.poTj === 0),
    kontrola: (u, st) => !st.kontrola || u.kontrola === st.kontrola,
  };
  const matchesExcept = (u, st, skip) => Object.entries(FILTRY).every(([k, f]) => k === skip || f(u, st));

  function updateCounts(st) {
    // Liczba ustaw po podmianie jednego filtra na daną opcję; pozostałe filtry bez zmian.
    const count = (_filtr, patch) => { const s = { ...st, ...patch }; let n = 0; for (const u of DATA) if (matchesExcept(u, s, null)) n++; return n; };
    const set = (key, n) => document.querySelectorAll(`[data-cnt="${key}"]`).forEach((e) => (e.textContent = `(${n})`));
    set("tylkoZnal", count("tylkoZnal", { tylkoZnal: "1" }));
    set("od1989", count("od1989", { od1989: "1" }));
    for (const b of BR_ALL.split(",")) set("br:" + b, count("br", { br: b }));
    const opts = { tj: "tj", poTj: "poTj", kontrola: "kontrola" };
    for (const [id, f] of Object.entries(opts)) {
      for (const o of el[id].options) {
        if (!o.dataset.label) o.dataset.label = o.textContent;
        o.textContent = o.value ? `${o.dataset.label} (${count(f, { [id]: o.value })})` : o.dataset.label;
      }
    }
    const n = ADV.filter((k) => st[k]).length + (st.br !== BR_ALL ? 1 : 0);
    el.advActive.textContent = n ? `· aktywne: ${n}` : "";
  }

  function cmp(a, b) {
    const k = sort.k;
    const x = a[k], y = b[k];
    const ex = x === null || x === undefined || x === "", ey = y === null || y === undefined || y === "";
    if (ex || ey) return ex === ey ? 0 : ex ? 1 : -1; // puste zawsze na końcu
    if (typeof x === "number" && typeof y === "number") return sort.dir * (x - y) || b.data.localeCompare(a.data);
    return sort.dir * String(x).localeCompare(String(y), "pl") || b.poz - a.poz;
  }

  function badge(k) {
    return `<span class="badge k-${esc(k)}">${esc(KONTROLA_OPIS[k] || k)}</span>`;
  }

  function render() {
    const st = readState();
    writeHash(st);
    const list = DATA.filter((u) => matchesExcept(u, st, null)).sort(cmp);
    updateCounts(st);
    el.summary.textContent = `Wyników: ${list.length} z ${DATA.length} ustaw.`;
    document.querySelectorAll("th[data-k]").forEach((th) => {
      th.setAttribute("aria-sort", th.dataset.k === sort.k ? (sort.dir > 0 ? "ascending" : "descending") : "none");
    });
    const html = list.map((u) => `
      <tr data-eli="${esc(u.eli)}" tabindex="0">
        <td>${esc(u.tytul)}<span class="eli">${esc(u.eli)} · ${esc(u.adres)}</span></td>
        <td class="nowrap">${esc(u.data)}</td>
        <td class="c" title="${esc(BR_OPIS[u.br] || u.br)}">${SYMBOL[u.br] || esc(u.br)}</td>
        <td class="num">${u.zmian ?? ""}</td>
        <td class="nowrap">${u.tj ? `${esc(u.tj)}<span class="eli">${esc(u.tjData)}</span>` : "—"}</td>
        <td class="num">${u.tj ? u.poTj ?? "" : "—"}</td>
        <td class="nowrap">${esc(u.tu) || "—"}</td>
        <td>${badge(u.kontrola)}</td>
        <td class="num">${u.znaleziska.length
          ? `<button type="button" class="znal-btn" data-znal="${esc(u.eli)}" aria-expanded="${rozwiniete.has(u.eli)}" title="Pokaż znaleziska">${u.znaleziska.length} ${rozwiniete.has(u.eli) ? "▴" : "▾"}</button>`
          : ""}</td>
      </tr>${rozwiniete.has(u.eli) ? znaleziskaRow(u) : ""}`).join("");
    el.rows.innerHTML = html || `<tr><td colspan="9" class="more">Brak ustaw spełniających filtry.</td></tr>`;
  }

  // ---- podlista znalezisk rozwijana pod wierszem ustawy ----
  const rozwiniete = new Set();
  const WAGA_OPIS = { wysoka: "wysoka", srednia: "średnia", niska: "niska" };
  function znaleziskaRow(u) {
    const items = u.znaleziska.map((z, i) => `
      <li class="zn">
        <div class="zn-head">
          <span class="zn-nr">${i + 1}.</span>
          <span class="badge zn-kat">${esc(KATEGORIA_OPIS[z.kategoria] || z.kategoria)}</span>
          <strong>${esc((z.przepisy || []).join(", "))}</strong>
          <span class="zn-meta">waga: ${esc(WAGA_OPIS[z.waga] || z.waga || "—")}
            · ${z.weryfikacja_krzyzowa ? "potwierdzone krzyżowo" : "jedno źródło"}</span>
        </div>
        <p>${esc(z.opis)}</p>
        ${(z.cytaty || []).slice(0, 2).map((c) => `<blockquote>${esc(c)}</blockquote>`).join("")}
        <details><summary>Uzasadnienie i źródła</summary>
          <p>${esc(z.uzasadnienie)}</p>
          <p class="eli">${esc(z.id)} · wykryto: ${esc((z.zrodla_wykrycia || []).join(", "))}</p>
        </details>
      </li>`).join("");
    return `<tr class="znal-row"><td colspan="9"><ul class="zn-list">${items}</ul></td></tr>`;
  }

  // ---- szczegóły ----
  function details(eli) {
    const u = DATA.find((x) => x.eli === eli);
    if (!u) return;
    const wyniki = u.wyniki.length
      ? `<table class="mini"><thead><tr><th>Kontrola</th><th>Parametr</th><th>W zbiorze</th><th>W źródle</th><th>Źródło</th><th>Wynik</th><th>Wyjaśnienie</th></tr></thead><tbody>${
          u.wyniki.map((w) => `<tr><td>${esc(w.k)}</td><td>${esc(w.parametr)}</td><td>${esc(w.wartosc_zbior)}</td><td>${esc(w.wartosc_zrodlo)}</td><td>${esc(w.zrodlo)}</td><td>${badge(w.werdykt)}</td><td>${esc(w.wyjasnienie)}</td></tr>`).join("")
        }</tbody></table>`
      : `<p>${badge("brak")} Metadanych tej ustawy nie sprawdzano jeszcze w niezależnym źródle.</p>`;
    const znal = u.znaleziska.length
      ? u.znaleziska.map((z, i) => `
          <div class="znal">
            <strong>${i + 1}. ${esc(KATEGORIA_OPIS[z.kategoria] || z.kategoria)}</strong>
            · ${esc((z.przepisy || []).join(", "))} · waga: ${esc(z.waga || "—")}
            ${z.weryfikacja_krzyzowa ? " · potwierdzone krzyżowo" : " · niepotwierdzone krzyżowo"}
            ${(z.cytaty || []).map((c) => `<blockquote>${esc(c)}</blockquote>`).join("")}
            <p>${esc(z.opis)}</p>
                ${z.uzasadnienie ? `<p><em>Uzasadnienie:</em> ${esc(z.uzasadnienie)}</p>` : ""}
            <p class="eli">${esc(z.id)} (${esc(z.k)}) · wykryto: ${esc((z.zrodla_wykrycia || []).join(", "))}</p>
          </div>`).join("")
      : "<p>Brak znalezisk.</p>";
    el.dlg.innerHTML = `
      <h2>${esc(u.tytul)}</h2>
      <div class="links">
        <a href="${esc(u.plik)}" target="_blank" rel="noopener">Tekst (Markdown) w repozytorium</a>
        <a href="${esc(u.pdf)}" target="_blank" rel="noopener">PDF źródłowy</a>
        <a href="${esc(u.isap)}" target="_blank" rel="noopener">ISAP</a>
      </div>
      <dl class="meta">
        <dt>ELI</dt><dd>${esc(u.eli)}</dd>
        <dt>Publikacja</dt><dd>${esc(u.adres)}</dd>
        <dt>Data ustawy</dt><dd>${esc(u.data) || "—"}</dd>
        <dt>Status (ISAP)</dt><dd>${esc(u.status)}</dd>
        <dt>Brzmienie</dt><dd>${SYMBOL[u.br] || ""} ${esc(BR_OPIS[u.br] || u.br)}</dd>
        <dt>Wejście w życie</dt><dd>${esc(u.wejscie) || "—"}</dd>
        <dt>Ustaw zmieniających</dt><dd>${u.zmian ?? "—"}${u.rokZm ? ` (ostatnia z ${u.rokZm} r.)` : ""}</dd>
        <dt>Ostatni tekst jednolity</dt><dd>${u.tj ? `${esc(u.tj)} z ${esc(u.tjData)}` : "—"}</dd>
        <dt>Zmian po t.j.</dt><dd>${u.tj ? u.poTj ?? "—" : "—"}</dd>
        <dt>Tekst ujednolicony z dnia</dt><dd>${esc(u.tu) || "—"}</dd>
        <dt>Opracowano na podstawie</dt><dd>${esc(u.podstawa) || "—"}</dd>
        <dt>Źródło tekstu</dt><dd>${esc(u.zrodloTekstu) || "—"}</dd>
        ${u.uwagi ? `<dt>Uwagi</dt><dd>${esc(u.uwagi)}</dd>` : ""}
      </dl>
      <h3>Weryfikacja metadanych</h3>${wyniki}
      <h3>Znaleziska</h3>${znal}`;
    el.dialog.showModal();
  }

  // ---- zdarzenia ----
  let t;
  const debounced = () => { clearTimeout(t); t = setTimeout(render, 120); };
  [el.q, el.rokOd, el.rokDo, el.zmOd, el.zmDo].forEach((i) => i.addEventListener("input", debounced));
  [el.tylkoZnal, el.od1989, el.tj, el.poTj, el.kontrola, ...el.br].forEach((i) => i.addEventListener("change", render));
  $("reset").addEventListener("click", () => { history.replaceState(null, "", location.pathname); applyHash(); render(); });
  document.querySelectorAll("th[data-k]").forEach((th) => th.addEventListener("click", () => {
    const k = th.dataset.k;
    sort = sort.k === k ? { k, dir: -sort.dir } : { k, dir: k === "tytul" ? 1 : -1 };
    render();
  }));
  el.rows.addEventListener("click", (e) => {
    const btn = e.target.closest("button[data-znal]");
    if (btn) {
      const eli = btn.dataset.znal;
      rozwiniete.has(eli) ? rozwiniete.delete(eli) : rozwiniete.add(eli);
      render();
      return;
    }
    if (e.target.closest("tr.znal-row")) return; // klik w podliście nie otwiera okna szczegółów
    const tr = e.target.closest("tr[data-eli]");
    if (tr) details(tr.dataset.eli);
  });
  el.rows.addEventListener("keydown", (e) => { if (e.key === "Enter") { const tr = e.target.closest("tr[data-eli]"); if (tr) details(tr.dataset.eli); } });
  el.dialog.addEventListener("click", (e) => { if (e.target === el.dialog) el.dialog.close(); });
  window.addEventListener("hashchange", () => { applyHash(); render(); });

  // ---- start ----
  const WERSJA = document.querySelector('meta[name="wersja"]')?.content || "";
  fetch("dane.json?v=" + encodeURIComponent(WERSJA))
    .then((r) => { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
    .then((d) => {
      DATA = d.ustawy.map((u) => ({ ...u, data: u.data || "", nZnal: u.znaleziska.length, _hay: norm(u.tytul + " " + u.eli + " " + u.adres) }));
      if (d.kontrole && d.kontrole.length) {
        $("kontrole").hidden = false;
        $("listaKontroli").innerHTML = d.kontrole.map((k) =>
          `<li><strong>${esc(k.id)}</strong> (${esc(k.spec)}) — ${esc(k.tytul)}, ${esc(k.data)}: ${k.liczba} ${k.rodzaj === "wyniki" ? "wyników" : "znalezisk"} · <a href="https://github.com/michalasobczak/nomystria/blob/main/${esc(k.plik)}">${esc(k.plik)}</a></li>`).join("");
      }
      applyHash();
      render();
    })
    .catch((e) => { el.summary.textContent = "Nie udało się wczytać danych (" + e.message + ")."; });
})();

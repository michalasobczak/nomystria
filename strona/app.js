// Nomystria — przeglądarka ustaw (S007). Bez zależności; dane z dane.json (skrypty/strona.py).
(function () {
  "use strict";

  const SYMBOL = { U: "●", P: "○", PZ: "◐" };
  const BR_OPIS = { U: "ujednolicone", P: "pierwotne", PZ: "pierwotne (zmieniana)" };
  const KONTROLA_OPIS = { zgodny: "zgodna", rozbiezny: "rozbieżna", niezweryfikowany: "niezweryfikowana", brak: "brak kontroli" };
  const KATEGORIA_OPIS = {
    sprzecznosc: "sprzeczność", niespojnosc: "niespójność", luka: "luka", wada: "wada legislacyjna",
    brak_sciezki_alternatywnej: "brak ścieżki alternatywnej", zaniechanie: "zaniechanie",
  };
  const WERDYKT_OPIS = { potwierdzone: "potwierdzone", odrzucone: "odrzucone", do_dyskusji: "do dyskusji", brak: "bez werdyktu" };

  const $ = (id) => document.getElementById(id);
  const el = {
    q: $("q"), rokOd: $("rokOd"), rokDo: $("rokDo"), zmOd: $("zmOd"), zmDo: $("zmDo"),
    tj: $("tj"), poTj: $("poTj"), kontrola: $("kontrola"), znal: $("znal"),
    br: Array.from(document.querySelectorAll('input[name="br"]')),
    rows: $("wiersze"), summary: $("summary"), dialog: $("szczegoly"), dlg: $("szTresc"),
  };

  let DATA = [];
  let sort = { k: "rok", dir: 1 };

  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const norm = (s) => String(s ?? "").toLocaleLowerCase("pl").normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/ł/g, "l");
  const num = (v) => (v === "" || v === null || v === undefined || isNaN(+v) ? null : +v);

  // ---- stan filtrów <-> adres URL (#q=...&br=U,P) ----
  function readState() {
    return {
      q: el.q.value.trim(), rokOd: el.rokOd.value, rokDo: el.rokDo.value, zmOd: el.zmOd.value, zmDo: el.zmDo.value,
      tj: el.tj.value, poTj: el.poTj.value, kontrola: el.kontrola.value, znal: el.znal.value,
      br: el.br.filter((c) => c.checked).map((c) => c.value).join(","),
      sort: sort.k + (sort.dir < 0 ? ":desc" : ""),
    };
  }
  function writeHash(st) {
    const p = new URLSearchParams();
    for (const [k, v] of Object.entries(st)) {
      if (k === "br" && v === "U,P,PZ") continue;
      if (k === "sort" && v === "rok") continue;
      if (v) p.set(k, v);
    }
    const h = p.toString();
    history.replaceState(null, "", h ? "#" + h : location.pathname + location.search);
  }
  function applyHash() {
    const p = new URLSearchParams(location.hash.slice(1));
    for (const k of ["q", "rokOd", "rokDo", "zmOd", "zmDo", "tj", "poTj", "kontrola", "znal"]) el[k].value = p.get(k) || "";
    const br = (p.get("br") || "U,P,PZ").split(",");
    el.br.forEach((c) => (c.checked = br.includes(c.value)));
    const s = (p.get("sort") || "rok").split(":");
    sort = { k: s[0], dir: s[1] === "desc" ? -1 : 1 };
  }

  // ---- filtrowanie ----
  function matches(u, st, words) {
    if (words.length) {
      const hay = u._hay;
      if (!words.every((w) => hay.includes(w))) return false;
    }
    const br = st.br ? st.br.split(",") : [];
    if (!br.includes(u.br)) return false;
    const ro = num(st.rokOd), rd = num(st.rokDo), zo = num(st.zmOd), zd = num(st.zmDo);
    if (ro !== null && (u.rok ?? -1) < ro) return false;
    if (rd !== null && (u.rok ?? 1e9) > rd) return false;
    if (zo !== null && (u.zmian ?? 0) < zo) return false;
    if (zd !== null && (u.zmian ?? 0) > zd) return false;
    if (st.tj === "jest" && !u.tj) return false;
    if (st.tj === "brak" && u.tj) return false;
    if (st.poTj === "1" && !(u.poTj > 0)) return false;
    if (st.poTj === "0" && !(u.tj && u.poTj === 0)) return false;
    if (st.kontrola && u.kontrola !== st.kontrola) return false;
    if (st.znal === "sa" && !u.znaleziska.length) return false;
    if (st.znal === "brak" && u.znaleziska.length) return false;
    if (st.znal === "potwierdzone" && !u.znaleziska.some((z) => z.werdykt_autora === "potwierdzone")) return false;
    return true;
  }

  function cmp(a, b) {
    const k = sort.k;
    let x = a[k], y = b[k];
    if (k === "tytul") return sort.dir * String(x).localeCompare(String(y), "pl");
    const ex = x === null || x === undefined || x === "", ey = y === null || y === undefined || y === "";
    if (ex || ey) return ex === ey ? a.rok - b.rok || a.poz - b.poz : ex ? 1 : -1; // puste zawsze na końcu
    if (typeof x === "number" && typeof y === "number") return sort.dir * (x - y) || a.poz - b.poz;
    return sort.dir * String(x).localeCompare(String(y), "pl");
  }

  function badge(k) {
    return `<span class="badge k-${esc(k)}">${esc(KONTROLA_OPIS[k] || k)}</span>`;
  }

  function render() {
    const st = readState();
    writeHash(st);
    const words = norm(st.q).split(/\s+/).filter(Boolean);
    const list = DATA.filter((u) => matches(u, st, words)).sort(cmp);
    el.summary.textContent = `Wyników: ${list.length} z ${DATA.length} ustaw.`;
    document.querySelectorAll("th[data-k]").forEach((th) => {
      th.setAttribute("aria-sort", th.dataset.k === sort.k ? (sort.dir > 0 ? "ascending" : "descending") : "none");
    });
    const html = list.map((u) => `
      <tr data-eli="${esc(u.eli)}" tabindex="0">
        <td>${esc(u.tytul)}<span class="eli">${esc(u.eli)} · ${esc(u.adres)}</span></td>
        <td class="num">${u.rok ?? ""}</td>
        <td class="c" title="${esc(BR_OPIS[u.br] || u.br)}">${SYMBOL[u.br] || esc(u.br)}</td>
        <td class="num">${u.zmian ?? ""}</td>
        <td class="nowrap">${u.tj ? `${esc(u.tj)}<span class="eli">${esc(u.tjData)}</span>` : "—"}</td>
        <td class="num">${u.tj ? u.poTj ?? "" : "—"}</td>
        <td class="nowrap">${esc(u.tu) || "—"}</td>
        <td>${badge(u.kontrola)}</td>
        <td class="num">${u.znaleziska.length || ""}</td>
      </tr>`).join("");
    el.rows.innerHTML = html || `<tr><td colspan="9" class="more">Brak ustaw spełniających filtry.</td></tr>`;
  }

  // ---- szczegóły ----
  function details(eli) {
    const u = DATA.find((x) => x.eli === eli);
    if (!u) return;
    const wyniki = u.wyniki.length
      ? `<table class="mini"><thead><tr><th>Kontrola</th><th>Parametr</th><th>W zbiorze</th><th>W źródle</th><th>Źródło</th><th>Werdykt</th><th>Wyjaśnienie</th></tr></thead><tbody>${
          u.wyniki.map((w) => `<tr><td>${esc(w.k)}</td><td>${esc(w.parametr)}</td><td>${esc(w.wartosc_zbior)}</td><td>${esc(w.wartosc_zrodlo)}</td><td>${esc(w.zrodlo)}</td><td>${badge(w.werdykt)}</td><td>${esc(w.wyjasnienie)}</td></tr>`).join("")
        }</tbody></table>`
      : `<p>${badge("brak")} Tej ustawy jeszcze nie kontrolowano.</p>`;
    const znal = u.znaleziska.length
      ? u.znaleziska.map((z) => `
          <div class="znal">
            <strong>${esc(KATEGORIA_OPIS[z.kategoria] || z.kategoria)}</strong>
            · ${esc((z.przepisy || []).join(", "))} · waga: ${esc(z.waga || "—")}
            · werdykt autora: <strong>${esc(WERDYKT_OPIS[z.werdykt_autora] || z.werdykt_autora)}</strong>
            ${z.weryfikacja_krzyzowa ? " · potwierdzone krzyżowo" : " · niepotwierdzone krzyżowo"}
            ${(z.cytaty || []).map((c) => `<blockquote>${esc(c)}</blockquote>`).join("")}
            <p>${esc(z.opis)}</p>
            ${z.uzasadnienie ? `<p><em>Uzasadnienie:</em> ${esc(z.uzasadnienie)}</p>` : ""}
            ${z.komentarz_autora ? `<p><em>Komentarz autora:</em> ${esc(z.komentarz_autora)}</p>` : ""}
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
        <dt>Status (ISAP)</dt><dd>${esc(u.status)}</dd>
        <dt>Brzmienie</dt><dd>${SYMBOL[u.br] || ""} ${esc(BR_OPIS[u.br] || u.br)}</dd>
        <dt>Wejście w życie</dt><dd>${esc(u.wejscie) || "—"}</dd>
        <dt>Ustaw zmieniających</dt><dd>${u.zmian ?? "—"}</dd>
        <dt>Ostatni tekst jednolity</dt><dd>${u.tj ? `${esc(u.tj)} z ${esc(u.tjData)}` : "—"}</dd>
        <dt>Zmian po t.j.</dt><dd>${u.tj ? u.poTj ?? "—" : "—"}</dd>
        <dt>Tekst ujednolicony z dnia</dt><dd>${esc(u.tu) || "—"}</dd>
        <dt>Opracowano na podstawie</dt><dd>${esc(u.podstawa) || "—"}</dd>
      </dl>
      <h3>Kontrola parametrów</h3>${wyniki}
      <h3>Znaleziska</h3>${znal}`;
    el.dialog.showModal();
  }

  // ---- zdarzenia ----
  let t;
  const debounced = () => { clearTimeout(t); t = setTimeout(render, 120); };
  [el.q, el.rokOd, el.rokDo, el.zmOd, el.zmDo].forEach((i) => i.addEventListener("input", debounced));
  [el.tj, el.poTj, el.kontrola, el.znal, ...el.br].forEach((i) => i.addEventListener("change", render));
  $("reset").addEventListener("click", () => { history.replaceState(null, "", location.pathname); applyHash(); render(); });
  document.querySelectorAll("th[data-k]").forEach((th) => th.addEventListener("click", () => {
    sort = sort.k === th.dataset.k ? { k: sort.k, dir: -sort.dir } : { k: th.dataset.k, dir: th.dataset.k === "tytul" || th.dataset.k === "rok" ? 1 : -1 };
    render();
  }));
  el.rows.addEventListener("click", (e) => { const tr = e.target.closest("tr[data-eli]"); if (tr) details(tr.dataset.eli); });
  el.rows.addEventListener("keydown", (e) => { if (e.key === "Enter") { const tr = e.target.closest("tr[data-eli]"); if (tr) details(tr.dataset.eli); } });
  el.dialog.addEventListener("click", (e) => { if (e.target === el.dialog) el.dialog.close(); });
  window.addEventListener("hashchange", () => { applyHash(); render(); });

  // ---- start ----
  fetch("dane.json")
    .then((r) => { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
    .then((d) => {
      DATA = d.ustawy.map((u) => ({ ...u, nZnal: u.znaleziska.length, _hay: norm(u.tytul + " " + u.eli + " " + u.adres) }));
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

#!/usr/bin/env python3
"""Pobiera Konstytucję RP i obowiązujące ustawy w brzmieniu ujednoliconym
(teksty ujednolicone Kancelarii Sejmu z ISAP, API ELI) i zapisuje je jako Markdown.

Użycie:
    python skrypty/pobierz.py                 # pełna synchronizacja
    python skrypty/pobierz.py --limit 20      # próbka
    python skrypty/pobierz.py --only DU/1997/553

PDF-y trafiają do katalogu podręcznego (domyślnie .cache/pdf, poza repozytorium);
pobierane są ponownie tylko wtedy, gdy w API zmieniła się data `changeDate` aktu.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from html2md import convert_html  # noqa: E402
from pdf2md import convert  # noqa: E402
from tabela import change_info, fetch_tj_meta, update_readme  # noqa: E402

API = "https://api.sejm.gov.pl/eli"
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "dane"
KONSTYTUCJA = "DU/1997/483"
SKIP_STATUSES = {"uchylony", "uchylony wykazem", "uznany za uchylony", "wygaśnięcie aktu", "brak mocy prawnej"}
UA = "nomystria/1.0 (+https://github.com/michalasobczak/nomystria)"


def get(url: str, retries: int = 5) -> bytes:
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)
            last = e  # noqa: F841
    raise RuntimeError("unreachable")


# Akty nowelizujące i uchylające — ich treść jest już w tekście aktu zmienianego.
AMENDING_RE = re.compile(r"^(o zmianie\b|o zmianach\b|w sprawie zmiany\b|zmieniająca\b|uchylająca\b|o uchyleniu\b)")
# Wyjątki: ustawy merytoryczne, których tytuł tylko wygląda na nowelizację.
NOT_AMENDING = {"o zmianie imienia i nazwiska"}
TREATY_RE = re.compile(r"^(o ratyfikacji|o wypowiedzeniu|w sprawie (przystąpienia|zatwierdzenia|ratyfikacji))\b")
# Ustawy bez tekstu ujednoliconego bierzemy tylko z tym statusem — to akty, których nie zmieniano.
ORIGINAL_STATUSES = {"obowiązujący"}


def short_title(title: str) -> str:
    return re.sub(r"^(?:Ustawa\s+)?z\s+(?:dnia\s+)?\d{1,2}\s+\S+\s+\d{4}(?:\s*r\.)?\s*[-–]?\s*", "", title)


def is_amending(title: str) -> bool:
    """Ustawa nowelizująca („o zmianie ustawy …”) — jej treść jest już w tekście aktu zmienianego."""
    t = short_title(title).rstrip(".")
    return t not in NOT_AMENDING and bool(AMENDING_RE.match(t))


def list_acts() -> list[dict]:
    items, off = [], 0
    while True:
        u = f"{API}/acts/search?publisher=DU&type=Ustawa&inForce=1&limit=500&offset={off}"
        d = json.loads(get(u))
        items += d["items"]
        off += 500
        if off >= d["totalCount"]:
            break
    out = []
    for it in items:
        it["title"] = re.sub(r"\s+", " ", it["title"]).strip()  # API zdarza się zwrócić tytuł z \n
        if it["status"] in SKIP_STATUSES or is_amending(it["title"]):
            continue
        texts = {t["type"]: t["fileName"] for t in it.get("texts", [])}
        if "U" in texts:
            it["_text"] = ("U", texts["U"])
        elif it["status"] in ORIGINAL_STATUSES and not TREATY_RE.match(short_title(it["title"])):
            # Brak tekstu ujednoliconego: tekst pierwotny (T — skład Kancelarii Sejmu, O — Dz. U.).
            kind = "T" if "T" in texts else "O" if "O" in texts else None
            if not kind:
                continue
            it["_text"] = (kind, texts[kind])
        else:
            continue
        out.append(it)
    return out


def slugify(title: str) -> str:
    t = short_title(title)
    t = t.replace("ł", "l").replace("Ł", "L")
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t[:80].rstrip("-") or "ustawa"


def out_path(act: dict) -> Path:
    if act["ELI"] == KONSTYTUCJA:
        return DATA / "konstytucja.md"
    return DATA / "ustawy" / str(act["year"]) / f"{act['year']}-{act['pos']:04d}-{slugify(act['title'])}.md"


def pdf_url(act: dict) -> str:
    kind, name = act["_text"]
    return f"{API}/acts/{act['ELI']}/text/{kind}/{name}"


def cache_name(act: dict) -> str:
    return f"{act['ELI'].replace('/', '_')}_{act['_text'][0]}.pdf"


def brzmienie(act: dict) -> str:
    if act["_text"][0] == "U":
        return "ujednolicone"
    # Zmieniana, ale ISAP nie ma tekstu ujednoliconego — tekst pierwotny może nie być aktualny.
    return "pierwotne (zmieniana)" if act.get("references", {}).get("Akty zmieniające") else "pierwotne"


def isap_url(act: dict) -> str:
    return f"https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id={act['address']}"


def download(act: dict, cache: Path, state: dict) -> tuple[str, bool]:
    dest = cache / cache_name(act)
    key = cache_name(act)
    if dest.exists() and state.get(key) == act.get("changeDate"):
        return key, False
    data = get(pdf_url(act))
    if not data.startswith(b"%PDF"):
        raise RuntimeError(f"{key}: odpowiedź nie jest PDF-em")
    tmp = dest.with_suffix(".part")
    tmp.write_bytes(data)
    tmp.replace(dest)
    return key, True


def yaml_str(v) -> str:
    return json.dumps(v, ensure_ascii=False)


def nieczytelny(md: str) -> bool:
    """S008 K2: tekst z uszkodzonym kodowaniem czcionek PDF (znaki sterujące zamiast liter)."""
    body = md.split("\n## Przypisy", 1)[0]
    ctrl = len(re.findall(r"[\x01-\x08\x0b\x0c\x0e-\x1f]", body))
    litery = len(re.findall(r"[A-Za-ząćęłńóśźżĄĆĘŁŃÓŚŹŻ]", body)) / max(len(body), 1)
    return ctrl > 20 or litery < 0.3


def _ctrl(t: str) -> bool:
    return bool(re.search(r"[\x01-\x08\x0b\x0c\x0e-\x1f]", t or ""))


def tj_z_ramki(basis: str) -> str | None:
    m = re.match(r"t\.j\. Dz\. U\. z (\d{4}) r\.(?: Nr \d+,)? poz\. (\d+)", basis or "")
    return f"DU/{m.group(1)}/{int(m.group(2))}" if m else None


def _cached(url: str, dest: Path) -> Path | None:
    if not dest.exists():
        data = get(url)
        if not data:
            return None
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(dest.suffix + ".part")
        tmp.write_bytes(data)
        tmp.replace(dest)
    return dest


def fetch_tj(tj_eli: str, cache: Path) -> tuple[Path, str, str] | None:
    """PDF obwieszczenia tekstu jednolitego: T (skład Kancelarii Sejmu), a w razie braku O (Dz. U.)."""
    d = json.loads(get(f"{API}/acts/{tj_eli}"))
    texts = {t["type"]: t["fileName"] for t in d.get("texts", [])}
    for kind in ("T", "O"):
        if kind in texts:
            url = f"{API}/acts/{tj_eli}/text/{kind}/{texts[kind]}"
            p = _cached(url, cache / f"{tj_eli.replace('/', '_')}_TJ_{kind}.pdf")
            if p:
                return p, url, kind
    return None


def render(act: dict, pdf: str) -> dict:
    kind = act["_text"][0]
    cache = Path(pdf).parent
    res = convert(pdf, dehyphenate=kind != "U")
    md, pages, basis = res.markdown, res.pages, res.basis
    tu_date = res.footer_date if kind == "U" else None
    br = brzmienie(act)
    zrodlo_tekstu = f"PDF {kind}"
    src_url = pdf_url(act)
    uwagi: list[str] = []
    zm = act["_zm"]

    # S008 K1: tekst ujednolicony starszy niż ostatni tekst jednolity → tekst jednolity z obwieszczenia
    if kind == "U" and zm["tekst_jednolity_eli"]:
        ramka = tj_z_ramki(basis)
        starszy = bool(tu_date and zm["tekst_jednolity_z_dnia"] and tu_date < zm["tekst_jednolity_z_dnia"])
        if (ramka and ramka != zm["tekst_jednolity_eli"]) or starszy:
            tj = fetch_tj(zm["tekst_jednolity_eli"], cache)
            if tj:
                r2 = convert(str(tj[0]), dehyphenate=True)
                md, pages = r2.markdown, r2.pages
                uwagi.append(
                    f"Tekst ujednolicony ISAP (z {tu_date or '?'}, na podstawie {ramka or basis or '?'}) był starszy niż ostatni "
                    f"tekst jednolity {zm['tekst_jednolity']} z {zm['tekst_jednolity_z_dnia']}; użyto tekstu jednolitego z Dz. U.")
                br, zrodlo_tekstu, src_url = "jednolite", f"tekst jednolity, PDF {tj[2]}", tj[1]
                tu_date, basis = None, zm["tekst_jednolity"]

    # S008 K2: nieczytelna warstwa tekstowa PDF → OCR (tekst ujednolicony) albo HTML (tekst pierwotny)
    if nieczytelny(md):
        if br == "ujednolicone":
            from ocr import convert_ocr

            md, f2, b2 = convert_ocr(pdf)
            tu_date, basis = tu_date or f2, basis if basis and not _ctrl(basis) else b2
            zrodlo_tekstu = "OCR (tesseract) PDF U"
            uwagi.append("Warstwa tekstowa PDF jest nieczytelna (uszkodzone kodowanie czcionek); "
                         "tekst odczytano przez OCR i może zawierać błędy rozpoznania.")
        else:
            url = f"{API}/acts/{act['ELI']}/text.html"
            h = _cached(url, cache.parent / "html" / f"{act['ELI'].replace('/', '_')}.html")
            if h:
                md = convert_html(h.read_text(encoding="utf-8", errors="replace"))
                zrodlo_tekstu, src_url = "HTML (API ELI)", url
                uwagi.append("Warstwa tekstowa PDF jest nieczytelna (uszkodzone kodowanie czcionek); użyto wersji HTML z API ELI.")
        if nieczytelny(md):
            uwagi.append("Tekst nadal może być nieczytelny — porównaj z PDF-em.")
    if basis and _ctrl(basis):  # ramka to głównie cyfry, więc sprawdzamy tylko znaki sterujące
        basis = None

    fm = {
        "tytul": act["title"],
        "eli": act["ELI"],
        "adres_publikacyjny": act["displayAddress"],
        "status": act["status"],
        "brzmienie": br,
        "data_aktu": act.get("announcementDate"),
        "data_wejscia_w_zycie": act.get("entryIntoForce"),
        "tekst_ujednolicony_z_dnia": tu_date,
        "opracowano_na_podstawie": basis,
        "liczba_ustaw_zmieniajacych": zm["liczba_ustaw_zmieniajacych"],
        "tekst_jednolity": zm["tekst_jednolity"] or None,
        "tekst_jednolity_z_dnia": zm["tekst_jednolity_z_dnia"] or None,
        "zmian_po_tekscie_jednolitym": zm["zmian_po_tekscie_jednolitym"] if zm["tekst_jednolity"] else None,
        "rok_ostatniej_zmiany": zm["rok_ostatniej_zmiany"] or None,
        "zrodlo_tekstu": zrodlo_tekstu,
        "uwagi": uwagi,
        "slowa_kluczowe": act.get("keywords", []),
        "zrodlo_pdf": src_url,
        "isap": isap_url(act),
    }
    lines = ["---"]
    for k, v in fm.items():
        lines.append(f"{k}: {yaml_str(v)}")
    lines.append("---")
    lines.append("")
    lines.append(f"# {act['title']}")
    lines.append("")
    path = out_path(act)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n" + md, encoding="utf-8")
    return {
        "eli": act["ELI"],
        "rok": act["year"],
        "pozycja": act["pos"],
        "tytul": act["title"],
        "adres_publikacyjny": act["displayAddress"],
        "status": act["status"],
        "brzmienie": br,
        "data_aktu": act.get("announcementDate") or "",
        "data_wejscia_w_zycie": act.get("entryIntoForce") or "",
        "tekst_ujednolicony_z_dnia": tu_date or "",
        "opracowano_na_podstawie": basis or "",
        **zm,
        "zrodlo_tekstu": zrodlo_tekstu,
        "uwagi": " ".join(uwagi),
        "strony_pdf": pages,
        "plik": str(path.relative_to(ROOT)),
        "zrodlo_pdf": src_url,
        "isap": isap_url(act),
    }


def _render_job(args):
    act, pdf = args
    try:
        return render(act, pdf), None
    except Exception as e:  # noqa: BLE001
        return None, f"{act['ELI']}: {type(e).__name__}: {e}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cache", default=str(ROOT / ".cache" / "pdf"))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--only", action="append", default=[], help="ELI, np. DU/1997/553 (można powtarzać)")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument("--download-workers", type=int, default=4)
    args = ap.parse_args()

    cache = Path(args.cache)
    cache.mkdir(parents=True, exist_ok=True)
    state_file = cache / "stan.json"
    state = json.loads(state_file.read_text()) if state_file.exists() else {}

    print("Pobieram listę aktów…", flush=True)
    acts = list_acts()
    full_run = not args.only and not args.limit
    if args.only:
        acts = [a for a in acts if a["ELI"] in set(args.only)]
    if args.limit:
        acts = acts[: args.limit]
    print(f"Ustaw do przetworzenia: {len(acts)}", flush=True)
    tj_meta = fetch_tj_meta(acts, cache / "teksty_jednolite.json", get, API)
    for a in acts:
        a["_zm"] = change_info(a, tj_meta)

    errors: list[str] = []
    fetched = 0
    with ThreadPoolExecutor(args.download_workers) as ex:
        futs = {ex.submit(download, a, cache, state): a for a in acts}
        for i, f in enumerate(as_completed(futs), 1):
            a = futs[f]
            try:
                _, new = f.result()
                fetched += new
                state[cache_name(a)] = a.get("changeDate")
            except Exception as e:  # noqa: BLE001
                errors.append(f"{a['ELI']}: pobieranie: {e}")
            if i % 100 == 0:
                print(f"  pobrano {i}/{len(acts)}", flush=True)
                state_file.write_text(json.dumps(state, indent=0))
    state_file.write_text(json.dumps(state, indent=0))
    print(f"Nowe/zmienione PDF-y: {fetched}", flush=True)

    jobs = []
    for a in acts:
        pdf = cache / cache_name(a)
        if pdf.exists():
            jobs.append((a, str(pdf)))

    rows = []
    with ProcessPoolExecutor(args.workers) as ex:
        for i, (row, err) in enumerate(ex.map(_render_job, jobs, chunksize=4), 1):
            if err:
                errors.append(err)
            else:
                rows.append(row)
            if i % 100 == 0:
                print(f"  skonwertowano {i}/{len(jobs)}", flush=True)

    if full_run:
        # Usuń pliki aktów, które wypadły z listy (uchylone).
        keep = {out_path(a) for a in acts}
        for p in (DATA / "ustawy").rglob("*.md"):
            if p not in keep:
                p.unlink()
        rows.sort(key=lambda r: (r["rok"], r["pozycja"]))
        with open(DATA / "indeks.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        update_readme(rows, ROOT / "README.md")
        stale = DATA / "LISTA.md"
        if stale.exists():
            stale.unlink()

    print(f"Gotowe: {len(rows)} plików, błędów: {len(errors)}")
    for e in errors:
        print("  BŁĄD", e)
    return 1 if errors and not rows else 0


if __name__ == "__main__":
    sys.exit(main())

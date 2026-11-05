#!/usr/bin/env python3
"""x001 (S005): jednorazowa weryfikacja ilościowa korpusu i parametrów na próbie 100 ustaw.

Każdy parametr sprawdzamy innym źródłem/narzędziem niż to, z którego go wyliczono:
- bilans: listowanie roczne /acts/DU/{rok} zamiast wyszukiwarki /acts/search;
- brzmienie, t.j., liczba zmian: szczegóły aktu GET /acts/{ELI} + relacje odwrotne
  (ustawa zmieniająca → „Akty zmienione”, obwieszczenie → „Tekst jednolity dla aktu”);
- zmiany po t.j. i data tekstu ujednoliconego: ramka „Opracowano na podstawie” i stopka PDF
  odczytane przez pdftotext (poppler), a nie PyMuPDF użyty w konwerterze;
- wykluczenia: treść aktu (HTML lub PDF), a nie tytuł.

Użycie: .venv/bin/python eksperymenty/x001-weryfikacja-100/x001.py
Wynik: kontrole/x001/{wyniki.json, wykluczenia.json, bilans.json}; cache w .cache/x001/.
"""

from __future__ import annotations

import csv
import json
import random
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "skrypty"))
from pobierz import ORIGINAL_STATUSES, SKIP_STATUSES, TREATY_RE, is_amending, short_title  # noqa: E402

API = "https://api.sejm.gov.pl/eli"
UA = "nomystria/1.0 (+https://github.com/michalasobczak/nomystria) x001"
CACHE = ROOT / ".cache" / "x001"
PDF_CACHE = ROOT / ".cache" / "pdf"
OUT = ROOT / "kontrole" / "x001"
SEED = 20261105
STALE = ["DU/1997/483", "DU/1997/553", "DU/2004/535"]  # zawsze w próbie: Konstytucja, KK, VAT


# ---------- HTTP z cache ----------
def get(url: str, binary: bool = False, retries: int = 5):
    key = re.sub(r"[^A-Za-z0-9._-]+", "_", url.replace(API, ""))[:180]
    f = CACHE / ("bin" if binary else "json") / key
    if f.exists():
        data = f.read_bytes()
        return data if binary else json.loads(data)
    for a in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if a == retries - 1:
                raise
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if a == retries - 1:
                raise
        time.sleep(2 ** a)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_bytes(data)
    return data if binary else json.loads(data)


def detail(eli: str) -> dict | None:
    return get(f"{API}/acts/{eli}")


def key(eli: str) -> tuple[int, int]:
    _, y, p = eli.split("/")
    return int(y), int(p)


def wynik(eli, parametr, zbior, zrodlo_val, zrodlo, werdykt, wyjasnienie=""):
    return {"eli": eli, "parametr": parametr, "wartosc_zbior": str(zbior), "wartosc_zrodlo": str(zrodlo_val),
            "zrodlo": zrodlo, "werdykt": werdykt, "wyjasnienie": wyjasnienie}


# ---------- PDF przez pdftotext (inne narzędzie niż konwerter) ----------
def pdftotext_crop(pdf: Path, x: int, y: int, w: int, h: int) -> str:
    r = subprocess.run(["pdftotext", "-f", "1", "-l", "1", "-x", str(x), "-y", str(y), "-W", str(w), "-H", str(h),
                        "-raw", str(pdf), "-"], capture_output=True, text=True)
    return r.stdout


def frame_and_date(pdf: Path) -> tuple[str | None, str | None]:
    """Ramka „Opracowano na podstawie: …” (prawy margines str. 1) i data ze stopki str. 1 — wycinki pdftotext."""
    margin = re.sub(r"\s+", " ", pdftotext_crop(pdf, 465, 60, 140, 420))
    m = re.search(r"Opracowano\s+na\s+podstawie:\s*(.*?poz\.\s*[\d,\si]+\.)", margin)
    if not m:  # starszy układ (np. Konstytucja): ramka wpleciona w szerszy wycinek
        wide = re.sub(r"\s+", " ", pdftotext_crop(pdf, 380, 60, 220, 420))
        m = re.search(r"Opracowano\s+na\s+podstawie:\s*(.*?poz\.\s*[\d,\si]+\.)", wide)
    frame = re.sub(r"\s+", " ", m.group(1)).strip() if m else None
    # Stopka: słowo-data położone najniżej na stronie 1 (pdftotext -bbox), w dolnych 20% strony.
    r = subprocess.run(["pdftotext", "-f", "1", "-l", "1", "-bbox", str(pdf), "-"], capture_output=True, text=True)
    hm = re.search(r'<page width="[\d.]+" height="([\d.]+)"', r.stdout)
    height = float(hm.group(1)) if hm else 842.0
    words = re.findall(r'<word xMin="[\d.]+" yMin="([\d.]+)" xMax="[\d.]+" yMax="[\d.]+">([^<]+)</word>', r.stdout)
    dates = sorted((float(y), w) for y, w in words
                   if float(y) > height * 0.8 and re.fullmatch(r"\d{4}-\d{2}-\d{2}|\d{2}\.\d{2}\.\d{4}", w))
    d = None
    if dates:
        d = dates[-1][1]
        if "." in d:
            d = "-".join(reversed(d.split(".")))
    return frame, d


def frame_positions(frame: str) -> list[str]:
    """„t.j. Dz. U. z 2026 r. poz. 1263, 1270 oraz z 2027 r. poz. 5.” → ['DU/2026/1263', 'DU/2026/1270', 'DU/2027/5']."""
    out = []
    frame = re.sub(r",\s*z\s*(\d{4})", r", z \1", frame)  # pdftotext gubi spacje: „1843,z2026 r.”
    for seg in re.split(r"(?=\bz \d{4} r\.)", frame):
        my = re.match(r"z (\d{4}) r\.", seg)
        if not my:
            continue
        y = my.group(1)
        for grp in re.findall(r"poz\.\s*([\d][\d,\si]*)", seg):
            for n in re.findall(r"\d+", grp):
                out.append(f"DU/{y}/{int(n)}")
    return out


# ---------- G1: bilans ----------
def bilans(indeks: list[dict]) -> dict:
    search = []
    off = 0
    while True:
        d = get(f"{API}/acts/search?publisher=DU&type=Ustawa&inForce=1&limit=500&offset={off}")
        search += d["items"]
        off += 500
        if off >= d["totalCount"]:
            break
    search_eli = {i["ELI"] for i in search}

    years = range(1918, date.today().year + 1)
    roczne = []
    with ThreadPoolExecutor(4) as ex:
        for d in ex.map(lambda y: get(f"{API}/acts/DU/{y}"), years):
            if d:
                roczne += [i for i in d["items"] if i.get("type") == "Ustawa"]
    # Statusy oznaczające akt obowiązujący (bez uchylonych/wygasłych).
    in_force = {i["ELI"]: i for i in roczne if i.get("status") not in SKIP_STATUSES | {"nieobowiązujący - przyczyna nieustalona", "nieobowiązujący - uchylona podstawa prawna"}}

    ours = {r["eli"] for r in indeks}
    kat = {"w_zbiorze": 0, "nowelizacje": 0, "ratyfikacje": 0, "jednorazowe_i_inne_statusy": 0,
           "obowiązujące_bez_tekstu": 0, "inne": 0}
    przyklady = {k: [] for k in kat}
    for i in search:
        e = i["ELI"]
        texts = {t["type"] for t in i.get("texts", [])}
        title = re.sub(r"\s+", " ", i["title"]).strip()
        if e in ours:
            k = "w_zbiorze"
        elif i["status"] in SKIP_STATUSES:
            k = "inne"
        elif is_amending(title):
            k = "nowelizacje"
        elif TREATY_RE.match(short_title(title)):
            k = "ratyfikacje"
        elif "U" not in texts and i["status"] not in ORIGINAL_STATUSES:
            k = "jednorazowe_i_inne_statusy"
        elif not texts & {"U", "T", "O"}:
            k = "obowiązujące_bez_tekstu"
        else:
            k = "inne"
        kat[k] += 1
        if len(przyklady[k]) < 5:
            przyklady[k].append(f"{e} {title[:90]}")
    only_yearly = sorted(set(in_force) - search_eli, key=key)
    only_search = sorted(search_eli - set(in_force), key=key)
    return {
        "search_inForce": len(search),
        "listowanie_roczne_obowiazujace": len(in_force),
        "kategorie": kat,
        "suma_kategorii": sum(kat.values()),
        "w_indeksie": len(ours),
        "tylko_w_listowaniu_rocznym": [f"{e} [{in_force[e]['status']}] {in_force[e]['title'][:90]}" for e in only_yearly],
        "tylko_w_wyszukiwarce": only_search,
        "przyklady": przyklady,
        "indeks_spoza_wyszukiwarki": sorted(ours - search_eli),
    }


# ---------- G2–G5: próba ----------
def probka(indeks: list[dict]) -> list[dict]:
    rnd = random.Random(SEED)
    by = {"ujednolicone": [], "pierwotne": [], "pierwotne (zmieniana)": []}
    for r in indeks:
        if r["eli"] not in STALE:
            # „jednolite” (S008) to ustawy z plikiem U, których tekst wzięto z t.j. — losujemy je razem z U
            by["ujednolicone" if r["brzmienie"] == "jednolite" else r["brzmienie"]].append(r)
    reszta = 100 - len(STALE)
    n_pz = max(2, round(reszta * len(by["pierwotne (zmieniana)"]) / len(indeks)))
    n_p = round(reszta * len(by["pierwotne"]) / len(indeks))
    n_u = reszta - n_pz - n_p
    pick = [r for r in indeks if r["eli"] in STALE]
    pick += rnd.sample(by["ujednolicone"], n_u) + rnd.sample(by["pierwotne"], n_p) + rnd.sample(by["pierwotne (zmieniana)"], n_pz)
    return sorted(pick, key=lambda r: key(r["eli"]))


def check_act(r: dict) -> list[dict]:
    eli = r["eli"]
    out = []
    d = detail(eli)
    if d is None:
        return [wynik(eli, p, r.get(p, ""), "", "GET /acts/{ELI}", "niezweryfikowany", "brak szczegółów w API")
                for p in ("brzmienie", "tekst_jednolity", "liczba_ustaw_zmieniajacych")]
    texts = {t["type"] for t in d.get("texts", [])}
    refs = d.get("references", {})
    zm = sorted({x["id"] for x in refs.get("Akty zmieniające", []) if x["id"].startswith("DU/")}, key=key)

    # Brzmienie
    if "U" in texts:
        exp = "jednolite" if r["brzmienie"] == "jednolite" else "ujednolicone"  # S008: t.j. zamiast starszego t.u.
    elif zm:
        exp = "pierwotne (zmieniana)"
    else:
        exp = "pierwotne"
    out.append(wynik(eli, "brzmienie", r["brzmienie"], exp, "GET /acts/{ELI}: texts + Akty zmieniające",
                     "zgodny" if exp == r["brzmienie"] else "rozbiezny"))

    # Liczba ustaw zmieniających: liczba + relacja odwrotna (zmieniająca → „Akty zmienione” zawiera ELI)
    with ThreadPoolExecutor(4) as ex:
        dets = dict(zip(zm, ex.map(detail, zm)))
    brak_rel = [z for z, dz in dets.items() if not dz or eli not in {x["id"] for x in dz.get("references", {}).get("Akty zmienione", [])}]
    ours_n = int(r["liczba_ustaw_zmieniajacych"] or 0)
    if ours_n != len(zm):
        out.append(wynik(eli, "liczba_ustaw_zmieniajacych", ours_n, len(zm), "GET /acts/{ELI}", "rozbiezny",
                         "liczba w szczegółach aktu różni się od wyniku wyszukiwarki"))
    elif brak_rel:
        out.append(wynik(eli, "liczba_ustaw_zmieniajacych", ours_n, len(zm) - len(brak_rel),
                         "relacja odwrotna „Akty zmienione”", "rozbiezny",
                         "brak relacji odwrotnej dla: " + ", ".join(brak_rel[:10])))
    else:
        out.append(wynik(eli, "liczba_ustaw_zmieniajacych", ours_n, len(zm),
                         "GET /acts/{ELI} + relacja odwrotna „Akty zmienione”", "zgodny"))

    # Tekst jednolity: szczegóły + relacja odwrotna + ramka PDF
    tjs = sorted({x["id"] for x in refs.get("Inf. o tekście jednolitym", []) if x["id"].startswith("DU/")}, key=key)
    tj = tjs[-1] if tjs else ""
    pdf = PDF_CACHE / f"{eli.replace('/', '_')}_U.pdf"
    frame, fdate = frame_and_date(pdf) if pdf.exists() else (None, None)
    fpos = frame_positions(frame) if frame and "t.j." in frame else []
    if tj != r["tekst_jednolity_eli"]:
        out.append(wynik(eli, "tekst_jednolity", r["tekst_jednolity_eli"] or "—", tj or "—", "GET /acts/{ELI}", "rozbiezny"))
    elif not tj:
        uw = "ramka PDF wskazuje t.j., którego API nie zna" if frame and "t.j." in frame else ""
        out.append(wynik(eli, "tekst_jednolity", "—", "—", "GET /acts/{ELI}" + (" + ramka PDF" if frame else ""),
                         "rozbiezny" if uw else "zgodny", uw))
    else:
        dtj = detail(tj)
        back = dtj and eli in {x["id"] for x in dtj.get("references", {}).get("Tekst jednolity dla aktu", [])}
        frame_tj = fpos[0] if fpos else None
        if not back:
            out.append(wynik(eli, "tekst_jednolity", tj, tj, "obwieszczenie → „Tekst jednolity dla aktu”", "rozbiezny",
                             "obwieszczenie nie wskazuje tej ustawy"))
        elif r["brzmienie"] == "ujednolicone" and frame_tj and frame_tj != tj:
            out.append(wynik(eli, "tekst_jednolity", tj, frame_tj, "ramka „Opracowano na podstawie” (pdftotext)", "rozbiezny",
                             "tekst ujednolicony opracowano na podstawie innego (wcześniejszego?) t.j."))
        else:
            src = "GET /acts/{ELI} + obwieszczenie" + (" + ramka PDF (pdftotext)" if frame_tj else "")
            out.append(wynik(eli, "tekst_jednolity", tj, frame_tj or tj, src, "zgodny"))

    # Zmiany po t.j. (tylko ustawy z t.j.): porównanie z pozycjami z ramki
    if tj and r["zmian_po_tekscie_jednolitym"] != "":
        po = [z for z in zm if key(z) > key(tj)]
        ours_po = int(r["zmian_po_tekscie_jednolitym"])
        if ours_po != len(po):
            out.append(wynik(eli, "zmian_po_tekscie_jednolitym", ours_po, len(po), "GET /acts/{ELI}", "rozbiezny"))
        elif r["brzmienie"] != "ujednolicone" or not frame:
            out.append(wynik(eli, "zmian_po_tekscie_jednolitym", ours_po, len(po), "GET /acts/{ELI}", "zgodny",
                             "brak ramki PDF do porównania" if r["brzmienie"] == "ujednolicone" else ""))
        else:
            w_ramce = set(fpos[1:])
            tu = r["tekst_ujednolicony_z_dnia"] or fdate or ""
            po_prom = {z: (dets.get(z) or {}).get("promulgation") or "" for z in po}
            do_tu = {z for z in po if po_prom[z] and tu and po_prom[z] <= tu}
            po_tu = sorted(set(po) - do_tu, key=key)
            nadmiar = sorted(w_ramce - set(po), key=key)
            brak = sorted(do_tu - w_ramce, key=key)
            if not nadmiar and not brak:
                ex_ = f"{len(w_ramce)} uwzględnione w tekście ujednoliconym"
                if po_tu:
                    ex_ += f"; {len(po_tu)} ogłoszone po dacie tekstu ujednoliconego ({tu}): " + ", ".join(po_tu)
                out.append(wynik(eli, "zmian_po_tekscie_jednolitym", ours_po, len(po),
                                 "ramka „Opracowano na podstawie” (pdftotext) + daty ogłoszenia", "zgodny", ex_))
            else:
                ex_ = []
                if nadmiar:
                    ex_.append("w ramce, a nie wśród aktów zmieniających: " + ", ".join(nadmiar))
                if brak:
                    ex_.append("ogłoszone przed datą t.u., a brak w ramce: " + ", ".join(brak))
                out.append(wynik(eli, "zmian_po_tekscie_jednolitym", ours_po, f"{len(w_ramce)} w ramce",
                                 "ramka „Opracowano na podstawie” (pdftotext)", "rozbiezny", "; ".join(ex_)))

    # Data tekstu ujednoliconego: stopka odczytana pdftotext vs PyMuPDF
    if r["brzmienie"] == "ujednolicone":
        if not fdate:
            out.append(wynik(eli, "tekst_ujednolicony_z_dnia", r["tekst_ujednolicony_z_dnia"], "", "stopka PDF (pdftotext)",
                             "niezweryfikowany", "pdftotext nie odczytał daty ze stopki"))
        else:
            out.append(wynik(eli, "tekst_ujednolicony_z_dnia", r["tekst_ujednolicony_z_dnia"], fdate, "stopka PDF (pdftotext)",
                             "zgodny" if fdate == r["tekst_ujednolicony_z_dnia"] else "rozbiezny"))
    return out


# ---------- Kontrole całego korpusu (wynikły z rozbieżności w próbie) ----------
def korpus(indeks: list[dict]) -> tuple[list[dict], dict]:
    """K1: tekst ujednolicony starszy niż ostatni t.j.; K2: tekst nieczytelny (zepsute kodowanie czcionek PDF)."""
    out, stat = [], {"K1_sprawdzono": 0, "K1_rozbiezne": 0, "K2_sprawdzono": 0, "K2_rozbiezne": 0}
    for r in indeks:
        if r["brzmienie"] == "ujednolicone" and r["tekst_jednolity_eli"]:
            stat["K1_sprawdzono"] += 1
            m = re.match(r"t\.j\. Dz\. U\. z (\d{4}) r\.(?: Nr \d+,)? poz\. (\d+)", r["opracowano_na_podstawie"])
            ramka_tj = f"DU/{m.group(1)}/{int(m.group(2))}" if m else None
            starszy = r["tekst_ujednolicony_z_dnia"] and r["tekst_ujednolicony_z_dnia"] < r["tekst_jednolity_z_dnia"]
            if (ramka_tj and ramka_tj != r["tekst_jednolity_eli"]) or starszy:
                stat["K1_rozbiezne"] += 1
                out.append(wynik(r["eli"], "aktualnosc_tekstu_ujednoliconego", f"t.u. z {r['tekst_ujednolicony_z_dnia'] or '?'}"
                                 f" na podstawie {ramka_tj or '?'}", f"ostatni t.j. {r['tekst_jednolity_eli']} z {r['tekst_jednolity_z_dnia']}",
                                 "ramka PDF + GET /acts/{ELI}", "rozbiezny",
                                 "ISAP nie zaktualizował jeszcze tekstu ujednoliconego po ostatnim obwieszczeniu; "
                                 "urzędowy tekst jednolity jest aktualniejszy niż tekst w zbiorze"))
        stat["K2_sprawdzono"] += 1
        t = (ROOT / r["plik"]).read_text(encoding="utf-8").split("---", 2)[2]
        ctrl = len(re.findall(r"[\x01-\x08\x0b\x0c\x0e-\x1f]", t))
        litery = len(re.findall(r"[A-Za-ząćęłńóśźżĄĆĘŁŃÓŚŹŻ]", t)) / max(len(t), 1)
        if ctrl > 20 or litery < 0.3:
            stat["K2_rozbiezne"] += 1
            out.append(wynik(r["eli"], "czytelnosc_tekstu", "tekst w zbiorze", f"{ctrl} znaków sterujących, {litery:.0%} liter",
                             "analiza pliku Markdown", "rozbiezny",
                             "PDF ma uszkodzone kodowanie czcionek; tekst w zbiorze jest nieczytelny i wymaga innego źródła (HTML, PDF O, OCR)"))
    return out, stat


# ---------- G6: wykluczenia ----------
AMEND_TXT = re.compile(r"wprowadza się następujące zmiany|otrzymuj[eą] brzmienie|uchyla się|dodaje się|skreśla się|traci moc|tracą moc"
                       r"|zastępuje się|w art\. \d+\w*(?: ust\. \d+\w*)? wyraz", re.I)
TREATY_TXT = re.compile(r"ratyfikac|przystąpieni|wypowiedzeni|zatwierdzeni", re.I)


def act_text(i: dict) -> tuple[str, str]:
    texts = {t["type"]: t["fileName"] for t in i.get("texts", [])}
    if "H" in texts:
        b = get(f"{API}/acts/{i['ELI']}/text.html", binary=True)
        if b:
            raw = b.decode("utf-8", "replace")
            t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", raw))
            # HTML bywa samą strukturą jednostek ('"type": "arti"') bez treści przepisów
            if '"type": "arti"' not in raw and len(re.findall(r"[a-ząćęłńóśźż]", t)) > 300:
                return t, "HTML"
    for k in ("T", "O"):
        if k in texts:
            b = get(f"{API}/acts/{i['ELI']}/text/{k}/{texts[k]}", binary=True)
            if b:
                tmp = CACHE / "tmp.pdf"
                tmp.write_bytes(b)
                r = subprocess.run(["pdftotext", str(tmp), "-"], capture_output=True, text=True)
                return re.sub(r"\s+", " ", r.stdout), f"PDF {k} (pdftotext)"
    return "", ""


def wykluczenia(search_items: list[dict], ours: set[str]) -> list[dict]:
    rnd = random.Random(SEED + 1)
    am = [i for i in search_items if i["ELI"] not in ours and i["status"] not in SKIP_STATUSES and is_amending(re.sub(r"\s+", " ", i["title"]))]
    tr = [i for i in search_items if i["ELI"] not in ours and i["status"] not in SKIP_STATUSES
          and not is_amending(i["title"]) and TREATY_RE.match(short_title(re.sub(r"\s+", " ", i["title"])))]
    out = []
    for grupa, items, rx in (("nowelizacja", rnd.sample(am, 50), AMEND_TXT), ("ratyfikacja", rnd.sample(tr, 20), TREATY_TXT)):
        for i in items:
            txt, src = act_text(i)
            if not txt:
                w, ex_ = "niezweryfikowany", "brak tekstu"
            elif len(re.findall(r"[\x01-\x08\x0b\x0c\x0e-\x1f]", txt)) > 5 and not rx.search(txt):
                w, ex_ = "niezweryfikowany", "tekst nieczytelny (uszkodzone kodowanie czcionek PDF)"
            else:
                m = rx.search(txt)
                w, ex_ = ("zgodny", f"„{m.group(0)}”") if m else ("rozbiezny", "w treści brak zwrotów typowych dla tej grupy")
            out.append({"eli": i["ELI"], "tytul": re.sub(r"\s+", " ", i["title"]), "wykluczona_jako": grupa,
                        "zrodlo": src, "werdykt": w, "wyjasnienie": ex_})
    return out


def main() -> int:
    CACHE.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    with open(ROOT / "dane" / "indeks.csv", encoding="utf-8") as fh:
        indeks = list(csv.DictReader(fh))

    print("G1 bilans…", flush=True)
    b = bilans(indeks)
    (OUT / "bilans.json").write_text(json.dumps(b, ensure_ascii=False, indent=1), encoding="utf-8")

    print("G2–G5 próba 100…", flush=True)
    sample = probka(indeks)
    wyn = []
    for n, r in enumerate(sample, 1):
        wyn += check_act(r)
        if n % 20 == 0:
            print(f"  {n}/100", flush=True)
    print("K1–K2 cały korpus…", flush=True)
    kw, kstat = korpus(indeks)
    doc = {"id": "x001", "spec": "S005", "tytul": "Weryfikacja ilościowa: próba 100 ustaw + kontrole całego korpusu",
           "data": date.today().isoformat(), "ziarno": SEED, "probka": [r["eli"] for r in sample],
           "korpus": kstat, "wyniki": wyn + kw}
    (OUT / "wyniki.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")

    print("G6 wykluczenia…", flush=True)
    search = []
    off = 0
    while True:
        d = get(f"{API}/acts/search?publisher=DU&type=Ustawa&inForce=1&limit=500&offset={off}")
        search += d["items"]
        off += 500
        if off >= d["totalCount"]:
            break
    wk = wykluczenia(search, {r["eli"] for r in indeks})
    (OUT / "wykluczenia.json").write_text(json.dumps({"id": "x001", "spec": "S005", "ziarno": SEED + 1, "wyniki": wk},
                                                     ensure_ascii=False, indent=1), encoding="utf-8")
    from collections import Counter
    print("bilans:", b["search_inForce"], b["listowanie_roczne_obowiazujace"], b["kategorie"])
    print("parametry:", Counter((w["parametr"], w["werdykt"]) for w in wyn))
    print("korpus:", kstat)
    print("wykluczenia:", Counter((w["wykluczona_jako"], w["werdykt"]) for w in wk))
    return 0


if __name__ == "__main__":
    sys.exit(main())

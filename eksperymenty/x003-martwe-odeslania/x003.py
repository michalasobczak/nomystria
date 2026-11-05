#!/usr/bin/env python3
"""x003 (S010): reguła R1 — martwe odesłania wewnętrzne („art. N” tej samej ustawy, którego w niej nie ma).

Zakres: ustawy uchwalone w 1989 r. lub później albo zmieniane ustawą ogłoszoną w 1989 r. lub później.
Analiza wyłącznie na wersji tekstowej (Markdown) — bez PDF (decyzja właściciela).

Użycie: .venv/bin/python eksperymenty/x003-martwe-odeslania/x003.py
Etap 1 (ten skrypt): kandydaci → kontrole/x003/kandydaci_skrypt.json (+ odrzucone.json, statystyka.json).
Etap 2 (filtr zgrubny) i etap 3 (ocena modelu z pełnym tekstem ustawy) opisuje kontrole/x003/RAPORT.md;
na stronę trafiają tylko znaleziska potwierdzone w etapie 3 (kontrole/x003/znaleziska.json).
"""

from __future__ import annotations

import csv
import html
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import date
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / ".cache"
OUT = ROOT / "kontrole" / "x003"
OD = 1989

# Wskazanie innego aktu w zdaniu → zdanie pomijamy w całości (zachowawczo: lepiej pominąć niż zgłosić fałszywie).
ZEWN = re.compile(
    r"\b(?:ustawy|ustawie|ustawą|ustawa|ustaw|Kodeksu|kodeksu|Kodeks|kodeks|Kodeksie|kodeksie|Kpa|Kpc|Kc|Kk|Kp|Kks|Kkw|Kpk|Ksh|Kw|"
    r"KK|KKS|KKW|KPK|KPC|KPA|KC|KP|rozporządzenia|rozporządzeniu|rozporządzeń|dyrektywy|dyrektywie|Traktatu|traktatu|"
    r"Konstytucji|Konwencji|konwencji|Statutu|Prawa\s+[a-ząćęłńóśźż]+|Prawie\s+[a-ząćęłńóśźż]+|Ordynacji|dekretu|Porozumienia|"
    r"Protokołu|Regulaminu|Karty|Karta|Karcie|przepisów\s+o)(?![a-ząćęłńóśźż])"
    r"|\bk\.\s?[a-z]{1,3}\.(?:[a-z]{1,2}\.)?|\bu\.[a-z]\.[a-z.]+|Dz\.\s?U\.|Dz\.\s?Urz\.")
WEWN = re.compile(r"\b(niniejszej ustawy|ustawy niniejszej|niniejszego kodeksu|kodeksu niniejszego)\b")
# zakres tylko bez spacji („art. 38d–38f”); „art. 18 – 300 000 zł” to nie zakres
REF = re.compile(r"\bart\. (\d+[a-z]{0,3})(?:[–-](\d+[a-z]{0,3}))?(?![\w)])")
# odesłanie do artykułu ustawy zmienianej w przepisach o wejściu w życie („art. 31 pkt 23 w zakresie art. 45b”)
POPRZEDZA = re.compile(r"(w zakresie|w brzmieniu nadanym|dodawanego|dodanego|zmienianego|zmienianym)\s*$")
LISTA = re.compile(r"^(\d+[a-z]?\)|[a-z]{1,2}\)|[–—-]\s)")
AMEND = re.compile(r"wprowadza się (następujące )?zmian|otrzymuj[eą] brzmienie|dodaje się|skreśla się|uchyla się|zastępuje się|"
                   r"^W (ustawie|Kodeksie|kodeksie|dekrecie|rozporządzeniu|ustawach)\b|^Traci moc|^Tracą moc")
# Granice zdań: średnik/dwukropek albo kropka po wyrazie z ≥ 4 małych liter przed wielką literą
# (nie dzielimy po skrótach „art.”, „ust.”, „pkt”, „poz.”, „lit.”, „Nr”).
# Akapit-operacja nowelizacyjna („2) w art. 233 skreśla się § 3”, „po art. 89 dodaje się …”) — dotyczy innego aktu.
OPERACJA = re.compile(r"skreśla się|otrzymuj[eą] brzmienie|trzymuje brzmienie|dodaje się|zastępuje się|uchyla się|w brzmieniu:|wyrazy|"
                      r"\d+[a-z]?\)\s+(?:w|po|przed)\s+art\.|^(?:w|po|przed)\s+art\.")
ZDANIA = re.compile(r"(?<=[;:])\s+|(?<=[a-ząćęłńóśźż]{4}\.)\s+(?=[A-ZĄĆĘŁŃÓŚŹŻ])")


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace(" ", " ")).strip()


def _num(n: str) -> tuple[int, str]:
    m = re.match(r"(\d+)([a-z]*)", n)
    return int(m.group(1)), m.group(2)


def analiza(md: str):
    """Spis artykułów i trafienia R1 — wyłącznie na wersji tekstowej (Markdown).

    Spis (zachowawczy, raczej za duży niż za mały): numery z każdego nagłówka „Art. N.” w treści, także cytowanego
    w nowelizacjach. Za duży spis może ukryć prawdziwe trafienie, ale nie tworzy fałszywego.
    Granice artykułów (do pomijania artykułów zmieniających): nagłówek „Art. N.” spoza cytatu, numer nie mniejszy niż poprzedni.
    """
    body = md.split("---", 2)[2].split("\n## Przypisy", 1)[0]
    paras = [p.strip() for p in body.split("\n\n") if p.strip()]
    arts = set(re.findall(r"(?m)^„?Art\. (\d+[a-z]{0,3})\.", body))
    # nagłówki zbiorcze pominiętych/uchylonych artykułów: „Art. 13–22. (pominięte)”, „Art. 5a–5c. (uchylone)”
    for a, b in re.findall(r"(?m)^„?Art\. (\d+[a-z]{0,3})\s*[–-]\s*(\d+[a-z]{0,3})\.", body):
        arts.update((a, b))
        (na, la), (nb, lb) = _num(a), _num(b)
        if not la and not lb and nb - na < 2000:
            arts.update(str(i) for i in range(na, nb + 1))
        elif na == nb and la and lb:  # 5a–5f
            arts.update(f"{na}{chr(c)}" for c in range(ord(la[-1]), ord(lb[-1]) + 1))
    hits = []
    cur, last, skip = None, (0, ""), False
    rows = []
    for p in paras:
        m = re.match(r"^Art\. (\d+[a-z]{0,3})\.\s*(.*)", p, re.S)
        if m and _num(m.group(1)) >= last:
            cur, last = m.group(1), _num(m.group(1))
            skip = bool(AMEND.search(m.group(2)[:400]))
        rows.append((p, cur, skip))
    wstep_zewn = False  # akapit wprowadzający wyliczenie („…określone w Kodeksie karnym:”) wskazywał inny akt
    for p, cur, skip in rows:
        if not LISTA.match(p):
            wstep_zewn = p.rstrip().endswith(":") and bool(ZEWN.search(WEWN.sub(" ", p)))
        elif wstep_zewn:
            continue  # punkt wyliczenia dziedziczy akt z akapitu wprowadzającego
        if skip or p.startswith(("„", "**", "## ", "|", "\"")) or OPERACJA.search(p):
            continue
        for zd in ZDANIA.split(p):
            if "„" in zd or "”" in zd:  # zdanie z cytatem (np. treść przepisów innego aktu)
                continue
            # „niniejszej ustawy” nie znosi wskazania innego aktu w tym samym zdaniu
            if ZEWN.search(WEWN.sub(" ", zd)):
                continue
            for r in REF.finditer(zd):
                if POPRZEDZA.search(zd[:r.start()]):
                    continue
                for n in (r.group(1), r.group(2)):
                    if n and n not in arts:
                        a, b = max(0, r.start() - 120), min(len(zd), r.end() + 120)
                        hits.append({"art_w": cur, "nr": n, "cytat": zd[a:b].strip()})
    return arts, hits


@lru_cache(maxsize=None)
def surowy_tekst(src: str) -> str | None:
    p = Path(src)
    if not p.exists():
        return None
    if p.suffix == ".html":
        t = re.sub(r"<script.*?</script>", " ", p.read_text(encoding="utf-8", errors="replace"), flags=re.S)
        return norm(html.unescape(re.sub(r"<[^>]+>", " ", t)))
    r = subprocess.run(["pdftotext", "-raw", str(p), "-"], capture_output=True, text=True)
    return norm(r.stdout)


def zrodlo(row: dict) -> tuple[str | None, str]:
    eli = row["eli"].replace("/", "_")
    zt = row["zrodlo_tekstu"]
    if zt.startswith("OCR"):
        return None, "tekst z OCR — brak niezależnej warstwy tekstowej do potwierdzenia"
    if zt.startswith("HTML"):
        return str(CACHE / "html" / f"{eli}.html"), "HTML"
    if zt.startswith("tekst jednolity"):
        m = re.search(r"/acts/(DU/\d+/\d+)/text/([TO])/", row["zrodlo_pdf"])
        return str(CACHE / "pdf" / f"{m.group(1).replace('/', '_')}_TJ_{m.group(2)}.pdf"), f"pdftotext ({zt})"
    kind = zt.split()[-1]
    return str(CACHE / "pdf" / f"{eli}_{kind}.pdf"), f"pdftotext (PDF {kind})"


def istnieje_w_surowym(surowy: str, nr: str) -> bool:
    # „Art. 22a.” albo z rozbitym indeksem górnym („Art. 22 1.”)
    pat = r"Art\.\s*" + r"\s*".join(map(re.escape, nr)) + r"\s*\."
    return re.search(pat, surowy) is not None


def main() -> int:
    with open(ROOT / "dane" / "indeks.csv", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh)
                if (int(r["rok"]) >= OD or (r["rok_ostatniej_zmiany"] and int(r["rok_ostatniej_zmiany"]) >= OD))
                and not re.search(r"Przepisy wprowadzające|przepisy wprowadzające", r["tytul"])]  # odsyłają do ustawy wprowadzanej
    znal, odrz, stat = [], [], Counter()
    for r in rows:
        md = (ROOT / r["plik"]).read_text(encoding="utf-8")
        arts, hits = analiza(md)
        stat["ustaw"] += 1
        stat["artykulow"] += len(arts)
        if not hits:
            continue
        full = md.split("---", 2)[2]
        seen = set()
        for h in hits:
            k = (h["nr"], h["art_w"])
            if k in seen:
                continue
            seen.add(k)
            # druga kontrola w tym samym tekście: numer nie występuje jako nagłówek nigdzie (także w przypisach i cytatach)
            if re.search(r"Art\.\s*" + re.escape(h["nr"]) + r"\.", full):
                odrz.append({"eli": r["eli"], "art_w": h["art_w"], "nr": h["nr"], "cytat": h["cytat"],
                             "powod": "nagłówek artykułu występuje gdzie indziej w tekście (cytat lub przypis)"})
                continue
            znal.append((r, h, "kontrola całego tekstu ustawy"))
    out = []
    for i, (r, h, narz) in enumerate(znal, 1):
        out.append({
            "id": f"x003-{i:04d}", "eli": r["eli"], "kategoria": "wada",
            "przepisy": [f"art. {h['art_w']}"] if h["art_w"] else [],
            "cytaty": [h["cytat"]],
            "opis": f"Odesłanie do art. {h['nr']}, którego nie ma w tej ustawie.",
            "uzasadnienie": f"Reguła R1 (S010): odesłanie „art. {h['nr']}” bez wskazania innego aktu, a w ustawie nie ma artykułu "
                            f"{h['nr']}. Druga kontrola: nagłówek „Art. {h['nr']}.” nie występuje nigdzie w tekście ustawy (także w cytatach i przypisach). "
                            "Możliwe przyczyny: błąd w odesłaniu, odesłanie do innego aktu bez jego wskazania albo pozostałość po zmianie numeracji.",
            "waga": "srednia", "zrodla_wykrycia": ["reguła R1 (mechaniczna)"], "weryfikacja_krzyzowa": False,
        })
    stat["znalezisk"] = len(out)
    stat["ustaw_ze_znaleziskami"] = len({z["eli"] for z in out})
    stat["odrzuconych"] = len(odrz)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "kandydaci_skrypt.json").write_text(json.dumps({
        "id": "x003", "spec": "S010", "tytul": "Reguła R1: martwe odesłania wewnętrzne", "data": date.today().isoformat(),
        "zakres": f"ustawy uchwalone lub zmieniane od {OD} r.", "kandydaci": out}, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "odrzucone.json").write_text(json.dumps(odrz, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "statystyka.json").write_text(json.dumps(dict(stat), ensure_ascii=False, indent=1), encoding="utf-8")
    print(dict(stat))
    print("powody odrzucenia:", Counter(o["powod"].split(" — ")[0][:40] for o in odrz).most_common(5))
    return 0


if __name__ == "__main__":
    sys.exit(main())

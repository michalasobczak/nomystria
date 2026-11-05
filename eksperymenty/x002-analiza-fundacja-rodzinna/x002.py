#!/usr/bin/env python3
"""x002 (S006): eksperymentalna analiza jednej ustawy — ustawa o fundacji rodzinnej (DU/2023/326).

Źródła znalezisk:
- kontrole mechaniczne (bez AI): martwe odesłania wewnętrzne, delegacje ustawowe vs akty wykonawcze (API ELI);
- dwa niezależne przebiegi AI (A: Claude Opus, B: Claude Sonnet), które nie widziały swoich wyników
  (pliki wejściowe: --a, --b).
Scalanie: walidacja cytatów (S006 G1) i przepisów (G2), dopasowanie znalezisk A↔B (weryfikacja krzyżowa, G4).
Werdykt autora (G5) wpisuje autor w kontrole/x002/znaleziska.json (pole werdykt_autora).

Użycie: .venv/bin/python eksperymenty/x002-analiza-fundacja-rodzinna/x002.py --a A.json --b B.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ELI = "DU/2023/326"
PLIK = ROOT / "dane" / "ustawy" / "2023" / "2023-0326-o-fundacji-rodzinnej.md"
OUT = ROOT / "kontrole" / "x002"
API = "https://api.sejm.gov.pl/eli"
UA = "nomystria/1.0 (+https://github.com/michalasobczak/nomystria) x002"
KATEGORIE = {"sprzecznosc", "niespojnosc", "luka", "wada", "brak_sciezki_alternatywnej", "zaniechanie"}
ZEWN = re.compile(r"^.{0,90}?(ustawy z dnia|ustawie z dnia|ustawy –|ustawy -|Kodeksu|kodeksu|Ordynacji|rozporządzenia|"
                  r"ustawy o |dyrektywy|Prawa|prawa |k\.c\.|k\.p\.c\.)")


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace(" ", " ")).strip()


def body_text() -> tuple[str, list[str]]:
    t = PLIK.read_text(encoding="utf-8").split("---", 2)[2]
    t = t.split("\n## Przypisy", 1)[0]
    return t, [p for p in t.split("\n\n") if p.strip()]


def artykuly(paras: list[str]) -> tuple[dict[str, str], int]:
    """Artykuły ustawy (bez cytowanych przepisów innych ustaw) i indeks akapitu, od którego zaczynają się zmiany w innych ustawach."""
    arts, start_zmian = {}, len(paras)
    for i, p in enumerate(paras):
        m = re.match(r"^Art\. (\d+[a-z]*)\.\s*(.*)", p)
        if m:
            arts.setdefault(m.group(1), m.group(2))
            if re.match(r"W ustawie z dnia .* wprowadza się", m.group(2)) and start_zmian == len(paras):
                start_zmian = i
    return arts, start_zmian


def kontrole_mechaniczne(paras: list[str]) -> list[dict]:
    arts, start_zmian = artykuly(paras)
    out = []
    # M1: odesłania wewnętrzne do nieistniejących lub uchylonych artykułów (tylko przepisy merytoryczne)
    seen = set()
    for p in paras[:start_zmian]:
        if p.startswith("„"):
            continue
        for m in re.finditer(r"\bart\. (\d+[a-z]*)\b", p):
            tail = p[m.end():]
            if ZEWN.match(tail):
                continue  # odesłanie do innego aktu
            nr = m.group(1)
            ctx = p[max(0, m.start() - 60): m.end() + 60]
            if nr not in arts and (nr, "brak") not in seen:
                seen.add((nr, "brak"))
                out.append({"kategoria": "wada", "przepisy": [f"art. {nr}"], "cytaty": [norm(ctx)],
                            "opis": f"Odesłanie do art. {nr}, którego nie ma w ustawie.",
                            "uzasadnienie": "Kontrola mechaniczna: artykułu o tym numerze nie znaleziono w tekście ustawy. "
                                            "Może to być odesłanie do innego aktu bez wyraźnego wskazania albo martwe odesłanie.",
                            "waga": "srednia", "zrodla_wykrycia": ["kontrola mechaniczna M1"]})
            elif nr in arts and re.match(r"^\(uchylony\)", arts[nr]) and (nr, "uchyl") not in seen:
                seen.add((nr, "uchyl"))
                out.append({"kategoria": "wada", "przepisy": [f"art. {nr}"], "cytaty": [norm(ctx)],
                            "opis": f"Odesłanie do art. {nr}, który jest uchylony.",
                            "uzasadnienie": "Kontrola mechaniczna: przepis odsyła do jednostki oznaczonej jako uchylona.",
                            "waga": "srednia", "zrodla_wykrycia": ["kontrola mechaniczna M1"]})
    # M2: delegacje ustawowe vs akty wykonawcze w ISAP
    deleg = []
    for p in paras[:start_zmian]:
        if "w drodze rozporządzenia" in p or "w drodze rozporządzeń" in p:
            m = re.match(r"^(Art\. \d+[a-z]*\.)", p)
            deleg.append((m.group(1) if m else "", p))
    d = get_json(f"{API}/acts/{ELI}")
    wyk = [x["id"] for x in d.get("references", {}).get("Akty wykonawcze", [])]
    tytuly = {w: get_json(f"{API}/acts/{w}").get("title", "") for w in wyk}
    info = {"delegacje": [(a, norm(p)[:200]) for a, p in deleg], "akty_wykonawcze": tytuly, "liczba_artykulow": len(arts),
            "przepisy_zmieniajace_od_akapitu": start_zmian}
    if len(deleg) > len(wyk):
        out.append({"kategoria": "zaniechanie", "przepisy": [a for a, _ in deleg if a] or ["—"],
                    "cytaty": [norm(deleg[0][1])[:250]],
                    "opis": f"Ustawa zawiera {len(deleg)} upoważnień do wydania rozporządzenia, a ISAP wskazuje {len(wyk)} aktów wykonawczych.",
                    "uzasadnienie": "Kontrola mechaniczna: liczba delegacji przekracza liczbę aktów wykonawczych powiązanych w ISAP. "
                                    "Wymaga ręcznego dopasowania, czy każda delegacja została wykonana.",
                    "waga": "niska", "zrodla_wykrycia": ["kontrola mechaniczna M2"]})
    return out, info


def waliduj(f: dict, text_norm: str, arts: dict) -> list[str]:
    bledy = []
    if f.get("kategoria") not in KATEGORIE:
        bledy.append(f"kategoria {f.get('kategoria')!r}")
    cyt = f.get("cytaty") or []
    if not cyt:
        bledy.append("brak cytatu")
    for c in cyt:
        if norm(c).strip("„”\"' ") not in text_norm:
            bledy.append(f"cytat nie występuje dosłownie: {c[:80]!r}")
    for p in f.get("przepisy") or []:
        m = re.match(r"art\. (\d+[a-z]*)", p.strip(), re.I)
        if m and m.group(1) not in arts:
            bledy.append(f"przepis {p!r} nie istnieje")
    return bledy


def units_of(f):
    """{'85', '91.3', …}: artykuł i ustęp (punkty pomijamy — przebiegi różnie je rozdrabniają)."""
    out = set()
    for p in f.get("przepisy") or []:
        m = re.match(r"art\. (\d+[a-z]*)(?: ust\. (\d+[a-z]*))?", p.strip(), re.I)
        if m:
            out.add(m.group(1) + ("." + m.group(2) if m.group(2) else ""))
    return out


def arts_of(f):
    return {m.group(1) for p in f.get("przepisy") or [] for m in [re.match(r"art\. (\d+[a-z]*)", p.strip(), re.I)] if m}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    args = ap.parse_args()
    text, paras = body_text()
    text_norm = norm(text)
    arts, _ = artykuly(paras)
    mech, info = kontrole_mechaniczne(paras)

    przebiegi = {}
    for tag, path in (("A", args.a), ("B", args.b)):
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
        przebiegi[tag] = (doc.get("narzedzie", tag), doc.get("znaleziska", []))

    wszystkie, odrzucone = [], []
    for tag, (narz, items) in przebiegi.items():
        for f in items:
            f = dict(f)
            f["zrodla_wykrycia"] = [narz]
            f["_tag"] = tag
            bl = waliduj(f, text_norm, arts)
            (odrzucone if bl else wszystkie).append({**f, "_bledy": bl} if bl else f)
    for f in mech:
        f["_tag"] = "M"
        bl = waliduj(f, text_norm, arts)
        (odrzucone if bl else wszystkie).append({**f, "_bledy": bl} if bl else f)

    # Dopasowanie A↔B: podobieństwo zbiorów jednostek (art. + ust.) — Jaccard + premia za tę samą kategorię.
    # Jedno znalezisko A może zebrać kilka znalezisk B (B bywa bardziej rozdrobnione), próg 0.4.
    a = [f for f in wszystkie if f["_tag"] == "A"]
    b = [f for f in wszystkie if f["_tag"] == "B"]
    for fa in a:
        fa["_b"] = []
    reszta_b = []
    for fb in b:
        best, best_s = None, 0.0
        for fa in a:
            ua, ub = units_of(fa), units_of(fb)
            if not ua or not ub:
                continue
            sc = len(ua & ub) / len(ua | ub) + (0.2 if fa["kategoria"] == fb["kategoria"] else 0)
            if sc > best_s:
                best, best_s = fa, sc
        if best is not None and best_s >= 0.4:
            best["_b"].append(fb)
        else:
            reszta_b.append(fb)
    scalone = []
    for fa in a:
        if fa["_b"]:
            bs = fa["_b"]
            fa = dict(fa, zrodla_wykrycia=fa["zrodla_wykrycia"] + bs[0]["zrodla_wykrycia"], weryfikacja_krzyzowa=True,
                      opis_drugiego_przebiegu=" | ".join(x["opis"] for x in bs),
                      kategoria_drugiego_przebiegu=", ".join(dict.fromkeys(x["kategoria"] for x in bs)),
                      cytaty=list(dict.fromkeys(fa["cytaty"] + [c for x in bs for c in x["cytaty"]])))
        else:
            fa = dict(fa, weryfikacja_krzyzowa=False)
        scalone.append(fa)
    scalone += [dict(fb, weryfikacja_krzyzowa=False) for fb in reszta_b]
    scalone += [dict(f, weryfikacja_krzyzowa=False) for f in wszystkie if f["_tag"] == "M"]

    znal = []
    for i, f in enumerate(sorted(scalone, key=lambda f: (not f["weryfikacja_krzyzowa"], {"wysoka": 0, "srednia": 1, "niska": 2}.get(f.get("waga"), 3))), 1):
        rec = {"id": f"x002-{i:03d}", "eli": ELI, "kategoria": f["kategoria"], "przepisy": f.get("przepisy", []),
               "cytaty": f["cytaty"], "opis": f.get("opis", ""), "uzasadnienie": f.get("uzasadnienie", ""),
               "waga": f.get("waga", ""), "zrodla_wykrycia": f["zrodla_wykrycia"],
               "weryfikacja_krzyzowa": f["weryfikacja_krzyzowa"], "werdykt_autora": "brak", "komentarz_autora": ""}
        if f.get("opis_drugiego_przebiegu"):
            rec["opis_drugiego_przebiegu"] = f["opis_drugiego_przebiegu"]
            rec["kategoria_drugiego_przebiegu"] = f["kategoria_drugiego_przebiegu"]
        znal.append(rec)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "znaleziska.json").write_text(json.dumps({
        "id": "x002", "spec": "S006", "tytul": "Analiza ustawy o fundacji rodzinnej (DU/2023/326)",
        "data": date.today().isoformat(), "plik_ustawy": str(PLIK.relative_to(ROOT)),
        "przebiegi": {k: v[0] for k, v in przebiegi.items()}, "znaleziska": znal}, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "odrzucone.json").write_text(json.dumps([{k: v for k, v in f.items() if k != "_tag"} | {"przebieg": f["_tag"]} for f in odrzucone],
                                                   ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "kontrole_mechaniczne.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    from collections import Counter
    print("przyjęte:", len(znal), Counter(f["kategoria"] for f in znal))
    print("krzyżowo potwierdzone:", sum(f["weryfikacja_krzyzowa"] for f in znal))
    print("odrzucone:", len(odrzucone), Counter(f["_tag"] for f in odrzucone))
    print("delegacje:", len(info["delegacje"]), "akty wykonawcze:", len(info["akty_wykonawcze"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

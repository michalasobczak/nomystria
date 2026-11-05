#!/usr/bin/env python3
"""x005 (S012), etap 1: kandydaci reguły R3 — ślubowanie składane wobec wskazanego podmiotu.

Dla każdej ustawy, w której zdanie o ślubowaniu wskazuje podmiot przyjmujący, zapisuje wyciąg przepisów
(akapity ze słowem „ślubowani” z numerem artykułu) i sygnały pomocnicze dla modelu (etap 2).
Wyłącznie wersja tekstowa korpusu (Markdown).

Użycie: .venv/bin/python eksperymenty/x005-slubowanie/x005.py
Wynik: kontrole/x005/kandydaci.json
"""

from __future__ import annotations

import csv
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "kontrole" / "x005"

ZDANIA = re.compile(r"(?<=[;:])\s+|(?<=[a-ząćęłńóśźż]{4}\.)\s+(?=[A-ZĄĆĘŁŃÓŚŹŻ])")
CZAS = r"(?!przystąpieniem|objęciem|podjęciem|rozpoczęciem|złożeniem|upływem|dniem|wydaniem|powołaniem|mianowaniem)"
PRZYJMUJACY = re.compile(
    r"(?:wobec|na ręce|przed\s+" + CZAS + r")\s*([A-ZĄĆĘŁŃÓŚŹŻ][^,.;:„]{2,70}|(?:ministr|prezes|marszał|komendant|dyrektor|rad[ąy]|"
    r"kierownik|przewodnicząc|wojewod|starost|komisarz|sejm|senat|zgromadzen)[^,.;:„]{2,70})"
    r"|(odbiera|przyjmuje|odebrania|przyjęcia)\s+(?:\w+\s+){0,3}ślubowani\w*", re.I)
NOWELIZACJA = re.compile(r"otrzymuje brzmienie|dodaje się|wprowadza się|skreśla się|zastępuje się")
# sygnały pomocnicze (model weryfikuje sam)
ZALEZNOSC = re.compile(r"któr[ay] złożył[ay]? ślubowani|z chwilą złożenia\s+(?:\w+\s+){0,3}ślubowani|od dnia złożenia ślubowani|"
                       r"powstaje[^.;]{0,60}(?:po )?złożeni\w* ślubowani|złożenia ślubowania\.|złożył[ay]? ślubowanie\.|"
                       r"poprzedza złożenie[^.;]{0,80}ślubowani|przed przystąpieniem do wykonywania mandatu[^.;]{0,60}ślubowani|"
                       r"po złożeniu ślubowani|przed przystąpieniem[^.;]{0,80}składa\s+(?:\w+\s+){0,3}ślubowani|"
                       r"przed objęciem[^.;]{0,80}ślubowani|przed rozpoczęciem[^.;]{0,80}ślubowani", re.I)
ODMOWA_OSOBY = re.compile(r"(odmow\w*|uchyl\w* się od)\s+(?:\w+\s+){0,2}złożenia\s+ślubowani|niezłożeni\w*\s+ślubowani", re.I)


def wyciag(md: str) -> tuple[list[dict], list[str]]:
    body = md.split("---", 2)[2].split("\n## Przypisy", 1)[0]
    akapity, przyjmujacy, art = [], [], None
    for p in body.split("\n\n"):
        p = p.strip()
        m = re.match(r"^(?:\*\*)?Art\. (\d+[a-z]{0,3})\.", p)
        if m and not p.startswith("„"):
            art = m.group(1)
        if "ślubowani" not in p or p.startswith("„") or NOWELIZACJA.search(p):
            continue
        akapity.append({"art": art, "tekst": p})
        for z in ZDANIA.split(p):
            if "ślubowani" in z:
                for mm in PRZYJMUJACY.finditer(z):
                    przyjmujacy.append(re.sub(r"\s+", " ", (mm.group(1) or mm.group(0))).strip()[:80])
    # akapit rozdzielony przy konwersji („… wobec” | „Prezydenta … ślubowanie”) — dołącz poprzedni akapit
    paras = [p.strip() for p in body.split("\n\n")]
    for i, p in enumerate(paras):
        if "ślubowani" in p and i and not re.match(r"^(?:\*\*)?Art\.|^\d+[a-z]?\.|^§", p) and re.search(r"(wobec|przed|na ręce)\s*$", paras[i - 1]):
            akapity.append({"art": None, "tekst": paras[i - 1] + " " + p})
            przyjmujacy.append(re.sub(r"\s+", " ", p[:60]))
    return akapity, przyjmujacy


def main() -> int:
    with open(ROOT / "dane" / "indeks.csv", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    kand = []
    for r in rows:
        md = (ROOT / r["plik"]).read_text(encoding="utf-8")
        if "ślubowani" not in md:
            continue
        akapity, przyjm = wyciag(md)
        md_body = md.split("---", 2)[2]
        # kandydat: wskazany przyjmujący ALBO ślubowanie jako warunek statusu (także gdy przyjmujący jest w innym akapicie)
        zal = bool(ZALEZNOSC.search(re.sub(r"\s+", " ", md_body)))
        if not przyjm and not zal:
            continue
        tekst = "\n".join(a["tekst"] for a in akapity)
        kand.append({
            "eli": r["eli"], "tytul": r["tytul"], "plik": r["plik"], "brzmienie": r["brzmienie"],
            "przyjmujacy_skrypt": sorted(set(przyjm)),
            "sygnal_zaleznosc": zal,
            "sygnal_odmowa_osoby": bool(ODMOWA_OSOBY.search(tekst)),
            "wyciag": akapity,
        })
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "kandydaci.json").write_text(json.dumps({"id": "x005", "spec": "S012", "etap": "1 (skrypt)",
                                                    "data": date.today().isoformat(), "kandydaci": kand},
                                                   ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(kand), "kandydatów;", sum(k["sygnal_zaleznosc"] for k in kand), "z sygnałem zależności;",
          sum(k["sygnal_odmowa_osoby"] for k in kand), "z regulacją odmowy osoby")
    for k in kand:
        print(f"  {k['eli']:13} {len(k['wyciag']):2} ak. | {k['tytul'][:70]} | {k['przyjmujacy_skrypt'][:2]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

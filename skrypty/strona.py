#!/usr/bin/env python3
"""S007: generuje dane strony (dane.json) z dane/indeks.csv i wyników kontroli w kontrole/.

Użycie:
    python skrypty/strona.py                    # zapisuje strona/dane.json (podgląd lokalny)
    python skrypty/strona.py --out _site/dane.json
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO_URL = "https://github.com/michalasobczak/nomystria"

WERDYKTY = ("zgodny", "rozbiezny", "niezweryfikowany")
# Najgorszy werdykt decyduje o statusie ustawy.
PRIORYTET = {"rozbiezny": 3, "niezweryfikowany": 2, "zgodny": 1}
KATEGORIE = ("sprzecznosc", "niespojnosc", "luka", "wada", "brak_sciezki_alternatywnej", "zaniechanie")
BRZMIENIE = {"ujednolicone": "U", "jednolite": "J", "pierwotne": "P", "pierwotne (zmieniana)": "PZ"}


class BladKontroli(ValueError):
    pass


def _int(v):
    return int(v) if str(v).strip().lstrip("-").isdigit() else None


def load_kontrole(kontrole_dir: Path, known: set[str]) -> tuple[list[dict], dict[str, list], dict[str, list]]:
    """Zwraca (lista kontroli, wyniki wg eli, znaleziska wg eli). Waliduje format."""
    meta, wyniki, znaleziska = [], {}, {}  # ścieżki plików względem katalogu repozytorium
    if not kontrole_dir.exists():
        return meta, wyniki, znaleziska
    for d in sorted(p for p in kontrole_dir.iterdir() if p.is_dir()):
        for name, key in (("wyniki.json", "wyniki"), ("znaleziska.json", "znaleziska")):
            f = d / name
            if not f.exists():
                continue
            doc = json.loads(f.read_text(encoding="utf-8"))
            kid = doc.get("id") or d.name
            meta.append({"id": kid, "spec": doc.get("spec", ""), "tytul": doc.get("tytul", ""), "data": doc.get("data", ""),
                         "rodzaj": key, "liczba": len(doc.get(key, [])), "plik": f.relative_to(kontrole_dir.parent).as_posix()})
            for i, item in enumerate(doc.get(key, [])):
                where = f"{f.relative_to(kontrole_dir.parent)}[{i}]"
                eli = item.get("eli")
                if eli not in known:
                    raise BladKontroli(f"{where}: nieznane eli {eli!r}")
                if key == "wyniki":
                    if item.get("werdykt") not in WERDYKTY:
                        raise BladKontroli(f"{where}: werdykt {item.get('werdykt')!r} spoza {WERDYKTY}")
                    wyniki.setdefault(eli, []).append({"k": kid, **{x: item.get(x, "") for x in (
                        "parametr", "wartosc_zbior", "wartosc_zrodlo", "zrodlo", "werdykt", "wyjasnienie")}})
                else:
                    if item.get("kategoria") not in KATEGORIE:
                        raise BladKontroli(f"{where}: kategoria {item.get('kategoria')!r} spoza {KATEGORIE}")
                    znaleziska.setdefault(eli, []).append({"k": kid, **{x: item.get(x) for x in (
                        "id", "kategoria", "przepisy", "cytaty", "opis", "uzasadnienie", "waga",
                        "zrodla_wykrycia", "weryfikacja_krzyzowa")}})
    return meta, wyniki, znaleziska


def diagramy(root: Path = ROOT) -> dict[str, Path]:
    """Diagramy ścieżek: kontrole/<eksperyment>/sciezki/<id znaleziska>.json."""
    return {f.stem: f for f in sorted((root / "kontrole").glob("*/sciezki/*.json"))}


def status_kontroli(items: list[dict] | None) -> str:
    """'brak' gdy ustawy nie kontrolowano — nigdy 'zgodny' z braku danych (S007 G5)."""
    if not items:
        return "brak"
    return max((i["werdykt"] for i in items), key=PRIORYTET.__getitem__)


def build(root: Path = ROOT) -> dict:
    with open(root / "dane" / "indeks.csv", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    known = {r["eli"] for r in rows}
    meta, wyniki, znaleziska = load_kontrole(root / "kontrole", known)
    diag = diagramy(root)
    for lista in znaleziska.values():
        for z in lista:
            if z.get("id") in diag:
                z["diagram"] = z["id"]
    ustawy = []
    for r in rows:
        w, z = wyniki.get(r["eli"]), znaleziska.get(r["eli"])
        ustawy.append({
            "eli": r["eli"],
            "tytul": r["tytul"],
            "rok": _int(r["rok"]),
            "poz": _int(r["pozycja"]),
            "data": r["data_aktu"],  # data uchwalenia (RRRR-MM-DD); domyślne sortowanie strony
            "adres": r["adres_publikacyjny"],
            "status": r["status"],
            "br": BRZMIENIE.get(r["brzmienie"], r["brzmienie"]),
            "zmian": _int(r["liczba_ustaw_zmieniajacych"]),
            "tj": r["tekst_jednolity"],
            "tjData": r["tekst_jednolity_z_dnia"],
            "poTj": _int(r["zmian_po_tekscie_jednolitym"]),
            "tu": r["tekst_ujednolicony_z_dnia"],
            "podstawa": r["opracowano_na_podstawie"],
            "zrodloTekstu": r.get("zrodlo_tekstu", ""),
            "uwagi": r.get("uwagi", ""),
            "wejscie": r["data_wejscia_w_zycie"],
            "plik": f"{REPO_URL}/blob/main/{r['plik']}",
            "pdf": r["zrodlo_pdf"],
            "isap": r["isap"],
            "kontrola": status_kontroli(w),
            "wyniki": w or [],
            "znaleziska": z or [],
        })
    return {"wygenerowano_z": "dane/indeks.csv + kontrole/", "kontrole": meta, "ustawy": ustawy}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "strona" / "dane.json"))
    args = ap.parse_args()
    try:
        data = build()
    except BladKontroli as e:
        print(f"BŁĄD kontroli: {e}", file=sys.stderr)
        return 1
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    # diagramy ścieżek obok dane.json (strona/sciezki.html czyta sciezki/<id>.json)
    for zid, f in diagramy().items():
        dst = out.parent / "sciezki" / f"{zid}.json"
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"{out}: {len(data['ustawy'])} ustaw, {len(data['kontrole'])} plików kontroli, {out.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())

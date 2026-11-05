"""Metadane o zmianach i tekstach jednolitych oraz tabela dane/LISTA.md."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable


def _key(eli: str) -> tuple[int, int]:
    _, year, pos = eli.split("/")
    return int(year), int(pos)


def latest_tj(act: dict) -> str | None:
    """ELI ostatniego obwieszczenia tekstu jednolitego (pozycje Dz. U. rosną chronologicznie)."""
    refs = act.get("references", {}).get("Inf. o tekście jednolitym", [])
    ids = [r["id"] for r in refs if r.get("id", "").startswith("DU/")]
    return max(ids, key=_key) if ids else None


def amendments(act: dict) -> list[str]:
    refs = act.get("references", {}).get("Akty zmieniające", [])
    return sorted({r["id"] for r in refs if r.get("id", "").startswith("DU/")}, key=_key)


def fetch_tj_meta(acts: list[dict], cache_file: Path, get: Callable[[str], bytes], api: str) -> dict[str, dict]:
    """Daty obwieszczeń tekstów jednolitych; obwieszczenia się nie zmieniają, więc trzymamy je w cache."""
    cache = json.loads(cache_file.read_text()) if cache_file.exists() else {}
    need = sorted({t for a in acts if (t := latest_tj(a)) and t not in cache})

    def one(eli):
        d = json.loads(get(f"{api}/acts/{eli}"))
        return eli, {
            "adres": d.get("displayAddress"),
            "data_obwieszczenia": d.get("announcementDate"),
            "data_ogloszenia": d.get("promulgation"),
        }

    with ThreadPoolExecutor(6) as ex:
        for eli, meta in ex.map(one, need):
            cache[eli] = meta
    cache_file.write_text(json.dumps(cache, ensure_ascii=False, indent=0))
    return cache


def change_info(act: dict, tj_meta: dict[str, dict]) -> dict:
    zm = amendments(act)
    tj = latest_tj(act)
    meta = tj_meta.get(tj, {}) if tj else {}
    after = [z for z in zm if tj and _key(z) > _key(tj)]
    return {
        "liczba_ustaw_zmieniajacych": len(zm),
        "tekst_jednolity": meta.get("adres") or "",
        "tekst_jednolity_eli": tj or "",
        "tekst_jednolity_z_dnia": meta.get("data_obwieszczenia") or "",
        "tekst_jednolity_ogloszony": meta.get("data_ogloszenia") or "",
        "zmian_po_tekscie_jednolitym": len(after) if tj else "",
    }


def _md_cell(v) -> str:
    return str(v if v not in (None, "") else "—").replace("|", "\\|")


START, END = "<!-- LISTA:START -->", "<!-- LISTA:END -->"


def render_list(rows: list[dict]) -> str:
    """Tabela Markdown wszystkich ustaw (rows — wiersze indeksu, ścieżki względem korzenia repo)."""
    uj = sum(r["brzmienie"] == "ujednolicone" for r in rows)
    zm = sum(r["brzmienie"] == "pierwotne (zmieniana)" for r in rows)
    lines = [
        f"Aktów w zbiorze: **{len(rows)}**, w tym Konstytucja. W brzmieniu ujednoliconym: {uj}. "
        f"W brzmieniu pierwotnym: {len(rows) - uj}, w tym {zm} zmienianych bez tekstu ujednoliconego.",
        "",
        "- **Zmian** to liczba ustaw zmieniających według ISAP („Akty zmieniające”).",
        "- **Tekst jednolity** to ostatnie obwieszczenie tekstu jednolitego w Dz. U. z datą obwieszczenia.",
        "- **Zmian po t.j.** to ustawy zmieniające ogłoszone po tym tekście jednolitym. "
        "Ich treść jest w tekście ujednoliconym, ale nie w jednolitym.",
        "- **Tekst ujednolicony z dnia** to data, na którą Kancelaria Sejmu opracowała tekst ujednolicony.",
        "",
        "| Lp. | Ustawa | Dz. U. | Brzmienie | Zmian | Tekst jednolity | Zmian po t.j. | Tekst ujednolicony z dnia |",
        "| ---: | --- | --- | --- | ---: | --- | ---: | --- |",
    ]
    for i, r in enumerate(rows, 1):
        tj = f"{r['tekst_jednolity']} ({r['tekst_jednolity_z_dnia']})" if r["tekst_jednolity"] else ""
        cells = [
            str(i),
            f"[{_md_cell(r['tytul'])}]({r['plik']})",
            _md_cell(r["adres_publikacyjny"]),
            _md_cell(r["brzmienie"]),
            _md_cell(r["liczba_ustaw_zmieniajacych"]),
            _md_cell(tj),
            _md_cell(r["zmian_po_tekscie_jednolitym"]),
            _md_cell(r["tekst_ujednolicony_z_dnia"]),
        ]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def update_readme(rows: list[dict], readme: Path) -> None:
    """Wstawia tabelę między znaczniki LISTA:START / LISTA:END w README."""
    text = readme.read_text(encoding="utf-8")
    if START not in text or END not in text:
        text = text.rstrip() + f"\n\n## Lista ustaw\n\n{START}\n{END}\n"
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    readme.write_text(f"{head}{START}\n{render_list(rows)}\n{END}{tail}", encoding="utf-8")


if __name__ == "__main__":
    # Odświeżenie tabeli w README z dane/indeks.csv bez ponownej konwersji.
    import csv

    root = Path(__file__).resolve().parent.parent
    with open(root / "dane" / "indeks.csv", encoding="utf-8") as fh:
        update_readme(list(csv.DictReader(fh)), root / "README.md")

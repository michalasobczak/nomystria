"""S007 G1, G2, G5, G6: generator danych strony i obecność ostrzeżenia."""

import csv
import json
import tempfile
import unittest
from pathlib import Path

from _wspolne import ROOT, indeks
from strona import BladKontroli, build, status_kontroli


def _mini_root(tmp: Path, kontrole: dict[str, dict]) -> Path:
    """Repozytorium testowe: 3 pierwsze wiersze prawdziwego indeksu + podane pliki kontroli."""
    (tmp / "dane").mkdir()
    rows = indeks()[:3]
    with open(tmp / "dane" / "indeks.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    for rel, doc in kontrole.items():
        p = tmp / "kontrole" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    return tmp


class TestGenerator(unittest.TestCase):
    def test_g1_kompletnosc(self):
        data = build(ROOT)
        self.assertEqual(len(data["ustawy"]), len(indeks()))
        self.assertEqual({u["eli"] for u in data["ustawy"]}, {r["eli"] for r in indeks()})

    def test_g2_kontrole_trafiaja_do_ustawy(self):
        eli = indeks()[1]["eli"]
        with tempfile.TemporaryDirectory() as t:
            root = _mini_root(Path(t), {
                "x001/wyniki.json": {"id": "x001", "spec": "S005", "wyniki": [
                    {"eli": eli, "parametr": "brzmienie", "werdykt": "zgodny"},
                    {"eli": eli, "parametr": "liczba_ustaw_zmieniajacych", "werdykt": "rozbiezny", "wyjasnienie": "test"},
                ]},
                "x002/znaleziska.json": {"id": "x002", "spec": "S006", "znaleziska": [
                    {"id": "x002-001", "eli": eli, "kategoria": "luka", "cytaty": ["…"], "werdykt_autora": "potwierdzone"},
                ]},
            })
            data = build(root)
        u = {x["eli"]: x for x in data["ustawy"]}
        self.assertEqual(u[eli]["kontrola"], "rozbiezny")  # najgorszy werdykt
        self.assertEqual(len(u[eli]["wyniki"]), 2)
        self.assertEqual(u[eli]["znaleziska"][0]["kategoria"], "luka")
        self.assertEqual(len(data["kontrole"]), 2)

    def test_g2_nieznane_eli_przerywa(self):
        with tempfile.TemporaryDirectory() as t:
            root = _mini_root(Path(t), {"x001/wyniki.json": {"wyniki": [{"eli": "DU/1800/1", "werdykt": "zgodny"}]}})
            with self.assertRaises(BladKontroli):
                build(root)

    def test_zle_wartosci_przerywaja(self):
        eli = indeks()[0]["eli"]
        for doc in (
            {"x/wyniki.json": {"wyniki": [{"eli": eli, "werdykt": "ok"}]}},
            {"x/znaleziska.json": {"znaleziska": [{"eli": eli, "kategoria": "inne"}]}},
        ):
            with tempfile.TemporaryDirectory() as t, self.assertRaises(BladKontroli):
                build(_mini_root(Path(t), doc))

    def test_g5_brak_kontroli_to_nie_zgodnosc(self):
        self.assertEqual(status_kontroli(None), "brak")
        self.assertEqual(status_kontroli([]), "brak")
        with tempfile.TemporaryDirectory() as t:
            data = build(_mini_root(Path(t), {}))
        self.assertTrue(all(u["kontrola"] == "brak" for u in data["ustawy"]))


class TestStrona(unittest.TestCase):
    def test_g6_ostrzezenie_i_autor(self):
        html = (ROOT / "strona" / "index.html").read_text(encoding="utf-8")
        self.assertIn("To projekt eksploracyjny.", html)
        self.assertIn("Nie jest to źródło prawa", html)
        self.assertIn("https://michalasobczak.pl", html)

    def test_strona_czyta_dane_json(self):
        js = (ROOT / "strona" / "app.js").read_text(encoding="utf-8")
        self.assertIn('fetch("dane.json")', js)


if __name__ == "__main__":
    unittest.main()

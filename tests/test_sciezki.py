"""Diagramy ścieżek (kontrole/*/sciezki/*.json): cytaty dosłowne, poprawna struktura, każda ścieżka kończy się wynikiem."""

import json
import re
import unittest

from _wspolne import ROOT, DATA

PLIKI = sorted((ROOT / "kontrole").glob("*/sciezki/*.json"))
WYNIKI = {"ok", "luka", "statut"}


def _norm(s):
    return re.sub(r"\s+", " ", s.replace(" ", " ")).strip()


class TestSciezki(unittest.TestCase):
    def test_sa_diagramy(self):
        self.assertTrue(PLIKI)

    def test_struktura_i_cytaty(self):
        for f in PLIKI:
            d = json.loads(f.read_text(encoding="utf-8"))
            w = d["wezly"]
            plik = next(p for p in (DATA / "ustawy").rglob("*.md")
                        if f'\neli: "{d["eli"]}"\n' in p.read_text(encoding="utf-8")[:2000])
            tekst = _norm(plik.read_text(encoding="utf-8").split("---", 2)[2])
            arts = set(re.findall(r"(?m)^Art\. (\d+[a-z]*)\.", plik.read_text(encoding="utf-8")))
            self.assertIn(d["start"], w)
            for k, n in w.items():
                self.assertIn(n["typ"], {"pytanie", "krok", "wynik"}, k)
                self.assertTrue(n["cytaty"], f"{f.name}:{k} bez cytatu")
                for c in n["cytaty"]:
                    self.assertIn(_norm(c), tekst, f"{f.name}:{k}: {c[:60]}")
                for p in n.get("przepisy", []):
                    m = re.match(r"art\. (\d+[a-z]*)", p)
                    self.assertTrue(m and m.group(1) in arts, f"{f.name}:{k}: {p}")
                if n["typ"] == "wynik":
                    self.assertIn(n["wynik"], WYNIKI, k)
                    self.assertFalse(n.get("odpowiedzi") or n.get("dalej"), k)
                elif n["typ"] == "pytanie":
                    self.assertGreaterEqual(len(n["odpowiedzi"]), 2, k)
                    for o in n["odpowiedzi"]:
                        self.assertIn(o["do"], w, f"{k} → {o['do']}")
                else:
                    self.assertIn(n["dalej"], w, k)
            # osiągalność i brak cykli: każdy węzeł ma najwyżej jednego rodzica i jest osiągalny ze startu
            seen, stack, parents = set(), [d["start"]], {}
            while stack:
                k = stack.pop()
                self.assertNotIn(k, seen, f"cykl lub wspólny węzeł: {k}")
                seen.add(k)
                n = w[k]
                for c in [o["do"] for o in n.get("odpowiedzi", [])] + ([n["dalej"]] if n.get("dalej") else []):
                    parents.setdefault(c, []).append(k)
                    stack.append(c)
            self.assertEqual(seen, set(w), f"{f.name}: nieosiągalne węzły {set(w) - seen}")

    def test_diagram_ma_znalezisko(self):
        for f in PLIKI:
            zn = json.loads((f.parent.parent / "znaleziska.json").read_text(encoding="utf-8"))
            self.assertIn(f.stem, {z["id"] for z in zn["znaleziska"]})


if __name__ == "__main__":
    unittest.main()

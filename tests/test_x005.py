"""S012 (R3): ślubowanie — kompletność ocen, cytaty dosłowne, wzorzec gminy, znaleziska = werdykty brak_sciezki."""

import json
import re
import unittest

from _wspolne import ROOT, wiersz

X = ROOT / "kontrole" / "x005"


def _n(s):
    return re.sub(r"\s+", " ", (s or "").replace(" ", " ")).strip().strip("„”\"")


@unittest.skipUnless((X / "znaleziska.json").exists(), "brak kontrole/x005")
class TestX005(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kand = json.loads((X / "kandydaci.json").read_text(encoding="utf-8"))["kandydaci"]
        cls.oceny = json.loads((X / "oceny_llm.json").read_text(encoding="utf-8"))["oceny"]
        cls.zn = json.loads((X / "znaleziska.json").read_text(encoding="utf-8"))["znaleziska"]

    def test_g1_kazdy_kandydat_ma_werdykt(self):
        self.assertEqual({k["eli"] for k in self.kand}, {o["eli"] for o in self.oceny})

    def test_g2_cytaty_doslowne(self):
        for o in self.oceny:
            plik = o.get("plik_cytatow") or wiersz(o["eli"])["plik"]
            t = _n((ROOT / plik).read_text(encoding="utf-8"))
            for f in ("cytat_zaleznosc", "cytat_odmowa", "cytat_ratunek"):
                if o.get(f):
                    self.assertIn(_n(o[f]), t, f"{o['eli']} {f}")

    def test_g3_wzorzec_gminy(self):
        self.assertEqual(next(o for o in self.oceny if o["eli"] == "DU/1990/95")["werdykt"], "sciezka_istnieje")

    def test_znaleziska_odpowiadaja_werdyktom(self):
        self.assertEqual({z["eli"] for z in self.zn}, {o["eli"] for o in self.oceny if o["werdykt"] == "brak_sciezki"})
        for z in self.zn:
            self.assertEqual(z["kategoria"], "brak_sciezki_alternatywnej")
            self.assertIn(z["waga"], {"wysoka", "srednia", "niska"})

    def test_tk_waga_wysoka(self):
        tk = {z["eli"]: z["waga"] for z in self.zn if z["eli"] in {"DU/2016/2072", "DU/2016/2073", "DU/2016/2074"}}
        self.assertEqual(set(tk.values()), {"wysoka"})


if __name__ == "__main__":
    unittest.main()

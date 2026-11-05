"""S006 G1–G3 (x002) i spójność plików kontroli w kontrole/."""

import json
import re
import unittest

from _wspolne import ROOT

X002 = ROOT / "kontrole" / "x002" / "znaleziska.json"


def _norm(s):
    return re.sub(r"\s+", " ", s.replace(" ", " ")).strip()


@unittest.skipUnless(X002.exists(), "brak kontrole/x002")
class TestX002(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(X002.read_text(encoding="utf-8"))
        tekst = (ROOT / cls.doc["plik_ustawy"]).read_text(encoding="utf-8").split("---", 2)[2]
        cls.tekst = _norm(tekst)
        cls.arts = set(re.findall(r"(?m)^Art\. (\d+[a-z]*)\.", tekst))

    def test_g1_cytaty_doslowne(self):
        for z in self.doc["znaleziska"]:
            self.assertTrue(z["cytaty"], z["id"])
            for c in z["cytaty"]:
                self.assertIn(_norm(c).strip("„”\"' "), self.tekst, f"{z['id']}: {c[:60]}")

    def test_g2_przepisy_istnieja(self):
        for z in self.doc["znaleziska"]:
            for p in z["przepisy"]:
                m = re.match(r"art\. (\d+[a-z]*)", p, re.I)
                if m:
                    self.assertIn(m.group(1), self.arts, f"{z['id']}: {p}")

    def test_g3_g4_pola(self):
        kat = {"sprzecznosc", "niespojnosc", "luka", "wada", "brak_sciezki_alternatywnej", "zaniechanie"}
        for z in self.doc["znaleziska"]:
            self.assertIn(z["kategoria"], kat)
            self.assertIsInstance(z["weryfikacja_krzyzowa"], bool)
            self.assertIn(z["werdykt_autora"], {"potwierdzone", "odrzucone", "do_dyskusji", "brak"})
            if z["weryfikacja_krzyzowa"]:
                self.assertGreaterEqual(len(z["zrodla_wykrycia"]), 2, z["id"])


if __name__ == "__main__":
    unittest.main()

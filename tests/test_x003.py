"""S010: znaleziska R1 (x003) — cytaty dosłowne, przepisy istnieją, odesłany artykuł naprawdę nie istnieje."""

import json
import re
import unittest

from _wspolne import ROOT, wiersz

X = ROOT / "kontrole" / "x003"


def _norm(s):
    return re.sub(r"\s+", " ", s.replace(" ", " ")).strip()


@unittest.skipUnless((X / "znaleziska.json").exists(), "brak kontrole/x003")
class TestX003(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.zn = json.loads((X / "znaleziska.json").read_text(encoding="utf-8"))["znaleziska"]
        cls.oceny = json.loads((X / "oceny_llm.json").read_text(encoding="utf-8"))["oceny"]

    def tekst(self, eli):
        return (ROOT / wiersz(eli)["plik"]).read_text(encoding="utf-8")

    def test_g2_cytaty_doslowne(self):
        for z in self.zn:
            t = _norm(self.tekst(z["eli"]))
            for c in z["cytaty"]:
                self.assertIn(_norm(c), t, z["id"])
        for o in self.oceny:
            self.assertIn(_norm(o["cytat"]), _norm(self.tekst(o["eli"])), f"{o['eli']} art. {o['nr']}")

    def test_odeslany_artykul_nie_istnieje(self):
        for z in self.zn:
            nr = re.search(r"art\. (\S+?),", z["opis"]).group(1)
            self.assertIsNone(re.search(r"(?m)^(?:\*\*)?„?Art\.\s*" + re.escape(nr) + r"\.", self.tekst(z["eli"])), z["id"])

    def test_znaleziska_tylko_z_werdyktu_modelu(self):
        martwe = {(o["eli"], o["nr"]) for o in self.oceny if o["werdykt"] == "martwe_odeslanie"}
        self.assertEqual({(z["eli"], re.search(r"art\. (\S+?),", z["opis"]).group(1)) for z in self.zn}, martwe)

    def test_g5_fundacja_rodzinna_bez_znalezisk(self):
        import sys
        sys.path.insert(0, str(ROOT / "eksperymenty" / "x003-martwe-odeslania"))
        import x003
        _, hits = x003.analiza(self.tekst("DU/2023/326"))
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()

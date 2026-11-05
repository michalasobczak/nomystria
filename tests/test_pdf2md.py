"""S003 G1–G4: konwerter na próbkach. Wymaga PDF-ów w .cache/pdf (po `skrypty/pobierz.py`)."""

import re
import unittest
from functools import lru_cache

from _wspolne import CACHE
from pdf2md import convert

KK = CACHE / "DU_1997_553_U.pdf"
VAT = CACHE / "DU_2004_535_U.pdf"


@lru_cache(maxsize=None)
def wynik(pdf):
    return convert(str(pdf))


@unittest.skipUnless(KK.exists(), "brak PDF Kodeksu karnego w .cache/pdf")
class TestKodeksKarny(unittest.TestCase):
    def test_g1_przepis_jednym_akapitem(self):
        md = wynik(KK).markdown
        art = (
            "Art. 1. § 1. Odpowiedzialności karnej podlega ten tylko, kto popełnia czyn zabroniony "
            "pod groźbą kary przez ustawę obowiązującą w czasie jego popełnienia."
        )
        self.assertIn("\n\n" + art + "\n\n", md)

    def test_g2_metadane_strony_tytulowej(self):
        r = wynik(KK)
        self.assertRegex(r.footer_date or "", r"^\d{4}-\d{2}-\d{2}$")
        self.assertTrue((r.basis or "").startswith("t.j. Dz. U."), r.basis)

    def test_g3_przypisy_maja_definicje(self):
        md = wynik(KK).markdown
        self.assertIn("\n## Przypisy\n", md)
        body, foot = md.split("\n## Przypisy\n", 1)
        refs = set(re.findall(r"\[\^([^\]]+)\](?!:)", body))
        defs = set(re.findall(r"^\[\^([^\]]+)\]:", foot, re.M))
        self.assertTrue(refs)
        self.assertEqual(refs - defs, set())


@unittest.skipUnless(VAT.exists(), "brak PDF ustawy o VAT w .cache/pdf")
class TestVat(unittest.TestCase):
    def test_g4_tabela_ze_spacjami(self):
        md = wynik(VAT).markdown
        self.assertRegex(md, r"\| 1 \| ex 09 \| Kawa, herbata, maté \(herbata paragwajska\) i przyprawy")


if __name__ == "__main__":
    unittest.main()

"""S002 G1–G5 i S003 G5–G6: bramki na zbudowanym katalogu dane/."""

import re
import unittest

from _wspolne import DATA, ROOT, indeks, tresc, wiersz
from pobierz import TREATY_RE, is_amending, short_title


class TestKorpus(unittest.TestCase):
    def test_g1_kompletnosc_indeksu(self):
        pliki_indeksu = {r["plik"] for r in indeks()}
        for p in pliki_indeksu:
            self.assertTrue((ROOT / p).exists(), p)
        na_dysku = {p.relative_to(ROOT).as_posix() for p in (DATA / "ustawy").rglob("*.md")}
        self.assertEqual(na_dysku, pliki_indeksu - {"dane/konstytucja.md"})
        self.assertEqual(len(pliki_indeksu), len(indeks()), "zduplikowane ścieżki w indeksie")

    def test_g2_konstytucja(self):
        t = (DATA / "konstytucja.md").read_text(encoding="utf-8")
        self.assertIn("Art. 1. Rzeczpospolita Polska jest dobrem wspólnym wszystkich obywateli.", t)

    def test_g3_kodeks_karny_aktualny(self):
        self.assertEqual(wiersz("DU/1997/553")["brzmienie"], "ujednolicone")
        self.assertIn("\nArt. 190a.", tresc("DU/1997/553"))

    def test_g4_brak_nowelizacji(self):
        bad = [r["eli"] for r in indeks() if is_amending(r["tytul"])]
        self.assertEqual(bad, [])

    def test_g5_brak_ratyfikacji_w_brzmieniu_pierwotnym(self):
        bad = [r["eli"] for r in indeks() if r["brzmienie"].startswith("pierwotne") and TREATY_RE.match(short_title(r["tytul"]))]
        self.assertEqual(bad, [])

    def test_tytuly_jednowierszowe(self):
        self.assertEqual([r["eli"] for r in indeks() if re.search(r"\s{2,}|[\n\r\t]", r["tytul"])], [])

    def test_s008_g1_aktualnosc(self):
        from pobierz import tj_z_ramki
        bad = []
        for r in indeks():
            if r["brzmienie"] != "ujednolicone" or not r["tekst_jednolity_eli"]:
                continue
            ramka = tj_z_ramki(r["opracowano_na_podstawie"])
            if (ramka and ramka != r["tekst_jednolity_eli"]) or (
                    r["tekst_ujednolicony_z_dnia"] and r["tekst_ujednolicony_z_dnia"] < r["tekst_jednolity_z_dnia"]):
                bad.append(r["eli"])
        self.assertEqual(bad, [])

    def test_s008_g2_czytelnosc(self):
        from pobierz import nieczytelny
        bad = [r["eli"] for r in indeks() if nieczytelny((ROOT / r["plik"]).read_text(encoding="utf-8").split("---", 2)[2])]
        self.assertEqual(bad, [])

    def test_s008_g3_zrodlo_tekstu(self):
        for r in indeks():
            self.assertTrue(r["zrodlo_tekstu"], r["eli"])
            if r["zrodlo_tekstu"].startswith(("HTML", "OCR")) or r["brzmienie"] == "jednolite":
                self.assertTrue(r["uwagi"], r["eli"])

    def test_s008_g4_g5_przyklady(self):
        self.assertEqual(wiersz("DU/1971/114")["brzmienie"], "jednolite")
        self.assertIn("Dz.U. 2026 poz. 1372", wiersz("DU/1971/114")["opracowano_na_podstawie"])
        self.assertIn("Art. 1. 1. W sprawach o przestępstwa i przestępstwa skarbowe", tresc("DU/1989/390"))

    def test_brzmienie_ma_dozwolone_wartosci(self):
        self.assertEqual({r["brzmienie"] for r in indeks()} - {"ujednolicone", "jednolite", "pierwotne", "pierwotne (zmieniana)"}, set())

    def test_s003_g5_g6_brak_smieci(self):
        naglowek = re.compile(r"^(©\s*Kancelaria Sejmu|s\.\s*\d+\s*/\s*\d+)\s*$", re.M)
        for r in indeks():
            t = (ROOT / r["plik"]).read_text(encoding="utf-8")
            self.assertNotIn("\x00", t, r["plik"])
            self.assertIsNone(naglowek.search(t), r["plik"])

    def test_metadane_yaml(self):
        for r in indeks():
            t = (ROOT / r["plik"]).read_text(encoding="utf-8")
            self.assertTrue(t.startswith("---\ntytul: "), r["plik"])
            self.assertIn(f'\neli: "{r["eli"]}"\n', t)


if __name__ == "__main__":
    unittest.main()

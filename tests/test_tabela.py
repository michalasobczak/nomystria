"""S004 G1–G4: tabela ustaw w README i pola o tekstach jednolitych."""

import re
import unittest

from _wspolne import ROOT, indeks, wiersz
from tabela import END, START, change_info, latest_tj


class TestLogika(unittest.TestCase):
    def test_ostatni_tj_i_zmiany_po_nim(self):
        act = {
            "references": {
                "Inf. o tekście jednolitym": [{"id": "DU/2025/383"}, {"id": "DU/2026/1342"}, {"id": "DU/2024/17"}],
                "Akty zmieniające": [{"id": "DU/2026/988"}, {"id": "DU/2026/1400"}, {"id": "DU/2026/1500"}],
            }
        }
        self.assertEqual(latest_tj(act), "DU/2026/1342")
        info = change_info(act, {"DU/2026/1342": {"adres": "Dz.U. 2026 poz. 1342", "data_obwieszczenia": "2026-10-02"}})
        self.assertEqual(info["liczba_ustaw_zmieniajacych"], 3)
        self.assertEqual(info["zmian_po_tekscie_jednolitym"], 2)

    def test_brak_tj(self):
        info = change_info({"references": {}}, {})
        self.assertEqual(info["tekst_jednolity"], "")
        self.assertEqual(info["zmian_po_tekscie_jednolitym"], "")


class TestReadme(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        cls.tabela = readme.split(START, 1)[1].split(END, 1)[0]
        cls.wiersze = [l for l in cls.tabela.splitlines() if re.match(r"^\| \d+ \|", l)]

    def test_g1_pelna_tabela(self):
        self.assertEqual(len(self.wiersze), len(indeks()))

    def test_g2_linki(self):
        for l in self.wiersze:
            m = re.search(r"\]\((dane/[^)]+\.md)\)", l)
            self.assertIsNotNone(m, l[:80])
            self.assertTrue((ROOT / m.group(1)).exists(), m.group(1))

    def test_g3_spojnosc_tj(self):
        for r in indeks():
            if r["tekst_jednolity"]:
                self.assertRegex(r["tekst_jednolity_z_dnia"], r"^\d{4}-\d{2}-\d{2}$", r["eli"])
                self.assertLessEqual(int(r["zmian_po_tekscie_jednolitym"]), int(r["liczba_ustaw_zmieniajacych"]), r["eli"])

    def test_g4_przyklad_kodeks_karny(self):
        r = wiersz("DU/1997/553")
        self.assertEqual(r["tekst_jednolity"], "Dz.U. 2026 poz. 1342")
        self.assertEqual(r["tekst_jednolity_z_dnia"], "2026-10-02")


if __name__ == "__main__":
    unittest.main()

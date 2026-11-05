"""S002 G6: reguły rozpoznawania tytułów (nowelizacje, ratyfikacje, skracanie)."""

import unittest

import _wspolne  # noqa: F401  (ścieżka do skrypty/)
from pobierz import TREATY_RE, is_amending, short_title, slugify


class TestTytuly(unittest.TestCase):
    def test_skracanie_tytulu(self):
        self.assertEqual(short_title("Ustawa z dnia 6 czerwca 1997 r. - Kodeks karny."), "Kodeks karny.")
        self.assertEqual(short_title("Ustawa z 16 kwietnia 2004 r. o zmianie ustawy o X"), "o zmianie ustawy o X")
        self.assertEqual(short_title("z dnia 14 marca 2002 r. o uchyleniu ustawy o Y."), "o uchyleniu ustawy o Y.")
        self.assertEqual(short_title("Ustawa z dnia 29 października 2003 o zmianie ustawy o Z"), "o zmianie ustawy o Z")

    def test_nowelizacje(self):
        for t in [
            "Ustawa z dnia 8 października 2026 r. o zmianie ustawy o podatku od towarów i usług",
            "Ustawa z dnia 1 marca 1985 r. o zmianie niektórych przepisów prawa karnego i prawa o wykroczeniach.",
            "Ustawa z dnia 7 stycznia 1950 r. w sprawie zmiany dekretu o pomocy sąsiedzkiej w rolnictwie.",
            "Ustawa z dnia 9 maja 1996 r. zmieniająca ustawę o zmianie ustawy o samorządzie terytorialnym",
            "Ustawa z dnia 20 czerwca 2008 r. uchylająca ustawę o klasyfikacji drewna surowego nieodrobionego",
            "Ustawa z dnia 15 grudnia 1990 r. o zmianach w organizacji i działalności spółdzielczości.",
        ]:
            self.assertTrue(is_amending(t), t)

    def test_nie_nowelizacje(self):
        for t in [
            "Ustawa z dnia 17 października 2008 r. o zmianie imienia i nazwiska",
            "Ustawa z dnia 6 czerwca 1997 r. - Kodeks karny.",
            "Ustawa z dnia 23 maja 2024 r. o bonie energetycznym oraz o zmianie niektórych ustaw",
            "Konstytucja Rzeczypospolitej Polskiej z dnia 2 kwietnia 1997 r.",
        ]:
            self.assertFalse(is_amending(t), t)

    def test_ratyfikacje(self):
        self.assertTrue(TREATY_RE.match(short_title("Ustawa z dnia 18 września 2026 r. o ratyfikacji Umowy X")))
        self.assertTrue(TREATY_RE.match(short_title("Ustawa z dnia 17 marca 1931 r. w sprawie przystąpienia Polski do traktatu")))
        self.assertFalse(TREATY_RE.match(short_title("Ustawa z dnia 3 lipca 2026 r. o systemach sztucznej inteligencji")))

    def test_slug(self):
        self.assertEqual(slugify("Ustawa z dnia 6 czerwca 1997 r. - Kodeks karny."), "kodeks-karny")
        self.assertEqual(slugify("Ustawa z dnia 11 marca 2004 r. o podatku od towarów i usług"), "o-podatku-od-towarow-i-uslug")
        self.assertLessEqual(len(slugify("Ustawa z dnia 1 stycznia 2000 r. o " + "bardzo " * 40)), 80)


if __name__ == "__main__":
    unittest.main()

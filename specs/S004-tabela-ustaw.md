# S004 — Tabela ustaw: zmiany, tekst jednolity i tekst ujednolicony

- **Status:** dostarczona
- **Data:** 2026-11-05
- **Powiązane:** S002

## 1. TL;DR

README zawiera tabelę wszystkich ustaw ze zbioru. Kolumny pokazują liczbę ustaw zmieniających, ostatni tekst jednolity i jego datę, liczbę zmian ogłoszonych po nim oraz datę tekstu ujednoliconego. Te same pola są w `indeks.csv` i w metadanych plików. Potwierdzenie: `tests/test_tabela.py`.

## 2. Abstract

Właściciel potrzebuje przeglądu zbioru: które ustawy i jak często były zmieniane, kiedy ogłoszono ostatni tekst jednolity i z kiedy jest tekst ujednolicony. Tak widać, jak bardzo urzędowy tekst jednolity odstaje od aktualnego brzmienia.

API ELI podaje dla ustawy listę „Akty zmieniające” oraz „Inf. o tekście jednolitym”, czyli wszystkie obwieszczenia tekstu jednolitego. Datę obwieszczenia daje dopiero osobne zapytanie o dane obwieszczenia.

Tabela początkowo była w `dane/LISTA.md`. Na prośbę właściciela przeniesiono ją do README.

## 3. Objective

- **Cele:**
  - pola `liczba_ustaw_zmieniajacych`, `tekst_jednolity`, `tekst_jednolity_eli`, `tekst_jednolity_z_dnia` (data obwieszczenia), `tekst_jednolity_ogloszony` (data ogłoszenia w Dz. U.) i `zmian_po_tekscie_jednolitym`;
  - tabela w README między znacznikami `<!-- LISTA:START -->` i `<!-- LISTA:END -->`.
- **Poza zakresem:** lista nazw ustaw zmieniających (jest w ISAP) i historia wszystkich tekstów jednolitych.
- **Kryteria sukcesu:** bramki G1–G4.

## 4. Artefact Inventory

| Artefakt | Rodzaj | Stan |
| --- | --- | --- |
| `skrypty/tabela.py` | kod | istnieje |
| `skrypty/pobierz.py` | kod | do zmiany (wywołuje `tabela`) |
| `README.md`, sekcja „Lista ustaw” | dokument | istnieje |
| `dane/indeks.csv` | dane | do zmiany (nowe kolumny) |
| `.cache/pdf/teksty_jednolite.json` | cache (poza repo) | istnieje |
| `dane/LISTA.md` | dane | do usunięcia |
| `tests/test_tabela.py` | testy | istnieje |

## 5. Functional Domain Changes

- **Ostatni tekst jednolity:** maksimum według (rok, pozycja) z „Inf. o tekście jednolitym”. Pozycje w Dz. U. rosną chronologicznie.
- **Zmian po t.j.:** liczba aktów zmieniających o (rok, pozycja) większym niż ostatni t.j. To przybliżenie: liczy akty ogłoszone po obwieszczeniu, niezależnie od daty wejścia w życie.
- Gdy ustawa nie ma tekstu jednolitego, kolumny t.j. są puste, a w tabeli pokazują „—”. Dotyczy to np. Konstytucji, której nigdy nie ogłoszono w formie tekstu jednolitego.
- Dane obwieszczeń trzymamy w cache na stałe, bo obwieszczenie się nie zmienia.
- Kolumna brzmienia pokazuje symbol, żeby tabela się nie rozjeżdżała: U ujednolicone, P pierwotne, PZ pierwotne (zmieniana). Legenda jest nad tabelą. Pełna nazwa zostaje w `indeks.csv` i w metadanych.
- `python skrypty/tabela.py` odświeża tabelę w README z `indeks.csv` bez ponownej konwersji.

## 6. Critical Path

1. Dla każdej ustawy wybrać ostatni t.j. i policzyć zmiany.
2. Pobrać dane brakujących obwieszczeń.
3. Dopisać pola do metadanych i indeksu.
4. Wstawić tabelę do README.

Warunek ukończenia: README ma tabelę z liczbą wierszy równą liczbie wierszy `indeks.csv`.

## 7. Control Gates

| # | Bramka | Warunek zaliczenia | Weryfikacja | Blokuje |
| --- | --- | --- | --- | --- |
| G1 | Pełna tabela | liczba wierszy tabeli w README = liczba wierszy `indeks.csv` | `tests/test_tabela.py` | commit |
| G2 | Linki | każdy link w tabeli wskazuje istniejący plik | test | commit |
| G3 | Spójność t.j. | jeśli `tekst_jednolity` jest niepusty, to `tekst_jednolity_z_dnia` ma format RRRR-MM-DD i `zmian_po_tekscie_jednolitym` ≤ `liczba_ustaw_zmieniajacych` | test | commit |
| G4 | Przykład | KK (DU/1997/553): `tekst_jednolity` = „Dz.U. 2026 poz. 1342”, `tekst_jednolity_z_dnia` = „2026-10-02” | test (zależny od danych z 2026-11-05) | commit |

## 8. Expected Outcome

- **Efekt bezpośredni:** przegląd całego zbioru w README.
- **Efekt mierzalny:** np. ustawa o VAT ma t.j. z 2026-09-01 i 2 zmiany ogłoszone po nim.
- **Skutki uboczne:** README ma ok. 360 KB. GitHub renderuje pliki Markdown do 512 KB. Przy dużym wzroście zbioru tabelę trzeba będzie znów wydzielić.
- **Wycofanie:** usunięcie znaczników z README.

## 9. Additional Information

- **Odrzucone:** osobny `dane/LISTA.md`, bo właściciel wolał README.
- **Korekta wniosku:** w rozmowie podano Kodeks karny jako przykład zmian ogłoszonych po tekście jednolitym. Według danych KK nie ma takich zmian: t.j. Dz. U. 2026 poz. 1342 jest z 2026-10-02, a ostatnia nowelizacja ma pozycję 988. Przypis z listą „zmian tekstu jednolitego” dotyczył innej ustawy, przywołanej w treści KK. Poprawnym przykładem jest ustawa o VAT.

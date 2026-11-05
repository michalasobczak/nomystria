# S012 — Reguła R3: ślubowanie bez ścieżki po stronie przyjmującego

- **Status:** dostarczona (wynik: [`kontrole/x005/RAPORT.md`](../kontrole/x005/RAPORT.md): 14 znalezisk)
- **Data:** 2026-11-05
- **Powiązane:** MANIFEST M12, S010 (schemat: skrypt → model → przegląd), S011 (odłożona)

## 1. TL;DR

Pierwsza reguła z kategorii „brak ścieżki alternatywnej”. Szukamy sytuacji, w których **status, urząd albo kadencja zależy od ślubowania złożonego wobec podmiotu X**, a ustawa nie przewiduje, co się dzieje, gdy X ślubowania nie przyjmie: odmówi, zwleka albo nie może. Oceniamy wszystkie ustawy z takim przepisem, czyli ok. 26 kandydatów. Wzorzec poprawnego rozwiązania to ustawa o samorządzie gminnym, art. 29a ust. 3: wójt składa ślubowanie przed komisarzem wyborczym, jeśli sesja rady się nie odbyła.

## 2. Abstract

Ślubowanie bywa warunkiem objęcia urzędu, np. „Sędzią … jest osoba powołana …, która złożyła ślubowanie wobec Prezydenta”. Ustawy regulują zwykle odmowę złożenia ślubowania przez osobę (jest równoznaczna ze zrzeczeniem się), ale nie regulują bezczynności podmiotu przyjmującego.

Skutek takiej luki widać w historii: w 2015 r. Prezydent nie przyjął ślubowania od sędziów Trybunału Konstytucyjnego wybranych przez Sejm, a prawo nie dawało ścieżki rozstrzygnięcia.

Próba przeglądu (rozmowa z 2026-11-05) wykazała, że temat jest łatwy w identyfikacji, bo frazy są powtarzalne, a w podważeniu krótka lista kontrolna.

## 3. Objective

- **Cele:** dla każdej ustawy ze ślubowaniem wobec wskazanego podmiotu ustalić:
  1. czy od ślubowania **zależy** status, objęcie urzędu, kadencja lub możliwość działania (z cytatem);
  2. czy ustawa reguluje **odmowę osoby** (z cytatem);
  3. czy ustawa daje **ścieżkę po stronie przyjmującego**: zastępczy podmiot, termin, fikcję albo inny tryb (z cytatem);
  4. werdykt.
- **Poza zakresem:**
  - ocena zgodności z Konstytucją;
  - ślubowania, od których nic nie zależy (oznaczone „nie dotyczy”);
  - przysięgi i ślubowania w aktach niższego rzędu.
- **Kryteria sukcesu:** bramki G1–G4.

## 4. Artefact Inventory

| Artefakt | Rodzaj | Stan |
| --- | --- | --- |
| `eksperymenty/x005-slubowanie/x005.py` (etap 1: kandydaci i wyciągi przepisów) | kod | do utworzenia |
| `kontrole/x005/{kandydaci.json, oceny_llm.json, znaleziska.json, RAPORT.md}` | dane i dokument | do utworzenia |
| Konstytucja RP, art. 131 (zastępstwo Prezydenta) | dane (przepis ogólny z listy kontrolnej) | istnieje |
| `tests/test_x005.py` | testy | do utworzenia |

## 5. Functional Domain Changes

- **Kandydat (etap 1, skrypt):** ustawa, w której zdanie ze słowem „ślubowanie” wskazuje podmiot przyjmujący: „wobec X”, „przed X” (bez „przed przystąpieniem / objęciem / podjęciem…”), „na ręce X”, „X odbiera / przyjmuje ślubowanie”. Pomijamy przepisy nowelizujące i cytaty.
- **Wyciąg dla modelu:** wszystkie akapity ze słowem „ślubowani” wraz z nagłówkami artykułów oraz akapity o statusie lub kadencji, które ich dotyczą. Model może też przeszukać pełny plik ustawy.
- **Lista kontrolna ratunków (podważenie):**
  1. tryb zastępczy lub termin w tej samej ustawie (jak art. 29a ust. 3 ustawy o samorządzie gminnym);
  2. fikcja złożenia ślubowania albo objęcie urzędu niezależne od ślubowania;
  3. zastępstwo przyjmującego z przepisów ogólnych (Konstytucja art. 131, ale tylko przy formalnie stwierdzonej przeszkodzie, nie przy odmowie);
  4. inny podmiot, który może przyjąć ślubowanie.
- **Werdykty:**
  - `brak_sciezki`: status zależy od ślubowania, a ratunku brak;
  - `sciezka_istnieje`: jest ratunek z listy;
  - `nie_dotyczy`: od ślubowania nic nie zależy albo przyjmującym jest podmiot w pełni zastępowalny (np. przełożony w hierarchii);
  - `niejasne`.

## 6. Critical Path

1. Skrypt x005 tworzy kandydatów z wyciągami.
2. Model ocenia wszystkich kandydatów (paczki).
3. Przegląd ręczny werdyktów `brak_sciezki` i `sciezka_istnieje`.
4. Znaleziska (kategoria `brak_sciezki_alternatywnej`) i raport.
5. Publikacja.

## 7. Control Gates

| # | Bramka | Warunek zaliczenia | Weryfikacja | Blokuje |
| --- | --- | --- | --- | --- |
| G1 | Kompletność | każdy kandydat z etapu 1 ma werdykt modelu | test | publikację |
| G2 | Cytaty | każdy cytat (zależność, odmowa osoby, ścieżka) występuje dosłownie w tekście ustawy | `tests/test_x005.py` | publikację |
| G3 | Wzorzec | ustawa o samorządzie gminnym (DU/1990/95) ma werdykt `sciezka_istnieje` | test | publikację |
| G4 | Przegląd ręczny | każde znalezisko `brak_sciezki` sprawdzone w tekście przed publikacją | raport | publikację |

## 8. Expected Outcome

- **Efekt bezpośredni:** lista ustaw, w których bezczynność podmiotu przyjmującego ślubowanie blokuje objęcie urzędu bez ścieżki wyjścia, widoczna na stronie.
- **Efekt mierzalny:** liczba ustaw `brak_sciezki` / `sciezka_istnieje` / `nie_dotyczy`.
- **Wycofanie:** usunięcie `kontrole/x005/`.

## 9. Additional Information

- **Odrzucone alternatywy:** wyłączenie zaskarżenia (A) jako pierwsza reguła, bo ślubowanie ma węższy wyzwalacz, krótszą listę ratunków i wzorzec poprawnej regulacji.
- **Ryzyka:** werdykt `brak_sciezki` nie przesądza o niekonstytucyjności ani o tym, że przyjmujący ma prawo odmówić. Stwierdza tylko brak trybu w tekście ustawy.

## Zmiany w trakcie realizacji (2026-11-05)

- **Kandydaci.** Pierwszy wzorzec (tylko „wobec / przed / odbiera” w tym samym zdaniu) pominął ustawę o statusie sędziów TK, bo jej akapit rozdzielił się przy konwersji. Pominął też ustawy, w których ślubowanie jest warunkiem statusu bez wskazania przyjmującego w tym samym zdaniu. Kryterium rozszerzono, a rozdzielone akapity są łączone. Liczba kandydatów wzrosła z 31 do 40.
- **Waga (dodana w przeglądzie ręcznym).** Rozróżniamy, czy przyjmujący to ten sam organ, który powołuje lub wybiera (waga niska), czy inny organ (wysoka, TK). Osobna kategoria to wpis plus ślubowanie przed jedną osobą bez zastępcy (średnia). Przebiegi modelu stosowały to rozróżnienie niekonsekwentnie, dlatego waga jest nadawana ręcznie według jawnej zasady opisanej w raporcie.

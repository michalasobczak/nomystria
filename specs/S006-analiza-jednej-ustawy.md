# S006 — Eksperymentalna analiza jednej ustawy pod kątem wad legislacyjnych

- **Status:** wycofana (2026-11-05). Wyniki x002 usunięto z repozytorium i strony, ale zostały w historii git (commit `b73f07f` i późniejsze).
- **Data:** 2026-11-05
- **Powiązane:** S002 (korpus), S005 (wiarygodność danych), S007 (strona z wynikami kontroli)

## 1. TL;DR

Eksperyment na jednej wybranej ustawie z korpusu sprawdza, czy zautomatyzowana analiza z użyciem AI, weryfikowana krzyżowo, znajduje w niej:

- niespójności,
- braki,
- wady,
- sprzeczności,
- brak ścieżek alternatywnych,
- zaniechania.

Wynik to raport ze znaleziskami. Każde znalezisko cytuje dosłownie przepis, ma kategorię, uzasadnienie i informację, czy potwierdziły je oba przebiegi. Znaleziska publikujemy bez werdyktów (decyzja właściciela).

## 2. Abstract

Celem projektu jest identyfikacja wad prawa i przekazywanie ich jako propozycji inicjatyw ustawodawczych. Korpus z S002 daje do tego materiał, ale nie wiemy jeszcze, czy automatyczna analiza daje znaleziska wartościowe, czy głównie szum i halucynacje.

Modele AI chętnie potwierdzają hipotezy, więc samo „znalazłem sprzeczność” nic nie znaczy. Potrzebne są trzy warunki:

- definicje kategorii;
- wymóg dosłownego cytatu, który da się mechanicznie sprawdzić w tekście;
- weryfikacja drugim, niezależnym narzędziem.

Eksperyment na jednej ustawie ma ustalić metodę i realny odsetek trafnych znalezisk, zanim rozszerzymy analizę na więcej aktów.

## 3. Objective

- **Cele:**
  1. Wybór jednej ustawy według kryteriów z sekcji 9 (decyzja autora).
  2. Definicje kategorii znalezisk (wersja robocza, do zatwierdzenia):
     - **Sprzeczność:** dwa przepisy nakazują albo dopuszczają wykluczające się zachowania w tym samym stanie faktycznym.
     - **Niespójność:** to samo pojęcie użyte w różnych znaczeniach, rozbieżna terminologia, niezgodność z definicją legalną.
     - **Luka:** sytuacja objęta celem ustawy, ale nieuregulowana.
     - **Wada legislacyjna:** błędne lub martwe odesłanie (do uchylonego przepisu albo nieistniejącej jednostki), błąd redakcyjny, przepis bez treści normatywnej.
     - **Brak ścieżki alternatywnej:** procedura bez trybu na wypadek niemożności, odmowy albo bezczynności, np. brak środka odwoławczego albo trybu zastępczego.
     - **Zaniechanie:** niewykonana delegacja ustawowa (brak aktu wykonawczego, według „Akty wykonawcze” w ISAP) albo obowiązek bez sankcji lub organu, który go egzekwuje.
  3. Analiza w dwóch przebiegach niezależnymi narzędziami (np. dwa różne modele AI). Do tego mechaniczne kontrole, które nie wymagają AI: odesłania do uchylonych jednostek, delegacje bez aktów wykonawczych, definicje legalne użyte niezgodnie.
  4. Raport: lista znalezisk w formacie do odczytu przez S007 i podsumowanie metody.
- **Poza zakresem:**
  - przygotowanie projektu inicjatywy ustawodawczej (osobna specyfikacja dla potwierdzonego znaleziska);
  - analiza orzecznictwa i doktryny;
  - więcej niż jedna ustawa.
- **Kryteria sukcesu:**
  - każde znalezisko przechodzi bramki G1–G3;
  - znamy zgodność przebiegów, czyli odsetek znalezisk wskazanych niezależnie przez oba narzędzia;
  - autor decyduje: kontynuować metodę, zmienić ją albo porzucić.

## 4. Artefact Inventory

| Artefakt | Rodzaj | Stan |
| --- | --- | --- |
| `dane/ustawy/<rok>/<plik>.md` wybranej ustawy | dane (wejście) | istnieje |
| API ELI: „Akty wykonawcze”, „Odesłania”, „Orzeczenie TK” dla ustawy | zewnętrzne | istnieje |
| `eksperymenty/x002-analiza-<ustawa>/` (prompty, skrypty kontroli mechanicznych) | kod | do utworzenia |
| `kontrole/x002/znaleziska.json` + `RAPORT.md` | dane i dokument | do utworzenia |
| dwa narzędzia AI do analizy krzyżowej | zewnętrzne | [DO USTALENIA] |

## 5. Functional Domain Changes

**Format znaleziska** (`znaleziska.json`):

- `id`
- `eli`
- `kategoria`
- `przepisy` (lista jednostek, np. „art. 12 ust. 3”)
- `cytaty` (dosłowne fragmenty)
- `opis`
- `uzasadnienie`
- `waga` (niska / średnia / wysoka)
- `zrodla_wykrycia` (które narzędzie lub kontrola)
- `weryfikacja_krzyzowa` (czy drugie narzędzie potwierdziło)

Ten sam format posłuży kolejnym analizom.

**Reguły:**

- Znalezisko bez dosłownego cytatu obecnego w pliku ustawy jest odrzucane automatycznie.
- Znalezisko wskazane tylko przez jedno narzędzie jest publikowane z oznaczeniem „jedno źródło”.
- Treść przepisów jest wyłącznie cytowana, nigdy przeredagowywana (MANIFEST M2).

## 6. Critical Path

1. Autor wybiera ustawę.
2. Zatwierdzenie definicji kategorii.
3. Kontrole mechaniczne.
4. Przebieg A (narzędzie 1).
5. Przebieg B (narzędzie 2), bez dostępu do wyników A.
6. Scalenie i automatyczna walidacja cytatów.
8. Raport i decyzja o dalszej metodzie.

Warunek ukończenia: znaleziska przeszły walidację (G1–G3), mają zapisany wynik weryfikacji krzyżowej (G4) i są opublikowane w raporcie i na stronie.

## 7. Control Gates

| # | Bramka | Warunek zaliczenia | Weryfikacja | Blokuje |
| --- | --- | --- | --- | --- |
| G1 | Cytat dosłowny | 100% znalezisk ma cytaty występujące dosłownie w pliku ustawy | skrypt walidacji | trafienie znaleziska do raportu |
| G2 | Istniejące przepisy | każda jednostka w `przepisy` istnieje w tekście ustawy | skrypt walidacji | raport |
| G3 | Kategoria | każde znalezisko ma kategorię z listy z sekcji 3 | walidacja schematu JSON | raport |
| G4 | Weryfikacja krzyżowa | dla każdego znaleziska zapisano wynik obu przebiegów | raport | zamknięcie S006 |
| G6 (negatywna) | Brak treści zmyślonej | 0 znalezisk powołujących się na przepisy spoza ustawy bez źródła | G1 + G2 | raport |
| G7 (negatywna) | Brak „porady prawnej” | raport nie formułuje rozstrzygnięć indywidualnych spraw; dotyczy wyłącznie tekstu ustawy | przegląd autora | publikację |

## 8. Expected Outcome

- **Efekt bezpośredni:** lista ocenionych znalezisk dla jednej ustawy i opis metody.
- **Efekt mierzalny:** liczba znalezisk według kategorii i zgodność między narzędziami (potwierdzone krzyżowo / wszystkie).
- **Skutki uboczne:** potwierdzone znaleziska mogą stać się kandydatami na pierwsze propozycje inicjatyw ustawodawczych.
- **Wycofanie:** nie dotyczy, bo eksperyment nie zmienia danych korpusu.

## 9. Additional Information

- **Kryteria wyboru ustawy (propozycja):**
  - średnia wielkość, np. 20–80 stron, żeby wyniki dało się przejrzeć;
  - brzmienie ujednolicone (●) i wiele nowelizacji, bo więcej zmian zwiększa ryzyko niespójności;
  - istnieją akty wykonawcze, co pozwala sprawdzić zaniechania;
  - dziedzina bliska autorowi.

  Kandydaci do decyzji autora: ustawa o fundacji rodzinnej (2023, 4 akty wykonawcze, mała), ustawa o funduszu sołeckim (2014), ustawa o systemach sztucznej inteligencji (2026, ○, nowa).
- **Odrzucone alternatywy:** analiza całego korpusu od razu, bo bez sprawdzenia metody na jednej ustawie grozi zalew szumu. Odrzucona też analiza jednym narzędziem bez weryfikacji krzyżowej.
- **Ryzyka:** AI chętnie zgadza się z hipotezą („znajdź sprzeczności” daje sprzeczności). Dlatego wymagamy dosłownego cytatu i drugiego, niezależnego przebiegu.
- **Decyzja właściciela:** znaleziska publikujemy tak po prostu, bez werdyktów autora. Bramkę G5 i pola `werdykt_autora`/`komentarz_autora` usunięto.
- **Decyzje z realizacji:** ustawę o fundacji rodzinnej wybrano spośród kandydatów, gdy właściciel poprosił o kontrolę jednej ustawy jako danych testowych dla strony. Narzędzia to dwa przebiegi AI (Claude Opus i Claude Sonnet) bez dostępu do wyników drugiego oraz kontrole mechaniczne M1 i M2.
- **Otwarte pytania:**
  - Którą ustawę wybrać? (rozstrzygnięte w realizacji)
  - Jakich dwóch narzędzi AI użyć?
  - Czy kategorie należy uzupełnić, np. o niezgodność z Konstytucją albo z prawem UE? Zostawiamy to na później, bo wymaga szerszego kontekstu.

## Wycofanie (2026-11-05)

Właściciel wycofał znaleziska x002 jako zbyt skomplikowane do automatycznej weryfikacji na pierwszym etapie.

Bezpośrednim powodem było pytanie o znalezisko x002-001 („skąd założenie, że nie ma zarządu?”). Okazało się, że oba przebiegi AI i analiza scalająca pominęły **art. 42 Kodeksu cywilnego**. Przepis ten nakazuje sądowi ustanowić kuratora, gdy osoba prawna nie ma organu. To podważyło dwa znaleziska:

- x002-001: luki „upływ kadencji” i „odwołanie bez powołania” mają ścieżkę przez kuratora;
- x002-003: kurator z art. 117 ust. 1 pkt 19 to najpewniej kurator z art. 42 k.c.

**Wnioski dla metody:**

1. Ograniczenie analizy do tekstu jednej ustawy (zasada 2 instrukcji) usunęło halucynacje przepisów, ale ukryło ogólne reguły z innych aktów, zwłaszcza z kodeksów.
2. Weryfikacja krzyżowa dwoma modelami nie wykryła tego błędu, bo oba przebiegi miały to samo ograniczenie. Niezależność narzędzi nie zastępuje niezależności kontekstu.
3. Nowy kierunek (MANIFEST M12): **jedna prosta, deterministyczna reguła naraz, sprawdzana na wielu ustawach.** Złożone analizy treści, diagramy ścieżek i formalne kodowanie przepisów wrócą później jako osobne specyfikacje.

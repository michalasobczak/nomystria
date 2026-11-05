# S007 — Strona na GitHub Pages: przeglądarka ustaw z filtrami i wynikami kontroli

- **Status:** w realizacji (kod gotowy, czeka na włączenie Pages w ustawieniach repozytorium)
- **Data:** 2026-11-05
- **Powiązane:** S002, S004, S005, S006

## 1. TL;DR

Statyczna strona na GitHub Pages pozwala przeglądać wszystkie ustawy z korpusu, filtrować je i oglądać wyniki kontroli z S005 i znaleziska z S006. Dane pochodzą wyłącznie z repozytorium (`dane/indeks.csv`, `kontrole/`), a GitHub Actions publikuje stronę przy każdym pushu na `main`. Potwierdzenie: test generatora danych i ręczne sprawdzenie filtrów na opublikowanej stronie.

## 2. Abstract

Tabela w README ma ponad 1100 wierszy i nie da się jej filtrować. Wyniki kontroli z S005 i S006 będą zapisywane w repozytorium jako JSON, ale bez przeglądarki trudno je czytać i komuś udostępnić.

Repozytorium jest publiczne, więc GitHub Pages jest bezpłatne i nie wymaga serwera. Zgodnie z MANIFEST M6 strona nie ma własnych danych. Jest widokiem na to, co jest w repozytorium, i powstaje automatycznie.

## 3. Objective

- **Cele:**
  - **Lista ustaw z filtrami:**
    - pełnotekstowe wyszukiwanie w tytule;
    - rok;
    - brzmienie (● ○ ◐);
    - przedział liczby zmian;
    - czy jest tekst jednolity;
    - czy są zmiany po t.j.;
    - wynik kontroli S005 (zgodny / rozbieżny / niezweryfikowany / brak kontroli);
    - liczba znalezisk S006 według kategorii i werdyktu.
  - Sortowanie po kolumnach i licznik wyników.
  - Szczegóły ustawy: metadane, wyniki kontroli z wyjaśnieniami, znaleziska z cytatami i werdyktem autora, linki do pliku Markdown w repozytorium, PDF-u źródłowego i ISAP.
  - Ostrzeżenie o eksploracyjnym charakterze projektu i informacja o autorze, jak w README.
  - Filtry zapisane w adresie URL (np. `#brzmienie=U&zmianyPoTj=1`), żeby wynik dało się komuś wysłać.
- **Poza zakresem:** edycja i komentowanie na stronie, logowanie, backend, wyszukiwanie w treści ustaw (opcja na później), wersje historyczne.
- **Kryteria sukcesu:** bramki G1–G6.

## 4. Artefact Inventory

| Artefakt | Rodzaj | Stan |
| --- | --- | --- |
| `kontrole/<eksperyment>/wyniki.json`, `kontrole/<eksperyment>/znaleziska.json` | dane (wejście, z S005/S006) | do utworzenia |
| `skrypty/strona.py`: generator `strona/dane.json` z `indeks.csv` i `kontrole/` | kod | do utworzenia |
| `strona/index.html`, `strona/app.js`, `strona/style.css` (bez frameworka, bez budowania) | kod | do utworzenia |
| `.github/workflows/strona.yml` (generowanie i `actions/deploy-pages`) | konfiguracja | do utworzenia |
| ustawienie GitHub Pages: źródło „GitHub Actions” | zewnętrzne (ustawienia repo) | do zmiany, wymaga zgody właściciela (asystent nie ma uprawnienia) |
| `kontrole/README.md` (format plików kontroli) | dokument | istnieje |
| `tests/test_strona.py` | testy | do utworzenia |

## 5. Functional Domain Changes

- **`dane.json`:** jedna lista rekordów: pola z `indeks.csv` plus `kontrole` (werdykty według parametrów) i `znaleziska` (lista skrócona). Pełna treść ustaw nie trafia do JSON-a, a strona linkuje do plików w repozytorium. Szacowany rozmiar to < 1 MB.
- **Filtrowanie i sortowanie** działają w przeglądarce, po stronie klienta. 1200 rekordów nie wymaga indeksu.
- Brak wyników kontroli dla ustawy oznacza „brak kontroli”, nigdy „zgodny” (jak S005 G7).
- **Tryb jasny i ciemny** według ustawień systemu, układ działa też na telefonie.
- **Publikacja:** workflow uruchamia się po pushu na `main` w ścieżkach `dane/indeks.csv`, `kontrole/**`, `strona/**`, `skrypty/strona.py`. Gdy generowanie się nie powiedzie, strona nie jest aktualizowana i zostaje poprzednia wersja.

## 6. Critical Path

1. Ustalić format `kontrole/` (wspólny z S005 i S006).
2. Generator `dane.json` i jego test.
3. Strona: lista, filtry, szczegóły.
4. Workflow Pages.
5. Włączyć Pages w ustawieniach repozytorium (za zgodą właściciela).
6. Sprawdzić opublikowaną stronę.

Warunek ukończenia: strona działa pod `https://michalasobczak.github.io/nomystria/` i przechodzi bramki.

## 7. Control Gates

| # | Bramka | Warunek zaliczenia | Weryfikacja | Blokuje |
| --- | --- | --- | --- | --- |
| G1 | Kompletność | liczba rekordów w `dane.json` = liczba wierszy `indeks.csv` | `tests/test_strona.py` | publikację |
| G2 | Kontrole | każdy wynik z `kontrole/` trafia do właściwego rekordu (po `eli`), a wynik z nieznanym `eli` przerywa generowanie | test | publikację |
| G3 | Filtry | dla ● + „zmiany po t.j. > 0” strona pokazuje tyle rekordów, ile wylicza skrypt z `indeks.csv` | sprawdzenie w przeglądarce (ręczne lub automat) | zamknięcie S007 |
| G4 | Linki | linki do pliku ustawy, PDF i ISAP otwierają się dla 5 losowych rekordów | sprawdzenie w przeglądarce | zamknięcie S007 |
| G5 (negatywna) | Brak „zgodny z braku danych” | rekord bez kontroli nigdy nie ma oznaczenia zgodności | test | publikację |
| G6 (negatywna) | Ostrzeżenie widoczne | ostrzeżenie o projekcie eksploracyjnym jest na każdej stronie | test (obecność w `index.html`) | publikację |

## 8. Expected Outcome

- **Efekt bezpośredni:** publiczny adres do przeglądania korpusu i wyników kontroli.
- **Efekt mierzalny:** filtrowanie 1200 rekordów < 100 ms, a strona waży (bez danych) < 50 KB.
- **Skutki uboczne:** każdy push uruchamia workflow, co zajmuje minuty z darmowej puli dla repozytoriów publicznych. Strona jest publiczna, więc ostrzeżenie musi być widoczne (G6).
- **Wycofanie:** wyłączenie Pages w ustawieniach i usunięcie workflow.

## 9. Additional Information

- **Odrzucone alternatywy:**
  - Strona z frameworkiem (React itp.) i krokiem budowania, bo przy tej skali to zbędna zależność (MANIFEST M9).
  - Kopiowanie treści ustaw (110 MB) do artefaktu Pages. Na razie linkujemy do repozytorium, a pełnotekstowe przeszukiwanie treści może być osobną specyfikacją.
  - Gałąź `gh-pages`, bo workflow z `deploy-pages` nie zaśmieca historii.
- **Zależności zewnętrzne:** GitHub Pages i GitHub Actions.
- **Otwarte pytania:**
  - Czy strona ma mieć własną domenę (np. subdomenę michalasobczak.pl)?
  - Czy dodać przeszukiwanie treści ustaw?

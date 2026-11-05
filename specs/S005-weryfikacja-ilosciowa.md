# S005 — Weryfikacja ilościowa korpusu i klasyfikacji (próba 100 ustaw)

- **Status:** dostarczona, czeka na przegląd autora (wynik: [`kontrole/x001/RAPORT.md`](../kontrole/x001/RAPORT.md))
- **Data:** 2026-11-05
- **Powiązane:** S002 (korpus), S004 (tabela), S007 (strona z wynikami kontroli)

## 1. TL;DR

Jednorazowy test sprawdza, czy korpus ma właściwą liczbę ustaw i czy dla losowej próby 100 ustaw zgadzają się parametry z tabeli. Chodzi o klasyfikację brzmienia, ostatni tekst jednolity, liczbę zmian i liczbę zmian po tekście jednolitym. Każdy parametr sprawdzamy z innego źródła niż to, z którego go wyliczono. Wynik to raport z odsetkiem zgodności i listą rozbieżności z przyczynami.

## 2. Abstract

S002 i S004 dostarczyły korpus 1177 aktów z tabelą parametrów. Wszystkie te parametry pochodzą z jednego zapytania `acts/search` w API ELI i z jednej heurystyki doboru opartej na tytułach.

Tytuły były już źródłem błędów. Pierwsza wersja zbioru zawierała 490 nowelizacji. Filtr trzeba było dwukrotnie rozszerzać. Jeden tytuł przyszedł z API ze znakiem nowej linii. Liczba „zmian po t.j.” jest przybliżeniem: liczy akty o pozycji w Dz. U. wyższej niż obwieszczenie (S004, sekcja 5).

Brakuje niezależnego potwierdzenia trzech rzeczy:

- czy nie zgubiliśmy ustaw (zbyt szeroki filtr);
- czy nie wpuściliśmy aktów, które nie powinny wejść;
- czy parametry odpowiadają rzeczywistości.

Zgodnie z MANIFEST M10 i z zasadą weryfikacji krzyżowej różnymi narzędziami potrzebny jest test na innych źródłach niż te, z których wyliczono dane.

## 3. Objective

- **Cele:**
  1. **Kompletność.** Liczba obowiązujących ustaw z Dz. U. w zbiorze plus liczba wykluczonych według kategorii (nowelizacje, ratyfikacje, akty jednorazowe, inne statusy) daje liczbę z niezależnego zapytania. Dane trzeba uzgodnić bez reszty.
  2. **Wykluczenia.** Losujemy 50 aktów wykluczonych jako nowelizacje i 20 jako ratyfikacje. Drugim narzędziem albo ręcznie sprawdzamy, czy rzeczywiście są tym, za co je uznano. Kryterium jest treść aktu (np. „W ustawie … wprowadza się następujące zmiany”), nie tytuł.
  3. **Próba 100 ustaw ze zbioru** (losowanie warstwowe z ziarnem, proporcjonalnie do ●/○/◐, z dodaniem zawsze Konstytucji, KK i ustawy o VAT). Dla każdej sprawdzamy:
     - **Brzmienie:** czy ISAP ma tekst ujednolicony, według strony `DocDetails` w ISAP (HTML), a nie wyniku `search`.
     - **Ostatni tekst jednolity:** adres i data obwieszczenia według strony ISAP oraz ramki „Opracowano na podstawie” w PDF-ie tekstu ujednoliconego.
     - **Liczba ustaw zmieniających:** według strony ISAP („Akty zmieniające”) i pełnego `GET /acts/{ELI}`.
     - **Zmiany po t.j.:** porównanie z pozycjami wymienionymi po t.j. w „Opracowano na podstawie”. Np. ustawa o VAT ma „t.j. Dz. U. z 2026 r. poz. 1263, 1270”, czyli 1 zmianę uwzględnioną w tekście ujednoliconym, a tabela pokazuje 2. Każda różnica musi mieć wyjaśnienie, np. nowelizacja ogłoszona po dacie tekstu ujednoliconego albo uchylenie zamiast zmiany.
     - **Tekst ujednolicony z dnia:** data ze stopki PDF zgodna z datą w ISAP.
- **Poza zakresem:** poprawianie danych w ramach tej specyfikacji. Wykryte błędy dają osobne specyfikacje albo poprawki S002/S004. Poza zakresem jest też weryfikacja treści przepisów, którą zajmuje się S006.
- **Kryteria sukcesu:** raport istnieje, każda rozbieżność ma przyczynę, a zgodność parametrów jest nie gorsza niż progi z sekcji 7.

## 4. Artefact Inventory

| Artefakt | Rodzaj | Stan |
| --- | --- | --- |
| `dane/indeks.csv` | dane (wejście) | istnieje |
| API ELI `GET /acts/{ELI}` | zewnętrzne | istnieje |
| strona ISAP `DocDetails.xsp?id=…` | zewnętrzne (drugie źródło) | istnieje |
| `.cache/pdf/*_U.pdf`, ramka „Opracowano na podstawie” | dane | istnieje |
| `eksperymenty/x001-weryfikacja-100/` (skrypt jednorazowy, próba) | kod | do utworzenia |
| `kontrole/x001/wyniki.json` + `RAPORT.md` (format do odczytu przez S007) | dane i dokument | do utworzenia |
| drugie narzędzie weryfikacji (inny model AI albo przegląd ręczny autora) | organizacja | [DO USTALENIA] |

## 5. Functional Domain Changes

- Produkcyjne dane się nie zmieniają. To eksperyment: kod jest jednorazowy, a liczy się wynik zapisany w repozytorium.
- **Losowanie:** stałe ziarno zapisane w raporcie, więc próbę da się odtworzyć.
- **Parsowanie strony ISAP:** strona może się zmienić albo być niedostępna. Wtedy parametr dostaje wynik „niezweryfikowany”, a nie „zgodny”.
- **Zasada uczciwości:** parametr zgadza się tylko przy zgodności z niezależnym źródłem. Brak danych w źródle nie jest zgodnością.
- **Wynik dla każdej ustawy** (do `wyniki.json`): `eli`, parametr, wartość w zbiorze, wartość w źródle kontrolnym, źródło, werdykt (`zgodny` / `rozbieżny` / `niezweryfikowany`), wyjaśnienie.

## 6. Critical Path

1. Uzgodnić bilans liczebności (cel 1).
2. Wylosować próbę i zapisać jej skład.
3. Pobrać drugie źródła (ISAP HTML, pełne `GET /acts`, ramka z PDF).
4. Porównać parametry.
5. Zweryfikować wykluczenia (cel 2).
6. Zapisać `wyniki.json` i raport z rozbieżnościami i przyczynami.
7. Przegląd wyników przez autora.

Warunek ukończenia: raport jest zatwierdzony przez autora, a rozbieżności mają przyczyny lub zgłoszone poprawki.

## 7. Control Gates

| # | Bramka | Warunek zaliczenia | Weryfikacja | Blokuje |
| --- | --- | --- | --- | --- |
| G1 | Bilans | zbiór + wykluczone (według kategorii) = liczba z niezależnego zapytania, różnica 0 | skrypt x001 | zamknięcie S005 |
| G2 | Brzmienie | 100/100 zgodnych | skrypt + ISAP HTML | zamknięcie S005 |
| G3 | Ostatni t.j. | ≥ 98/100 zgodnych, reszta wyjaśniona | skrypt | zamknięcie S005 |
| G4 | Liczba zmian | ≥ 95/100 zgodnych, reszta wyjaśniona | skrypt | zamknięcie S005 |
| G5 | Zmiany po t.j. | każda różnica względem „Opracowano na podstawie” wyjaśniona | raport | zamknięcie S005 |
| G6 (negatywna) | Brak fałszywych wykluczeń | 0 ustaw merytorycznych wśród 70 wylosowanych wykluczonych | przegląd treści (drugie narzędzie) | zamknięcie S005 |
| G7 (negatywna) | Brak „zgodności z braku danych” | żaden parametr bez danych w drugim źródle nie jest liczony jako zgodny | przegląd kodu x001 | raport |

Progi G3 i G4 są propozycją do zatwierdzenia przez autora.

## 8. Expected Outcome

- **Efekt bezpośredni:** wiemy, na ile można ufać tabeli w README i doborowi aktów.
- **Efekt mierzalny:** odsetek zgodności dla każdego parametru i liczba wykrytych błędów doboru.
- **Skutki uboczne:** prawdopodobne poprawki S002 i S004, np. rozszerzenie `NOT_AMENDING` albo inna definicja „zmian po t.j.”.
- **Wycofanie:** nie dotyczy, bo eksperyment nie zmienia danych.

## 9. Additional Information

- **Odrzucone alternatywy:** weryfikacja całego zbioru zamiast próby, bo jako pierwszy krok jest zbyt kosztowna. Odrzucona też weryfikacja tym samym zapytaniem API, które dało dane, bo nie byłaby niezależna.
- **Otwarte pytania:**
  - Czy progi G3/G4 są właściwe?
  - Kto lub co jest drugim narzędziem weryfikacji: inny model AI, przegląd ręczny czy oba?
  - Czy definicję „zmian po t.j.” zmienić na „zmiany ogłoszone po t.j. i nieuwzględnione w tekście ujednoliconym”?
- **Źródła:** ISAP, API ELI, art. 16 ustawy o ogłaszaniu aktów normatywnych (teksty jednolite).
- **Zmiany w trakcie realizacji:**
  - Strony ISAP `DocDetails` blokują automatyczne zapytania (HTTP 403), więc ich nie użyliśmy. Drugim źródłem były listowanie roczne API, szczegóły aktu, relacje odwrotne, ramka PDF odczytana przez pdftotext oraz treść aktów.
  - Drugim narzędziem są deterministyczne kontrole (inne ścieżki API, inny parser PDF). Modelu AI nie użyto, bo nie był potrzebny.
  - Rozbieżności z próby (Kodeks wykroczeń, DU/1992/451) doprowadziły do dwóch kontroli całego korpusu: K1 (aktualność tekstu ujednoliconego) i K2 (czytelność tekstu).

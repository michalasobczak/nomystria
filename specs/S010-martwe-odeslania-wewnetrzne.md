# S010 — Reguła R1: martwe odesłania wewnętrzne

- **Status:** dostarczona (wynik: [`kontrole/x003/RAPORT.md`](../kontrole/x003/RAPORT.md): 2 martwe odesłania)
- **Data:** 2026-11-05
- **Powiązane:** MANIFEST M12, S002, S007

## 1. TL;DR

Pierwsza reguła sprawdzana na wielu ustawach: **przepis odsyła do „art. N” tej samej ustawy, a artykułu N w niej nie ma.** Sprawdzamy 1147 ustaw uchwalonych lub zmienianych w 1989 r. lub później. Każde trafienie potwierdzamy drugim narzędziem, czyli surowym tekstem PDF odczytanym przez pdftotext, żeby odrzucić błędy naszej konwersji. Wynik jest w `kontrole/x003/` i na stronie jako znaleziska kategorii „wada”.

## 2. Abstract

Po wycofaniu S006 (MANIFEST M12) zaczynamy od reguły, która nie wymaga interpretacji. Reguła polega na porównaniu numeru w odesłaniu ze spisem artykułów tej samej ustawy.

Ryzyko leży w rozpoznaniu, czy odesłanie jest wewnętrzne. Polskie ustawy często odsyłają do artykułów innych aktów („art. 5 ustawy z dnia…”, „art. 42 Kodeksu cywilnego”, „art. 5 k.p.a.”). Przepisy zmieniające cytują też artykuły ustaw zmienianych („w art. 5 ust. 2 otrzymuje brzmienie”). Reguła ma więc działać zachowawczo: lepiej pominąć wątpliwe odesłanie niż zgłosić fałszywe.

## 3. Objective

- **Cele:**
  - wykryć odesłania „art. N” bez wskazania innego aktu, gdy w ustawie nie ma artykułu N;
  - potwierdzić każde trafienie w surowym tekście PDF;
  - opublikować wyniki ze statystyką.
- **Poza zakresem:**
  - odesłania do ustępów, punktów i liter (reguła nr 8 z listy);
  - odesłania do innych aktów (reguła 3);
  - kolejne numery w wyliczeniach („art. 5, 7 i 9”): sprawdzamy tylko pierwszy;
  - zakresy („art. 5–9”): sprawdzamy oba krańce.
- **Kryteria sukcesu:** bramki G1–G5.

## 4. Artefact Inventory

| Artefakt | Rodzaj | Stan |
| --- | --- | --- |
| `dane/ustawy/**` (zakres: rok ≥ 1989 albo rok ostatniej zmiany ≥ 1989) | dane (wejście) | istnieje |
| `.cache/pdf/*` (surowy tekst przez pdftotext) | dane (drugie narzędzie) | istnieje |
| `eksperymenty/x003-martwe-odeslania/x003.py` | kod | do utworzenia |
| `kontrole/x003/znaleziska.json`, `kontrole/x003/RAPORT.md`, `kontrole/x003/odrzucone.json` | dane i dokument | do utworzenia |
| `tests/test_x003.py` | testy | do utworzenia |

## 5. Functional Domain Changes

- **Spis artykułów:** wiersze zaczynające się od „Art. N.” w treści ustawy. Nie liczymy akapitów cytowanych („„Art. …”), przypisów ani artykułów z numeracją rzymską.
- **Pomijane fragmenty:**
  - artykuły zmieniające inne ustawy, czyli takie, których treść zawiera „wprowadza się następujące zmiany” albo zaczyna się od „W ustawie z dnia”;
  - akapity cytowane;
  - sekcja przypisów.
- **Odesłanie zewnętrzne (pomijane):** po „art. N” (z ewentualnymi „ust.”, „pkt”, „lit.”, „§”, numerami i spójnikami) w ciągu 90 znaków występuje wskazanie innego aktu, np. „ustawy”, „ustawie”, „Kodeksu”, „k.c.”, „k.p.a.”, „rozporządzenia”, „dyrektywy”, „Traktatu”, „Konstytucji”, „Konwencji”, „umowy”, „Prawa …”, „Ordynacji”, „Statutu”, „regulaminu”, „decyzji”. Wyjątek: „niniejszej ustawy” i „tej ustawy” oznaczają odesłanie wewnętrzne.
- **Potwierdzenie (drugie narzędzie):** w tekście z pdftotext szukamy nagłówka „Art. N.”. Jeśli go nie ma, trafienie jest potwierdzone. Jeśli jest, problem leży w konwersji, a nie w ustawie: trafienie trafia do `odrzucone.json` jako uwaga do S003.

## 6. Critical Path

1. Skrypt, który dla każdej ustawy buduje spis artykułów i wykrywa odesłania.
2. Potwierdzenie w pdftotext.
3. Ręczny przegląd próbki 20 trafień i poprawki reguły.
4. Ponowny przebieg.
5. Publikacja i raport.

## 7. Control Gates

| # | Bramka | Warunek zaliczenia | Weryfikacja | Blokuje |
| --- | --- | --- | --- | --- |
| G1 | Zakres | sprawdzono wszystkie ustawy z zakresu (1147) | raport | publikację |
| G2 | Cytat | każde znalezisko ma dosłowny cytat z pliku ustawy zawierający odesłanie | `tests/test_x003.py` | publikację |
| G3 | Potwierdzenie | każde znalezisko jest potwierdzone w pdftotext (brak „Art. N.” w surowym tekście) | skrypt + test | publikację |
| G4 (negatywna) | Brak odesłań zewnętrznych | w próbie 20 losowych znalezisk 0 odesłań do innych aktów (przegląd) | raport | publikację |
| G5 (negatywna) | Kontrola na znanej ustawie | ustawa o fundacji rodzinnej (DU/2023/326) daje 0 znalezisk (wynik z x002) | test | publikację |

## 8. Expected Outcome

- **Efekt bezpośredni:** lista ustaw z martwymi odesłaniami wewnętrznymi, widoczna na stronie (przełącznik „Tylko ustawy ze znaleziskami”).
- **Efekt mierzalny:** liczba znalezisk, liczba ustaw, których dotyczą, i precyzja z przeglądu próbki.
- **Skutki uboczne:** trafienia odrzucone przez pdftotext pokażą błędy konwertera.
- **Wycofanie:** usunięcie `kontrole/x003/`.

## 9. Additional Information

- **Odrzucone alternatywy:** analiza AI (wycofana w S006). Odrzucona też reguła bez potwierdzenia drugim narzędziem.
- **Ryzyka:**
  - artykuły z numeracją z indeksem górnym („art. 22¹”) po konwersji mają postać „221” po obu stronach porównania, więc nie dają fałszywych trafień, ale mogą ukryć prawdziwe;
  - odesłania do uchylonych artykułów to osobna reguła (R2).

## Zmiany w trakcie realizacji (2026-11-05)

- **Bez PDF.** Właściciel zdecydował, że analizujemy wyłącznie wersję tekstową, bo w PDF-ach przeszkadza dzielenie wyrazów i podział na strony. Potwierdzanie przez pdftotext (G3) zastąpiono kontrolą całego tekstu: numer nie występuje jako „Art. N.” nigdzie, także w cytatach i przypisach.
- **Trzy etapy** (na wniosek właściciela):
  1. skrypt znajduje kandydatów;
  2. filtr zgrubny zawęża ich do około 50;
  3. model ocenia każdego kandydata z tekstem ustawy w kontekście.

  Wynik: 531 → 48 → 2. Szczegóły są w raporcie.
- **Kolejne poprawki reguły** po przeglądach próbek. Każda wyeliminowała klasę fałszywych trafień:
  - podział na zdania po skrótach „art.” i „ust.”;
  - zbyt szeroka lista wskazań innego aktu („prawa”, „umowy”);
  - zdania mieszane z „niniejszą ustawą”;
  - zakresy przy kwotach („art. 18 – 300 000 zł”);
  - zbiorcze nagłówki „Art. 13–22. (pominięte)”;
  - punkty nowelizacji i cytaty;
  - punkty wyliczeń dziedziczące akt.

  Pierwszy przebieg dał 4173 trafienia, ostatni 531.
- **G4** zastąpiono oceną modelem wszystkich 48 kandydatów z etapu 2. Precyzja skryptu wyniosła ok. 4% (2/48), co uzasadnia etap z modelem.

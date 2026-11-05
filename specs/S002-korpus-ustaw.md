# S002 — Korpus: Konstytucja i obowiązujące ustawy w aktualnym brzmieniu

- **Status:** dostarczona
- **Data:** 2026-11-05
- **Powiązane:** S003 (konwersja), S004 (tabela)

## 1. TL;DR

Katalog `dane/` z Konstytucją RP i wszystkimi obowiązującymi ustawami merytorycznymi z Dziennika Ustaw w aktualnym brzmieniu. Format to Markdown z metadanymi YAML plus indeks CSV. Całość buduje skrypt `skrypty/pobierz.py`. Potwierdzenie: testy w `tests/test_korpus.py`.

## 2. Abstract

Do analizy struktury prawa potrzebny jest kompletny tekst obowiązujących ustaw w formie tekstowej, a nie w PDF. ISAP udostępnia przez API ELI metadane każdego aktu i jego pliki tekstowe. Plik `U` to tekst ujednolicony Kancelarii Sejmu, `T` to tekst w składzie Kancelarii, `O` to akt ogłoszony, a `H` to HTML tekstu pierwotnego.

Tekst jednolity, czyli obwieszczenie Marszałka Sejmu w Dz. U., jest urzędowy, ale opisuje stan na dzień obwieszczenia. Tekst ujednolicony bierze ostatni tekst jednolity i dopisuje późniejsze nowelizacje. Jest najbardziej aktualny, ale nie jest źródłem prawa (MANIFEST M4). Dla ustaw zmienianych wybraliśmy tekst ujednolicony.

Historia decyzji:

1. Pierwsza wersja brała każdą obowiązującą ustawę, która ma plik `U`, czyli 1426 aktów. Właściciel zauważył, że to w dużej części nowelizacje („o zmianie ustawy…”), które też mają własne teksty ujednolicone. Odrzuciliśmy je, bo ich treść jest już w tekście ustawy zmienianej.
2. Pierwszy filtr nowelizacji obejmował tylko „o zmianie ustawy / ustaw / niektórych ustaw”. Przegląd wyników pokazał inne formy: „o zmianie niektórych przepisów…”, „o zmianie Kodeksu…”, „w sprawie zmiany dekretu…”, „zmieniająca ustawę…”, „uchylająca…”, „o uchyleniu…”, „o zmianach w…”. Filtr rozszerzyliśmy i dodaliśmy wyjątek dla „o zmianie imienia i nazwiska”.
3. Ustawy, których nigdy nie zmieniano, nie mają tekstu ujednoliconego, a ich tekst pierwotny jest aktualny. Właściciel zdecydował, że wchodzą do zbioru jako `brzmienie: pierwotne`.

## 3. Objective

- **Cele:**
  - Konstytucja w `dane/konstytucja.md`;
  - każda ustawa z Dz. U., która spełnia trzy warunki: ma `inForce=1`, nie ma statusu uchylenia ani wygaśnięcia i nie jest nowelizacją. Ma też plik `U` (brzmienie ujednolicone) albo status `obowiązujący` bez `U` i nie jest ustawą ratyfikacyjną (brzmienie pierwotne z `T`, a w razie braku z `O`);
  - nagłówek YAML z metadanymi w każdym pliku i `dane/indeks.csv`.
- **Poza zakresem:** rozporządzenia i inne akty niebędące ustawami, Monitor Polski, historia wersji aktów, ustawy ratyfikacyjne i akty jednorazowe („o nadaniu nazwy…”, „o wypowiedzeniu…”).
- **Kryteria sukcesu:** wszystkie bramki z sekcji 7 są zaliczone.

## 4. Artefact Inventory

| Artefakt | Rodzaj | Stan |
| --- | --- | --- |
| API ELI `api.sejm.gov.pl/eli/acts/search`, `/acts/{ELI}`, `/acts/{ELI}/text/{typ}/{plik}` | zewnętrzne | istnieje |
| `skrypty/pobierz.py` | kod | istnieje |
| `skrypty/requirements.txt` | konfiguracja | istnieje |
| `dane/konstytucja.md` | dane | istnieje |
| `dane/ustawy/<rok>/<rok>-<poz>-<slug>.md` | dane | istnieje |
| `dane/indeks.csv` | dane | istnieje |
| `.cache/pdf/*.pdf`, `.cache/pdf/stan.json` | cache (poza repo) | istnieje |
| `tests/test_korpus.py`, `tests/test_wybor_aktow.py` | testy | istnieje |

## 5. Functional Domain Changes

**Reguły doboru** (funkcje `list_acts`, `is_amending`, `short_title`):

- statusy pomijane: `uchylony`, `uchylony wykazem`, `uznany za uchylony`, `wygaśnięcie aktu`, `brak mocy prawnej`;
- nowelizacja to skrócony tytuł (bez „Ustawa z dnia … r.”), który pasuje do `^(o zmianie|o zmianach|w sprawie zmiany|zmieniająca|uchylająca|o uchyleniu)\b`, z wyjątkiem pozycji z listy `NOT_AMENDING`;
- ustawa ratyfikacyjna to tytuł pasujący do `^(o ratyfikacji|o wypowiedzeniu|w sprawie (przystąpienia|zatwierdzenia|ratyfikacji))\b`.

**Brzmienie:**

- `ujednolicone`, gdy jest plik `U`;
- `pierwotne`, gdy ustawa nie ma aktów zmieniających;
- `pierwotne (zmieniana)`, gdy ISAP zna akty zmieniające, ale nie ma tekstu ujednoliconego. Tekst może wtedy być nieaktualny (MANIFEST M3).

**Ścieżka pliku:** rok i pozycja ogłoszenia pierwotnego (MANIFEST M5), np. Kodeks karny leży w `dane/ustawy/1997/1997-0553-kodeks-karny.md`.

**Metadane:** `tytul`, `eli`, `adres_publikacyjny`, `status`, `brzmienie`, `data_aktu`, `data_wejscia_w_zycie`, `tekst_ujednolicony_z_dnia`, `opracowano_na_podstawie`, pola z S004, `slowa_kluczowe`, `zrodlo_pdf`, `isap`.

**Normalizacja:** białe znaki w tytułach z API są sprowadzane do pojedynczych spacji. API zwróciło tytuł DU/2004/625 ze znakiem nowej linii.

**Odporność:** do 5 ponowień z wykładniczym odstępem. Plik zapisujemy przez `.part`, a potem `rename`. PDF-y pobieramy ponownie tylko przy zmianie `changeDate`. Błąd pojedynczego aktu nie przerywa przebiegu i trafia do raportu. Pliki aktów, które wypadły z listy, są usuwane tylko w pełnym przebiegu (bez `--only` i `--limit`).

## 6. Critical Path

1. Pobrać listę ustaw (`search?publisher=DU&type=Ustawa&inForce=1`, stronicowanie po 500).
2. Odfiltrować akty według reguł z sekcji 5.
3. Pobrać PDF-y do `.cache/pdf`.
4. Przekonwertować je (S003) i zapisać Markdown z metadanymi.
5. Zapisać `indeks.csv` i usunąć pliki nieaktualne.

Warunek ukończenia: pełny przebieg kończy się bez błędów, a bramki G1–G7 przechodzą.

## 7. Control Gates

| # | Bramka | Warunek zaliczenia | Weryfikacja | Blokuje |
| --- | --- | --- | --- | --- |
| G1 | Kompletność indeksu | każdy wiersz `indeks.csv` ma istniejący plik, a każdy plik w `dane/ustawy` ma wiersz | `tests/test_korpus.py` | commit danych |
| G2 | Konstytucja | `dane/konstytucja.md` istnieje i zawiera „Art. 1. Rzeczpospolita Polska jest dobrem wspólnym wszystkich obywateli.” | test | commit danych |
| G3 | Aktualność kodeksu | Kodeks karny ma `brzmienie: ujednolicone` i zawiera „Art. 190a.” | test | commit danych |
| G4 (negatywna) | Brak nowelizacji | żaden tytuł w indeksie nie jest nowelizacją według `is_amending` | test | commit danych |
| G5 (negatywna) | Brak ratyfikacji w brzmieniu pierwotnym | żaden akt `pierwotne*` nie pasuje do `TREATY_RE` | test | commit danych |
| G6 | Reguły tytułów | przypadki brzegowe w `tests/test_wybor_aktow.py` (np. „o zmianie imienia i nazwiska” to nie nowelizacja, a tytuł bez „Ustawa” i „dnia” jest poprawnie skracany) | test | commit kodu |
| G7 | Pełny przebieg | `skrypty/pobierz.py` kończy z „błędów: 0” | log przebiegu | commit danych |

## 8. Expected Outcome

- **Efekt bezpośredni:** tekstowy korpus obowiązujących ustaw z 2026-11-05. W wersji dostarczonej ma 1177 aktów: Konstytucję i 1176 ustaw. 936 ma brzmienie ujednolicone, 224 pierwotne, a 17 brzmienie „pierwotne (zmieniana)”.
- **Efekt mierzalny:** 0 nowelizacji w zbiorze (G4), 0 błędów konwersji (G7).
- **Skutki uboczne:** ok. 140 MB tekstu w repozytorium, a pliki zmieniają się przy każdej aktualizacji tekstów ujednoliconych.
- **Wycofanie:** usunięcie `dane/`, które da się w pełni odtworzyć skryptem.

## 9. Additional Information

- **Odrzucone alternatywy:**
  - Urzędowe teksty jednolite z Dz. U. jako główne źródło. Są nieaktualne między obwieszczeniami. Ich adres i data są w metadanych (S004).
  - HTML (`H`) jako źródło. Istnieje tylko dla tekstu pierwotnego, a nie dla ujednoliconego.
  - Przechowywanie PDF-ów w repozytorium. Wykluczone przez MANIFEST M7, bo zajęłyby ok. 700 MB.
  - Katalogi według tytułów bez roku. Właściciel wybrał rok ustawy, bo ta ścieżka jest stabilna.
- **Dług techniczny:** filtr nowelizacji opiera się na tytułach. Ustawa merytoryczna o tytule „o zmianie …” wymaga dopisania do `NOT_AMENDING`.
- **Zależności zewnętrzne:** dostępność i format API ELI Sejmu.
- **Otwarte pytania:** czy dołączyć rozporządzenia i akty z Monitora Polskiego.

# CHANGELOG

Chronologiczny zapis tego, co faktycznie dostarczono. Wpisy są uporządkowane według dat, najnowsze na górze.

## 2026-11-05

### Propozycje specyfikacji S005–S007

- Dodano specyfikacje o statusie „proponowana”:
  - **S005:** weryfikacja ilościowa korpusu i klasyfikacji, czyli jednorazowy test próby 100 ustaw względem niezależnych źródeł (strona ISAP, pełne `GET /acts`, ramka „Opracowano na podstawie”);
  - **S006:** eksperymentalna analiza jednej ustawy pod kątem niespójności, braków, wad, sprzeczności, braku ścieżek alternatywnych i zaniechań, z weryfikacją krzyżową dwoma narzędziami i werdyktem autora;
  - **S007:** strona na GitHub Pages z filtrami i wynikami kontroli z katalogu `kontrole/`.

### README: weryfikacja krzyżowa

- Do opisu sposobu pracy (sekcja „Uwagi”) dopisano, że wyniki są weryfikowane krzyżowo za pomocą różnych narzędzi.

### README: cel i motywacja projektu

- Na początku README dodano cel: identyfikacja sprzeczności, niespójności, luk, wad i braków (w tym brakujących ścieżek alternatywnych) w prawie, aby je opracować indywidualnie i przekazać odpowiednim organom jako propozycje inicjatyw ustawodawczych. Dodano też motywację: częściową dowolność interpretacyjną polskiego, i nie tylko polskiego, prawodawstwa.

### README: sekcja „Uwagi” pod tabelą ustaw

- Ostrzeżenie o eksploracyjnym charakterze projektu i informację o autorze przeniesiono z początku README do nowej sekcji „Uwagi” pod tabelą ustaw. Odświeżanie tabeli (`skrypty/tabela.py`) zachowuje tę sekcję.

### README: autor i sposób pracy

- Dodano informację o autorze inicjatywy (Michał Sobczak, michalasobczak.pl): ustala wytyczne, szablon i schemat działania oraz kontroluje wyniki. Prace są prowadzone automatycznie, z wykorzystaniem sztucznej inteligencji.

### README: adnotacja o charakterze projektu

- Na początku README dodano ostrzeżenie: projekt jest eksploracyjny, teksty są dobierane i konwertowane automatycznie i mogą zawierać błędy oraz nieścisłości, a każdy przypadek trzeba rozpatrywać indywidualnie (MANIFEST M4).

### S004: symbole brzmienia w tabeli

- Kolumna „Brzmienie” w tabeli README zastąpiona wąską kolumną „Br.” z legendą. Na prośbę właściciela, bo tabela się rozjeżdżała. Właściciel sprawdził też symbole tekstowe U / P / PZ, ale wybrał graficzne ● / ○ / ◐.

### Metodyka CDD (backfill)

- Projekt prowadzimy zgodnie z [workwithrondo.com](https://workwithrondo.com).
- Uzupełniono artefakty dla zmian już dostarczonych:
  - `MANIFEST.md`,
  - `specs/` (szablon oraz S001–S004),
  - ten CHANGELOG,
  - testy w `tests/` jako bramki kontrolne,
  - README ze stanem, glosariuszem, architekturą i listą specyfikacji,
  - `CLAUDE.md` z instrukcją dla asystenta.

### S004: tabela ustaw w README

- Nowe pola w metadanych i w `dane/indeks.csv`: `liczba_ustaw_zmieniajacych`, `tekst_jednolity`, `tekst_jednolity_eli`, `tekst_jednolity_z_dnia`, `tekst_jednolity_ogloszony`, `zmian_po_tekscie_jednolitym`. Dane pochodzą z „Akty zmieniające” i „Inf. o tekście jednolitym” w API ELI.
- Tabela wszystkich ustaw jest w README (sekcja „Lista ustaw”) i powstaje skryptem `skrypty/tabela.py`. Pierwsza wersja trafiła do `dane/LISTA.md`, ale na prośbę właściciela przeniesiono ją do README, a plik usunięto.
- **Korekta:** Kodeks karny błędnie podano w rozmowie jako przykład zmian ogłoszonych po tekście jednolitym. Według danych KK takich zmian nie ma. Przykładem jest ustawa o VAT (2 zmiany po t.j. z 2026-09-01).

### S002: korekty doboru aktów

- **Błąd:** pierwszy zbiór (1426 aktów z tekstem ujednoliconym) zawierał 490 ustaw nowelizujących i uchylających. Mają one własne teksty ujednolicone, ale ich treść jest już w ustawach zmienianych. Zgłosił to właściciel. Nowelizacje wyłączono.
- Filtr nowelizacji rozszerzono z „o zmianie ustawy/ustaw/niektórych ustaw” na wszystkie formy: „o zmianie…”, „o zmianach…”, „w sprawie zmiany…”, „zmieniająca…”, „uchylająca…”, „o uchyleniu…”. Wyjątek to „o zmianie imienia i nazwiska”. Poprawiono też skracanie tytułów bez „r.” albo bez „Ustawa z dnia”.
- Dołączono obowiązujące ustawy bez tekstu ujednoliconego (`brzmienie: pierwotne`) na podstawie tekstu `T` w składzie Kancelarii Sejmu, a gdy go brak, aktu ogłoszonego `O`. Ustawy, które ISAP zna jako zmieniane, ale bez tekstu ujednoliconego, mają `brzmienie: pierwotne (zmieniana)`.
- Wyłączono ustawy ratyfikacyjne, w tym przedwojenne „w sprawie przystąpienia / zatwierdzenia …”.
- Pliki w `.cache/pdf` mają w nazwie typ tekstu (`_U`, `_T`, `_O`).
- Normalizacja białych znaków w tytułach: API zwróciło tytuł DU/2004/625 ze znakiem nowej linii, przez co rozjeżdżały się tabela i nagłówek pliku. Błąd wykrył test S004 G2.
- Wynik: 1177 aktów (Konstytucja i 1176 ustaw), w tym 936 ujednoliconych, 224 pierwotne i 17 „pierwotne (zmieniana)”.

### S003: konwerter PDF → Markdown

- `skrypty/pdf2md.py` (PyMuPDF): usuwa nagłówki i stopki stron, wydziela ramkę „Opracowano na podstawie” i datę opracowania, składa akapity, zamienia przypisy na `[^n]`, a tabele na tabele Markdown (komórki składane ze słów, bo `extract()` gubił spacje), oznacza nagłówki systematyki.
- Poprawki po kontroli jakości korpusu:
  - indeksy górne bez przypisu na stronie, np. numery pól formularzy, zostawały jako `\x00`. Teraz zostają tekstem `n)`;
  - daty stopki w formacie DD.MM.RRRR nie były rozpoznawane (241 aktów);
  - starszy układ PDF Konstytucji (nagłówek w jednym wierszu, ramka na marginesie wplatana w treść);
  - rozstrzelone wersaliki „R Z E C Z Y P O S P O L I T E J  P O L S K I E J” są scalane z zachowaniem spacji między słowami.
- Teksty pierwotne mają dzielenie wyrazów, więc konwerter je usuwa (`dehyphenate`) tylko dla nich.

### S002: korpus ustaw

- `skrypty/pobierz.py` pobiera listę obowiązujących ustaw z API ELI, ściąga PDF-y do `.cache/pdf` (ponownie tylko przy zmianie `changeDate`), konwertuje je i zapisuje `dane/konstytucja.md`, `dane/ustawy/<rok>/…md` oraz `dane/indeks.csv`.
- Wybrano teksty ujednolicone Kancelarii Sejmu zamiast urzędowych tekstów jednolitych, bo są aktualniejsze. Nie są źródłem prawa, co README mówi wprost.
- Katalogi według roku ustawy pierwotnej, zgodnie z decyzją właściciela.

### S001: repozytorium

- Utworzono `github.com/michalasobczak/nomystria` z README (nomos + mysterium) i `.gitignore`. Repozytorium było prywatne, a na prośbę właściciela stało się publiczne.

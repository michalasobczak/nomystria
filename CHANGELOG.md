# CHANGELOG

Chronologiczny zapis tego, co faktycznie dostarczono. Wpisy są uporządkowane według dat, najnowsze na górze.

## 2026-11-05

### S007: przełącznik „uchwalone lub zmieniane od 1989 r.”

- Nowe pole `rok_ostatniej_zmiany` (rok ogłoszenia ostatniej ustawy zmieniającej, z ELI) w metadanych, `indeks.csv` i `dane.json`.
- W wyszukiwaniu podstawowym jest przełącznik „Tylko ustawy uchwalone lub zmieniane w 1989 r. lub później”. Obejmuje 1147 z 1177 aktów: 1082 uchwalone w 1989 r. lub później i 65 starszych, ale zmienianych od 1989 r. W oknie szczegółów widać rok ostatniej zmiany.

### Zmiana kierunku: jedna reguła naraz (M12); wycofanie S006 i S009

- Pytanie właściciela o x002-001 ujawniło, że analiza pominęła art. 42 Kodeksu cywilnego (kurator dla osoby prawnej bez organu). Podważyło to znaleziska x002-001 i x002-003.
- Właściciel wycofał wszystkie znaleziska x002 jako zbyt skomplikowane do automatycznej weryfikacji na tym etapie. Usunięto je razem z diagramem ścieżek:
  - `kontrole/x002/`,
  - `eksperymenty/x002-…`,
  - `strona/sciezki.*`,
  - `tests/test_sciezki.py`, `tests/test_kontrole.py`,
  - kod diagramów w `skrypty/strona.py` i `strona/app.js`.

  Wszystko zostaje w historii git. S006 i S009 mają status „wycofana” z opisem wniosków.
- Nowa zasada MANIFEST M12: jedna prosta, deterministyczna reguła naraz, sprawdzana na wielu ustawach.
- Sprawdzono, że wszystkie 14 obowiązujących kodeksów jest w korpusie: KC, KPC, KRO, KP, KK, KPK, KKW, KKS, KSH, KPA, Kodeks wykroczeń, KPW, Kodeks morski i Kodeks wyborczy.

### S007: wersjonowanie plików strony

- Właściciel nie widział linku do diagramu, bo przeglądarka trzymała starą wersję `app.js` i `dane.json` (GitHub Pages: `cache-control: max-age=600`). Workflow wstawia teraz skrót commita w miejsce `__WERSJA__` w HTML, a pliki JS, CSS i dane są ładowane z `?v=<commit>`. Link do diagramu ma postać wyraźnego przycisku.

### S009: diagram ścieżek i numeracja znalezisk

- Znaleziska mają ciągłą numerację (1–18) w liście pod wierszem i w oknie szczegółów.
- Nowa strona `sciezki.html` pokazuje diagram drzewa decyzyjnego w układzie „drabiny decyzji”, symulator przechodzenia ścieżki z cytatami przepisów i tabelę wszystkich ścieżek. Pierwszy diagram: `kontrole/x002/sciezki/x002-001.json` (pusty zarząd fundacji rodzinnej, art. 26, 61, 64, 71 i 114). Ma 15 węzłów i 9 ścieżek: 5 istnieje, 3 luki, 1 zależy od statutu. Link do diagramu jest przy znalezisku.
- **W trakcie:**
  - zwykły układ drzewa był za szeroki (2134 px), więc zastąpiła go „drabina decyzji”;
  - etykiety wachlarza odpowiedzi nachodziły na siebie i przeniesiono je nad węzły docelowe;
  - tekst kroku miał odwróconą relację („zarząd powołuje zgromadzenie”). Pierwsza poprawka („Nowy zarząd powołuje zgromadzenie…”) nadal była niejasna, co zgłosił właściciel. Obecny tekst opisuje wprost błędne koło w stronie biernej: nowy zarząd może zostać powołany tylko przez zgromadzenie, a zgromadzenie jest zwoływane przez zarząd, którego brak.
- Testy `tests/test_sciezki.py` sprawdzają dosłowne cytaty, poprawne przepisy, strukturę drzewa, brak cykli i powiązanie ze znaleziskiem.

### S006: znaleziska bez werdyktów

- Decyzja właściciela: znaleziska publikujemy tak po prostu, bez werdyktów autora. Usunięto pola `werdykt_autora` i `komentarz_autora` (dane, generator strony, format `kontrole/`), filtr „Werdykt autora” i oznaczenia werdyktu na stronie oraz bramkę S006 G5. S006 ma status „dostarczona”.

### S007: rozwijana lista znalezisk

- Na stronie liczba znalezisk w tabeli jest przyciskiem. Kliknięcie rozwija pod wierszem ustawy listę znalezisk: kategorię, przepisy, wagę, informację o weryfikacji krzyżowej, werdykt autora, opis, cytaty oraz uzasadnienie i źródła w zwijanym bloku. Kliknięcie w liście nie otwiera okna szczegółów.

### S006: analiza ustawy o fundacji rodzinnej (x002)

- Ustawę o fundacji rodzinnej (DU/2023/326) wybrano jako dane testowe dla strony, na prośbę właściciela.
- Wykonano:
  - kontrole mechaniczne M1 (odesłania) i M2 (delegacje a akty wykonawcze), które dały 0 znalezisk;
  - dwa niezależne przebiegi AI (Claude Opus i Claude Sonnet, po 12 znalezisk).
- Walidacja cytatów i przepisów odrzuciła 0 znalezisk. Po scaleniu jest ich 18, z czego 5 potwierdzonych krzyżowo.
- Dopasowanie przebiegów poprawiono w trakcie: z dopasowania „jeden do jednego” po artykułach na podobieństwo zbiorów „artykuł + ustęp” z premią za kategorię, przy czym jedno znalezisko A może zebrać kilka znalezisk B.
- Wynik jest w `kontrole/x002/`: `znaleziska.json`, `RAPORT.md`, surowe przebiegi i kontrole mechaniczne. Czeka na werdykt autora.

### S008: aktualność i czytelność tekstów

- K1: 12 ustaw ma brzmienie **jednolite (◆)**, czyli tekst obwieszczenia tekstu jednolitego z Dz. U. (PDF T albo O), bo tekst ujednolicony ISAP był starszy niż ostatni t.j. Dotyczy to m.in. Kodeksu wykroczeń, Prawa ochrony środowiska i ustawy o finansach publicznych.
- K2: 25 ustaw ma tekst z HTML z API ELI (`skrypty/html2md.py`), a 5 z OCR (`skrypty/ocr.py`: tesseract z modelem `pol`, geometria z warstwy PDF). Powód to uszkodzone kodowanie czcionek w PDF.
- Nowe pola `zrodlo_tekstu` i `uwagi` w metadanych, `indeks.csv` i na stronie. Symbol ◆ jest w tabeli i w filtrach.
- Bramki S008 G1–G5 są w `tests/test_korpus.py`. Ponowna kontrola x001 dała K1 = 0, K2 = 0, t.j. 100/100 i zmiany po t.j. 69/69.
- **Błąd w trakcie:** ramka „Opracowano na podstawie” z OCR była odrzucana jako nieczytelna, bo składa się głównie z cyfr. Teraz sprawdzamy w niej tylko znaki sterujące.

### S005: weryfikacja ilościowa (x001)

- Skrypt `eksperymenty/x001-weryfikacja-100/x001.py` zapisał wyniki do `kontrole/x001/`: `wyniki.json` (widoczne na stronie), `bilans.json`, `wykluczenia.json` i `RAPORT.md`.
- Wynik:
  - **G1:** bilans 6092 = 6092. Listowanie roczne uzgodnione: +1237 aktów „bez statusu”, −4 akty z `inForce=1` i statusem „uchylony”.
  - **G2:** brzmienie 100/100.
  - **G3:** t.j. 99/100.
  - **G4:** liczba zmian 100/100 (z relacją odwrotną).
  - **G5:** wszystkie różnice w zmianach po t.j. wyjaśnione.
  - **G6:** 69/70 wykluczeń potwierdzonych treścią, 1 nieczytelne, 0 fałszywych.
- **Wykryte problemy korpusu:**
  - K1: 12 ustaw ma tekst ujednolicony starszy niż ostatni t.j., np. Kodeks wykroczeń i ustawa o finansach publicznych;
  - K2: 29 ustaw ma nieczytelny tekst (uszkodzone kodowanie czcionek w PDF-ach z ISAP).

  Danych nie poprawiano (poza zakresem S005), a ustawy są oznaczone na stronie.
- **Poprawki narzędzia kontrolnego w trakcie:**
  - pdftotext gubił spacje w ramce („z2026”);
  - stopka jest teraz odczytywana według położenia słów (`-bbox`);
  - HTML bywa samą strukturą bez treści;
  - rozszerzono zwroty nowelizujące;
  - nieczytelny tekst daje „niezweryfikowany”, a nie „rozbieżny”.
- Strony ISAP blokują automatyczne zapytania (403), więc zastąpiliśmy je innymi ścieżkami API i relacjami odwrotnymi.

### S007: poprawki strony po uwagach właściciela

- **Błąd:** opcje filtra „Zmiany po t.j.” miały w nawiasach progi „(> 0)” i „(0)”, które wyglądały jak liczniki. Teraz każda opcja (brzmienie, tekst jednolity, zmiany po t.j., weryfikacja, werdykt, przełącznik znalezisk) pokazuje prawdziwą liczbę ustaw, uwzględniającą pozostałe filtry. Pierwsza wersja liczników też była błędna, bo pomijała filtr, dla którego liczyła, i wszędzie pokazywała 1177. Wykryło to sprawdzenie w przeglądarce.
- „Kontrola parametrów” przemianowana na „Weryfikacja metadanych”. Dodano opis (sprawdzenie brzmienia, tekstu jednolitego i liczby zmian w niezależnym źródle, S005) i zrozumiałe wartości: potwierdzone / rozbieżność / nie dało się potwierdzić / nie sprawdzano.
- Wyszukiwanie podstawowe zawiera pole tekstowe i przełącznik „Tylko ustawy ze znaleziskami” (domyślnie wyłączony). Pozostałe filtry są w zwijanej sekcji „Wyszukiwanie zaawansowane” z licznikiem aktywnych filtrów.
- Domyślne sortowanie: data ustawy malejąco. Kolumna „Rok” zastąpiona kolumną „Data”, a do `dane.json` dodano pole `data`.
- Na prośbę właściciela usunięto ze strony ostrzeżenie i informację o autorze. Stopka zawiera tylko link do repozytorium.

### S007: strona opublikowana

- Za zgodą właściciela włączono GitHub Pages (źródło: GitHub Actions). Strona działa pod adresem https://michalasobczak.github.io/nomystria/.
- Pierwsze uruchomienie workflow (przed włączeniem Pages) zakończyło się błędem, a ponowne uruchomienie powiodło się.
- Sprawdzenie opublikowanej strony:
  - G3: filtr ● + „zmiany po t.j. > 0” daje 292 rekordy, tyle samo co CSV;
  - G4: 5 losowych ustaw, każda z 3 linkami (repozytorium, PDF, ISAP), wszystkie się otwierają. ISAP odpowiada `curl` przekierowaniem 307, ale w przeglądarce otwiera właściwą ustawę.

### S007: strona na GitHub Pages (kod)

- `strona/` (`index.html`, `app.js`, `style.css`, bez frameworka) to lista ustaw z filtrami: tytuł/ELI, rok, brzmienie, liczba zmian, tekst jednolity, zmiany po t.j., wynik kontroli, znaleziska. Ma sortowanie, filtry zapisane w adresie URL, okno szczegółów z linkami do pliku, PDF i ISAP, tryb ciemny i układ na telefon.
- `skrypty/strona.py` generuje `dane.json` z `dane/indeks.csv` i `kontrole/`. Waliduje format, a nieznane `eli` przerywa generowanie. Ustawa bez kontroli ma status „brak”, nigdy „zgodny”.
- `kontrole/README.md` opisuje format `wyniki.json` (S005) i `znaleziska.json` (S006).
- `.github/workflows/strona.yml` buduje `_site/` i publikuje przez `actions/deploy-pages`.
- Test lokalny: filtr ● + „zmiany po t.j. > 0” daje 292 rekordy, tyle samo co wyliczenie z CSV (G3). Na szerokości 375 px strona nie przewija się w poziomie. Testy `tests/test_strona.py` wykryły błąd ścieżek w generatorze, który został poprawiony.
- Do zrobienia: włączenie Pages (Settings → Pages → Source: GitHub Actions) i sprawdzenie opublikowanej strony (G4).

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

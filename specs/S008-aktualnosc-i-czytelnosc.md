# S008 — Aktualność i czytelność tekstów (naprawa problemów K1 i K2 z S005)

- **Status:** dostarczona
- **Data:** 2026-11-05
- **Powiązane:** S005 (wykrycie: [`kontrole/x001/RAPORT.md`](../kontrole/x001/RAPORT.md)), S002, S003

## 1. TL;DR

Usuwamy dwa problemy korpusu wykryte w S005:

- **K1.** 12 ustaw miało tekst ujednolicony ISAP starszy niż ostatni urzędowy tekst jednolity. Teraz używamy dla nich tekstu jednolitego z Dz. U. (brzmienie `jednolite`).
- **K2.** 29 ustaw miało nieczytelny tekst z powodu uszkodzonego kodowania czcionek w PDF. Teraz używamy HTML z API ELI, a gdy HTML zawierałby tekst nieaktualny, OCR.

Potwierdzenie: bramki K1 i K2 w `tests/test_korpus.py` oraz ponowne uruchomienie kontroli x001.

## 2. Abstract

S005 pokazała, że tekst ujednolicony nie zawsze jest najaktualniejszy. Gdy Marszałek Sejmu ogłosi nowy tekst jednolity, a Kancelaria nie zaktualizuje jeszcze tekstu ujednoliconego, urzędowy t.j. jest nowszy. Tak było z Kodeksem wykroczeń, ustawą o finansach publicznych i Prawem ochrony środowiska.

Starsze PDF-y z ISAP (głównie lata 1950–1997) mają z kolei czcionki bez poprawnej mapy znaków. Tekst wyciągnięty z nich składa się ze znaków sterujących.

Dla 24 z 29 nieczytelnych ustaw (tekst pierwotny) API ma poprawny HTML z pełną treścią. Dla pozostałych 5 (tekst ujednolicony bez tekstu jednolitego) HTML to tekst pierwotny, który byłby nieaktualny. Dla nich zostaje OCR obrazu strony.

## 3. Objective

- **Cele:**
  - K1: gdy ramka „Opracowano na podstawie” wskazuje inny t.j. niż ostatni albo data tekstu ujednoliconego jest wcześniejsza niż data ostatniego obwieszczenia, bierzemy tekst obwieszczenia t.j.: PDF `T` (skład Kancelarii), a w razie braku `O`. Brzmienie to `jednolite`, w `uwagi` jest wyjaśnienie.
  - K2: gdy tekst jest nieczytelny, dla tekstu pierwotnego bierzemy HTML z API (`text.html`), a dla tekstu ujednoliconego OCR (tesseract, model `pol`) obrazu strony. Brzmienie się nie zmienia.
  - Nowe pola metadanych `zrodlo_tekstu` i `uwagi` (YAML, CSV, strona) oraz symbol ◆ dla brzmienia jednolitego.
- **Poza zakresem:** ręczna korekta błędów OCR, OCR całego korpusu, zastąpienie wszystkich tekstów ujednoliconych tekstami jednolitymi.
- **Kryteria sukcesu:** bramki G1–G5.

## 4. Artefact Inventory

| Artefakt | Rodzaj | Stan |
| --- | --- | --- |
| `skrypty/pobierz.py` (`render`: wybór źródła, `fetch_tj`, `nieczytelny`) | kod | do zmiany |
| `skrypty/html2md.py` (HTML ISAP → Markdown) | kod | do utworzenia |
| `skrypty/ocr.py` (render PyMuPDF + tesseract, geometria z warstwy PDF) | kod | do utworzenia |
| `.cache/tessdata/pol.traineddata` (model OCR z `tesseract-ocr/tessdata_fast`) | zależność (poza repo) | do utworzenia |
| `skrypty/tabela.py`, `skrypty/strona.py`, `strona/` (symbol ◆, pola źródła i uwag) | kod | do zmiany |
| `tests/test_korpus.py` (bramki K1, K2) | testy | do zmiany |

## 5. Functional Domain Changes

- **Brzmienie `jednolite` (◆):** tekst obwieszczenia tekstu jednolitego z Dz. U. Obejmuje samo obwieszczenie z listą zmian i przepisów nieobjętych, a potem załącznik z tekstem ustawy. `tekst_ujednolicony_z_dnia` jest puste, a `opracowano_na_podstawie` wskazuje obwieszczenie.
- **`zrodlo_tekstu`:** `PDF U`, `PDF T`, `PDF O`, `tekst jednolity, PDF T`, `tekst jednolity, PDF O`, `HTML (API ELI)` albo `OCR (tesseract) PDF U`.
- **Nieczytelność:** ponad 20 znaków sterujących albo poniżej 30% liter w treści (bez przypisów). Ramkę „Opracowano na podstawie” sprawdzamy tylko pod kątem znaków sterujących, bo składa się głównie z cyfr.
- **OCR:** z warstwy PDF bierzemy tylko geometrię: linię nagłówka, kreskę przypisów i położenie ramki, którą zamalowujemy przed rozpoznaniem treści. Treść i przypisy rozpoznajemy osobno, a przypisy trafiają do sekcji „Przypisy (OCR)” bez łączenia z odwołaniami. Wynik może zawierać błędy rozpoznania, np. „art. I” zamiast „art. 1”, i ma o tym uwagę.
- **HTML:** jednostki `unit_*` z etykietą `<h3>` i treścią `xText` składamy w akapity w formacie korpusu, a rozdziały (`with-title`) zamieniamy w nagłówki `##`.

## 6. Critical Path

1. Funkcje `nieczytelny`, `tj_z_ramki`, `fetch_tj`.
2. `html2md` i `ocr`.
3. Wybór źródła w `render`.
4. Próba na 4 aktach (Kodeks wykroczeń, Prawo ochrony środowiska, amnestia, DU/1992/451).
5. Pełna przebudowa.
6. Bramki K1/K2 w testach.
7. Ponowna kontrola x001.

## 7. Control Gates

| # | Bramka | Warunek zaliczenia | Weryfikacja | Blokuje |
| --- | --- | --- | --- | --- |
| G1 (K1) | Aktualność | żadna ustawa `ujednolicone` nie ma daty t.u. wcześniejszej niż data ostatniego t.j. ani ramki wskazującej inny t.j. | `tests/test_korpus.py` | commit danych |
| G2 (K2) | Czytelność | żaden plik nie jest nieczytelny według `nieczytelny()` | test | commit danych |
| G3 | Oznaczenie źródła | każdy wiersz indeksu ma `zrodlo_tekstu`, a każdy plik z HTML lub OCR ma wpis w `uwagi` | test | commit danych |
| G4 | Przykład K1 | Kodeks wykroczeń ma brzmienie `jednolite` i treść obwieszczenia Dz.U. 2026 poz. 1372 | test | commit danych |
| G5 | Przykład K2 | ustawa o amnestii (DU/1989/390) zawiera „Art. 1. 1. W sprawach o przestępstwa i przestępstwa skarbowe” | test | commit danych |

## 8. Expected Outcome

- **Efekt bezpośredni:** 12 ustaw ma aktualne brzmienie, a 29 czytelny tekst.
- **Efekt mierzalny:** kontrole K1 i K2 z x001 dają 0 rozbieżności.
- **Skutki uboczne:**
  - przebudowa korpusu wymaga tesseract i modelu `pol`, ale tylko dla kilku aktów (OCR uruchamia się wyłącznie przy nieczytelnym tekście ujednoliconym);
  - teksty z OCR mogą mieć pojedyncze błędy rozpoznania.
- **Wycofanie:** przywrócenie poprzedniej wersji `render`, bo dane da się odtworzyć skryptem.

## 9. Additional Information

- **Odrzucone alternatywy:**
  - Zastąpienie wszystkich tekstów ujednoliconych tekstami jednolitymi, bo t.j. jest zwykle starszy niż t.u.
  - OCR wszystkich 29 nieczytelnych ustaw, bo dla 24 istnieje poprawny HTML.
  - HTML dla 5 ustaw z tekstem ujednoliconym, bo HTML zawiera tekst pierwotny, więc byłby nieaktualny.
- **Zależności zewnętrzne:** tesseract (Homebrew) i model `pol.traineddata` (repozytorium `tesseract-ocr/tessdata_fast`).
- **Dług techniczny:** heurystyka akapitów OCR jest prostsza niż w konwerterze PDF.

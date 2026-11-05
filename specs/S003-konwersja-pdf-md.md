# S003 — Konwersja PDF → Markdown

- **Status:** dostarczona
- **Data:** 2026-11-05
- **Powiązane:** S002

## 1. TL;DR

Konwerter `skrypty/pdf2md.py` zamienia PDF tekstu ujednoliconego lub pierwotnego w czysty Markdown. Każdy przepis jest osobnym akapitem, nie ma nagłówków ani stopek stron, przypisy mają postać `[^n]`, a tabele są tabelami Markdown. Potwierdzenie: testy w `tests/test_pdf2md.py` i `tests/test_korpus.py`.

## 2. Abstract

ISAP udostępnia teksty ujednolicone wyłącznie jako PDF, a `pdftotext` daje tekst z twardo łamanymi wierszami. Do tego dochodzą nagłówki „©Kancelaria Sejmu s. N/M”, stopki z datą i przypisy wymieszane z treścią.

Z próbek wynikło, że PDF-y Kancelarii Sejmu mają powtarzalny układ:

- kreska pod nagłówkiem strony;
- treść ustawy czcionką ok. 12 pt;
- przypisy pod krótką kreską przy lewym marginesie, czcionką ok. 10 pt;
- ramka „Opracowano na podstawie” na prawym marginesie pierwszej strony;
- stopka z datą opracowania.

Teksty pierwotne (`T`, `O`) mają inny skład: czcionkę ok. 10 pt, przypisy ok. 9 pt i dzielenie wyrazów na końcu wiersza.

## 3. Objective

- **Cele:** czytelny tekst z zachowaną treścią (MANIFEST M2), podział na przepisy, przypisy jako przypisy Markdown, tabele, metadane strony tytułowej (data opracowania, podstawa).
- **Poza zakresem:** OCR skanów, odtwarzanie grafik, wzorów i map, semantyczne drzewo jednostek redakcyjnych.
- **Kryteria sukcesu:** bramki G1–G6.

## 4. Artefact Inventory

| Artefakt | Rodzaj | Stan |
| --- | --- | --- |
| `skrypty/pdf2md.py` | kod | istnieje |
| `pymupdf` | zależność | istnieje |
| `tests/test_pdf2md.py` | testy | istnieje |

## 5. Functional Domain Changes

- **Wiersze wizualne:** fragmenty linii PyMuPDF są grupowane po środku wysokości, bo justowanie dzieli wiersz na kilka linii.
- **Usuwane:** wszystko nad kreską nagłówka; wiersze „©Kancelaria Sejmu”, „s. N/M”; stopka z datą (RRRR-MM-DD lub DD.MM.RRRR), którą zapisujemy jako `tekst_ujednolicony_z_dnia`; ramka „Opracowano na podstawie”, którą zapisujemy jako `opracowano_na_podstawie`.
- **Przypisy:** strefa poniżej krótkiej kreski przy lewym marginesie, jeśli pod nią jest tylko tekst o rozmiarze ≤ 92% rozmiaru treści. Indeks górny w treści staje się `[^n]`, gdy na tej stronie jest przypis o tej etykiecie, a w przeciwnym razie zostaje tekstem `n)`, np. numer pola w formularzu. Powtórzona etykieta dostaje sufiks `-sN`.
- **Akapity:** nowy akapit zaczyna się, gdy wiersz rozpoczyna jednostkę („Art. 1”, „1)”, „a)” albo wcięte „§”, „–”, „Rozdział”, …), gdy odstęp jest większy niż 1,25 × typowa interlinia, albo gdy poprzedni wiersz nie sięga prawego marginesu.
- **Nagłówki:** wyśrodkowane „CZĘŚĆ/KSIĘGA/TYTUŁ/DZIAŁ/Rozdział/Oddział/Załącznik” stają się `## …`, a wyśrodkowane pogrubione tytuły stają się `**…**`. Rozstrzelone wersaliki („U S T A W A”) są scalane.
- **Tabele:** `page.find_tables()` na stronach z liniami. Tekst komórek składamy ze słów z ich współrzędnych, bo `extract()` gubi spacje.
- **Dzielenie wyrazów:** tylko dla tekstów pierwotnych (`dehyphenate=True`). W tekstach ujednoliconych łącznik na końcu wiersza jest częścią wyrazu, np. „społeczno-gospodarczy”.
- Bez escapowania „1.” na początku akapitu, żeby surowy tekst pozostał czysty. Wyjątek: wiodący `#`.

## 6. Critical Path

1. Ustalić rozmiar czcionki treści.
2. Dla każdej strony: odciąć nagłówki i stopki, wydzielić ramkę podstawy, tabele i przypisy.
3. Złożyć wiersze w akapity i oznaczyć nagłówki.
4. Dodać przypisy na końcu.

Warunek ukończenia: Kodeks karny, ustawa o VAT i Konstytucja dają poprawny tekst (G1–G4), a cały korpus nie ma śladów nagłówków ani znaków sterujących (G5, G6).

## 7. Control Gates

| # | Bramka | Warunek zaliczenia | Weryfikacja | Blokuje |
| --- | --- | --- | --- | --- |
| G1 | Akapity | w Kodeksie karnym „Art. 1. § 1. Odpowiedzialności karnej podlega ten tylko, kto popełnia czyn zabroniony pod groźbą kary przez ustawę obowiązującą w czasie jego popełnienia.” jest jednym akapitem | test | commit |
| G2 | Metadane strony | KK: `tekst_ujednolicony_z_dnia` ma format RRRR-MM-DD, `opracowano_na_podstawie` zaczyna się od „t.j. Dz. U.” | test | commit |
| G3 | Przypisy | KK ma sekcję „## Przypisy” i każde odwołanie `[^x]` ma definicję `[^x]:` | test | commit |
| G4 | Tabele | ustawa o VAT, załącznik nr 3: wiersz tabeli z „Kawa, herbata” w jednej komórce (słowa ze spacjami) | test | commit |
| G5 (negatywna) | Brak nagłówków stron | żaden plik w `dane/` nie zawiera wiersza zaczynającego się od „©Kancelaria Sejmu” ani „s. N/M” | test | commit danych |
| G6 (negatywna) | Brak znaków sterujących | żaden plik w `dane/` nie zawiera `\x00` | test | commit danych |

## 8. Expected Outcome

- **Efekt bezpośredni:** tekst nadaje się do czytania na GitHubie i do NLP.
- **Efekt mierzalny:** cały korpus przechodzi bez błędów, a Kodeks karny (148 stron) konwertuje się w ok. 3 s.
- **Skutki uboczne:** w złożonych załącznikach (formularze, wzory) tabele mogą być niedokładne, a grafiki giną. Link `zrodlo_pdf` prowadzi do oryginału.
- **Wycofanie:** podmiana konwertera i ponowny przebieg `pobierz.py` z cache.

## 9. Additional Information

- **Odrzucone alternatywy:**
  - `pdftotext -layout`, bo nie rozróżnia przypisów ani nagłówków;
  - `Table.to_markdown()` z PyMuPDF, bo skleja słowa;
  - escapowanie list Markdown, bo zanieczyszcza surowy tekst.
- **Dług techniczny:** heurystyki układu (marginesy, rozmiary czcionek) są dostrojone do składu Kancelarii Sejmu. Nietypowe PDF-y mogą wymagać poprawek. Część PDF-ów wywołuje niegroźny komunikat MuPDF „No default Layer config”.
- **Otwarte pytania:** czy budować drzewo jednostek redakcyjnych (artykuł → ustęp → punkt) jako osobny format, np. JSON.

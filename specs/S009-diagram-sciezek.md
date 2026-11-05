# S009 — Diagram ścieżek przepisów dla znaleziska

- **Status:** dostarczona
- **Data:** 2026-11-05
- **Powiązane:** S006 (znalezisko x002-001), S007 (strona)

## 1. TL;DR

Dla znaleziska typu „luka” albo „brak ścieżki alternatywnej” budujemy drzewo decyzyjne z pytań, kroków i wyników. Każdy węzeł wskazuje przepis i cytuje go dosłownie. Strona `sciezki.html` rysuje drzewo jako diagram. Pozwala przejść ścieżkę krok po kroku i pokazuje wszystkie ścieżki z wynikiem: ścieżka istnieje, luka albo rozstrzyga statut. Pierwszy diagram dotyczy x002-001, czyli pustego zarządu fundacji rodzinnej.

## 2. Abstract

Znalezisko opisane prozą („nie ma trybu na wypadek upływu kadencji…”) trudno sprawdzić bez prześledzenia warunków ustawy. Właściciel poprosił o diagram ścieżek, który pozwala „wyobrazić sobie i przetestować ścieżki tekstu”.

Drzewo decyzyjne z cytatami robi z opisu sprawdzalną strukturę. Każdą odpowiedź można zweryfikować w przepisie, a liczba ścieżek kończących się luką jest jawna.

## 3. Objective

- **Cele:**
  - format `kontrole/<eksperyment>/sciezki/<id znaleziska>.json`;
  - strona `strona/sciezki.html?id=<id>` z diagramem, symulatorem i tabelą wszystkich ścieżek;
  - link „Diagram ścieżek” przy znalezisku na stronie głównej;
  - ciągła numeracja znalezisk (1, 2, 3, …) w liście i w oknie szczegółów.
- **Poza zakresem:** automatyczne generowanie diagramów z tekstu ustawy, edycja diagramu na stronie, grafy z cyklami.
- **Kryteria sukcesu:** bramki G1–G5.

## 4. Artefact Inventory

| Artefakt | Rodzaj | Stan |
| --- | --- | --- |
| `kontrole/x002/sciezki/x002-001.json` | dane | do utworzenia |
| `strona/sciezki.html`, `strona/sciezki.js`, `strona/sciezki.css` | kod | do utworzenia |
| `skrypty/strona.py` (kopiowanie diagramów obok `dane.json`, pole `diagram` przy znalezisku) | kod | do zmiany |
| `strona/app.js` (numeracja, link do diagramu) | kod | do zmiany |
| `.github/workflows/strona.yml` (kopiowanie wszystkich plików strony) | konfiguracja | do zmiany |
| `tests/test_sciezki.py` | testy | do utworzenia |

## 5. Functional Domain Changes

**Węzeł** ma pola:

- `typ`: `pytanie` (z `odpowiedzi`: etykieta i węzeł docelowy), `krok` (z `dalej`) albo `wynik` (z `wynik`: `ok` / `luka` / `statut`);
- `tekst`;
- `przepisy`;
- `cytaty`, czyli dosłowne fragmenty ustawy.

**Diagram** ma układ „drabiny decyzji”. Gdy pytanie ma dwie odpowiedzi, a jedna z nich kończy ścieżkę, wynik stoi obok pytania. Dalsza część schodzi w dół po prostej osi, a rozgałęzienia idą w prawo.

**Symulator** pokazuje bieżące pytanie z przepisem i cytatem oraz przyciski odpowiedzi. Kliknięcie węzła diagramu albo wiersza tabeli ustawia trasę do tego punktu. Bieżąca trasa jest podświetlona na diagramie.

**Wynik dla x002-001:** 9 ścieżek. W 5 ścieżka istnieje (fundator, rada nadzorcza, rezygnacja, śmierć, odwołanie z jednoczesnym powołaniem). 3 to luki (upływ kadencji, odwołanie bez powołania, odmowa osoby wskazanej w testamencie). 1 zależy od statutu.

## 6. Critical Path

1. Przeczytać przepisy art. 26, 61, 64, 71 i 114.
2. Zbudować model JSON z cytatami.
3. Test cytatów i struktury.
4. Strona: diagram, symulator, tabela.
5. Link ze znaleziska i numeracja.
6. Publikacja.

## 7. Control Gates

| # | Bramka | Warunek zaliczenia | Weryfikacja | Blokuje |
| --- | --- | --- | --- | --- |
| G1 | Cytaty | każdy cytat w diagramie występuje dosłownie w tekście ustawy, a każdy przepis istnieje | `tests/test_sciezki.py` | publikację |
| G2 | Struktura | start istnieje, każda odpowiedź prowadzi do istniejącego węzła, wyniki nie mają dzieci, pytania mają ≥ 2 odpowiedzi | test | publikację |
| G3 (negatywna) | Brak cykli i sierot | każdy węzeł jest osiągalny ze startu i ma najwyżej jednego rodzica | test | publikację |
| G4 | Powiązanie | każdy diagram odpowiada istniejącemu znalezisku | test | publikację |
| G5 | Strona | dla x002-001 strona pokazuje 15 węzłów i 9 ścieżek (5/3/1), a wybór ścieżki 6 kończy się wynikiem „luka” | sprawdzenie w przeglądarce | zamknięcie S009 |

## 8. Expected Outcome

- **Efekt bezpośredni:** znalezisko x002-001 można przejść krok po kroku i sprawdzić każdą odpowiedź w przepisie.
- **Efekt mierzalny:** 3 z 9 ścieżek kończą się luką.
- **Skutki uboczne:** diagram jest interpretacją przepisów. Odpowiedzi na pytania, np. „czy zgromadzenie powołało nowy zarząd na tym samym posiedzeniu”, to scenariusze faktyczne, a nie treść ustawy.
- **Wycofanie:** usunięcie plików `sciezki*` i pola `diagram`.

## 9. Additional Information

- **Odrzucone alternatywy:**
  - Mermaid lub inne biblioteki z CDN, bo to zbędna zależność (MANIFEST M9) i trudniej podświetlić trasę.
  - Zwykły układ drzewa (wszystkie liście w jednym rzędzie), bo był za szeroki: 2134 px wobec obecnych ok. 1680 px.
- **Otwarte pytania:** czy diagramy dodawać do każdego znaleziska typu luka lub brak ścieżki alternatywnej.

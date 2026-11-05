# x002: eksperymentalna analiza ustawy o fundacji rodzinnej (S006)

- **Data:** 2026-11-05
- **Specyfikacja:** [S006](../../specs/S006-analiza-jednej-ustawy.md)
- **Ustawa:** Ustawa z dnia 26 stycznia 2023 r. o fundacji rodzinnej (DU/2023/326), tekst ujednolicony z 2023-10-17, 149 artykułów ([plik](../../dane/ustawy/2023/2023-0326-o-fundacji-rodzinnej.md))
- **Skrypt scalający i kontrole mechaniczne:** [`eksperymenty/x002-analiza-fundacja-rodzinna/x002.py`](../../eksperymenty/x002-analiza-fundacja-rodzinna/x002.py)
- **Dane:**
  - [`znaleziska.json`](znaleziska.json): widoczne na stronie projektu po kliknięciu liczby znalezisk;
  - surowe przebiegi [A](przebiegi/A-opus.json) i [B](przebiegi/B-sonnet.json);
  - [`kontrole_mechaniczne.json`](kontrole_mechaniczne.json);
  - [`odrzucone.json`](odrzucone.json).
- **Status:** czeka na werdykt autora (G5). Wszystkie znaleziska mają `werdykt_autora: brak`.

## Metoda

1. **Kontrole mechaniczne (bez AI):**
   - M1: odesłania wewnętrzne do nieistniejących lub uchylonych artykułów;
   - M2: delegacje „w drodze rozporządzenia” w porównaniu z aktami wykonawczymi w ISAP.
2. **Dwa niezależne przebiegi AI** z tą samą instrukcją. Żaden nie widział wyników drugiego:
   - A: Claude Opus;
   - B: Claude Sonnet.

   Instrukcja zawierała sześć kategorii z S006, wymóg dosłownego cytatu, limit 12 znalezisk i zakaz porad prawnych.
3. **Walidacja automatyczna:**
   - G1: każdy cytat występuje dosłownie w pliku ustawy;
   - G2: każdy wskazany artykuł istnieje;
   - G3: kategoria pochodzi z listy.
4. **Weryfikacja krzyżowa (G4):** znaleziska A i B łączymy, gdy dotyczą tych samych jednostek. Miarą jest podobieństwo zbiorów „artykuł + ustęp” (Jaccard) z premią za tę samą kategorię, próg 0,4. Jedno znalezisko A może zebrać kilka znalezisk B.

## Wyniki

| | Liczba |
| --- | ---: |
| Znaleziska przebiegu A (Opus) | 12 |
| Znaleziska przebiegu B (Sonnet) | 12 |
| Odrzucone przez walidację (G1–G3) | **0** |
| Znaleziska po scaleniu | **18** |
| Potwierdzone krzyżowo (A i B niezależnie) | **5** |
| Znaleziska z kontroli mechanicznych | 0 |

**Kontrole mechaniczne niczego nie wykazały.** Ustawa nie odsyła wewnętrznie do nieistniejących ani uchylonych artykułów. Obie delegacje do rozporządzeń (formularze wniosków i art. 127 o rejestrze) mają w ISAP akty wykonawcze, łącznie 4.

**Znaleziska potwierdzone krzyżowo:**

| ID | Kategoria | Przepisy | Istota |
| --- | --- | --- | --- |
| x002-001 | brak ścieżki alternatywnej (B: luka) | art. 71, art. 61 | Gdy zarząd jest pusty, zgromadzenie beneficjentów można zwołać tylko po rezygnacji lub śmierci członka zarządu. Brak trybu przy upływie kadencji, odwołaniu albo odmowie osoby wskazanej. Waga wysoka. |
| x002-002 | niespójność | art. 19 ust. 1, art. 9, art. 104 ust. 2 | Definicja wartości mienia wniesionego (dzień wniesienia) a wycena według stanu z chwili zaspokojenia wierzyciela. |
| x002-003 | wada | art. 105 ust. 1 pkt 3, art. 117 ust. 1 pkt 19–21 | Odesłania do instytucji, których ustawa nie ustanawia: postępowania przymuszającego, kuratora, zarządu komisarycznego i zarządcy. B zgłosił to jako dwa osobne znaleziska. |
| x002-004 | niespójność (B: sprzeczność) | art. 85, art. 89–91 | „Rozwiązanie” w dwóch znaczeniach. Dla fundacji w organizacji przepisy wskazują dwie różne chwile rozwiązania. |
| x002-005 | zaniechanie | art. 64 ust. 2, art. 79 ust. 1, art. 128 | Obowiązkowa rada nadzorcza (ponad 25 beneficjentów) i audyt bez podmiotu, trybu i sankcji. Jedyny przepis karny obejmuje art. 84. |

Pozostałe 13 znalezisk ma jedno źródło: 7 z przebiegu A i 6 z B. Pełna lista z cytatami i uzasadnieniami jest w `znaleziska.json` i na stronie.

## Ocena metody (wstępna, przed werdyktem autora)

- **Wymóg dosłownego cytatu działa.** Wszystkie 63 cytaty z obu przebiegów występują w tekście, więc nie ma zmyślonych przepisów.
- **Zgodność przebiegów jest umiarkowana:** 5 wspólnych tematów na 18. Przebiegi częściej się uzupełniają, niż powtarzają. Weryfikacja krzyżowa podnosi wiarygodność tych 5 znalezisk, ale nie oznacza, że pozostałe są błędne.
- **Kategorie się nakładają,** np. luka a brak ścieżki alternatywnej albo niespójność a sprzeczność. Przy scalaniu decyduje kategoria z przebiegu A, a kategoria B jest zapisana obok.
- **Precyzja jest nieznana** do czasu werdyktów autora. To jest główny wynik, którego potrzebuje decyzja o dalszej metodzie (S006, sekcja 3).

## Następny krok

Autor wpisuje `werdykt_autora` (`potwierdzone` / `odrzucone` / `do_dyskusji`) i ewentualnie `komentarz_autora` w `znaleziska.json`. Strona pokaże werdykty po kolejnym pushu.

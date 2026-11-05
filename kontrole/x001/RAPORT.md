# x001: weryfikacja ilościowa korpusu i parametrów (S005)

- **Data:** 2026-11-05
- **Specyfikacja:** [S005](../../specs/S005-weryfikacja-ilosciowa.md)
- **Skrypt:** [`eksperymenty/x001-weryfikacja-100/x001.py`](../../eksperymenty/x001-weryfikacja-100/x001.py)
- **Dane:** [`wyniki.json`](wyniki.json) (próba i kontrole korpusu, widoczne na stronie projektu), [`bilans.json`](bilans.json), [`wykluczenia.json`](wykluczenia.json)
- **Ziarno losowania:** 20261105 dla próby, 20261106 dla wykluczeń
- **Status:** wykonane, czeka na przegląd autora

## Podsumowanie

Bilans i klasyfikacja się zgadzają. Na próbie 100 ustaw wszystkie bramki S005 są zaliczone. Kontrola pokazała jednak dwa problemy w korpusie, których próba nie obejmowała:

- **12 ustaw ma tekst ujednolicony starszy niż ostatni urzędowy tekst jednolity.** W tych przypadkach zbiór nie zawiera najaktualniejszego brzmienia.
- **29 ustaw ma tekst nieczytelny**, bo PDF-y z ISAP mają uszkodzone kodowanie czcionek.

Oba problemy wymagają osobnych poprawek (sekcja „Wnioski”).

| Bramka | Warunek | Wynik | Werdykt |
| --- | --- | --- | --- |
| G1 Bilans | zbiór + wykluczone = niezależne zapytanie | 6092 = 6092; listowanie roczne uzgodnione bez reszty | ✅ |
| G2 Brzmienie | 100/100 | 100/100 | ✅ |
| G3 Ostatni t.j. | ≥ 98/100, reszta wyjaśniona | 99/100, 1 wyjaśniona | ✅ |
| G4 Liczba zmian | ≥ 95/100, reszta wyjaśniona | 100/100 (z relacją odwrotną) | ✅ |
| G5 Zmiany po t.j. | każda różnica wyjaśniona | 68 zgodnych, 1 rozbieżność wyjaśniona | ✅ |
| G6 Brak fałszywych wykluczeń | 0 ustaw merytorycznych wśród 70 wykluczonych | 69 potwierdzonych treścią, 1 nie dało się odczytać, 0 fałszywych | ✅ (z zastrzeżeniem) |
| G7 Brak „zgodności z braku danych” | brak danych daje „niezweryfikowany” | spełnione z konstrukcji (przegląd kodu) | ✅ |

Progi G3 i G4 to propozycja ze specyfikacji. Autor ich jeszcze nie zatwierdził.

## Metoda: niezależne źródła

Strony ISAP (`DocDetails.xsp`) blokują automatyczne zapytania (HTTP 403). Nie obchodziliśmy tego zabezpieczenia. Zamiast tego każdy parametr sprawdziliśmy inną ścieżką albo innym narzędziem niż to, które go wyliczyło:

| Parametr | Źródło w zbiorze | Źródło kontrolne |
| --- | --- | --- |
| liczebność | `GET /acts/search?inForce=1` | listowanie roczne `GET /acts/DU/{rok}` (1918–2026) |
| brzmienie | `search`: lista plików | `GET /acts/{ELI}`: pliki i „Akty zmieniające” |
| liczba zmian | `search`: „Akty zmieniające” | `GET /acts/{ELI}` oraz relacja odwrotna: każda ustawa zmieniająca ma tę ustawę w „Akty zmienione” |
| ostatni t.j. | `search`: „Inf. o tekście jednolitym” | `GET /acts/{ELI}`, relacja odwrotna (obwieszczenie → „Tekst jednolity dla aktu”) i ramka „Opracowano na podstawie” w PDF-ie |
| zmiany po t.j. | pozycje Dz. U. po t.j. | pozycje wymienione w ramce PDF i daty ogłoszenia nowelizacji |
| data t.u. | stopka PDF odczytana przez PyMuPDF | stopka PDF odczytana przez **pdftotext** (poppler) |
| wykluczenia | tytuł aktu | **treść** aktu (HTML albo PDF), w której szukamy zwrotów nowelizujących lub ratyfikacyjnych |

Próba miała 100 ustaw: Konstytucję, Kodeks karny i ustawę o VAT oraz 97 losowych, warstwowo według brzmienia. W sumie: 80 ●, 18 ○, 2 ◐.

## G1: bilans

- Wyszukiwarka (`inForce=1`) zwraca 6092 ustawy. Wszystkie trafiają do kategorii:

  | Kategoria | Liczba |
  | --- | ---: |
  | w zbiorze | 1177 |
  | nowelizacje | 3804 |
  | ratyfikacje | 968 |
  | akty jednorazowe i inne statusy | 139 |
  | inne | 4 |
  | **suma** | **6092** |

- Listowanie roczne daje 7325 ustaw, które nie mają statusu uchylenia ani wygaśnięcia. Bilans się domyka:
  - **+1237** to akty ze statusem „bez statusu”, prawie wyłącznie przedwojenne (1918–1939). API nie oznacza ich jako obowiązujących (`inForce` ≠ 1), więc wyszukiwarka ich nie zwraca.
  - **−4** to akty z flagą `inForce=1`, ale ze statusem „uchylony” lub „wygaśnięcie aktu” (DU/1989/21, DU/1991/446, DU/1994/369, DU/1996/113). To niespójność danych ISAP. Zbiór je pomija.
  - 7325 − 1237 + 4 = 6092. ✅
- Wszystkie 1177 aktów z indeksu są w wyniku wyszukiwarki.

## G2–G5: próba 100 ustaw

- **Brzmienie:** 100/100.
- **Liczba ustaw zmieniających:** 100/100. Dla każdej z ~2000 relacji ustawa zmieniająca potwierdza zmianę w swoich „Aktach zmienionych”.
- **Ostatni t.j.:** 99/100. Wyjątek to **Kodeks wykroczeń (DU/1971/114)**. API zna t.j. Dz. U. 2026 poz. 1372 z 2026-10-02, ale tekst ujednolicony w ISAP (z 2026-05-05) opracowano na podstawie wcześniejszego t.j. Dz. U. 2025 poz. 734. Dane w zbiorze są poprawne, natomiast źródło (ISAP) nie zaktualizowało tekstu ujednoliconego. To zjawisko sprawdziliśmy w całym korpusie (K1).
- **Zmiany po t.j.:** 68 zgodnych i 1 rozbieżność (ten sam przypadek Kodeksu wykroczeń). W 4 przypadkach ramki nie dało się porównać, bo PDF jej nie zawiera. Wartość w zbiorze liczy też nowelizacje ogłoszone po dacie tekstu ujednoliconego, np. ustawa o VAT: 1 zmiana uwzględniona w t.u. i 1 ogłoszona później (DU/2026/1446).
- **Data tekstu ujednoliconego:** 77 zgodnych, 3 niezweryfikowane. pdftotext nie odczytał stopki w starszych PDF-ach (DU/1992/451, DU/1994/396, DU/2001/1149). Nie ma żadnej rozbieżności.

## Kontrole całego korpusu (K1, K2)

Rozbieżności z próby wskazały dwa zjawiska. Sprawdziliśmy je więc na wszystkich ustawach.

- **K1: tekst ujednolicony starszy niż ostatni t.j.** Sprawdzono 813 ustaw z t.j. **12 rozbieżności**:
  - DU/1971/114 (Kodeks wykroczeń),
  - DU/1981/101,
  - DU/2001/627 (Prawo ochrony środowiska),
  - DU/2006/1354,
  - DU/2006/1658,
  - DU/2009/1240 (finanse publiczne),
  - DU/2010/44,
  - DU/2010/835,
  - DU/2011/814,
  - DU/2012/769,
  - DU/2014/575,
  - DU/2018/771.

  Dla tych ustaw urzędowy tekst jednolity jest aktualniejszy niż tekst w zbiorze.
- **K2: tekst nieczytelny.** Sprawdzono 1177 plików. **29 rozbieżności.** Tekst zawiera znaki sterujące zamiast liter, bo PDF-y (głównie z lat 1950–1997) mają uszkodzone kodowanie czcionek, np. DU/1964/60 (Przepisy wprowadzające kodeks rodzinny), DU/1989/390 (amnestia), DU/1992/451. Pełna lista jest w `wyniki.json` (parametr `czytelnosc_tekstu`).

Wszystkie te ustawy mają na stronie oznaczenie „rozbieżność” w kolumnie „Weryfikacja”.

## G6: wykluczenia

Wylosowano 50 nowelizacji i 20 ratyfikacji. **69** potwierdzono treścią, np. „wprowadza się następujące zmiany” albo „otrzymuje brzmienie” dla nowelizacji i „ratyfikacji” dla ratyfikacji. **1** nie dało się zweryfikować: DU/1990/258 „o uchyleniu ustawy o zwalczaniu spekulacji” ma nieczytelny PDF (jak w K2). Tytuł wskazuje na akt uchylający. Nie znaleziono żadnej ustawy merytorycznej wykluczonej przez pomyłkę.

Przy okazji poprawiono samo narzędzie kontrolne. Dla DU/1995/6 HTML z API zawierał samą strukturę bez treści, więc trzeba było sięgnąć po PDF i rozszerzyć listę zwrotów, np. „w art. 2 wyrazy…”.

## Wnioski i propozycje

1. **Korpus jest wiarygodny ilościowo.** Bilans się zgadza, klasyfikacja jest poprawna, a parametry w tabeli potwierdzono niezależnie.
2. **Nowa specyfikacja: aktualność (K1).** Dla 12 ustaw ISAP ma tekst ujednolicony starszy niż ostatni t.j. Propozycja: w takim przypadku wziąć tekst z obwieszczenia t.j. (PDF w Dz. U.) albo oznaczyć brzmienie jako nieaktualne. Do tego stała kontrola K1 przy każdej aktualizacji.
3. **Nowa specyfikacja: czytelność (K2).** 29 ustaw trzeba pobrać z innego źródła: HTML (`H`), akt ogłoszony (`O`) albo OCR. Do tego stała bramka K2 w testach korpusu.
4. **Definicja „zmian po t.j.”.** Rozważyć rozbicie na dwie kolumny: „uwzględnione w tekście ujednoliconym” i „ogłoszone po tekście ujednoliconym”. To otwarte pytanie z S005.
5. **Akty „bez statusu” (1237, głównie przedwojenne).** Poza zakresem. Część może formalnie obowiązywać. Do decyzji autora, czy to badać.

# S011 — Reguła R2: odesłania do uchylonych artykułów

- **Status:** proponowana (odłożona: właściciel wybrał najpierw braki ścieżek, S012)
- **Data:** 2026-11-05
- **Powiązane:** S010 (R1, ten sam schemat i filtry), MANIFEST M12

## 1. TL;DR

Reguła R2: **przepis odsyła do „art. N” tej samej ustawy, a artykuł N jest uchylony** („Art. N. (uchylony)” albo zakres „Art. N–M. (uchylone)”). Sprawdzamy 1112 ustaw z zakresu R1 w trzech etapach:

1. skrypt znajduje kandydatów;
2. filtr zgrubny zawęża ich do około 50;
3. model ocenia każdego kandydata z tekstem ustawy w kontekście.

Na stronę trafiają tylko przypadki potwierdzone przez model i ręcznie.

## 2. Abstract

Uchylenie artykułu bez dostosowania przepisów, które do niego odsyłają, zostawia odesłanie bez treści. To typowa wada techniki legislacyjnej przy nowelizacjach: przepis odsyłający traci sens albo wymaga wykładni.

W korpusie jest ok. 3400 uchylonych artykułów, więc reguła ma duży zasięg. Wiele odesłań do uchylonych przepisów jest jednak uzasadnionych. Dotyczy to przepisów przejściowych („stosuje się art. 5 w brzmieniu dotychczasowym”), przepisów o skutkach uchylenia, przepisów o wejściu w życie i samych uchyleń („uchyla się art. 5”). Dlatego etap z modelem jest konieczny od początku (wniosek z S010).

## 3. Objective

- **Cele:** lista odesłań do uchylonych artykułów, które pozostały w obowiązujących przepisach merytorycznych.
- **Poza zakresem:**
  - uchylone ustępy, punkty i litery (osobna reguła);
  - odesłania do uchylonych przepisów innych ustaw.
- **Kryteria sukcesu:** bramki G1–G4.

## 4. Artefact Inventory

| Artefakt | Rodzaj | Stan |
| --- | --- | --- |
| `eksperymenty/x003-martwe-odeslania/x003.py` (filtry odesłań wewnętrznych z R1) | kod (wykorzystywany) | istnieje |
| `eksperymenty/x004-odeslania-do-uchylonych/x004.py` | kod | do utworzenia |
| `kontrole/x004/{kandydaci_skrypt.json, oceny_llm.json, znaleziska.json, RAPORT.md}` | dane i dokument | do utworzenia |
| `tests/test_x004.py` | testy | do utworzenia |

## 5. Functional Domain Changes

- **Uchylony artykuł:** nagłówek „Art. N. (uchylony)” albo zakres „Art. N–M. (uchylone)”. Rozpoznajemy różne kreski (–, ‒, -) i pogrubione nagłówki.
- **Odesłanie wewnętrzne:** te same reguły co w R1 (S010). Pomijamy artykuły i punkty nowelizujące, zdania z cytatem, zdania ze wskazaniem innego aktu i punkty wyliczeń dziedziczące akt.
- **Dodatkowo pomijamy** zdania o charakterze przejściowym lub dotyczące samego uchylenia: „w brzmieniu dotychczasowym”, „dotychczasow”, „przed dniem wejścia w życie”, „uchyl”, „traci moc”, „wchodzi w życie” i „wchodzą w życie”.
- **Werdykty modelu:**
  - `odeslanie_do_uchylonego`: wada, czyli obowiązujący przepis merytoryczny odsyła do uchylonego artykułu;
  - `uzasadnione`: przepis przejściowy, o wejściu w życie, o skutkach uchylenia itp.;
  - `inny_akt`;
  - `artykul_nie_uchylony`;
  - `niejasne`.

## 6. Critical Path

1. Skrypt i przegląd próbki.
2. Filtr zgrubny.
3. Ocena modelem.
4. Przegląd ręczny przypadków „odesłanie do uchylonego”.
5. Publikacja i raport.

## 7. Control Gates

| # | Bramka | Warunek zaliczenia | Weryfikacja | Blokuje |
| --- | --- | --- | --- | --- |
| G1 | Cytaty | każdy cytat w znaleziskach i ocenach występuje dosłownie w tekście ustawy | `tests/test_x004.py` | publikację |
| G2 | Uchylenie | dla każdego znaleziska w tekście jest nagłówek uchylonego artykułu N (lub zakres go obejmujący) | test | publikację |
| G3 | Źródło znalezisk | znaleziska odpowiadają dokładnie werdyktom `odeslanie_do_uchylonego` modelu | test | publikację |
| G4 | Przegląd ręczny | każde znalezisko sprawdzone w tekście przed publikacją | raport | publikację |

## 8. Expected Outcome

- **Efekt bezpośredni:** odesłania do uchylonych artykułów widoczne na stronie jako znaleziska kategorii „wada”.
- **Efekt mierzalny:** liczba kandydatów na każdym etapie i precyzja skryptu.
- **Wycofanie:** usunięcie `kontrole/x004/`.

## 9. Additional Information

- **Odrzucone alternatywy:** sam skrypt bez modelu, bo precyzja R1 wyniosła ok. 4%.
- **Ryzyka:** granica między odesłaniem uzasadnionym (przejściowym) a wadliwym bywa interpretacyjna. Model podaje uzasadnienie i cytat, a przypadki wątpliwe dostają werdykt „niejasne” i nie są publikowane.

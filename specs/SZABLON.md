# SNNN — Tytuł zmiany

- **Status:** szkic | zamknięta | dostarczona | porzucona
- **Data:** RRRR-MM-DD
- **Powiązane:** SNNN, …

## 1. TL;DR

Jedno do trzech zdań: co się zmienia, dla kogo i jak potwierdzimy wynik.

## 2. Abstract

Od 3 do 15 zdań w akapitach:

- stan obecny,
- luka lub problem,
- uzasadnienie zmiany,
- historia decyzji.

## 3. Objective

- **Cele:** co musi zostać osiągnięte.
- **Poza zakresem:** czego świadomie nie robimy.
- **Kryteria sukcesu:** warunki, które oznaczają, że zmiana jest skończona.

## 4. Artefact Inventory

| Artefakt | Rodzaj | Stan |
| --- | --- | --- |
| `ścieżka/plik` | kod / dane / dokument / zewnętrzne | istnieje / do utworzenia / do zmiany / do usunięcia / [DO USTALENIA] |

## 5. Functional Domain Changes

- stan obecny i stan docelowy,
- reguły i przypadki brzegowe,
- odporność na awarie usług zewnętrznych i współbieżność,
- wpływ na dane.

## 6. Critical Path

Najkrótsza sekwencja kroków od stanu obecnego do działającej zmiany. Na końcu warunek ukończenia.

## 7. Control Gates

| # | Bramka | Warunek zaliczenia | Weryfikacja | Blokuje |
| --- | --- | --- | --- | --- |
| G1 | … | warunek logiczny lub liczbowy | test / polecenie | commit / publikację |

Uwzględnij też bramki negatywne, czyli to, czego system nie może robić.

## 8. Expected Outcome

- efekt bezpośredni,
- efekt mierzalny,
- skutki uboczne,
- możliwość wycofania zmiany.

## 9. Additional Information

- odrzucone alternatywy,
- dług techniczny,
- zależności zewnętrzne,
- źródła i otwarte pytania.

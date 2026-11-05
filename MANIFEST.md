# Manifest

Zasady projektu i zasady inżynierskie nomystrii. Obowiązują przy każdej specyfikacji w `specs/`. Specyfikacja, która łamie którąś z zasad, musi to powiedzieć wprost i uzasadnić w sekcji „Additional Information”.

## Zasady dotyczące danych

**M1. Jedno źródło.** Teksty prawa pochodzą wyłącznie z API ELI Sejmu (`api.sejm.gov.pl/eli`), czyli z ISAP. Nie korzystamy z serwisów komercyjnych ani z kopii zewnętrznych.

**M2. Nie zmieniamy treści prawa.** Konwersja może zmienić układ: łamanie wierszy, nagłówki stron, położenie przypisów, formatowanie Markdown. Nie może zmienić słów przepisu. Jeżeli treść da się odczytać tylko z PDF-u, na przykład z mapy, wzoru albo grafiki, zostawiamy lukę i link do PDF-u. Nie zgadujemy treści.

**M3. Uczciwe metadane.** Każdy plik mówi, jakie ma brzmienie (`ujednolicone`, `pierwotne`, `pierwotne (zmieniana)`) i na jakiej podstawie powstał. Tekst, który może być nieaktualny, jest tak oznaczony. Nigdy nie udaje aktualnego.

**M4. Tekst ujednolicony to nie źródło prawa.** README i metadane mówią wprost, że wiąże wyłącznie Dziennik Ustaw.

**M5. Stabilna tożsamość aktu.** Plik ustawy jest przypisany do jej ELI (rok i pozycja ogłoszenia pierwotnego). Ścieżka nie zmienia się po kolejnym tekście jednolitym ani po nowelizacji.

## Zasady inżynierskie

**M6. Odtwarzalność.** Cały katalog `dane/` powstaje jednym poleceniem `skrypty/pobierz.py`. Nie edytujemy plików w `dane/` ręcznie: poprawki wprowadzamy w konwerterze albo w regułach doboru aktów.

**M7. PDF-y poza repozytorium.** Źródłowe PDF-y leżą w katalogu podręcznym `.cache/`. Repozytorium przechowuje tylko tekst, metadane i kod.

**M8. Uprzejmość wobec API.** Pobieramy w kilku wątkach. Ponownie ściągamy tylko akty, którym zmieniła się data `changeDate`. W User-Agent podajemy adres repozytorium.

**M9. Minimum zależności.** Python 3 z biblioteką standardową plus `pymupdf`. Testy działają na `unittest` z biblioteki standardowej.

**M10. Bramki weryfikujemy maszynowo.** Każda bramka kontrolna ze specyfikacji ma test w `tests/` albo polecenie, które da się powtórzyć.

**M11. Język.** Artefakty, komunikaty skryptów i nazwy pól metadanych są po polsku. Nazwy pól piszemy bez polskich znaków.

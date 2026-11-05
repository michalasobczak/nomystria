# x003: reguła R1, martwe odesłania wewnętrzne (S010)

- **Data:** 2026-11-05
- **Specyfikacja:** [S010](../../specs/S010-martwe-odeslania-wewnetrzne.md)
- **Zakres:** 1112 ustaw uchwalonych lub zmienianych od 1989 r. Pominięto ustawy „Przepisy wprowadzające”, bo odsyłają do artykułów ustawy wprowadzanej bez jej nazywania.
- **Źródło:** wyłącznie wersja tekstowa korpusu (Markdown), bez PDF (decyzja właściciela).
- **Wynik:** **2 martwe odesłania** potwierdzone przez model i ręcznie. Są widoczne na stronie jako znaleziska.

## Metoda: skrypt → filtr zgrubny → ocena modelem z pełnym tekstem

| Etap | Co robi | Wynik |
| --- | --- | ---: |
| 1. Skrypt [`x003.py`](../../eksperymenty/x003-martwe-odeslania/x003.py) | Szuka „art. N” bez wskazania innego aktu, gdy w ustawie nie ma artykułu N. Pomija artykuły i akapity nowelizujące, zdania z cytatem, zdania ze wskazaniem innego aktu i punkty wyliczeń, które dziedziczą akt z akapitu wprowadzającego. Uwzględnia zakresy „Art. 13–22. (pominięte)”. | 531 kandydatów w 153 ustawach ([`kandydaci_skrypt.json`](kandydaci_skrypt.json)) |
| 2. Filtr zgrubny | Odrzuca: prawdopodobny indeks górny („art. 1891” przy „Art. 189…”), numer występujący gdziekolwiek jako „Art. N”, zdania z 3 lub więcej odesłaniami (wyliczenia), punkty list. Zostawia 1 kandydata na ustawę i ustawy do 200 KB, żeby zmieściły się w kontekście modelu. | 134, potem 73, potem **48** (47 ustaw) |
| 3. Ocena modelem | 10 niezależnych przebiegów Claude Sonnet, każdy z paczką ustaw. Werdykt z uzasadnieniem i dosłownym cytatem. | [`oceny_llm.json`](oceny_llm.json) |
| 4. Przegląd ręczny | Sprawdzenie spisu nagłówków artykułów dla przypadków „martwe odesłanie”. | 2 potwierdzone |

**Werdykty modelu dla 48 kandydatów:**

| Werdykt | Liczba | Typowa przyczyna |
| --- | ---: | --- |
| `inny_akt` | 38 | odesłanie do ustawy zmienianej, której przepisy cytuje nowelizacja (np. „art. 62bb” dodawany do Prawa energetycznego), albo do aktu wskazanego wcześniej w tekście |
| `artykul_istnieje` | 8 | artykuł w zakresie „Art. 12‒14. (pominięte)” zapisanym z innym rodzajem kreski, nagłówek pogrubiony („**Art. 2.**”), rozdział uchylony bez nagłówków artykułów |
| `martwe_odeslanie` | **2** | patrz niżej |
| `niejasne` | 0 | |

Wszystkie 48 cytatów modelu sprawdzono automatycznie: każdy występuje dosłownie w tekście ustawy.

## Znaleziska

| ID | Ustawa | Przepis | Odesłanie | Istota |
| --- | --- | --- | --- | --- |
| x003-001 | o funkcjonowaniu banków spółdzielczych, ich zrzeszaniu się i bankach zrzeszających (DU/2000/1252) | art. 35a ust. 7 | art. 22s ust. 1 | Rozdział o systemie ochrony kończy się na art. 22n, po nim następuje art. 23. Artykułu 22s nie ma. |
| x003-002 | o szczególnych rozwiązaniach w zakresie niektórych źródeł ciepła… (DU/2022/1967) | art. 30 ust. 4c | art. 4a | Po art. 4 następuje art. 5. Z kontekstu wynika, że chodzi o ust. 4a tego samego artykułu (wniosek wojewody), czyli błąd redakcyjny. |

Oba odesłania występują w tekście ujednoliconym ISAP. Przed ewentualnym przekazaniem dalej trzeba je porównać z tekstem w Dzienniku Ustaw.

## Ograniczenia

- **Pokrycie.** Model ocenił tylko 48 z 531 kandydatów, wybranych filtrem zgrubnym (1 na ustawę, ustawy do 200 KB). Pozostali kandydaci nie zostali ocenieni, a duże ustawy (np. kodeksy) nie były ocenianie modelem.
- **Sposób czytania przez model.** Polecenie wymagało przeczytania całych ustaw, ale większość przebiegów zamiast tego przeszukiwała tekst i czytała fragmenty wokół odesłań. Przebiegi same to zgłosiły. Werdykty mają cytaty i uzasadnienia, a oba „martwe odesłania” sprawdzono ręcznie.
- **Precyzja samego skryptu jest niska:** 2 prawdziwe na 48 ocenionych, czyli ok. 4%. Główne źródło szumu to odesłania do ustaw zmienianych w przepisach nowelizujących i nierówna postać tekstów (różne kreski, pogrubione nagłówki, indeksy górne). Potwierdza to uwagę właściciela, że parser na nierównych tekstach zgłasza fałszywe alarmy.

## Wnioski i kolejne kroki

1. **Poprawki parsera spisu artykułów** wynikają wprost z werdyktów `artykul_istnieje`: kreska „‒” (U+2012) w zakresach, pogrubione nagłówki „**Art. N.**” i rozdziały uchylone w całości.
2. **Lepsze rozpoznanie przepisów nowelizujących.** Odesłanie wewnątrz artykułu, który dodaje lub zmienia przepisy innej ustawy, dotyczy tamtej ustawy. To główna przyczyna werdyktów `inny_akt`.
3. **Ocena modelem pozostałych kandydatów**, po poprawkach 1–2, które powinny wyraźnie zmniejszyć ich liczbę.

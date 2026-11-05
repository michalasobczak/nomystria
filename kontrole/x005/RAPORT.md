# x005: reguła R3, ślubowanie bez ścieżki po stronie przyjmującego (S012)

- **Data:** 2026-11-05
- **Specyfikacja:** [S012](../../specs/S012-slubowanie-sciezka-przyjmujacego.md)
- **Pytanie:** czy status, urząd, kadencja albo prawo wykonywania zawodu zależy od ślubowania wobec podmiotu X, a ustawa nie mówi, co się dzieje, gdy X ślubowania nie przyjmie (odmowa, zwłoka, niemożność)?
- **Wzorzec poprawnego rozwiązania:** ustawa o samorządzie gminnym, art. 29a ust. 3. Gdy sesja rady się nie odbyła, wójt składa ślubowanie przed komisarzem wyborczym.
- **Wynik:** **14 znalezisk** (3 o wadze wysokiej, 2 średniej, 9 niskiej), widocznych na stronie.

## Metoda

| Etap | Co robi | Wynik |
| --- | --- | ---: |
| 1. Skrypt [`x005.py`](../../eksperymenty/x005-slubowanie/x005.py) | Wyszukuje ustawy, w których zdanie o ślubowaniu wskazuje przyjmującego („wobec”, „przed”, „odbiera”, „przyjmuje”) albo czyni ślubowanie warunkiem statusu („która złożyła ślubowanie”, „z chwilą złożenia ślubowania”, „powstaje po złożeniu ślubowania”). Tworzy wyciąg przepisów. Łączy akapity rozdzielone przy konwersji (tak odnalazła się ustawa o statusie sędziów TK). | 40 kandydatów ([`kandydaci.json`](kandydaci.json)) |
| 2. Ocena modelem | 4 niezależne przebiegi Claude Sonnet po 10 ustaw. Każdy miał wyciąg i dostęp do pełnego tekstu oraz listę kontrolną ratunków: tryb zastępczy lub termin, status niezależny od ślubowania, zastępowalny przyjmujący, Konstytucja art. 131 (działa tylko przy przeszkodzie, nie przy odmowie). | [`oceny_llm.json`](oceny_llm.json) |
| 3. Przegląd ręczny | Weryfikacja przypadków wątpliwych (radcy prawni, rzecznicy patentowi) i nadanie wagi według jawnej zasady. | 14 znalezisk |

Cytaty modelu sprawdzono automatycznie: każdy występuje dosłownie w tekście ustawy. Wyjątek to DU/2011/622: plik zawiera tylko nowelizację, więc cytaty pochodzą z ustawy o tłumaczu przysięgłym (DU/2004/2702).

**Werdykty dla 40 kandydatów:** brak ścieżki 14, ścieżka istnieje 10, nie dotyczy 13, niejasne 3.

## Zasada wagi

| Waga | Kiedy |
| --- | --- |
| wysoka | przyjmujący (Prezydent RP) to inny organ niż wybierający (Sejm), a sytuacja już się zdarzyła (2015, sędziowie TK) |
| średnia | o statusie decyduje wpis, a ślubowanie odbiera jedna wskazana osoba bez zastępcy i bez terminu |
| niska | ten sam organ powołuje lub wybiera i przyjmuje ślubowanie, więc odmowa jest mało prawdopodobna, ale prawnie nieuregulowana |

## Znaleziska (brak ścieżki)

| ID | Waga | Ustawa | Przepis | Przyjmujący |
| --- | --- | --- | --- | --- |
| x005-001 | wysoka | 30 listopada 2016 r. o organizacji i trybie postępowania przed Trybunałem Konstytucyjnym | art. 6 | Prezydent Rzeczypospolitej Polskiej |
| x005-002 | wysoka | 30 listopada 2016 r. o statusie sędziów Trybunału Konstytucyjnego | art. 5 | Prezydent Rzeczypospolitej Polskiej |
| x005-003 | wysoka | 13 grudnia 2016 r. - Przepisy wprowadzające ustawę o organizacji i trybie postępowania przed Trybunałem Konstytucyjnym oraz ustawę o statusie sędziów Trybunału Konstytucyjnego | art. 18 | Prezydent Rzeczypospolitej Polskiej (ślubowanie sędziów TK; sama rota i tryb w ustawie o statusie sędziów TK, tu tylko skutki) |
| x005-004 | srednia | 6 lipca 1982 r. o radcach prawnych. | art. 23 | dziekan rady okręgowej izby radców prawnych prowadzącej listę (art. 27 ust. 2) |
| x005-005 | srednia | 11 kwietnia 2001 r. o rzecznikach patentowych. | art. 18 | Prezes Urzędu Patentowego (w obecności przedstawiciela samorządu) |
| x005-006 | niska | 15 lipca 1987 r. o Rzeczniku Praw Obywatelskich. | art. 5 | Sejm |
| x005-007 | niska | 21 sierpnia 1997 r. - Prawo o ustroju sądów wojskowych. | art. 23 | Prezydent Rzeczypospolitej Polskiej (sędzia sądu wojskowego); prezes sądu wojskowego (ławnicy) |
| x005-008 | niska | 18 grudnia 1998 r. o Instytucie Pamięci Narodowej - Komisji Ścigania Zbrodni przeciwko Narodowi Polskiemu. | art. 10 | Sejm Rzeczypospolitej Polskiej |
| x005-009 | niska | 6 stycznia 2000 r. o Rzeczniku Praw Dziecka. | art. 6 | Sejm |
| x005-010 | niska | 27 lipca 2001 r. Prawo o ustroju sądów powszechnych. | art. 55 | Prezydent Rzeczypospolitej Polskiej (sędzia i asesor); prezes sądu (referendarz, ławnik) |
| x005-011 | niska | 25 lipca 2002 r. Prawo o ustroju sądów administracyjnych. | art. 5 | Prezydent Rzeczypospolitej Polskiej |
| x005-012 | niska | 10 maja 2018 r. o ochronie danych osobowych | art. 34 | Sejm |
| x005-013 | niska | 8 grudnia 2017 r. o Sądzie Najwyższym | art. 29 | Prezydent Rzeczypospolitej Polskiej (sędzia); Pierwszy Prezes SN (ławnik) |
| x005-014 | niska | 30 sierpnia 2019 r. o Państwowej Komisji do spraw przeciwdziałania wykorzystaniu seksualnemu małoletnich poniżej lat 15 | art. 8 | Sejm Rzeczypospolitej Polskiej |

## Ścieżka istnieje (dla porównania)

| Ustawa | Ratunek |
| --- | --- |
| 26 maja 1982 r. Prawo o adwokaturze. | Pkt 3: dziekan jest organem z ustawowym stałym zastępcą (wicedziekan), który może przyjąć ślubowanie przy niedostępności dziekana. |
| 14 lutego 1991 r. Prawo o notariacie. | Pkt 3: Minister może upoważnić prezesa sądu apelacyjnego do przyjęcia ślubowania; Minister to organ zastępowalny hierarchicznie; prezes rady izby ma wiceprezesa, który wykonuje jego obowiązki w razie nieobecności. |
| 15 czerwca 2007 r. o licencji doradcy restrukturyzacyjnego | Pkt 3 (oraz tryb zastępczy z pkt 1): Minister może upoważnić prezesa sądu okręgowego do przyjęcia ślubowania; Minister jest organem zastępowalnym hierarchicznie; ponadto złożenie ślubowania potwierdza podpis pod rotą. |
| 22 marca 2018 r. o komornikach sądowych | Ustawowy termin dla przyjmującego (14 dni od zawiadomienia) oraz przyjmujący jest organem hierarchicznym z zastępcą (pkt 1 i 3 listy); ten sam wzorzec dla asesora (art. 136 ust. 1, prezes sądu rejonowego, 14 dni) |
| 9 maja 1996 r. o wykonywaniu mandatu posła i senatora. | Termin trzech miesięcy i fikcja zrzeczenia się mandatu; tryb rozpatrywania spraw posłów, którzy nie złożyli ślubowania, określają regulaminy izb (Prezydium Sejmu/Senatu). Mandat wynika z wyboru, a przyjmującym jest organ kolegialny. |
| 5 czerwca 1998 r. o samorządzie województwa. | Termin/tryb zastępczy: radny nieobecny lub z mandatem uzyskanym w trakcie kadencji składa ślubowanie na pierwszej sesji, na której jest obecny; przyjmującym jest organ kolegialny, a mandat wynika z wyboru. |
| 10 grudnia 2020 r. o zawodzie farmaceuty | Ratunek 3 i 1: ustawowy zastępca przyjmującego (wskazany wiceprezes) oraz wymóg odbycia ślubowania bez zbędnej zwłoki. |
| 8 marca 1990 r. o samorządzie gminnym | Pkt 1 listy: tryb zastępczy – gdy sesja się nie odbyła lub upłynął termin, wójt składa ślubowanie przed komisarzem wyborczym, potwierdza podpisem. |
| 5 lipca 1996 r. o doradztwie podatkowym. | Pkt 3 listy: przyjmujący zastępowalny – przewodniczący lub osoba przez niego upoważniona spośród członków Rady (wielu możliwych przyjmujących). |
| 11 maja 2017 r. o biegłych rewidentach, firmach audytorskich oraz nadzorze publicznym | Pkt 3 listy: ślubowanie odbiera Prezes KRBR lub inny upoważniony członek Rady. |

## Nie dotyczy i niejasne

| Ustawa | Werdykt | Uzasadnienie (skrót) |
| --- | --- | --- |
| Konstytucja Rzeczypospolitej Polskiej z dnia 2 kwietnia 1997 r. | niejasne | Ślubowanie składa się przed Sejmem jako organem kolegialnym, a mandat powstaje z wyboru. Konstytucja reguluje wyłącznie odmowę posła, a nie sytuację, w której Sejm ślubowania nie przyjmie. Brak podmio |
| 5 stycznia 2011 r. - Kodeks wyborczy | nie_dotyczy | Kodeks wyborczy reguluje tylko skutki odmowy osoby ślubującej (wygaśnięcie mandatu), nie wskazuje podmiotu przyjmującego ani nie uzależnia objęcia mandatu od czynności przyjmującego. Ścieżka dla wójta |
| 23 grudnia 1994 r. o Najwyższej Izbie Kontroli. | nie_dotyczy | Przyjmującym jest Prezes NIK, który sam dokonuje mianowania, więc nie ma osobnego podmiotu mogącego zablokować status. Ślubowanie jest potwierdzane podpisem, a Prezesa NIK w razie potrzeby zastępuje w |
| 27 lipca 2001 r. o kuratorach sądowych. | nie_dotyczy | Stosunek pracy kuratora nawiązuje się przez mianowanie, więc ślubowanie jest obowiązkiem przed przystąpieniem do obowiązków, a nie warunkiem statusu. Przyjmującymi są prezesi sądów i kurator okręgowy, |
| 21 listopada 2008 r. o pracownikach samorządowych | nie_dotyczy | Ślubowanie składa się w obecności kierownika jednostki lub sekretarza, więc przyjmujący jest zastępowalny, a złożenie jest potwierdzane podpisem pracownika. Odmowa pracownika jest uregulowana (wygaśni |
| 25 marca 2011 r. o ograniczaniu barier administracyjnych dla obywateli i przedsiębiorców | niejasne | Prawo wykonywania zawodu zależy od ślubowania wobec Ministra Sprawiedliwości (art. 6 ust. 1 i art. 7 ust. 1 ustawy z 2004 r.), a ustawa milczy o terminie i skutku bezczynności Ministra. Minister jest  |
| 11 września 2019 r. - Prawo zamówień publicznych | nie_dotyczy | Członkostwo i stosunek pracy powstają z powołania przez ministra (art. 474 ust. 1, art. 483 ust. 1), a ślubowanie jest obowiązkiem poprzedzającym podjęcie obowiązków i potwierdzanym podpisem. Odmowa c |
| 30 czerwca 2000 r. Prawo własności przemysłowej. | nie_dotyczy | Ślubowanie przyjmuje przełożony i organ powołujący, w pełni zastępowalny w hierarchii urzędu; ustawa reguluje skutek odmowy eksperta. Nie ma luki po stronie przyjmującego. |
| 21 listopada 2008 r. o służbie cywilnej | nie_dotyczy | Dla urzędników ślubowanie jest jednostronne (podpis), a odmowa jest uregulowana. Szef SC ślubuje przed organem, który go powołuje i który kontroluje obsadę stanowiska, więc nie ma zależności od cudzej |
| 28 stycznia 2016 r. Prawo o prokuraturze | nie_dotyczy | Ustawa wiąże powstanie stosunku służbowego z doręczeniem powołania (art. 91 § 1), a nie ze ślubowaniem. Ślubowanie jest obowiązkiem, więc bierność przyjmującego nie blokuje statusu. |
| 15 grudnia 2016 r. o Prokuratorii Generalnej Rzeczypospolitej Polskiej | nie_dotyczy | Ślubowanie przyjmuje ten sam podmiot, który powołuje lub zatrudnia, więc nie ma zewnętrznego przyjmującego, którego bierność blokowałaby status. Zależność jest po stronie pracodawcy, a nie osoby trzec |
| 5 czerwca 1998 r. o samorządzie powiatowym. | nie_dotyczy | Przyjmujący to kolegialna rada, a ślubowanie można złożyć na dowolnej kolejnej sesji; mandat wynika z wyboru. Skutki odmowy radnego reguluje Kodeks wyborczy (poza plikiem). |
| 25 listopada 2004 r. o zawodzie tłumacza przysięgłego | niejasne | Ślubowanie składane wobec Ministra Sprawiedliwości; ustawa nie przewiduje upoważnienia, zastępcy ani trybu na wypadek odmowy czy zwłoki. Minister jest organem z hierarchią i prawdopodobnie może upoważ |
| 23 stycznia 2009 r. o Krajowej Szkole Sądownictwa i Prokuratury | nie_dotyczy | Status aplikanta wynika z przyjęcia i rozpoczęcia aplikacji, a przyjmujący (Dyrektor) ma ustawowych zastępców. |
| 20 lipca 2018 r. - Prawo o szkolnictwie wyższym i nauce | nie_dotyczy | Brak wskazanego podmiotu X poza uczelnią, ślubowanie realizowane w strukturze uczelni (rektor ze swoimi zastępcami); ustawa milczy też o trybie, ale nie ma jednego niezastępowalnego przyjmującego. Do  |
| 21 stycznia 2021 r. o służbie zagranicznej | nie_dotyczy | Minister jest zarazem organem powołującym i przyjmującym, więc nie może jednostronnie zablokować nominata bez odwołania; dyplomata składa ślubowanie w trybie wyznaczonym zarządzeniem ministra. Ryzyko  |

## Wnioski

1. **Najważniejsze znalezisko dotyczy sędziów Trybunału Konstytucyjnego.** Trzy ustawy z 2016 r. uzależniają nawiązanie stosunku służbowego, udział w Zgromadzeniu Ogólnym i przydział spraw od ślubowania wobec Prezydenta. Żadna nie reguluje odmowy ani zwłoki Prezydenta. Wzorzec z ustawy o samorządzie gminnym pokazuje, że da się to rozwiązać.
2. **Odmowa osoby jest regulowana często, odmowa przyjmującego prawie nigdy.** Ustawy przewidują, że odmowa złożenia ślubowania oznacza zrzeczenie się. Nie przewidują sytuacji odwrotnej.
3. **Zawody zaufania publicznego** (radcy prawni, rzecznicy patentowi) mają ten sam wzorzec: wpis plus ślubowanie przed jedną osobą. Dla porównania adwokatura ma zastępcę (wicedziekan), a notariat upoważnienie prezesa sądu apelacyjnego.
4. **Znalezisko nie przesądza o niekonstytucyjności** ani o tym, że przyjmujący może odmówić. Stwierdza tylko brak trybu w tekście ustawy.

## Ograniczenia

- Część wyciągów była niepełna, więc przebiegi uzupełniały je przeszukiwaniem pełnego tekstu.
- Klasyfikacja „zastępowalny w hierarchii” (np. przełożony w służbach) była przez przebiegi stosowana różnie: raz jako „nie dotyczy”, raz jako „ścieżka istnieje”. Dla znalezisk nie ma to znaczenia.
- Służby mundurowe (Policja, Straż Graniczna, ABW, SOP i inne) nie zostały kandydatami: ślubowanie składa się tam „przed podjęciem służby”, bez wskazanego przyjmującego.

# Wyniki kontroli

Każda kontrola, czyli eksperyment ze specyfikacji, ma tu swój katalog `kontrole/<id>/`, np. `kontrole/x001/` dla S005 i `kontrole/x002/` dla S006. Strona projektu (S007) czyta te pliki i pokazuje je przy ustawach.

Pliki są przetwarzane automatycznie przez `skrypty/strona.py`. Wynik z nieznanym `eli` (spoza `dane/indeks.csv`) przerywa generowanie strony.

## `wyniki.json`: kontrole parametrów (np. S005)

```json
{
  "id": "x001",
  "spec": "S005",
  "tytul": "Weryfikacja ilościowa — próba 100 ustaw",
  "data": "2026-11-06",
  "wyniki": [
    {
      "eli": "DU/2004/535",
      "parametr": "zmian_po_tekscie_jednolitym",
      "wartosc_zbior": "2",
      "wartosc_zrodlo": "1",
      "zrodlo": "Opracowano na podstawie (PDF U)",
      "werdykt": "rozbiezny",
      "wyjasnienie": "DU/2026/1446 ogłoszona po dacie tekstu ujednoliconego"
    }
  ]
}
```

Dopuszczalne wartości `werdykt`:

- `zgodny`,
- `rozbiezny`,
- `niezweryfikowany`.

Brak danych w źródle kontrolnym daje `niezweryfikowany`, nigdy `zgodny`.

## `znaleziska.json`: analiza treści (np. S006)

```json
{
  "id": "x002",
  "spec": "S006",
  "tytul": "Analiza ustawy o …",
  "data": "2026-11-10",
  "znaleziska": [
    {
      "id": "x002-001",
      "eli": "DU/2023/326",
      "kategoria": "luka",
      "przepisy": ["art. 12 ust. 3"],
      "cytaty": ["dosłowny fragment przepisu"],
      "opis": "…",
      "uzasadnienie": "…",
      "waga": "srednia",
      "zrodla_wykrycia": ["narzędzie A", "narzędzie B"],
      "weryfikacja_krzyzowa": true
    }
  ]
}
```

Opcjonalnie `kontrole/<id>/sciezki/<id znaleziska>.json` zawiera diagram ścieżek przepisów (S009). Strona pokazuje go pod adresem `sciezki.html?id=<id znaleziska>`. Węzły mają typ `pytanie` (z `odpowiedzi`), `krok` (z `dalej`) albo `wynik` (`ok` / `luka` / `statut`), a każdy węzeł ma `przepisy` i dosłowne `cytaty`.

Dopuszczalne wartości pól:

| Pole | Wartości |
| --- | --- |
| `kategoria` | `sprzecznosc`, `niespojnosc`, `luka`, `wada`, `brak_sciezki_alternatywnej`, `zaniechanie` |
| `waga` | `niska`, `srednia`, `wysoka` |

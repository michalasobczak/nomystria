# S001 — Repozytorium projektu

- **Status:** dostarczona
- **Data:** 2026-11-05
- **Powiązane:** S002

## 1. TL;DR

Publiczne repozytorium `michalasobczak/nomystria` na GitHubie z README, które wyjaśnia nazwę i cel projektu. Potwierdzenie: repozytorium jest widoczne publicznie, a gałąź `main` jest zsynchronizowana z lokalną kopią.

## 2. Abstract

Projekt zaczyna się od zera i nie ma jeszcze kodu ani danych. Nazwa *nomystria* łączy *nomos* (gr. prawo) i *mysterium* (łac. tajemnica). Hasło projektu brzmi: „Odkrywanie tajemnic i ukrytej struktury prawa”.

Repozytorium najpierw powstało jako prywatne, bo nie ustalono widoczności. Na prośbę właściciela zostało przełączone na publiczne.

## 3. Objective

- **Cele:** repozytorium na GitHubie z opisem, plikami README i `.gitignore` oraz lokalnym katalogiem połączonym z `origin`.
- **Poza zakresem:** dane i kod (S002).
- **Kryteria sukcesu:** `gh repo view michalasobczak/nomystria --json visibility` zwraca `PUBLIC`.

## 4. Artefact Inventory

| Artefakt | Rodzaj | Stan |
| --- | --- | --- |
| `github.com/michalasobczak/nomystria` | zewnętrzne | istnieje |
| `README.md` | dokument | istnieje |
| `.gitignore` | konfiguracja | istnieje |

## 5. Functional Domain Changes

Brak zmian w zachowaniu systemu, bo to start projektu. Opis repozytorium na GitHubie: „Nomystria (nomos + mysterium) — odkrywanie tajemnic i ukrytej struktury prawa”.

## 6. Critical Path

1. `git init`, README i `.gitignore`.
2. `gh repo create … --source . --push`.
3. Zmiana widoczności na publiczną.

Warunek ukończenia: repozytorium jest publiczne, a `main` jest wypchnięty.

## 7. Control Gates

| # | Bramka | Warunek zaliczenia | Weryfikacja | Blokuje |
| --- | --- | --- | --- | --- |
| G1 | Widoczność | `visibility == PUBLIC` | `gh repo view --json visibility` | — |
| G2 | Synchronizacja | `git status -sb` pokazuje `main...origin/main` bez rozbieżności | polecenie | publikację danych |

## 8. Expected Outcome

- **Efekt bezpośredni:** publiczne repozytorium gotowe na dane.
- **Wycofanie:** zmiana widoczności albo usunięcie repozytorium.

## 9. Additional Information

- **Odrzucone:** start jako repozytorium publiczne. Bez decyzji właściciela bezpieczniejsza była widoczność prywatna.

import csv
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "dane"
CACHE = ROOT / ".cache" / "pdf"
sys.path.insert(0, str(ROOT / "skrypty"))


@lru_cache(maxsize=1)
def indeks() -> list[dict]:
    with open(DATA / "indeks.csv", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def wiersz(eli: str) -> dict:
    return next(r for r in indeks() if r["eli"] == eli)


def tresc(eli: str) -> str:
    return (ROOT / wiersz(eli)["plik"]).read_text(encoding="utf-8")

"""Konwersja PDF tekstu ujednoliconego (ISAP / Kancelaria Sejmu) do Markdown.

Usuwa nagłówki i stopki stron, skleja wiersze w akapity, wyodrębnia przypisy
i metrykę „Opracowano na podstawie” z pierwszej strony.
"""

from __future__ import annotations

import re
import statistics
from dataclasses import dataclass, field

import pymupdf

LABEL_RE = re.compile(r"^\s*(\d+[a-z]?|[IVXLCDM]+)\)\s*$")
STRUCT_RE = re.compile(
    r"^(Art\.|§|\d+[a-z]*\)|[a-z]{1,3}\)|[–—•-]\s|"
    r"CZĘŚĆ|KSIĘGA|TYTUŁ|DZIAŁ|Dział|ROZDZIAŁ|Rozdział|Oddział|ODDZIAŁ|Załącznik|ZAŁĄCZNIK)"
)
STRUCT_RE_ANY = re.compile(r"^(Art\.\s*\d|\d+[a-z]*\)\s|[a-z]\)\s)")
HEADING_RE = re.compile(
    r"^(CZĘŚĆ|KSIĘGA|TYTUŁ|DZIAŁ|Dział|ROZDZIAŁ|Rozdział|Oddział|ODDZIAŁ|Załącznik|ZAŁĄCZNIK)\b"
)
SPACED_CAPS_RE = re.compile(r"^(?:[A-ZĄĆĘŁŃÓŚŹŻ]{1,2}\s+){2,}[A-ZĄĆĘŁŃÓŚŹŻ]+$")
DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}|\d{2}\.\d{2}\.\d{4})$")
HEADER_RE = re.compile(r"^(©\s*Kancelaria Sejmu|s\.\s*\d+\s*/\s*\d+)$")


@dataclass
class Row:
    page: int
    x0: float
    y0: float
    x1: float
    y1: float
    text: str
    size: float
    bold: bool
    label: str | None = None  # etykieta przypisu na początku wiersza (strefa przypisów)
    table: bool = False


@dataclass
class Result:
    markdown: str
    footer_date: str | None = None
    basis: str | None = None
    pages: int = 0
    warnings: list[str] = field(default_factory=list)


def _span_is_bold(span) -> bool:
    return bool(span["flags"] & 16) or "Bold" in span["font"]


def _body_size(doc) -> float:
    counts: dict[float, int] = {}
    for page in doc:
        for b in page.get_text("dict")["blocks"]:
            for line in b.get("lines", []):
                for s in line["spans"]:
                    t = s["text"].strip()
                    if t:
                        k = round(s["size"], 1)
                        counts[k] = counts.get(k, 0) + len(t)
    return max(counts, key=counts.get) if counts else 12.0


def _thin_rects(page):
    out = []
    for d in page.get_drawings():
        r = d["rect"]
        if r.height <= 2 and r.width >= 40:
            out.append(r)
    return out


def _page_rows(page, pno: int, body: float):
    """Zwraca (rows_body, rows_foot, footer_date, basis_lines)."""
    H = page.rect.height
    rects = _thin_rects(page)
    header_y = 0.0
    for r in rects:
        if r.y0 < 90 and r.width > 250:
            header_y = max(header_y, r.y0)

    # Tabele (tylko gdy na stronie są linie siatki).
    tables = []
    if len(rects) + len(page.get_drawings()) >= 6:
        words = page.get_text("words")
        try:
            for tb in page.find_tables().tables:
                if tb.row_count >= 2 and tb.col_count >= 2:
                    tables.append((pymupdf.Rect(tb.bbox), _table_md(tb, words)))
        except Exception:  # noqa: BLE001 — wykrywanie tabel bywa kapryśne
            tables = []

    def in_table(x0, y0, x1, y1):
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        return any(r.x0 - 1 <= cx <= r.x1 + 1 and r.y0 - 1 <= cy <= r.y1 + 1 for r, _ in tables)

    # Zbierz fragmenty wierszy (linie PyMuPDF) z informacją o spanach.
    frags = []
    basis_frags = []
    for b in page.get_text("dict")["blocks"]:
        for line in b.get("lines", []):
            spans = [s for s in line["spans"] if s["text"] != ""]
            if not spans or not "".join(s["text"] for s in spans).strip():
                continue
            x0, y0, x1, y1 = line["bbox"]
            if pno == 0 and x0 > page.rect.width * 0.78 and max(sp["size"] for sp in spans) < body:
                basis_frags.append((y0, "".join(sp["text"] for sp in spans)))
                continue
            if tables and in_table(x0, y0, x1, y1):
                continue
            frags.append((x0, y0, x1, y1, spans))

    # Grupuj fragmenty w wiersze wizualne po środku wysokości.
    frags.sort(key=lambda f: ((f[1] + f[3]) / 2, f[0]))
    groups: list[list] = []
    for f in frags:
        cy = (f[1] + f[3]) / 2
        main = max(f[4], key=lambda s: len(s["text"].strip()))
        tol = max(2.5, main["size"] * 0.35)
        if groups:
            g = groups[-1]
            gcy = statistics.mean((h[1] + h[3]) / 2 for h in g)
            if abs(cy - gcy) <= tol:
                g.append(f)
                continue
        groups.append([f])

    rows: list[Row] = []
    for g in groups:
        g.sort(key=lambda f: f[0])
        spans_all = [s for f in g for s in f[4]]
        sizes = [s["size"] for s in spans_all if s["text"].strip()]
        size = max(set(sizes), key=lambda v: sum(len(s["text"]) for s in spans_all if s["size"] == v))
        text_parts = []
        label = None
        prev_x1 = None
        for fi, f in enumerate(g):
            if prev_x1 is not None and f[0] - prev_x1 > 0.8:
                text_parts.append(" ")
            for si, s in enumerate(f[4]):
                t = s["text"]
                small = s["size"] < size * 0.8 and LABEL_RE.match(t)
                if small:
                    lab = LABEL_RE.match(t).group(1)
                    if not "".join(text_parts).strip() and label is None:
                        label = lab  # etykieta na początku wiersza
                    else:
                        text_parts.append(f"\u0000{lab}\u0000")
                    continue
                text_parts.append(t)
            prev_x1 = f[2]
        raw = "".join(text_parts).replace("\u00a0", " ")
        text = re.sub(r"[ \t]+", " ", raw).strip()
        if SPACED_CAPS_RE.match(text):
            # „K O N S T Y T U C J A” → „KONSTYTUCJA” (słowa rozdzielone ≥2 spacjami)
            text = " ".join(re.sub(r"\s+", "", w) for w in re.split(r"\s{2,}", raw.strip()))
        bold_chars = sum(len(s["text"]) for s in spans_all if _span_is_bold(s))
        all_chars = sum(len(s["text"]) for s in spans_all) or 1
        x0 = min(f[0] for f in g)
        y0 = min(f[1] for f in g)
        x1 = max(f[2] for f in g)
        y1 = max(f[3] for f in g)
        if not text and label is None:
            continue
        rows.append(Row(pno, x0, y0, x1, y1, text, size, bold_chars / all_chars > 0.5, label))

    for r, md in tables:
        if md:
            rows.append(Row(pno, r.x0, r.y0, r.x1, r.y1, md, body, False, None, True))
    rows.sort(key=lambda r: r.y0)

    footer_date = None
    basis = [
        t for y, t in sorted(basis_frags) if 60 < y < H - 80 and not HEADER_RE.match(t.strip()) and not DATE_RE.match(t.strip())
    ]
    body_rows: list[Row] = []
    rest: list[Row] = []
    for r in rows:
        if (header_y and (r.y0 + r.y1) / 2 < header_y) or (r.y0 < 70 and HEADER_RE.match(r.text)):
            continue
        if r.y0 < 70 and r.text.startswith("©Kancelaria Sejmu"):
            continue
        if r.y0 > H - 80 and DATE_RE.match(r.text):
            footer_date = r.text if "-" in r.text else "-".join(reversed(r.text.split(".")))
            continue
        if r.y0 < 70 and (HEADER_RE.match(r.text) or not r.text):
            continue
        rest.append(r)

    # Strefa przypisów: poniżej krótkiej poziomej kreski, gdy pod nią jest tylko drobny tekst.
    foot_y = None
    left = min((r.x0 for r in rest), default=0)
    for rc in sorted(rects, key=lambda r: r.y0):
        if rc.y0 < 150 or rc.y0 > H - 40 or abs(rc.x0 - left) > 6:
            continue
        below = [r for r in rest if r.y0 >= rc.y0 - 1]
        if below and all(r.size <= body * 0.92 for r in below):
            foot_y = rc.y0
            break
    foot_rows = []
    for r in rest:
        if foot_y is not None and r.y0 >= foot_y - 1:
            foot_rows.append(r)
        else:
            body_rows.append(r)
    return body_rows, foot_rows, footer_date, basis


def _cell_text(cell, words) -> str:
    if cell is None:
        return ""
    x0, y0, x1, y1 = cell
    ws = [w for w in words if x0 - 1 <= (w[0] + w[2]) / 2 <= x1 + 1 and y0 - 1 <= (w[1] + w[3]) / 2 <= y1 + 1]
    ws.sort(key=lambda w: (w[5], w[6], w[7]))  # blok, linia, słowo
    return " ".join(w[4] for w in ws)


def _table_md(tb, words) -> str:
    clean = [
        [re.sub(r"\s+", " ", _cell_text(c, words)).strip().replace("|", "\\|") for c in row.cells]
        for row in tb.rows
    ]
    clean = [row for row in clean if any(row)]
    if len(clean) < 2:
        return ""
    n = max(len(r) for r in clean)
    clean = [r + [""] * (n - len(r)) for r in clean]
    lines = ["| " + " | ".join(clean[0]) + " |", "|" + " --- |" * n]
    lines += ["| " + " | ".join(r) + " |" for r in clean[1:]]
    return "\n".join(lines)


def _plain_markers(t: str) -> str:
    return re.sub(r"\u0000([^\u0000]*)\u0000", r"\1)", t).replace("\u0000", "")


def _fix_spaced_caps(t: str) -> str:
    if SPACED_CAPS_RE.match(t):
        return re.sub(r"\s+", "", t)
    return t



def convert(pdf_path: str, dehyphenate: bool = False) -> Result:
    """dehyphenate=True dla składu Dz. U. (teksty pierwotne), gdzie wyrazy są dzielone na końcu wiersza."""
    doc = pymupdf.open(pdf_path)
    body = _body_size(doc)
    all_body: list[Row] = []
    footnotes: list[list[str]] = []  # [id, text]
    footer_dates = []
    basis: list[str] = []
    used_ids: set[str] = set()
    marker_maps: dict[int, dict[str, str]] = {}

    for pno, page in enumerate(doc):
        b_rows, f_rows, fdate, bas = _page_rows(page, pno, body)
        if fdate:
            footer_dates.append(fdate)
        basis += bas
        # Przypisy tej strony
        mapping: dict[str, str] = {}
        for r in f_rows:
            r.text = _plain_markers(r.text)
            if r.label is not None:
                fid = r.label
                if fid in used_ids:
                    fid = f"{r.label}-s{pno + 1}"
                used_ids.add(fid)
                mapping[r.label] = fid
                footnotes.append([fid, r.text])
            elif footnotes:
                footnotes[-1][1] = (footnotes[-1][1] + " " + r.text).strip()
            else:
                footnotes.append([f"s{pno + 1}", r.text])
        marker_maps[pno] = mapping
        for r in b_rows:
            if r.label is not None:
                # etykieta (indeks górny) na początku wiersza treści
                r.text = f"\u0000{r.label}\u0000 " + r.text
            all_body.append(r)

    def sub_markers(row: Row) -> str:
        mp = marker_maps.get(row.page, {})

        def rep(m):
            lab = m.group(1)
            # Indeks górny bez przypisu na tej stronie (np. numer pola w formularzu) — zostaw jako tekst.
            return f"[^{mp[lab]}]" if lab in mp else f"{lab})"

        return re.sub(r"\u0000([^\u0000]+)\u0000", rep, row.text)

    # Parametry układu
    if all_body:
        left = statistics.median(sorted(r.x0 for r in all_body)[: max(1, len(all_body) // 3)])
        right = statistics.median(sorted((r.x1 for r in all_body), reverse=True)[: max(1, len(all_body) // 3)])
    else:
        left, right = 70, 525
    pitches = [
        b.y0 - a.y0
        for a, b in zip(all_body, all_body[1:])
        if a.page == b.page and abs(a.size - body) < 0.5 and abs(b.size - body) < 0.5 and 0 < b.y0 - a.y0 < body * 3
    ]
    pitch = statistics.median(pitches) if pitches else body * 1.7
    center = (left + right) / 2

    paras: list[dict] = []
    prev: Row | None = None
    for r in all_body:
        if r.table:
            paras.append({"text": r.text, "centered": False, "bold": False, "table": True})
            prev = None
            continue
        text = _fix_spaced_caps(sub_markers(r))
        if not text:
            continue
        is_centered = abs((r.x0 + r.x1) / 2 - center) < 25 and r.x0 > left + 30
        new = True
        if prev is not None:
            same_page = prev.page == r.page
            gap_ok = (not same_page) or (r.y0 - prev.y0) <= pitch * 1.25
            prev_full = prev.x1 >= right - 45
            struct = bool(STRUCT_RE_ANY.match(text)) or (bool(STRUCT_RE.match(text)) and r.x0 > left + 4)
            if gap_ok and prev_full and not struct and not is_centered and not prev_centered:
                new = False
            if (
                gap_ok
                and is_centered
                and prev_centered
                and same_page
                and prev_bold == r.bold
                and not HEADING_RE.match(text)
                and not HEADING_RE.match(paras[-1]["text"] if paras else "")
            ):
                new = False  # wielowierszowy wyśrodkowany tytuł
        if new or not paras:
            paras.append({"text": text, "centered": is_centered, "bold": r.bold})
        else:
            p = paras[-1]
            if dehyphenate and re.search(r"[a-ząćęłńóśźż]-$", p["text"]) and text[:1].islower():
                p["text"] = p["text"][:-1] + text  # przeniesienie wyrazu: „inteli-” + „gencji”
            elif p["text"].endswith("-") and not p["text"].endswith(" -") and text[:1].islower():
                p["text"] = p["text"] + text  # łącznik na końcu wiersza (np. „społeczno-gospodarczy”)
            else:
                p["text"] = p["text"] + " " + text
        prev = r
        prev_centered = is_centered
        prev_bold = r.bold

    out: list[str] = []
    for p in paras:
        t = p["text"].strip()
        if p.get("table"):
            out.append(t)
        elif p["centered"] and HEADING_RE.match(t) and len(t) < 80:
            out.append(f"## {t}")
        elif p["centered"] and p["bold"] and len(t) < 300:
            out.append(f"**{t}**")
        else:
            if re.match(r"^#", t):
                t = "\\" + t
            out.append(t)

    md = "\n\n".join(out)
    if footnotes:
        md += "\n\n---\n\n## Przypisy\n\n" + "\n\n".join(f"[^{fid}]: {txt}" for fid, txt in footnotes)

    res = Result(markdown=md + "\n", pages=len(doc))
    if footer_dates:
        res.footer_date = max(set(footer_dates), key=footer_dates.count)
    if basis:
        res.basis = re.sub(r"^Opracowano na\s+podstawie:\s*", "", re.sub(r"\s+", " ", " ".join(basis)).strip())
    return res


if __name__ == "__main__":
    import sys

    r = convert(sys.argv[1])
    print(f"<!-- strony={r.pages} data={r.footer_date} podstawa={r.basis} -->")
    print(r.markdown)

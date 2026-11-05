"""S008: OCR dla PDF-ów z uszkodzonym kodowaniem czcionek (tekst wyciągnięty wprost jest nieczytelny).

Strony renderujemy (PyMuPDF), a tekst rozpoznaje tesseract z modelem `pol` (TESSDATA_PREFIX, domyślnie
.cache/tessdata). Z warstwy PDF bierzemy tylko geometrię (linie nagłówka i przypisów, położenie ramki
„Opracowano na podstawie”), a nie tekst.
"""

from __future__ import annotations

import csv
import io
import os
import re
import statistics
import subprocess
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent.parent
TESSDATA = os.environ.get("TESSDATA_PREFIX", str(ROOT / ".cache" / "tessdata"))
DPI = 300
STRUCT = re.compile(r"^(Art\.|§|\d+[a-z]*\)|[a-z]\)|[–—-]\s|Rozdział|DZIAŁ|Dział|Oddział|ODDZIAŁ|Załącznik)")
DATE = re.compile(r"\b(\d{4}-\d{2}-\d{2}|\d{2}[.-]\d{2}[.-]\d{2,4})\b")


def _tesseract_tsv(png: bytes) -> list[dict]:
    env = dict(os.environ, TESSDATA_PREFIX=TESSDATA)
    r = subprocess.run(["tesseract", "stdin", "stdout", "-l", "pol", "--psm", "4", "-c", "tessedit_create_tsv=1"],
                       input=png, capture_output=True, env=env, check=True)
    rows = list(csv.DictReader(io.StringIO(r.stdout.decode("utf-8", "replace")), delimiter="\t", quoting=csv.QUOTE_NONE))
    lines: dict[tuple, dict] = {}
    for w in rows:
        if w.get("level") != "5" or not (w.get("text") or "").strip():
            continue
        k = (w["block_num"], w["par_num"], w["line_num"])
        x, y, wd, h = int(w["left"]), int(w["top"]), int(w["width"]), int(w["height"])
        ln = lines.setdefault(k, {"x0": x, "y0": y, "x1": x + wd, "y1": y + h, "words": []})
        ln["x0"], ln["y0"] = min(ln["x0"], x), min(ln["y0"], y)
        ln["x1"], ln["y1"] = max(ln["x1"], x + wd), max(ln["y1"], y + h)
        ln["words"].append(w["text"])
    out = [dict(v, text=" ".join(v["words"])) for v in lines.values()]
    return sorted(out, key=lambda l: (l["y0"], l["x0"]))


def _ocr_clip(page, clip: pymupdf.Rect, white: list[pymupdf.Rect] = ()) -> list[dict]:
    if clip.is_empty or clip.height < 5:
        return []
    pix = page.get_pixmap(dpi=DPI, clip=clip)
    if white:
        s = DPI / 72
        for r in white:
            # współrzędne pixmapy z clip są bezwzględne (origin = clip.x0*s, clip.y0*s)
            ir = pymupdf.IRect(int(r.x0 * s), int(r.y0 * s), int(r.x1 * s) + 1, int(r.y1 * s) + 1)
            pix.set_rect(ir & pix.irect, (255, 255, 255))
    return _tesseract_tsv(pix.tobytes("png"))


def _paragraphs(lines: list[dict]) -> list[str]:
    if not lines:
        return []
    right = max(l["x1"] for l in lines)
    hs = [l["y1"] - l["y0"] for l in lines]
    lh = statistics.median(hs) if hs else 40
    paras: list[str] = []
    prev = None
    for l in lines:
        t = l["text"].strip()
        new = True
        if prev is not None and paras:
            gap = l["y0"] - prev["y1"]
            prev_full = prev["x1"] > right - lh * 2
            # wiersz kontynuuje akapit, gdy poprzedni sięga prawego marginesu (justowanie),
            # a bieżący nie zaczyna nowej jednostki; wcięcia wiszące punktów są wtedy kontynuacją
            if gap < lh * 1.2 and prev_full and not STRUCT.match(t):
                new = False
            # w starszym składzie „Art. N.” stoi wyśrodkowane w osobnym wierszu — dołącz treść
            if re.fullmatch(r"Art\. \d+[a-z]*\.", paras[-1]) and not STRUCT.match(t) and gap < lh * 1.5:
                new = False
        if new:
            paras.append(t)
        else:
            p = paras[-1]
            paras[-1] = p[:-1] + t if re.search(r"[a-ząćęłńóśźż]-$", p) and t[:1].islower() else p + " " + t
        prev = l
    return paras


def convert_ocr(pdf_path: str) -> tuple[str, str | None, str | None]:
    """Zwraca (markdown, data ze stopki str. 1, ramka „Opracowano na podstawie”)."""
    doc = pymupdf.open(pdf_path)
    body_out: list[str] = []
    foot_out: list[str] = []
    footer_date = basis = None
    for pno, page in enumerate(doc):
        W, H = page.rect.width, page.rect.height
        thin = [d["rect"] for d in page.get_drawings() if d["rect"].height <= 2 and 40 <= d["rect"].width]
        header_y = max([r.y0 for r in thin if r.y0 < 90 and r.width > 250] or [40])
        sep = sorted(r.y0 for r in thin if 150 < r.y0 < H - 40 and r.width < 250)
        foot_y = sep[0] if sep else None
        bottom = H - 62  # stopka z datą
        white = []
        if pno == 0:
            # ramka na prawym marginesie: położenie z warstwy PDF (glify bywają zepsute, współrzędne nie)
            spans = [s for b in page.get_text("dict")["blocks"] for l in b.get("lines", []) for s in l["spans"]
                     if s["text"].strip() and s["bbox"][0] > W * 0.78 and s["bbox"][1] < H * 0.6]
            if spans:
                fr = pymupdf.Rect(min(s["bbox"][0] for s in spans) - 2, min(s["bbox"][1] for s in spans) - 2,
                                  W - 5, max(s["bbox"][3] for s in spans) + 2)
                white.append(fr)
                txt = " ".join(l["text"] for l in _ocr_clip(page, fr))
                m = re.search(r"podstawie:?\s*(.*)", re.sub(r"\s+", " ", txt))
                basis = (m.group(1) if m else txt).strip() or None
            for l in _ocr_clip(page, pymupdf.Rect(W * 0.55, H - 70, W, H)):
                m = DATE.search(l["text"])
                if m:
                    footer_date = m.group(1)
        body_clip = pymupdf.Rect(0, header_y + 3, W, (foot_y - 2) if foot_y else bottom)
        body_out += _paragraphs(_ocr_clip(page, body_clip, white))
        if foot_y:
            foot_out += _paragraphs(_ocr_clip(page, pymupdf.Rect(0, foot_y + 1, W, bottom)))
    md = "\n\n".join(re.sub(r"^#", r"\\#", p) for p in body_out)
    if foot_out:
        md += "\n\n---\n\n## Przypisy (OCR)\n\n" + "\n\n".join(foot_out)
    if footer_date and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", footer_date):
        footer_date = None  # format niejednoznaczny (np. 24-02-99) — nie zgadujemy
    return md + "\n", footer_date, basis


if __name__ == "__main__":
    import sys

    md, d, b = convert_ocr(sys.argv[1])
    print(f"<!-- data={d} podstawa={b} -->")
    print(md)

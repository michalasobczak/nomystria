"""S008: konwersja HTML tekstu aktu z API ELI (text.html) do Markdown w formacie korpusu.

Struktura HTML ISAP: <h1> z typem, datą i tytułem; jednostki <div class="unit unit_XXX">,
każda z etykietą <h3> („Art. 1.”, „§ 2.”, „1.”, „1)”) i treścią <div data-template="xText">.
Jednostki systematyki (rozdziały) mają klasę „with-title” i w <h3> akapity z nazwą i tytułem.
"""

from __future__ import annotations

import html
import re
from html.parser import HTMLParser


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(s).replace(" ", " ")).strip()


class _Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.pending: list[str] = []  # etykiety jednostek czekające na treść („Art. 1.”, „1.”)
        self.units: list[bool] = []  # stos jednostek: czy z tytułem (systematyka)
        self.div_stack: list[str] = []  # rodzaj otwartego <div>: unit / xtext / other
        self.mode: str | None = None  # h1 / h3 / xtext / script
        self.buf: list[str] = []
        self.h3_parts: list[str] = []
        self.h1_parts: list[str] = []
        self.span_class: str | None = None
        self.xtext_depth = 0

    # --- pomocnicze ---
    def _emit(self, text: str):
        text = _clean(text)
        if not text:
            return
        if self.pending:
            text = " ".join(self.pending + [text])
            self.pending = []
        self.out.append(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class") or ""
        if tag == "script":
            self.mode = "script"
            return
        if self.mode == "script":
            return
        if tag == "h1":
            self.mode = "h1"
            self.h1_parts = []
            return
        if self.mode == "h1" and tag == "span":
            self.span_class = cls
            self.buf = []
            return
        if tag == "div":
            if a.get("data-template") == "xText":
                self.div_stack.append("xtext")
                self.mode = "xtext"
                self.buf = []
                self.xtext_depth = 1
                return
            if self.mode == "xtext":
                self.div_stack.append("other")
                self.xtext_depth += 1
                return
            if cls.startswith("unit "):
                self.units.append("with-title" in cls)
                self.div_stack.append("unit")
            else:
                self.div_stack.append("other")
            return
        if tag == "h3" and self.mode is None:
            self.mode = "h3"
            self.h3_parts = []
            self.buf = []
            return
        if self.mode == "h3" and tag == "p":
            if _clean("".join(self.buf)):
                self.h3_parts.append(_clean("".join(self.buf)))
            self.buf = []
            return
        if tag == "br" and self.mode in ("xtext", "h3"):
            self.buf.append(" ")

    def handle_endtag(self, tag):
        if tag == "script":
            self.mode = None
            return
        if self.mode == "script":
            return
        if self.mode == "h1":
            if tag == "span":
                t = _clean("".join(self.buf))
                if t:
                    self.h1_parts.append((self.span_class or "", t))
                self.span_class = None
                return
            if tag == "h1":
                for c, t in self.h1_parts:
                    if "head-type" in c:
                        self.out.append(f"**{t.upper()}**")
                    elif "head-title" in c:
                        self.out.append(f"**{t}**")
                    else:
                        self.out.append(t)
                self.mode = None
                return
        if tag == "div" and self.div_stack:
            kind = self.div_stack.pop()
            if kind == "xtext" or (self.mode == "xtext" and kind == "other"):
                self.xtext_depth -= 1
                if self.xtext_depth == 0:
                    self._emit("".join(self.buf))
                    self.mode = None
                    self.buf = []
                return
            if kind == "unit" and self.units:
                self.units.pop()
                self.pending = []  # etykieta jednostki bez treści (np. uchylona) nie przechodzi dalej
            return
        if self.mode == "h3" and tag == "p":
            if _clean("".join(self.buf)):
                self.h3_parts.append(_clean("".join(self.buf)))
            self.buf = []
            return
        if tag == "h3" and self.mode == "h3":
            if _clean("".join(self.buf)):
                self.h3_parts.append(_clean("".join(self.buf)))
            self.mode = None
            if self.units and self.units[-1]:
                # jednostka systematyki: „Rozdział I” + tytuł
                parts = [p for p in self.h3_parts if p]
                if parts:
                    self.out.append(f"## {parts[0]}")
                    for p in parts[1:]:
                        self.out.append(f"**{p}**")
            else:
                label = " ".join(self.h3_parts)
                if label:
                    self.pending.append(label)
            return

    def handle_data(self, data):
        if self.mode in ("h1", "h3", "xtext"):
            self.buf.append(data)


def convert_html(text: str) -> str:
    p = _Parser()
    p.feed(text)
    p.close()
    if p.pending:
        p.out.append(" ".join(p.pending))
    return "\n\n".join(p.out) + "\n"

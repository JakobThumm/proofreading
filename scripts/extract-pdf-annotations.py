#!/usr/bin/env python3
"""Extract PDF annotations (highlights, notes, strikethroughs, etc.) using pymupdf."""
import sys
import fitz  # pymupdf

SUBTYPE_LABELS = {
    "Text":      "NOTE",
    "Highlight": "HIGHLIGHT",
    "StrikeOut": "STRIKEOUT",
    "Underline": "UNDERLINE",
    "Squiggly":  "SQUIGGLY",
    "FreeText":  "FREETEXT",
    "Ink":       "INK",
    "Square":    "SHAPE",
    "Circle":    "SHAPE",
    "Line":      "LINE",
}

def main():
    if len(sys.argv) < 2:
        print("Usage: extract-pdf-annotations.py <file.pdf>")
        sys.exit(1)

    doc = fitz.open(sys.argv[1])
    total = 0

    for page_num, page in enumerate(doc, start=1):
        annots = list(page.annots())
        if not annots:
            continue
        for annot in annots:
            subtype = SUBTYPE_LABELS.get(annot.type[1], annot.type[1])
            content = annot.info.get("content", "").strip()
            highlighted_text = ""
            if annot.type[1] in ("Highlight", "StrikeOut", "Underline", "Squiggly"):
                highlighted_text = page.get_textbox(annot.rect).strip()

            print(f"[Page {page_num}] [{subtype}]")
            if highlighted_text:
                print(f"  Text:    {highlighted_text!r}")
            if content:
                print(f"  Comment: {content!r}")
            print()
            total += 1

    print(f"--- {total} annotation(s) found across {len(doc)} page(s) ---")

if __name__ == "__main__":
    main()

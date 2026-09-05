#!/usr/bin/env python3
"""Generate bilingual (EN/BM) OpenLP liturgy slides for the Holy Eucharist.

Reads the fixed Ordinary from ordinary.json and (optionally) the weekly propers
(Collect + Post Communion) from propers/<date>.json, filters by liturgical season,
and emits an OpenLP-importable output.html using the same conventions as the
readings pipeline: slides separated by [===], English line(s) then a blank line
then the Bahasa Malaysia line(s) wrapped in {y}{it}...{/y}{/it}.

Usage:
    python generate_liturgy.py                              # season=ordinary, no propers
    python generate_liturgy.py --season lent
    python generate_liturgy.py --date 2026-06-28            # merge that week's propers
    python generate_liturgy.py --date 2026-06-28 --out output.html
    python generate_liturgy.py --only collect_of_purity kyrie gloria
"""
import argparse
import json
import os
import sys

SEASONS = ["advent", "christmas", "epiphany", "ordinary", "lent", "easter"]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def include_item(item, season):
    """Decide whether an item belongs in this season's service."""
    only = item.get("only_seasons")
    if only:
        return season in only
    omit = item.get("omit_seasons")
    if omit:
        return season not in omit
    return True


def fill_proper(item, propers):
    """Populate a proper item (collect / post_communion) from the propers file."""
    if not propers:
        return None
    key = "post_communion" if item["id"] == "post_communion" else "collect"
    data = propers.get(key)
    if not data:
        return None
    return [{"lines": [{"role": "All", "en": data.get("en", ""), "bm": data.get("bm", "")}]}]


def render_bm(text):
    """Wrap each non-empty BM line in OpenLP yellow-italic tags (per readings convention)."""
    out = []
    for line in text.split("\n"):
        out.append("{y}{it}" + line + "{/y}{/it}" if line.strip() else line)
    return "\n".join(out)


def render_slide(slide, missing):
    """Render one slide block: EN line(s), blank line, BM line(s)."""
    en_lines, bm_lines = [], []
    for ln in slide["lines"]:
        role = (ln.get("role", "").strip())
        prefix = f"{role}: " if role else ""
        en = ln.get("en", "").strip()
        bm = ln.get("bm", "").strip()
        # role prefix only on the first physical line of a multi-line block
        en_block = en.split("\n")
        en_lines.append(prefix + en_block[0])
        en_lines.extend(en_block[1:])
        if bm:
            bm_block = bm.split("\n")
            bm_lines.append(prefix + bm_block[0])
            bm_lines.extend(bm_block[1:])
        else:
            missing.append(en[:40])
            bm_lines.append("&lt;BM diperlukan / BM needed&gt;")
    parts = ["\n".join(en_lines), "", render_bm("\n".join(bm_lines))]
    return "\n".join(parts)


def build(ordinary, propers, season, only_ids):
    sections, missing = [], []
    for item in ordinary["items"]:
        if only_ids and item["id"] not in only_ids:
            continue
        if not include_item(item, season):
            continue
        slides = item.get("slides", [])
        if item.get("proper"):
            slides = fill_proper(item, propers) or []
            if not slides:
                slides = [{"lines": [{"role": "All",
                                      "en": f"[{item['title']} — supply propers for this date]",
                                      "bm": ""}]}]
        if not slides:
            continue
        body = "\n[===]\n".join(render_slide(s, missing) for s in slides)
        sections.append(f'<div id="{item["id"]}" data-title="{item["title"]}">\n{body}\n</div>')
    return "\n".join(sections), missing


def wrap_html(body, title):
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
        "  <meta charset=\"UTF-8\">\n"
        f"  <title>{title}</title>\n"
        "  <link rel=\"stylesheet\" href=\"../readings/style.css\">\n"
        "</head>\n<body>\n" + body + "\n</body>\n</html>\n"
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--season", default="ordinary", choices=SEASONS)
    ap.add_argument("--date", help="YYYY-MM-DD; merges propers/<date>.json if present")
    ap.add_argument("--only", nargs="+", help="generate only these item ids")
    ap.add_argument("--ordinary", default=os.path.join(BASE_DIR, "ordinary.json"))
    ap.add_argument("--out", default=os.path.join(BASE_DIR, "output.html"))
    args = ap.parse_args()

    ordinary = load_json(args.ordinary)

    propers = None
    if args.date:
        p = os.path.join(BASE_DIR, "propers", f"{args.date}.json")
        if os.path.exists(p):
            propers = load_json(p)
        else:
            print(f"WARNING: no propers file at {p} — Collect/Post Communion left as placeholders.",
                  file=sys.stderr)

    title = (propers.get("title") if propers else f"Holy Eucharist — {args.season.title()}")
    body, missing = build(ordinary, propers, args.season, set(args.only or []))
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(wrap_html(body, title))

    print(f"Wrote {args.out}  (season={args.season}, date={args.date or 'none'})")
    if missing:
        print(f"\n{len(missing)} slide(s) still need BM translation:")
        for m in missing:
            print(f"  - {m}...")
        print("Fill the empty \"bm\" fields in ordinary.json / the propers file, then re-run.")


if __name__ == "__main__":
    main()

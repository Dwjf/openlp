# OpenLP Liturgy Resources

Scripture-reading and liturgy resources for OpenLP. The repository produces bilingual (English / Bahasa Malaysia) worship
slides for projection.

## Contents

| Path | Description |
|---|---|
| [`readings/`](readings/) | Bilingual scripture-reading slide generator (HTML → 1920×1080 PNGs). |
| `BM.sqlite` | Bahasa Malaysia Bible (public domain) — 66 books, 30,159 verses, for OpenLP's Bible importer. |
| `Eng Lectionary 2026 final_*.pdf` | English lectionary reference (Year C readings). |

## Generating reading slides

```bash
cd readings
python3 generate_images.py
```

The generator reads `readings/input.html` and writes one PNG slide per verse into
`readings/images/<section>/<section>_NNN.png`, with the English line on top and the
Bahasa Malaysia line below in yellow italics.

See [`readings/README.md`](readings/README.md) for the input format, styling rules,
and importing instructions.

## Bible database

`BM.sqlite` follows the OpenLP Bible schema (`book`, `verse`, `metadata` tables).
Import it via **Tools → Bibles → Import Bible** in OpenLP to use Bahasa Malaysia
scripture for live verse selection.

## Requirements

- Python 3
- [Playwright](https://playwright.dev/python/) with a Chromium browser
  (`pip install playwright && playwright install chromium`)

# AGENTS.md

Context and conventions for working in this repository.

## Project

OpenLP liturgy resources  — bilingual
(English / Bahasa Malaysia) scripture-reading slides for worship projection.

## Layout

| Path | What it is |
|---|---|
| `readings/input.html` | Source reading text (edit this to change slides). |
| `readings/generate_images.py` | Generates PNG slides from `input.html` using Playwright/Chromium. |
| `readings/images/` | Generated output: `images/<section>/<section>_NNN.png`. |
| `readings/style.css` | Stylesheet used when importing `output.html` into OpenLP. |
| `readings/README.md` | Detailed generator docs (input format, styling, import). |
| `BM.sqlite` | Bahasa Malaysia Bible (public domain), OpenLP Bible schema. 66 books, 30,159 verses. |
| `Eng Lectionary 2026 final_*.pdf` | English lectionary reference. |
| `README.md` | Top-level project overview. |

## Commands

```bash
# Generate reading slides
cd readings
python3 generate_images.py
```

Playwright is installed system-wide in `/usr/local/lib/python3.13/dist-packages`
(version 1.65.2), via `python3-pip` with `--break-system-packages` because
Debian 13 marks the system Python as externally managed (PEP 668) and ships no
`python3-playwright` package. If it is ever missing:

```bash
sudo apt install -y python3-pip
sudo python3 -m pip install --break-system-packages playwright
```

The script uses Playwright's bundled Chromium if installed, otherwise falls back
to the system browser (`chromium`, `chromium-browser`, `google-chrome`), so
`playwright install chromium` is optional on this machine.

The script resolves `input.html` and `images/` relative to its own directory
(`readings/`), independent of the current working directory.

## Conventions

- `input.html` has one `<div>` per section, keyed by id: `ot`, `nt`, `gospel`,
  `psalms`. Slides are separated by `[===]`; each slide is an English block
  followed by a Bahasa Malaysia block, with `{su}…{/su}` wrapping verse refs.
- Styling: English = white, BM = yellow italic; psalm congregation lines
  (every even slide) are bolded.
- Long slides are auto-shrunk from 70px down to 24px so they fit 1080p. The run
  prints `Shrunk …` / `Warning: … still overflows`; a warning means the verse
  must be split in `input.html`.
- A section with no slides (e.g. an empty `<div id="ot">`) still creates its
  output directory but writes nothing.
- No code comments unless asked.
- Do not commit generated PNGs or large binaries unnecessarily; `BM.sqlite` is
  tracked intentionally as the source Bible database.

## Testing / verification

No test suite. To verify the generator, run the command above and confirm PNGs
are written under `readings/images/` without errors or overflow warnings.

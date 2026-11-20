# Readings slide generator

Generates bilingual (English / Bahasa Malaysia) **scripture reading** slides for
OpenLP, as used at Prince of Peace, Putrajaya. It renders `input.html` into
1920×1080 PNG slides, one per verse, with the English line on top and the BM line
below in yellow italics.

## Files

| File | What it is |
|---|---|
| `input.html` | The source reading text. Edit this. |
| `generate_images.py` | The generator — reads `input.html`, writes PNGs. |
| `images/` | Generated output (`images/<section>/<section>_NNN.png`). |
| `output.html` | Optional OpenLP-tagged output (see below). |
| `style.css` | Stylesheet used when importing `output.html` into OpenLP. |

## Everyday use

```bash
cd readings
python3 generate_images.py
```

Playwright is installed system-wide (1.65.2 in
`/usr/local/lib/python3.13/dist-packages`), so the plain `python3` works. If it is
ever missing, reinstall it with:

```bash
sudo apt install -y python3-pip
sudo python3 -m pip install --break-system-packages playwright
```

The script uses Playwright's bundled Chromium when it is installed, otherwise it
falls back to the system browser (`chromium`, `chromium-browser` or
`google-chrome`), so no browser download is required.

The script always reads `input.html` and writes `images/` from its **own folder**
(the `readings/` level), regardless of the current working directory.

## Input format

`input.html` contains one `<div>` per reading section, keyed by id:

| id | Section |
|---|---|
| `ot` | Old Testament |
| `nt` | New Testament (Epistle) |
| `gospel` | Gospel |
| `psalms` | Responsorial Psalm |

Inside each `<div>`, slides are separated by `[===]`. Each slide is:

```
{su}21:23 {/su}English text…

{su}21:23 {/su}Bahasa Malaysia text…
```

- `{su}…{/su}` wraps the verse reference (rendered as a superscript).
- First block = English, second block = BM.

For **psalms**, the generator bolds every even slide (the congregation's
response), matching the responsive-reading pattern.

## Styling

- English = white, left-aligned.
- BM = yellow (`#FFFF00`) and italic.
- Psalms congregation lines = extra bold (`font-weight: 900`).
- Text starts at 70px and is shrunk automatically (down to 24px) when a slide
  would otherwise overflow the 1080px canvas. If a slide still does not fit at
  24px, the run prints a warning naming the slide — split that verse in
  `input.html`.

## Importing into OpenLP (alternative to PNGs)

The PNGs are used directly as imported slides. If you instead want editable
OpenLP slides, the historical workflow converted `input.html` into `output.html`
by wrapping the BM text in `{y}{it}…{/y}{/it}` (plus `{b}…{/b}` for psalms
responses); `output.html` is then styled by `style.css` on import.

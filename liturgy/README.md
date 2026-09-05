# Liturgy slide generator

Generates bilingual (English / Bahasa Malaysia) **Holy Eucharist** slides for OpenLP,
following Common Worship Order One as used at Prince of Peace, Putrajaya.

It produces an `output.html` in the same format as the `readings/` pipeline:
slides separated by `[===]`, English line(s) → blank line → BM line(s) wrapped in
`{y}{it}…{/y}{/it}`. Import `output.html` into OpenLP; it is styled by `../readings/style.css`.

## Files

| File | What it is |
|---|---|
| `ordinary.json` | The **fixed Ordinary** (Greeting → Dismissal) as data. Edit BM here. |
| `propers/<YYYY-MM-DD>.json` | One file **per Sunday** — that week's Collect + Post Communion. |
| `generate_liturgy.py` | The generator. |
| `output.html` | Generated output (overwritten each run). Import this into OpenLP. |

## Everyday use

```bash
cd liturgy

# 1. Full service for a given Sunday (merges that week's propers):
python3 generate_liturgy.py --date 2026-06-28

# 2. A different season (Gloria auto-dropped in Advent/Lent; Easter acclamation added in Easter):
python3 generate_liturgy.py --season lent
python3 generate_liturgy.py --season easter --date 2026-04-05

# 3. Only certain items (by their id in ordinary.json):
python3 generate_liturgy.py --only kyrie gloria lords_prayer

# 4. Write somewhere other than output.html:
python3 generate_liturgy.py --date 2026-06-28 --out /tmp/service.html
```

Options: `--season` (advent|christmas|epiphany|ordinary|lent|easter, default `ordinary`),
`--date YYYY-MM-DD`, `--only <id> <id> …`, `--out <path>`, `--ordinary <path>`.

## Adding a new Sunday

1. Copy an existing propers file:
   `cp propers/2026-06-28.json propers/<new-date>.json`
2. Edit the new file: set `date`, `title`, `lectionary_year`, `proper`, and the
   `collect` / `post_communion` (`en` + `bm`). Get the texts from the Common Worship
   collects pages (see the parish booklet or churchofengland.org).
3. Run: `python3 generate_liturgy.py --date <new-date>`
4. Import `output.html` into OpenLP.

> The four scripture **readings** are not produced here — they use the `readings/`
> pipeline (`input.html` + `process_slides.py`).

## Editing the fixed Ordinary

Edit `ordinary.json`. Each item:

```json
{
  "id": "kyrie",
  "title": "Kyrie",
  "omit_seasons": ["advent", "lent"],   // optional
  "only_seasons": ["easter"],           // optional
  "slides": [
    { "lines": [
        { "role": "Minister", "en": "Lord, have mercy.", "bm": "Tuhan, kasihanilah kami." },
        { "role": "All",      "en": "Lord, have mercy.", "bm": "Tuhan, kasihanilah kami." }
    ] }
  ]
}
```

- One object in `slides` = one projected slide.
- `role` is optional; if present it is prefixed to the line ("Minister: …").
- Use `\n` inside `en`/`bm` for line breaks within a slide.

## BM status (important)

- **EN is authoritative** (from the parish booklet / Common Worship).
- **BM is an unvetted draft** — review against the Diocese of West Malaysia's
  authorised BM texts before worship use.
- Some BM fields are still **empty** (`""`). The script lists them after every run,
  and renders `‹BM diperlukan / BM needed›` on those slides so they can't slip through.
  Currently missing: the **Nicene Creed** and the **Prayer of Humble Access**.

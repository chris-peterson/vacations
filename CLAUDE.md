# Vacations

Static HTML/CSS vacation site. Zero npm dependencies.

## Architecture

- **Public site**: GitHub Pages (`main` branch). Shows trip "shape" without private details.
- **Private data**: JSON files in `private/` (gitignored). Served from a separate Netlify site with auth.
- **Schemas**: `schemas/trip.schema.json` defines the private data format.

## Private Data

Private JSON files live in `private/2026/<trip>.json`. Schema is at `schemas/trip.schema.json`.

### Editing private data

When editing `private/` JSON files:
1. Run `python3 scripts/validate.py` after changes
2. Run `python3 scripts/check_conflicts.py` to verify no timing conflicts
3. The `dayDetails` array contains raw HTML strings for the scrapbook. Maintain the clipping/tip structure.
4. Times in card objects are display strings (e.g., "4:55 PM"). Times in constraints are ISO 8601.

### Card types

- `transit`: has `time`, `subtitle`, `sleep`, `sleepIcon`
- `game`: has `time`, `timeNote`, `matchup` (object with `away`/`home`)

### Scrapbook HTML structure

Each `dayDetails` entry uses:
- `<div class="clipping">` wrapper
- `<div class="clipping-label">` for section headers
- `<p>` for prose
- `<div class="clipping-tip">` with `<span class="clipping-tip-icon">` + `<span>` for tips
- `<div class="scrap-ornament">` for separators between clipping groups

## Scripts

- `scripts/pull.sh` -- Download private data from Netlify
- `scripts/push.sh` -- Upload private data to Netlify (runs validate first)
- `scripts/validate.py` -- Validate private JSON against schema
- `scripts/check_conflicts.py` -- Check for timing conflicts in itinerary

## Conventions

- All display times are Pacific
- CSS uses custom properties defined in `:root` (no hardcoded RGB values)
- No npm/node dependencies for the site itself
- Self-contained HTML files (CSS + JS inline)
- `private/` is gitignored; personal data never enters the public repo

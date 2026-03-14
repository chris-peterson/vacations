# Backlog

## Private Netlify site

- Create separate repo for private data hosting
- Netlify Function with `?key=` auth
- CORS `_headers` allowing GitHub Pages origin
- Site-wide password for browser access
- Document setup steps in README

## Local dev workflow

- `scripts/pull.sh` / `scripts/push.sh` point to Netlify — not usable until private site exists
- For now: manually copy private JSON → `2026/private-data.json` for local dev

## HTML public shell polish

- Day labels ("Day 1" through "Day 9") could be more descriptive in public mode
- Consider hiding empty card-meta divs when no private data loaded
- Map routes/cities may need updating when itinerary changes

## Schema / tooling

- `scripts/validate.py` could lint dayDetails HTML (unclosed tags, missing clipping structure)
- `scripts/check_conflicts.py` could warn about nights with no lodging booked

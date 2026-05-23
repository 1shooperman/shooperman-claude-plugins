---
name: get-rankings
description: This skill should be used when ranking data from pvpoke.com is needed for a specific cup and CP cap. Fetches and caches GBL combat rankings across categories (overall, leads, closers, switches, chargers, attackers, consistency).
allowed-tools: [WebFetch(domain:pvpoke.com), WebFetch(domain:pokemongo.com)]
user-invocable: false
---

## Instructions

Fetch current GBL rankings for the requested cup and CP cap from pvpoke.com. Cache results to limit requests to a free, community-maintained service.

Requires: `cp` (e.g. `1500`) and `cup` (e.g. `all` or `jungle`). If either is missing, request them before proceeding.

## Sources

### PVPoke
IMPORTANT: https://pvpoke.com/ is the source of truth
- The format of the pvpoke urls is: https://pvpoke.com/rankings/{cup}/{cp}/{category}.
- The {category} enum is [overall, leads, closers, switches, chargers, attackers, consistency]
- The rankings data is JS-rendered and will NOT appear in a plain WebFetch of the page. The CSV export is also a client-side JS blob and is not fetchable.
- Instead, fetch the raw JSON data directly using this URL pattern:
  `https://pvpoke.com/data/rankings/{cup}/{category}/rankings-{cp}.json`
  Example: `https://pvpoke.com/data/rankings/jungle/overall/rankings-1500.json`
- The `{category}` in the JSON path matches the page category (overall, leads, closers, switches, etc.).

### Pokemongo.com
https://pokemongo.com/en/news/ entries labeled GO Battle League* have current information with dates and should be considered for move changes impacting the meta.

## Caching

Cache data for 48 hours in `~/.cache/pokemon-gbl/rankings/`. Refresh if the cached file is older than 48 hours.

Write cache files as `~/.cache/pokemon-gbl/rankings/{cup}_{cp}_{category}.json` (e.g. `~/.cache/pokemon-gbl/rankings/jungle_1500_overall.json`).

Create the directory if it does not exist.

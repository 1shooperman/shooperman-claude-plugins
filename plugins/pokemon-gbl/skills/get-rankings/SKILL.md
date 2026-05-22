---
name: get-rankings
description: Fetches and caches pvpoke.com tier list rankings for a given cup and CP cap. Activated when team-builder needs current meta data.
allowed-tools: [WebFetch(domain:pvpoke.com), WebFetch(domain:pokemongo.com)]
user-invocable: false
---

## Instructions

Fetch current GBL rankings for the requested cup and CP cap from pvpoke.com. Cache results for 48 hours to avoid repeated requests to a free service.

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
- You should cache data for 48 hours in the local .cache folder in this skill so we aren't slamming this free service.
- You should refresh the cache if it's older than 48 hours

## Expectation
- You should have cp (e.g. 1500), cup (e.g. 'all' or 'jungle'). If you don't have this information, ask for it.
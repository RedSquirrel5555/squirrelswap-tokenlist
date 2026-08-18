# SquirrelSwap Token List

The public token list for the [SquirrelSwap](https://app.squirrelswap.pro) aggregator —
address, symbol, decimals and logo for every token SquirrelSwap can route. Standard
token-list format.

- **`tokenlist.json`** — the list (`name`, `version`, `tokens[]`)
- **`token-logo/<address>.png`** — token logos

Served for integrators at **`https://api.squirrelswap.pro/tokenlist.json`**
(logos at `https://api.squirrelswap.pro/token-logos/<address>.png`), which mirrors this
repo. Same-origin with the SquirrelSwap aggregator API.

## Updating

Run `refresh-from-frontend.py` after tokens change in the app — it regenerates
`tokenlist.json` from the app's source, fetches any new logos, and commits. The serving
host picks up the change on its next pull automatically.

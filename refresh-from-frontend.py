#!/usr/bin/env python3
"""Regenerate this public token list from the SquirrelSwap app's source, then commit.

Reads the app's canonical list (private repo), applies the public transform
(list name -> SquirrelSwap, drop the upstream list-icon, rewrite upstream logo URLs to
our own domain, keeping EVERY token), fetches any newly-referenced logos, and commits.
The serving host (api.squirrelswap.pro) pulls this repo, so a push is all that's needed.

Run from this repo's directory after adding tokens in the app:
    python refresh-from-frontend.py
"""
import subprocess, json, os, urllib.request, concurrent.futures, sys

HERE   = os.path.dirname(os.path.abspath(__file__))
APP    = r"C:\Users\redsq\Claude Code\NodeOS\SquirrelSwap"   # private app repo
LOGO   = os.path.join(HERE, "token-logo")
PBASE  = "https://raw.githubusercontent.com/piteasio/app-tokens/main/token-logo/"
OURS   = "https://api.squirrelswap.pro/token-logos/"


def main():
    os.makedirs(LOGO, exist_ok=True)
    subprocess.run(["git", "-C", APP, "fetch", "-q", "origin", "main"], check=False)
    raw = subprocess.run(["git", "-C", APP, "show", "main:src/config/tokenlist.json"],
                         capture_output=True).stdout
    if not raw:
        print("ERROR: could not read the app token list"); sys.exit(1)
    d = json.loads(raw)

    d["name"] = "SquirrelSwap"; d.pop("logoURI", None)
    if isinstance(d.get("keywords"), list):
        d["keywords"] = [k for k in d["keywords"] if "piteas" not in str(k).lower()] \
            or ["pulsechain", "squirrelswap", "aggregator"]
    files = set()
    for t in d.get("tokens", []):
        lu = t.get("logoURI", "") or ""
        if "piteasio" in lu.lower():
            fn = lu.rsplit("/", 1)[-1]; files.add(fn); t["logoURI"] = OURS + fn
    if "piteas" in json.dumps({k: v for k, v in d.items() if k != "tokens"}).lower():
        print("ERROR: 'piteas' still in list metadata"); sys.exit(1)

    # Merge the overlay: tokens added directly here (not in the frontend list) survive a refresh.
    overlay = os.path.join(HERE, "extra-tokens.json")
    if os.path.exists(overlay):
        have_addr = {t["address"].lower() for t in d["tokens"]}
        extra = [t for t in json.load(open(overlay, encoding="utf-8")).get("tokens", [])
                 if t.get("address", "").lower() not in have_addr]
        d["tokens"].extend(extra)
        print(f"merged {len(extra)} overlay token(s)")

    open(os.path.join(HERE, "tokenlist.json"), "w", encoding="utf-8").write(json.dumps(d, indent=2))
    have = set(os.listdir(LOGO))
    missing = sorted(files - have)

    def dl(fn):
        try:
            r = urllib.request.Request(PBASE + fn, headers={"User-Agent": "squirrelswap"})
            b = urllib.request.urlopen(r, timeout=20).read()
            if b and len(b) > 50:
                open(os.path.join(LOGO, fn), "wb").write(b); return 1
        except Exception:
            pass
        return 0
    got = 0
    if missing:
        with concurrent.futures.ThreadPoolExecutor(max_workers=24) as ex:
            got = sum(ex.map(dl, missing))
    print(f"tokens {len(d['tokens'])} | new logos {got}/{len(missing)}")

    subprocess.run(["git", "-C", HERE, "add", "tokenlist.json", "token-logo"], check=True)
    if subprocess.run(["git", "-C", HERE, "diff", "--cached", "--quiet"]).returncode == 0:
        print("no changes"); return
    subprocess.run(["git", "-C", HERE, "commit", "-m",
                    f"refresh token list ({len(d['tokens'])} tokens)"], check=True)
    subprocess.run(["git", "-C", HERE, "push"], check=True)
    print("pushed — serving host will pull on its next cycle")


if __name__ == "__main__":
    main()

"""Command line: generate, match, fetch-corpus and test mode."""

import argparse
import csv
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from . import audio, recipe

MANIFEST = Path(__file__).resolve().parents[2] / "tests" / "corpus" / "manifest.csv"
CACHE = Path(".cache")
AGENT = "corpus-fetch/0.1 (python-urllib)"  # generic: no project or personal details in requests


def corpus(manifest=MANIFEST) -> list[dict]:
    with open(manifest, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["path"] = CACHE / "corpus" / (r["name"] + Path(r["url"].split("?")[0]).suffix.lower())
        r["duration"] = float(r["duration"] or "nan")  # blank: not downloaded when the manifest was built
    return rows


def download(url: str, path: Path, sha256: str | None = None) -> str:
    """Download url to path (via a .part file), retrying when rate-limited; check and
    return the SHA-256."""
    path.parent.mkdir(parents=True, exist_ok=True)
    part = path.with_suffix(path.suffix + ".part")
    for attempt in range(30):
        digest = hashlib.sha256()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": AGENT})
            with urllib.request.urlopen(req, timeout=300) as resp, open(part, "wb") as out:
                while chunk := resp.read(1 << 20):
                    digest.update(chunk)
                    out.write(chunk)
            break
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:  # HTTPError is a URLError
            if getattr(e, "code", 429) not in (429, 500, 502, 503, 504) or attempt == 29:  # rate limits and network drops: wait and retry
                raise
            wait = getattr(e, "headers", None) and e.headers.get("Retry-After")
            print(f"  {e}; retry {attempt + 1}", file=sys.stderr, flush=True)
            time.sleep(max(int(wait) if wait and wait.isdigit() else 0, min(600, 60 * (attempt + 1))))
    if "wikimedia.org" in url:
        time.sleep(10)  # ponytail: fixed pause; upload.wikimedia.org limits bytes per IP and answers 429 for long stretches
    if sha256 and digest.hexdigest() != sha256:
        raise SystemExit(f"{url}: SHA-256 {digest.hexdigest()} does not match the manifest ({part} kept)")
    part.replace(path)
    return digest.hexdigest()


def seconds(path) -> float:
    """Duration by decoding: container headers can be wrong (a VBR MP3 without a Xing header)."""
    return round(len(audio.decode(path)) / audio.RATE, 1)


def fetch(manifest=MANIFEST):
    """Download every corpus file into .cache/corpus and check its SHA-256 (files already
    there are checked too). Rows left blank when the manifest was built (Commons files
    not yet downloaded) get their SHA-256 and duration filled in."""
    rows, filled = corpus(manifest), 0
    for r in rows:
        if r["path"].exists():
            sha = hashlib.sha256(r["path"].read_bytes()).hexdigest()
            if r["sha256"] and sha != r["sha256"]:
                raise SystemExit(f"{r['path']}: SHA-256 does not match the manifest; delete it and fetch again")
        else:
            print(f"fetching {r['name']} ...", flush=True)
            sha = download(r["url"], r["path"], r["sha256"] or None)
        if not r["sha256"]:
            r["sha256"], r["duration"], filled = sha, seconds(r["path"]), filled + 1
    if filled:
        with open(manifest, newline="", encoding="utf-8") as f:
            cols = next(csv.reader(f))
        with open(manifest, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        print(f"filled in {filled} rows of {manifest}")


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")  # reports hold – and × ; Windows consoles default to a code page
    ap = argparse.ArgumentParser(prog="audio-simprints")
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate", help="print an audio file's codes as JSON")
    g.add_argument("audio")
    g.add_argument("--role", default="creator", choices=["creator", "verifier"])
    g.add_argument("--settings", default="{}", help='JSON, e.g. {"step": 0.5}')
    m = sub.add_parser("match", help="check a clip against creator results")
    m.add_argument("clip", help="an audio file, or a verifier JSON written by generate")
    m.add_argument("creators", nargs="+", help="creator JSON files written by generate")
    m.add_argument("--settings", default="{}", help='JSON, e.g. {"tolerance": 20, "min_windows": 3}')
    sub.add_parser("fetch-corpus", help="download the test corpus into .cache/corpus")
    t = sub.add_parser("test", help="manipulate the corpus, match, write a report")
    t.add_argument("--split", default="tuning", choices=["tuning", "test"])
    t.add_argument("--out", type=Path)
    t.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    a = ap.parse_args(argv)
    if a.cmd == "fetch-corpus":
        return fetch()
    if a.cmd == "test":
        from .evaluate import test

        return test(a.split, a.out or MANIFEST.parent / f"report-{a.split}", a.workers)
    s = json.loads(a.settings)
    if a.cmd == "generate":
        json.dump(recipe.generate(a.audio, a.role, s), sys.stdout)
        return
    clip = json.loads(Path(a.clip).read_text()) if a.clip.endswith(".json") else recipe.generate(a.clip, "verifier", s)
    hits = [{"declaration": p} | r for p in a.creators if (r := recipe.match(clip, json.loads(Path(p).read_text()), s))["relationship"] != "none"]
    print(json.dumps(sorted(hits, key=lambda h: -h["windows"]), indent=1))


if __name__ == "__main__":
    main()

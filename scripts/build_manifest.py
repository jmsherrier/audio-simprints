"""Choose the test corpus and write tests/corpus/manifest.csv (run once; the manifest is
the record, since the sources change).

    python scripts/build_manifest.py --video-manifest ../video-simprints/tests/corpus/manifest.csv

Sources, all CC0, public domain or CC BY (CC BY-SA, NC and ND are left out):
- Wikimedia Commons music (Musopen; per-work categories for look-alikes: one piece in
  several performances). Tuning: Musopen's "Set Chopin Free" (solo piano); test:
  Musopen's Kickstarter project and its main category (orchestral, chamber).
- LibriVox (archive.org), public domain: first chapters of different books, split by
  book; and several readings of one chapter (look-alikes).
- archive.org's netlabels collection, CC BY releases, one track per artist: test, and
  (added with --add-netlabels tuning, other artists) tuning.
- archive.org items with a full mix and its stems (mix.mp3 and drums, bass and keys
  stems), CC BY: the "stems" split (added with --add-stems), for Phase 4.
- ccMixter: not used. Its API lists files, but its file server answers 403 to scripts.
- NASA, JPL and White House series from video-simprints' corpus (Wikimedia Commons,
  public domain): other episodes share the series' intro music ("series").
- Free Music Archive: not used. Its downloads need an account.

Downloads go to .cache/corpus (as fetch-corpus); the SHA-256 and duration of each file
are recorded. Selection is seeded.
"""

import argparse
import csv
import hashlib
import html
import json
import random
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from audio_simprints.testmode import AGENT, CACHE, MANIFEST, download, seconds

ACCEPT = re.compile(r"^(Public domain|Public Domain|PDM-owner|CC0|CC BY \d\.\d)$")
SKIP_TITLE = re.compile(r"sample|bars? \d|measures|excerpt|violin [BF] \d|\.mid$|opening", re.I)
LOOKALIKES = {  # set: (split, [Commons title prefixes, the first is the original])
    "gymnopedie-1": ("tuning", ["Erik Satie - gymnopedies - la 1 ere", "Gymnopedie No. 1 (ISRC", "Gymnopedie No. 1..ogg",
                                "Satie Gymnopedie No 1 performed by Michael Laucke"]),
    "gymnopedie-2": ("tuning", ["Satie Gymnopedie No 2 performed by Michael Laucke", "Gymnopedie No. 2 (ISRC"]),
    "gymnopedie-3": ("tuning", ["Satie Gymnopedie No 3 performed by Michael Laucke", "Gymnopedie No. 3 (ISRC", "Gymnopédie no.3",
                                "Debussy Gymnopedie 1, arrangement"]),
    "minute-waltz": ("tuning", ["Chopin - Waltz No. 6 in D-flat major, Op. 64, No. 1 'Minute'", "Chopin Minute Waltz.ogg"]),
    "moonlight-1": ("test", ["Ludwig van Beethoven - sonata no. 14", "Moonlight Sonata.ogg", "Moonlight.ogg", "Sonate Clair de lune"]),
    "entertainer": ("test", ["The Entertainer - Scott Joplin", '"The Entertainer" (1902)', '"The Entertainer", by Scott Joplin',
                             "Scott Joplin - 04 - The Entertainer", "The Entertainer - 1902", "The Entertainer by Kevin MacLeod"]),
    "maple-leaf-rag": ("test", ["Scott Joplin - Maple Leaf Rag", "1906 - Scott Joplin's Maple Leaf Rag", "Maple leaf rag - played by Scott Joplin 1916 V2",
                                "Maple Leaf Rag - Strolling Strings", "Maple Leaf RagQ"]),
    "fur-elise": ("test", ["FurElise.ogg", "Audionautix-com-ccby-furelise"]),
}  # fmt: skip
WORK_CATEGORIES = ["Gymnopédies", "Minute Waltz", "Piano Sonata No. 14 (Beethoven)", "The Entertainer", "Maple Leaf Rag", "Für Elise"]
READINGS = {  # set: (split, [archive.org LibriVox items, the first is the original]): chapter 1 in several readings
    "pride-prejudice-ch1": ("tuning", ["pride_and_prejudice_librivox", "solo_pride_librivox", "pride_prejudice_krs_librivox",
                                       "prideandprejudice_1005_librivox", "pride_prejudice_1102_librivox"]),
    "christmas-carol-1": ("test", ["christmascarol_librivox", "christmas_carol_1111_librivox", "christmascarol_1012_librivox",
                                   "christmas_carol_gg_1611_librivox", "christmascarol_km_librivox"]),
    "call-of-the-wild-ch1": ("test", ["call_of_the_wild", "callofthewild_1509_librivox", "callofthewild_5_2007_librivox",
                                      "callofthewild_tc_1010_librivox"]),
}  # fmt: skip
SERIES = {  # set: (split, originals, other episodes), names in video-simprints' manifest
    "nasa-this-week": ("tuning", ["nasa-twan-2020-01-25", "nasa-twan-2020-02-07"],
                       ["nasa-twan-2020-01-31", "nasa-twan-2020-01-18", "nasa-twan-2020-02-14", "nasa-twan-2017-08-18"]),
    "west-wing-week": ("tuning", ["wh-west-wing-week-2015-06-05"], ["wh-west-wing-week-2016-09-09", "wh-west-wing-week-2015-04-10"]),
    "nasa-space-to-ground": ("test", ["nasa-s2g-2017-01-06", "nasa-s2g-2016-08-11"],
                             ["nasa-s2g-2015-10-16", "nasa-s2g-2017-05-26", "nasa-s2g-2023-07-28", "nasa-s2g-2018-02-23"]),
    "jpl-whats-up": ("test", ["jpl-whats-up-2025-09", "jpl-whats-up-2026-10"],
                     ["jpl-whats-up-2026-05", "jpl-whats-up-2025-08", "jpl-whats-up-2025-12", "jpl-whats-up-2026-11"]),
    "nasa-moment": ("test", ["nasa-moment-kate-rubins", "nasa-moment-tim-peake"],
                    ["nasa-moment-jeff-williams", "nasa-moment-aleksey-ovchinin", "nasa-moment-scott-kelly", "nasa-moment-kjell-lindgren"]),
}  # fmt: skip
COUNTS = {  # (originals, unrelated) per split and source
    ("tuning", "commons"): (8, 22), ("test", "commons"): (12, 40),
    ("tuning", "librivox"): (6, 15), ("test", "librivox"): (8, 30),
    ("test", "netlabels"): (10, 30), ("tuning", "netlabels"): (6, 20),
}  # fmt: skip


def get(url: str, params: dict | None = None, raw=False):
    url += "?" + urllib.parse.urlencode(params) if params else ""
    for attempt in range(8):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": AGENT}), timeout=120) as r:
                body = r.read()
            return body if raw else json.loads(body.decode("utf-8", errors="replace"))
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if getattr(e, "code", 429) not in (429, 500, 502, 503, 504) or attempt == 7:
                raise
            time.sleep(20 * (attempt + 1))


def text(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(s or ""))).strip()


def slug(s: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")[:60]


# --- sources ---------------------------------------------------------------------------


def commons_category(cat: str, depth: int) -> list[dict]:
    out, cont = [], {}
    while True:
        d = get("https://commons.wikimedia.org/w/api.php", {
            "action": "query", "format": "json", "generator": "categorymembers", "gcmtitle": cat, "gcmtype": "file|subcat",
            "gcmlimit": 500, "prop": "imageinfo", "iiprop": "url|size|extmetadata|mediatype",
            "iiextmetadatafilter": "LicenseShortName|Artist", **cont})  # fmt: skip
        for p in d.get("query", {}).get("pages", {}).values():
            if p["ns"] == 14 and depth > 0:
                out += commons_category(p["title"], depth - 1)
            elif p["ns"] == 6 and p.get("imageinfo") and p["imageinfo"][0].get("mediatype") == "AUDIO":
                ii, m = p["imageinfo"][0], p["imageinfo"][0].get("extmetadata", {})
                out.append({"title": p["title"][5:], "cat": cat[9:], "url": ii["url"], "size": ii["size"],
                            "licence": m.get("LicenseShortName", {}).get("value", ""), "artist": text(m.get("Artist", {}).get("value", ""))})  # fmt: skip
        if "continue" not in d:
            return out
        cont = d["continue"]
        time.sleep(0.5)


def commons_row(f: dict, split, role, set_) -> dict:
    who = f" ({f['artist'][:80]})" if f["artist"] else ""
    return {"name": slug(Path(f["title"]).stem), "split": split, "role": role, "set": set_, "source": "wikimedia-commons",
            "url": f["url"], "licence": f["licence"], "credit": f"Wikimedia Commons: {f['title']}{who}"}  # fmt: skip


def librivox_file(item: str, lo=3e6, hi=14e6) -> dict | None:
    """The first 64 kbit/s chapter of an item within the size range, with the item's licence."""
    meta = get(f"https://archive.org/metadata/{item}")
    lic = meta.get("metadata", {}).get("licenseurl", "")
    if not re.search(r"publicdomain|/zero/", lic):
        return None
    files = sorted((f for f in meta.get("files", []) if f["name"].endswith("_64kb.mp3")), key=lambda f: f["name"])
    f = next((f for f in files if lo <= int(f.get("size", 0)) <= hi), None)
    if f is None:
        return None
    title = text(str(meta["metadata"].get("title", item)))
    return {"url": f"https://archive.org/download/{item}/{urllib.parse.quote(f['name'])}",
            "licence": "Public domain (CC0)" if "/zero/" in lic else "Public domain",
            "credit": f"LibriVox: {title}, {f['name']} (archive.org item {item}; read by LibriVox volunteers)"}  # fmt: skip


def librivox_items(n: int) -> list[str]:
    q = {"q": "collection:librivoxaudio AND mediatype:audio AND language:(English OR eng)", "fl[]": "identifier",
         "sort[]": "downloads desc", "rows": n, "output": "json"}  # fmt: skip
    return [d["identifier"] for d in get("https://archive.org/advancedsearch.php", q)["response"]["docs"]]


def netlabel_tracks(n: int, rng: random.Random, exclude=frozenset()) -> list[dict]:
    """n tracks from archive.org's netlabels collection, CC BY 2.0-4.0, one per artist
    (compilations left out, and artists or items in exclude, lower case): the first
    original MP3 of 3-12 MB of each release."""
    lics = " OR ".join(f'"http://creativecommons.org/licenses/by/{v}/"' for v in ("2.0", "2.5", "3.0", "4.0"))
    q = {"q": f"collection:netlabels AND mediatype:audio AND licenseurl:({lics})", "fl[]": "identifier,creator",
         "sort[]": "downloads desc", "rows": 500, "output": "json"}  # fmt: skip
    docs = [d for d in get("https://archive.org/advancedsearch.php", q)["response"]["docs"]
            if isinstance(d.get("creator"), str) and not re.search(r"various|v\.?a\.?$|compilation", d["creator"], re.I)]  # fmt: skip
    rng.shuffle(docs)
    out, artists = [], set()
    for d in docs:
        if len(out) == n:
            break
        if d["creator"].lower() in artists or d["creator"].lower() in exclude or d["identifier"].lower() in exclude:
            continue
        meta = get(f"https://archive.org/metadata/{d['identifier']}")
        lic = re.search(r"creativecommons\.org/licenses/by/(\d\.\d)/$", meta.get("metadata", {}).get("licenseurl", ""))
        files = sorted((f for f in meta.get("files", []) if f["name"].lower().endswith(".mp3") and f.get("source") == "original"
                        and 3e6 <= int(f.get("size", 0)) <= 12e6), key=lambda f: f["name"])  # fmt: skip
        if not lic or not files:
            continue
        artists.add(d["creator"].lower())
        f, title = files[0], text(str(meta["metadata"].get("title", d["identifier"])))
        out.append({"name": slug(f"{d['creator']}-{Path(f['name']).stem}"), "source": "archive-netlabels",
                    "url": f"https://archive.org/download/{d['identifier']}/{urllib.parse.quote(f['name'])}", "licence": f"CC BY {lic.group(1)}",
                    "credit": f"archive.org netlabels: {f['name']} by {d['creator']}, from {title} (item {d['identifier']})"})  # fmt: skip
        time.sleep(0.5)
    return out


# --- main ------------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video-manifest", type=Path, required=True)
    ap.add_argument("--skip-missing-commons", action="store_true",
                    help="do not wait for upload.wikimedia.org (it throttles per IP for hours): leave the SHA-256 and duration of Commons files not yet downloaded blank; fetch-corpus fills them in later")
    ap.add_argument("--add-netlabels", metavar="SPLIT", help="only add this split's netlabel rows (COUNTS) to the existing manifest, "
                    "leaving out every artist and item already in it; nothing else is reselected")
    ap.add_argument("--add-stems", type=int, metavar="N", help="only add a stems split of N songs (full mix and drums, bass and "
                    "keys stems) to the existing manifest")
    a = ap.parse_args()
    if a.add_stems:
        return add_stems(a.add_stems)
    if a.add_netlabels:
        return add_netlabels(a.add_netlabels)
    rng = random.Random("audio-simprints corpus")
    rows = []

    # Commons: look-alike sets, then random originals and unrelated recordings
    works = [f for c in WORK_CATEGORIES for f in commons_category("Category:" + c, 1)]
    for set_, (split, prefixes) in LOOKALIKES.items():
        for i, pre in enumerate(prefixes):
            f = next(f for f in works if f["title"].startswith(pre) and ACCEPT.match(f["licence"]))
            rows.append(commons_row(f, split, "original" if i == 0 else "lookalike", set_))
    used = {r["url"] for r in rows}
    musopen = [f for f in commons_category("Category:Musopen", 1)
               if ACCEPT.match(f["licence"]) and not SKIP_TITLE.search(f["title"]) and 1.5e6 <= f["size"] <= 12e6 and f["url"] not in used]  # fmt: skip
    pools = {"tuning": [f for f in musopen if f["cat"] == "Set Chopin Free"],
             "test": [f for f in musopen if f["cat"] in ("Musopen Kickstarter Project", "Musopen")]}  # fmt: skip
    for split, pool in pools.items():
        n_orig, n_unrel = COUNTS[(split, "commons")]
        for i, f in enumerate(rng.sample(sorted(pool, key=lambda f: f["url"]), n_orig + n_unrel)):
            rows.append(commons_row(f, split, "original" if i < n_orig else "unrelated", "music"))

    # LibriVox: readings of one chapter, then first chapters of other books (split by book)
    for set_, (split, items) in READINGS.items():
        for i, item in enumerate(items):
            f = librivox_file(item, 1e6, 60e6)
            if f:
                rows.append({"name": slug(item), "split": split, "role": "original" if i == 0 else "lookalike", "set": set_, "source": "librivox"} | f)
    skip = {i for _, items in READINGS.values() for i in items}
    items = [i for i in librivox_items(400) if i not in skip]
    rng.shuffle(items)
    for split, pool in (("tuning", items[::2]), ("test", items[1::2])):
        n_orig, n_unrel = COUNTS[(split, "librivox")]
        got = 0
        for item in pool:
            if got == n_orig + n_unrel:
                break
            if f := librivox_file(item):
                rows.append({"name": slug(item), "split": split, "role": "original" if got < n_orig else "unrelated", "set": "speech", "source": "librivox"} | f)
                got += 1

    # Netlabel music on archive.org (test only), one track per artist
    n_orig, n_unrel = COUNTS[("test", "netlabels")]
    for i, t in enumerate(netlabel_tracks(n_orig + n_unrel, rng)):
        rows.append(t | {"split": "test", "role": "original" if i < n_orig else "unrelated", "set": "netlabels"})

    # Series from video-simprints
    with open(a.video_manifest, newline="", encoding="utf-8") as fh:
        video = {r["name"]: r for r in csv.DictReader(fh)}
    for set_, (split, originals, others) in SERIES.items():
        for name in originals + others:
            v = video[name]
            rows.append({"name": name, "split": split, "role": "original" if name in originals else "series", "set": set_,
                         "source": "wikimedia-commons-video", "url": v["url"], "licence": v["licence"], "credit": v["credit"], "sha256": v["sha256"]})  # fmt: skip

    # Unique names, download, hash, duration
    seen = {}
    for r in rows:
        n = seen[r["name"]] = seen.get(r["name"], 0) + 1
        r["name"] += f"-{n}" if n > 1 else ""
        r["path"] = CACHE / "corpus" / (r["name"] + Path(urllib.parse.urlparse(r["url"]).path).suffix.lower())
    # upload.wikimedia.org throttles per IP for long stretches: fetch everything else first
    for r in sorted(rows, key=lambda r: "upload.wikimedia.org" in r["url"]):
        if not r["path"].exists() and a.skip_missing_commons and "upload.wikimedia.org" in r["url"]:
            print("not downloaded:", r["name"], flush=True)
            r["sha256"], r["duration"] = r.get("sha256", ""), ""
            continue
        if not r["path"].exists():
            print("fetching", r["name"], flush=True)
            r["sha256"] = download(r["url"], r["path"], r.get("sha256"))
        else:
            r["sha256"] = r.get("sha256") or hashlib.sha256(r["path"].read_bytes()).hexdigest()
        r["duration"] = seconds(r["path"])
    cols = ["name", "split", "role", "set", "source", "url", "licence", "credit", "sha256", "duration", "stems"]
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} rows ({sum(r['duration'] == '' for r in rows)} not downloaded), "
          f"{sum(r['duration'] or 0 for r in rows) / 3600:.1f} h -> {MANIFEST}")


def add_netlabels(split: str):
    """Append a split's netlabel rows to tests/corpus/manifest.csv (download, SHA-256,
    duration), with artists and items not already in the manifest."""
    with open(MANIFEST, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        cols, old = reader.fieldnames, list(reader)
    if any(r["split"] == split and r["source"] == "archive-netlabels" for r in old):
        raise SystemExit(f"{split} already has netlabel rows")
    exclude = set()
    for r in old:
        if r["source"] == "archive-netlabels":
            m = re.match(r"archive.org netlabels: .* by (.+), from .* \(item (.+)\)$", r["credit"])
            exclude |= {m.group(1).lower(), m.group(2).lower()}
    n_orig, n_unrel = COUNTS[(split, "netlabels")]
    names = {r["name"] for r in old}
    new = []
    for i, t in enumerate(netlabel_tracks(n_orig + n_unrel, random.Random(f"audio-simprints {split} netlabels"), frozenset(exclude))):
        t |= {"split": split, "role": "original" if i < n_orig else "unrelated", "set": "netlabels"}
        while t["name"] in names:
            t["name"] += "-2"
        names.add(t["name"])
        path = CACHE / "corpus" / (t["name"] + Path(urllib.parse.urlparse(t["url"]).path).suffix.lower())
        if not path.exists():
            print("fetching", t["name"], flush=True)
        t["sha256"] = download(t["url"], path) if not path.exists() else hashlib.sha256(path.read_bytes()).hexdigest()
        t["duration"] = seconds(path)
        new.append(t)
    with open(MANIFEST, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(old + new)
    print(f"added {len(new)} {split} netlabel rows ({sum(t['duration'] for t in new) / 3600:.1f} h) -> {MANIFEST}")


STEM_KINDS = {"drums": r"drum", "bass": r"bass", "keys": r"keys"}


def stem_songs(n: int, rng: random.Random) -> list[list[dict]]:
    """n archive.org items, CC BY, with mix.mp3 and drums, bass and keys stems (for each
    kind the shortest file name that has it): [mix row, stem rows] per song."""
    lics = " OR ".join(f'"http://creativecommons.org/licenses/by/{v}/"' for v in ("2.0", "2.5", "3.0", "4.0"))
    q = {"q": f"mediatype:audio AND (title:(stems OR stem OR multitrack OR multitracks) OR subject:(stems OR stem OR multitrack "
              f"OR multitracks)) AND licenseurl:({lics})", "fl[]": "identifier,item_size", "sort[]": "identifier asc", "rows": 500, "output": "json"}  # fmt: skip
    docs = [d for d in get("https://archive.org/advancedsearch.php", q)["response"]["docs"] if (d.get("item_size") or 0) < 6e8]
    rng.shuffle(docs)
    out = []
    for d in docs:
        if len(out) == n:
            break
        meta = get(f"https://archive.org/metadata/{d['identifier']}")
        lic = re.search(r"creativecommons\.org/licenses/by/(\d\.\d)/$", meta.get("metadata", {}).get("licenseurl", ""))
        names = sorted(f["name"] for f in meta.get("files", []) if f.get("source") == "original" and f["name"].lower().endswith(".mp3"))
        kinds = {k: min((f for f in names if re.search(rx, f, re.I) and f != "mix.mp3"), key=len, default=None) for k, rx in STEM_KINDS.items()}
        if not lic or "mix.mp3" not in names or None in kinds.values():
            continue
        title = text(str(meta["metadata"].get("title", d["identifier"])))
        song = slug(f"stems-{title}")
        def row(f, name, role):
            return {"name": name, "split": "stems", "role": role, "set": song, "source": "archive-stems", "licence": f"CC BY {lic.group(1)}",
                    "url": f"https://archive.org/download/{d['identifier']}/{urllib.parse.quote(f)}",
                    "credit": f"archive.org: {f} of {title} (item {d['identifier']})"}  # fmt: skip
        out.append([row("mix.mp3", song, "original")] + [row(f, f"{song}--{k}", "stem") for k, f in kinds.items()])
        time.sleep(0.5)
    return out


def add_stems(n: int):
    """Append a stems split of n songs to tests/corpus/manifest.csv (download, SHA-256,
    duration)."""
    with open(MANIFEST, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        cols, old = reader.fieldnames, list(reader)
    if any(r["split"] == "stems" for r in old):
        raise SystemExit("the manifest already has a stems split")
    new = [t for song in stem_songs(n, random.Random("audio-simprints stems")) for t in song]
    for t in new:
        path = CACHE / "corpus" / (t["name"] + ".mp3")
        if not path.exists():
            print("fetching", t["name"], flush=True)
        t["sha256"] = download(t["url"], path) if not path.exists() else hashlib.sha256(path.read_bytes()).hexdigest()
        t["duration"] = seconds(path)
    with open(MANIFEST, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(old + new)
    print(f"added {len(new)} stems rows, {len(new) // 4} songs ({sum(t['duration'] for t in new) / 3600:.1f} h) -> {MANIFEST}")


if __name__ == "__main__":
    main()

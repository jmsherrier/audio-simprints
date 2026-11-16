"""Command line: generate and match."""

import argparse
import json
import sys
from pathlib import Path

from . import recipe


def main(argv=None):
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
    a = ap.parse_args(argv)
    s = json.loads(a.settings)
    if a.cmd == "generate":
        json.dump(recipe.generate(a.audio, a.role, s), sys.stdout)
        return
    clip = json.loads(Path(a.clip).read_text()) if a.clip.endswith(".json") else recipe.generate(a.clip, "verifier", s)
    hits = [{"declaration": p} | r for p in a.creators if (r := recipe.match(clip, json.loads(Path(p).read_text()), s))["relationship"] != "none"]
    print(json.dumps(sorted(hits, key=lambda h: -h["windows"]), indent=1))


if __name__ == "__main__":
    main()

"""Phase 1 smoke check on a handful of recordings (not the benchmark: test mode is).

    python scripts/smoke.py a.ogg b.mp3 ...

Each file is an original; seeded random excerpts of 5, 10, 30 and 60 s, re-encoded as
MP3 128 kbit/s, are matched against every file. Prints storage, skipped windows,
times, and found / false matches over the tolerance t and M, at both verifier steps.
"""

import json
import random
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

from audio_simprints import audio, recipe

LENGTHS = (5, 10, 30, 60)
REPEATS = 4
TOLERANCES = (12, 16, 20, 24, 28)
MS = (1, 2, 3, 4)
STEPS = {"0.124 s": recipe.FP_HOP, "0.5 s": 0.5}


def main(paths):
    rng = random.Random("audio-simprints smoke")
    creators, minutes, seconds = {}, 0.0, 0.0
    for p in paths:
        t = time.perf_counter()
        creators[p] = recipe.generate(p)
        seconds += time.perf_counter() - t
        minutes += creators[p]["duration"] / 60
    n_codes = sum(len(c["codes"]) for c in creators.values())
    skipped = {k: sum(c["skipped"][k] for c in creators.values()) for k in ("silent", "constant")}
    print(f"{audio.versions()}\n\n{len(paths)} recordings, {minutes:.1f} min. Creator: {n_codes / minutes:.1f} codes/min, "
          f"{16 * n_codes / minutes:.0f} bytes/min as 128-bit codes (start times implied by the grid), "
          f"{sum(len(json.dumps(c)) for c in creators.values()) / minutes:.0f} bytes/min as JSON; "
          f"skipped windows {skipped} of {n_codes + sum(skipped.values())}; {seconds / minutes:.2f} s per minute of audio.\n")  # fmt: skip
    queries = []
    with tempfile.TemporaryDirectory() as tmp:
        for p, c in creators.items():
            for n in LENGTHS:
                for i in range(REPEATS):
                    if c["duration"] < n + 1:
                        continue
                    s = round(rng.uniform(0, c["duration"] - n), 2)
                    out = Path(tmp) / f"q{len(queries)}.mp3"
                    subprocess.run([audio.tool("ffmpeg"), "-nostdin", "-v", "error", "-ss", str(s), "-t", str(n), "-i", p, "-b:a", "128k", str(out)], check=True)
                    t = time.perf_counter()
                    v = {name: recipe.generate(out, "verifier", {"step": st}) for name, st in STEPS.items()}
                    queries.append({"source": p, "start": s, "length": n, "v": v, "seconds": time.perf_counter() - t})
    print(f"{len(queries)} queries; verifier {np.mean([q['seconds'] for q in queries]):.2f} s per query (both steps).\n")
    for name in STEPS:
        print(f"## verifier step {name}\n\n| t | M | " + " | ".join(f"{n} s" for n in LENGTHS) + " | false matches | median offset error (s) | match ms/query |")
        print("|" + " --- |" * (len(LENGTHS) + 5))
        for tol in TOLERANCES:
            for m in MS:
                found, false, err, ms = {n: [0, 0] for n in LENGTHS}, 0, [], []
                for q in queries:
                    t = time.perf_counter()
                    rs = {p: recipe.match(q["v"][name], c, {"tolerance": tol, "min_windows": m}) for p, c in creators.items()}
                    ms.append(1000 * (time.perf_counter() - t))
                    found[q["length"]][1] += 1
                    r = rs[q["source"]]
                    if r["relationship"] != "none" and abs(r["offset"] - q["start"]) <= 1:
                        found[q["length"]][0] += 1
                        err.append(abs(r["offset"] - q["start"]))
                    false += sum(r["relationship"] != "none" for p, r in rs.items() if p != q["source"])
                cells = " | ".join(f"{a}/{b}" for a, b in found.values())
                print(f"| {tol} | {m} | {cells} | {false} | {np.median(err) if err else float('nan'):.2f} | {np.mean(ms):.0f} |")
        print()


if __name__ == "__main__":
    main(sys.argv[1:])

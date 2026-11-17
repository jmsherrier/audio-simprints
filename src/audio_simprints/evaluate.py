"""Test mode: make the manipulated clips of a split, fingerprint each once (cached), match
them against an index of the split's originals, and write report.json and summary.md."""

import hashlib
import json
import random
import statistics
import subprocess
import tempfile
import time
import wave
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from . import audio, recipe
from .testmode import CACHE, corpus

SR = 44100  # manipulations work at this rate, stereo
REPEATS = 2  # random clips per original and manipulation
STEPS = {"0.124": recipe.FP_HOP, "0.5": 0.5}  # verifier steps (seconds)
OFFSET_OK = 2.0  # seconds: a found clip's fitted offset must be this close to the truth
# name: (seconds of the clip, what is done). Codec and level changes apply to 30 s excerpts.
MANIPULATIONS = {
    "excerpt5": 5, "excerpt10": 10, "excerpt30": 30, "excerpt60": 60,
    "mp3-128": 30, "mp3-64": 30, "aac-128": 30, "opus-32": 30,
    "resample-22k": 30, "mono": 30, "volume+6": 30, "volume-6": 30, "phone": 30,
    "noise-snr20": 30, "noise-snr10": 30,
    "speed+2": 30, "speed-2": 30, "speed+5": 30, "speed-5": 30, "tempo+5": 30, "tempo-5": 30,
    "under-speech-6": 30, "under-speech-12": 30, "under-music-6": 30, "under-music-12": 30,
    "reedit": 60, "video": 30,
}  # fmt: skip
ENCODE = {"mp3-128": ["-c:a", "libmp3lame", "-b:a", "128k"], "mp3-64": ["-c:a", "libmp3lame", "-b:a", "64k"],
          "aac-128": ["-c:a", "aac", "-b:a", "128k"], "opus-32": ["-c:a", "libopus", "-b:a", "32k"]}  # fmt: skip
EXT = {"mp3-128": ".mp3", "mp3-64": ".mp3", "aac-128": ".m4a", "opus-32": ".opus"}
FILTER = {"resample-22k": "aresample=22050,aresample=48000", "phone": "highpass=f=300,highpass=f=300,lowpass=f=3400,lowpass=f=3400,aresample=8000",
          "mono": "pan=mono|c0=0.5*c0+0.5*c1"}  # fmt: skip
REEDIT = (3, 20.0)  # segments, seconds each


def speed_of(m: str) -> float:
    """Original seconds per clip second: "speed+2" -> 1.02."""
    return 1 + int(m[5:]) / 100 if m.startswith(("speed", "tempo")) else 1.0


# --- plan ------------------------------------------------------------------------------


def plan(split: str) -> tuple[list, list]:
    """(recordings of the split, queries). Queries: every manipulation of each original,
    REPEATS times at seeded random places; two 30 s excerpts and the whole of every other
    recording (unrelated, look-alike, other episodes of a series)."""
    rows = [r for r in corpus() if r["split"] == split and r["path"].exists()]
    rng = random.Random(f"audio-simprints {split}")
    fg = {"speech": [r for r in rows if r["role"] == "unrelated" and r["source"] == "librivox"],
          "music": [r for r in rows if r["role"] == "unrelated" and r["source"] != "librivox"]}  # fmt: skip
    queries = []
    for r in rows:
        dur = r["duration"]
        if r["role"] == "original":
            for m, n in MANIPULATIONS.items():
                need = REEDIT[0] * REEDIT[1] * 1.1 if m == "reedit" else n * speed_of(m) + 1
                for i in range(REPEATS if dur >= need else 0):
                    q = {"id": f"{r['name']}__{m}__{i}", "source": r["name"], "role": "original", "set": r["set"], "manipulation": m}
                    if m == "reedit":
                        third = dur / REEDIT[0]
                        starts = [round(rng.uniform(k * third, (k + 1) * third - REEDIT[1]), 2) for k in range(REEDIT[0])]
                        rng.shuffle(starts)
                        q["segments"] = [[k * REEDIT[1], s] for k, s in enumerate(starts)]  # [clip time, original time]
                    else:
                        s = round(rng.uniform(0, dur - n * speed_of(m) - 0.5), 2)
                        q["segments"] = [[0.0, s]]
                        q["length"] = round(n * speed_of(m), 2)  # seconds of the original
                    if m.startswith("under"):
                        b = rng.choice(fg["speech" if "speech" in m else "music"])
                        q["foreground"] = [b["name"], round(rng.uniform(0, b["duration"] - n - 0.5), 2)]
                    queries.append(q)
        else:
            for i in range(2):
                s = round(rng.uniform(0, max(0, dur - 30.5)), 2)
                queries.append({"id": f"{r['name']}__excerpt30__{i}", "source": r["name"], "role": r["role"], "set": r["set"],
                                "manipulation": "excerpt30", "segments": [[0.0, s]], "length": min(30.0, dur)})  # fmt: skip
            queries.append({"id": f"{r['name']}__whole", "source": r["name"], "role": r["role"], "set": r["set"], "manipulation": "whole"})
    return rows, queries


# --- manipulations ---------------------------------------------------------------------


def ff(*args, data: bytes | None = None) -> bytes:
    return subprocess.run([audio.tool("ffmpeg"), "-nostdin", "-y", "-v", "error", *map(str, args)], input=data, capture_output=True, check=True).stdout


def load(path, start: float, seconds: float) -> np.ndarray:
    """(n, 2) float32 at SR from start, for seconds."""
    return np.frombuffer(ff("-ss", f"{start:.3f}", "-t", f"{seconds:.3f}", "-i", path, "-ac", 2, "-ar", SR, "-f", "f32le", "-"), "<f4").reshape(-1, 2)


def write_wav(path: Path, x: np.ndarray, rate=SR):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(x.shape[1])
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(np.round(np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())


def rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(x, dtype=np.float64)))) + 1e-9


def make_clip(q: dict, paths: dict, tmp: Path) -> Path:
    """Write one manipulated clip with ffmpeg (and numpy for levels); return its path."""
    m, src = q["manipulation"], paths[q["source"]]
    rng = np.random.default_rng(list(q["id"].encode()))  # seeded by the query id
    wav = tmp / "clip.wav"
    if m == "whole":
        return Path(src)
    if m == "reedit":
        x = np.concatenate([load(src, s, REEDIT[1]) for _, s in q["segments"]])
    else:
        x = load(src, q["segments"][0][1], q["length"])
    if m.startswith("volume"):
        x = x * 10 ** (int(m[6:]) / 20)
    elif m.startswith("noise"):
        x = x + rng.normal(0, rms(x) / 10 ** (int(m[9:]) / 20), x.shape)
    elif m.startswith("under"):
        b, s = q["foreground"]
        f = load(paths[b], s, len(x) / SR)
        f = np.pad(f, ((0, max(0, len(x) - len(f))), (0, 0)))[: len(x)]
        x = x * rms(f) / rms(x) * 10 ** (-int(m.rsplit("-", 1)[1]) / 20) + f
        x = x / max(1.0, float(np.abs(x).max()))
    write_wav(wav, x)
    if m in ENCODE:
        out = tmp / ("clip" + EXT[m])
        ff("-i", wav, *ENCODE[m], out)
        return out
    if m in FILTER:
        out = tmp / "clip2.wav"
        ff("-i", wav, "-af", FILTER[m], out)
        return out
    if m.startswith(("speed", "tempo")):
        out = tmp / "clip2.wav"
        a = speed_of(m)
        ff("-i", wav, "-af", f"asetrate={SR * a:.0f},aresample={SR}" if m.startswith("speed") else f"atempo={a}", out)
        return out
    if m == "video":  # mux under a picture, H.264 + AAC 128k at 48 kHz, then take the soundtrack back out
        mp4, out = tmp / "clip.mp4", tmp / "clip.m4a"
        ff("-f", "lavfi", "-i", "color=c=black:s=320x240:r=25", "-i", wav, "-shortest", "-c:v", "libx264", "-preset", "veryfast",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-ar", 48000, mp4)  # fmt: skip
        ff("-i", mp4, "-vn", "-c:a", "copy", out)
        return out
    return wav


# --- fingerprints (cached) -------------------------------------------------------------


def cached(key: str, make) -> dict:
    """raw fingerprint, block energy, duration and seconds taken, cached as .npz."""
    path = CACHE / "eval" / (key + ".npz")
    if not path.exists():
        t = time.perf_counter()
        pcm = audio.decode(make())
        raw = audio.fingerprint(pcm)
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez(path, raw=raw, energy=recipe.block_energy(pcm), duration=len(pcm) / audio.RATE, seconds=time.perf_counter() - t)
    z = np.load(path)
    return {k: z[k] for k in z.files}


def _recording(r: dict) -> tuple[str, dict]:
    return r["name"], cached(f"recordings/{r['name']}", lambda: r["path"])


def _query(args) -> tuple[str, dict]:
    q, paths, split = args
    if q["manipulation"] == "whole":
        return q["id"], cached(f"recordings/{q['source']}", lambda: paths[q["source"]])
    with tempfile.TemporaryDirectory() as tmp:
        key = hashlib.sha1(json.dumps(q, sort_keys=True).encode()).hexdigest()[:8]  # a changed plan makes a new clip
        return q["id"], cached(f"{split}/{q['id']}-{key}", lambda: make_clip(q, paths, Path(tmp)))


def result(fp: dict, role: str, settings: dict | None = None) -> dict:
    return recipe.from_fingerprint(fp["raw"], fp["energy"], float(fp["duration"]), role, settings)


# --- scoring ---------------------------------------------------------------------------


def score(q: dict, hits: list, sets: dict) -> dict:
    """What one query's hits mean: found (right recording, offset within OFFSET_OK of a
    segment), and every other match as false, shared (another episode of the query's
    series) or look-alike (another performance of the query's piece)."""
    out = {"id": q["id"], "role": q["role"], "manipulation": q["manipulation"], "set": q["set"], "hits": len(hits), "found": False}
    for h in hits:
        if h["declaration"] == q["source"] and q["role"] == "original":
            a = speed_of(q["manipulation"])
            errs = [abs(h["offset"] - (s - a * c)) for c, s in q["segments"]]
            if min(errs) <= OFFSET_OK and not out["found"]:
                k = int(np.argmin(errs))
                c, s = q["segments"][k]
                n = REEDIT[1] if q["manipulation"] == "reedit" else q["length"]
                cover = max(0.0, min(h["original"][1], s + n) - max(h["original"][0], s)) / n
                out |= {"found": True, "relationship": h["relationship"], "offset_error": round(errs[k], 3),
                        "slope_error": round(h["slope"] - a, 4), "coverage": round(cover, 3), "windows": h["windows"]}  # fmt: skip
            continue
        kind = "shared" if sets.get(h["declaration"]) == q["set"] and q["set"] in SERIES_SETS else \
               "lookalike" if sets.get(h["declaration"]) == q["set"] and q["set"] not in GENERIC_SETS else "false"  # fmt: skip
        out.setdefault(kind, []).append([h["declaration"], h["windows"], h["relationship"]])
    return out


GENERIC_SETS = {"music", "speech", "netlabels"}  # sets that are just a source, not a piece or a series
SERIES_SETS = set()  # filled from the manifest: sets with role "series" rows


def pct(a, b) -> str:
    return f"{100 * a / b:.{0 if a == 0 or a / b >= 0.1 else 1}f}% ({a}/{b})" if b else "–"


# --- main ------------------------------------------------------------------------------


def test(split: str, out: Path, workers: int):
    rows, queries = plan(split)
    paths = {r["name"]: str(r["path"]) for r in rows}
    sets = {r["name"]: r["set"] for r in rows}
    SERIES_SETS.update(r["set"] for r in rows if r["role"] == "series")
    originals = [r for r in rows if r["role"] == "original"]
    print(f"{split}: {len(rows)} recordings, {len(originals)} originals, {len(queries)} queries; fingerprinting ...", flush=True)
    with Pool(workers) as pool:
        recs = dict(pool.map(_recording, rows))
        fps = dict(pool.imap_unordered(_query, [(q, paths, split) for q in queries], chunksize=4))
    creators = {r["name"]: result(recs[r["name"]], "creator") for r in originals}
    idx = recipe.index(creators)
    report = {"split": split, "missing": sorted(r["name"] for r in corpus() if r["split"] == split and not r["path"].exists()), "versions": audio.versions(), "recipe": recipe.RECIPE, "match": recipe.MATCH,
              "counts": {role: sum(r["role"] == role for r in rows) for role in ("original", "unrelated", "lookalike", "series")},
              "hours": round(sum(r["duration"] for r in rows) / 3600, 2), "steps": {},
              "originals_per_set": {st: sum(r["set"] == st for r in originals) for st in {r["set"] for r in rows}}}  # fmt: skip
    for name, step in STEPS.items():
        scored, ms = [], []
        for q in queries:
            v = result(fps[q["id"]], "verifier", {"step": step})
            t = time.perf_counter()
            hits = recipe.verify(v, idx)
            ms.append((1000 * (time.perf_counter() - t), v["duration"]))
            scored.append(score(q, hits, sets))
        report["steps"][name] = {"queries": scored, "match_ms": {"median_per_query": round(statistics.median(m for m, _ in ms), 1),
                                 "per_minute_of_clip": round(sum(m for m, _ in ms) / sum(d for _, d in ms) * 60, 1)}}  # fmt: skip
    minutes = sum(float(recs[r["name"]]["duration"]) for r in originals) / 60
    n_codes = sum(len(c["codes"]) for c in creators.values())
    report["volume"] = {"original_minutes": round(minutes, 1), "codes_per_minute": round(n_codes / minutes, 2),
                        "bytes_per_minute_codes": round(16 * n_codes / minutes, 1),
                        "bytes_per_minute_json": round(sum(len(json.dumps(c)) for c in creators.values()) / minutes, 1),
                        "skipped": {k: sum(c["skipped"][k] for c in creators.values()) for k in ("silent", "constant")},
                        "windows": n_codes + sum(sum(c["skipped"].values()) for c in creators.values())}  # fmt: skip
    report["timing"] = timing(originals[:10])
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    (out / "summary.md").write_text(summary(report), encoding="utf-8")
    print((out / "summary.md").read_text(encoding="utf-8"))


def timing(rows: list) -> dict:
    """Creator time per minute of audio (decode, fingerprint, codes), one process, on up
    to ten originals; verifier generation on 30 s of each."""
    t_c, t_v, minutes = 0.0, 0.0, 0.0
    for r in rows:
        t = time.perf_counter()
        c = recipe.generate(r["path"])
        t_c += time.perf_counter() - t
        minutes += c["duration"] / 60
        with tempfile.TemporaryDirectory() as tmp:
            clip = Path(tmp) / "c.wav"
            ff("-t", 30, "-i", r["path"], clip)
            t = time.perf_counter()
            recipe.generate(clip, "verifier")
            t_v += time.perf_counter() - t
    return {"recordings": len(rows), "creator_s_per_minute": round(t_c / minutes, 3), "verifier_s_per_30s_clip": round(t_v / len(rows), 3)}


def summary(r: dict) -> str:
    v, tm = r["volume"], r["timing"]
    L = [f"# Test mode: {r['split']} split", "",
         f"Recipe `{r['recipe']}`, match settings {r['match']}. {r['versions']['fpcalc']}; {r['versions']['ffmpeg'].split(' Copyright')[0]}.",
         f"{r['counts']['original']} originals, {r['counts']['unrelated']} unrelated recordings, {r['counts']['lookalike']} look-alikes "
         f"(other performances or readings of an original's piece), {r['counts']['series']} other episodes of a series; {r['hours']} h in all.",
         *([f"Left out, not downloaded (upload.wikimedia.org throttled this IP): {len(r['missing'])} recordings, "
            + ", ".join(r["missing"]) + "."] if r["missing"] else []),
         f"Found: the right recording, fitted offset within {OFFSET_OK:g} s of the truth (for re-edits, of one segment).", "",
         f"Storage: {v['codes_per_minute']} codes per minute, {v['bytes_per_minute_codes']:.0f} bytes per minute as 128-bit codes "
         f"({v['bytes_per_minute_json']:.0f} as JSON); {v['skipped']['silent']} silent and {v['skipped']['constant']} constant windows "
         f"skipped of {v['windows']}. Time, one process: creator {tm['creator_s_per_minute']} s per minute of audio, "
         f"verifier {tm['verifier_s_per_30s_clip']} s per 30 s clip (decode and fpcalc included).", ""]  # fmt: skip
    steps = r["steps"]
    L += ["## Found per manipulation", "", "| manipulation | " + " | ".join(f"step {s} s" for s in steps) + " | right relationship | median offset error (s) | median coverage | wrong recording |",
          "|" + " --- |" * (len(steps) + 5)]  # fmt: skip
    first = next(iter(steps.values()))["queries"]
    for m in MANIPULATIONS:
        cells = []
        for st in steps.values():
            qs = [q for q in st["queries"] if q["role"] == "original" and q["manipulation"] == m]
            cells.append(pct(sum(q["found"] for q in qs), len(qs)))
        qs = [q for q in first if q["role"] == "original" and q["manipulation"] == m]
        f = [q for q in qs if q["found"]]
        rel = sum(q["relationship"] == ("overlapping" if m == "reedit" else "contained_in") for q in f)
        med = lambda k: f"{statistics.median(q[k] for q in f):.2f}" if f else "–"  # noqa: E731
        L.append(f"| {m} | " + " | ".join(cells) + f" | {pct(rel, len(f))} | {med('offset_error')} | {med('coverage')} | {sum(len(q.get('false', [])) for q in qs)} |")
    L += ["", "Right relationship: contained_in, or overlapping for re-edits (no one stored stretch holds the whole clip). " f"Relationship, offset, coverage and wrong-recording columns: step {next(iter(steps))} s. Coverage: share of the clip's "
          "stretch of the original inside the matched range (stored windows start every 5 s, so the ends are missed).", ""]
    L += ["## False matches", "", "| step | unrelated: queries with a match | unrelated: pairs (whole recording × original) | "
          "look-alike: queries | look-alike: pairs | series episodes: queries matching their series (shared intro) | series: pairs | false matches of series queries |",
          "|" + " --- |" * 8]  # fmt: skip
    n_orig = r["counts"]["original"]
    for s, st in steps.items():
        cell = []
        for role, kinds in (("unrelated", ("false",)), ("lookalike", ("lookalike", "false")), ("series", ("shared",))):
            qs = [q for q in st["queries"] if q["role"] == role]
            ex = [q for q in qs if q["manipulation"] != "whole"]
            wh = [q for q in qs if q["manipulation"] == "whole"]
            pairs = sum(n_orig if role == "unrelated" else r["originals_per_set"][q["set"]] for q in wh)
            cell += [pct(sum(any(q.get(k) for k in kinds) for q in ex), len(ex)), pct(sum(len(q.get(k, [])) for q in wh for k in kinds), pairs)]
        sq = [q for q in st["queries"] if q["role"] == "series"]
        L.append(f"| {s} s | " + " | ".join(cell) + f" | {sum(len(q.get('false', [])) for q in sq)} |")
    L += ["", "Pairs: for unrelated recordings, each whole recording against every original; for look-alikes and series "
          "episodes, each whole recording against the original(s) of its own set. Queries: two 30 s excerpts per recording.", ""]
    st = next(iter(steps.values()))
    bad = [(q["id"], q[k]) for q in st["queries"] for k in ("false", "lookalike") if q.get(k)]
    if bad:
        L += [f"False and look-alike matches at step {next(iter(steps))} s (query: matched recording, windows, relationship):", ""]
        L += [f"- {i}: " + "; ".join(f"{d}, {w}, {rel}" for d, w, rel in h) for i, h in bad]
        L.append("")
    L += ["## Match time", "", "| step | median per query (ms) | per minute of clip (ms) |", "| --- | --- | --- |"]
    L += [f"| {s} s | {st['match_ms']['median_per_query']} | {st['match_ms']['per_minute_of_clip']} |" for s, st in steps.items()]
    return "\n".join(L) + "\n"

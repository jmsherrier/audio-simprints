"""Test mode: make the manipulated clips of a split, fingerprint each once (cached), match
them against an index of the split's originals in several runs (the settings, a coarser
step, stop codes with shared references, speed passes, segments), and write report.json
and summary.md."""

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
PASSES = (0.96, 0.98, 1.02, 1.04)  # the speed-passes run: an experiment, not a default (passes added false matches on tuning)


def speed_of(m: str) -> float:
    """Original seconds per clip second: "speed+2" -> 1.02."""
    return 1 + int(m[5:]) / 100 if m.startswith(("speed", "tempo")) else 1.0


# --- plan ------------------------------------------------------------------------------


def plan(split: str) -> tuple[list, list, dict]:
    """(recordings of the split, queries, reference episodes). Queries: every manipulation
    of each original, REPEATS times at seeded random places, and the whole original
    (against the other originals); two 30 s excerpts and the whole of every other
    recording (unrelated, look-alike, other episodes of a series). One episode per series
    (the first by name) is not queried: it is the series' reference for shared material."""
    rows = [r for r in corpus() if r["split"] == split and r["path"].exists() and r["duration"] == r["duration"]]  # nan: not filled in yet
    rng = random.Random(f"audio-simprints {split}")
    fg = {"speech": [r for r in rows if r["role"] == "unrelated" and r["source"] == "librivox"],
          "music": [r for r in rows if r["role"] == "unrelated" and r["source"] != "librivox"]}  # fmt: skip
    refs = {}
    for r in sorted(rows, key=lambda r: r["name"]):
        if r["role"] == "series":
            refs.setdefault(r["set"], r["name"])
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
            queries.append({"id": f"{r['name']}__whole", "source": r["name"], "role": "original", "set": r["set"],
                            "manipulation": "whole", "segments": [[0.0, 0.0]], "length": dur})  # fmt: skip
        else:
            for i in range(2):  # drawn for reference episodes too, so the other recordings' draws stay put
                s = round(rng.uniform(0, max(0, dur - 30.5)), 2)
                queries.append({"id": f"{r['name']}__excerpt30__{i}", "source": r["name"], "role": r["role"], "set": r["set"],
                                "manipulation": "excerpt30", "segments": [[0.0, s]], "length": min(30.0, dur)})  # fmt: skip
            queries.append({"id": f"{r['name']}__whole", "source": r["name"], "role": r["role"], "set": r["set"], "manipulation": "whole"})
    return rows, [q for q in queries if q["source"] not in refs.values()], refs


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


def cached(key: str, make, speed: float = 1.0) -> dict:
    """raw fingerprint, block energy, duration and seconds taken, cached as .npz. speed:
    the decoded samples are rescaled first (recipe.rescale), for speed passes."""
    path = CACHE / "eval" / (key + (f"@{speed:g}" if speed != 1.0 else "") + ".npz")
    if not path.exists():
        t = time.perf_counter()
        pcm = audio.decode(make())
        pcm = recipe.rescale(pcm, speed) if speed != 1.0 else pcm
        raw = audio.fingerprint(pcm)
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez(path, raw=raw, energy=recipe.block_energy(pcm), duration=len(pcm) / audio.RATE, seconds=time.perf_counter() - t)
    z = np.load(path)
    return {k: z[k] for k in z.files}


def _recording(r: dict) -> tuple[str, dict]:
    return r["name"], cached(f"recordings/{r['name']}", lambda: r["path"])


def _query(args) -> tuple[str, dict]:
    q, paths, split, speed = args
    if q["manipulation"] == "whole":
        return q["id"], cached(f"recordings/{q['source']}", lambda: paths[q["source"]], speed)
    with tempfile.TemporaryDirectory() as tmp:
        key = hashlib.sha1(json.dumps(q, sort_keys=True).encode()).hexdigest()[:8]  # a changed plan makes a new clip
        return q["id"], cached(f"{split}/{q['id']}-{key}", lambda: make_clip(q, paths, Path(tmp)), speed)


def result(fp: dict, role: str, settings: dict | None = None, speed: float = 1.0) -> dict:
    return recipe.from_fingerprint(fp["raw"], fp["energy"], float(fp["duration"]), role, settings, speed)


def prepare(split: str, workers: int, speeds=()) -> dict:
    """Plan a split and fingerprint everything (cached): recordings, queries, and the
    queries rescaled by each of speeds. workers=0: no process pool (all cached already)."""
    rows, queries, refs = plan(split)
    paths = {r["name"]: str(r["path"]) for r in rows}
    SERIES_SETS.update(r["set"] for r in rows if r["role"] == "series")
    jobs = lambda a: [(q, paths, split, a) for q in queries]  # noqa: E731
    if workers:
        with Pool(workers) as pool:
            recs = dict(pool.map(_recording, rows))
            fps = {a: dict(pool.imap_unordered(_query, jobs(a), chunksize=4)) for a in (1.0, *speeds)}
    else:
        recs = dict(map(_recording, rows))
        fps = {a: dict(map(_query, jobs(a))) for a in (1.0, *speeds)}
    return {"split": split, "rows": rows, "queries": queries, "refs": refs, "recs": recs, "fps": fps,
            "sets": {r["name"]: r["set"] for r in rows}, "originals": [r["name"] for r in rows if r["role"] == "original"]}  # fmt: skip


# --- scoring ---------------------------------------------------------------------------


def truth(q: dict) -> list[float]:
    """The offsets (original time minus speed x clip time) of a query's segments."""
    a = speed_of(q["manipulation"])
    return [s - a * c for c, s in q.get("segments", [])]


def score(q: dict, hits: list, sets: dict) -> dict:
    """What one query's hits mean: found (right recording, offset within OFFSET_OK of a
    segment); shared material (a "shared_branding" label); and every other match as false,
    shared (another episode of the query's series) or look-alike (another performance of
    the query's piece). With segments: how many of a query's segments were found, and
    how many reported segments are at no true offset."""
    out = {"id": q["id"], "role": q["role"], "manipulation": q["manipulation"], "set": q["set"], "hits": len(hits), "found": False}
    for h in hits:
        if h.get("label") == "shared_branding":
            out.setdefault("branding", []).append([h["declaration"], h["windows"], h["relationship"]])
            continue
        if h["declaration"] == q["source"] and q["role"] == "original":
            offs = truth(q)
            errs = [abs(h["offset"] - x) for x in offs]
            if min(errs) <= OFFSET_OK:
                k = int(np.argmin(errs))
                c, s = q["segments"][k]
                n = REEDIT[1] if q["manipulation"] == "reedit" else q["length"]
                cover = max(0.0, min(h["original"][1], s + n) - max(h["original"][0], s)) / n
                out |= {"found": True, "relationship": h["relationship"], "offset_error": round(errs[k], 3),
                        "slope_error": round(h["slope"] - speed_of(q["manipulation"]), 4), "coverage": round(cover, 3),
                        "windows": h["windows"], "density": h["density"]}  # fmt: skip
            if "segments" in h:
                out["segments_found"] = sum(any(abs(g["offset"] - x) <= OFFSET_OK for g in h["segments"]) for x in offs)
                out["segments_false"] = sum(all(abs(g["offset"] - x) > OFFSET_OK for x in offs) for g in h["segments"])
            continue
        kind = "shared" if sets.get(h["declaration"]) == q["set"] and q["set"] in SERIES_SETS else \
               "lookalike" if sets.get(h["declaration"]) == q["set"] and q["set"] not in GENERIC_SETS else "false"  # fmt: skip
        out.setdefault(kind, []).append([h["declaration"], h["windows"], h["relationship"], h["density"]])
    return out


def truth_bits(q: dict, v: dict, creator: dict) -> float | None:
    """Median Hamming distance between each stored window inside the query's stretch of
    the original and the verifier window at its true place in the clip (within one
    sub-fingerprint): how far a manipulation moves the codes, whatever the tolerance."""
    vq, vt = recipe.parse(v)
    cq, ct = recipe.parse(creator)
    w, a = recipe.window_of(creator["recipe_version"]), speed_of(q["manipulation"])
    n = REEDIT[1] if q["manipulation"] == "reedit" else q["length"]
    out = []
    for c0, s0 in q["segments"]:
        for code, t in zip(cq, ct):
            if len(vt) and s0 <= t and t + w <= s0 + n:
                x = c0 + (t - s0) / a
                i = int(np.abs(vt - x).argmin())
                if abs(vt[i] - x) <= recipe.FP_HOP:
                    out.append(int(np.bitwise_count(vq[i] ^ code).sum()))
    return float(np.median(out)) if out else None


GENERIC_SETS = {"music", "speech", "netlabels"}  # sets that are just a source, not a piece or a series
SERIES_SETS = set()  # filled from the manifest: sets with role "series" rows


def pct(a, b) -> str:
    return f"{100 * a / b:.{0 if a == 0 or a / b >= 0.1 else 1}f}% ({a}/{b})" if b else "–"


# --- runs ------------------------------------------------------------------------------


def creators_of(ctx: dict, settings: dict, names) -> dict:
    return {n: result(ctx["recs"][n], "creator", settings) for n in names}


def run(ctx: dict, settings: dict | None = None, shared: bool = False, speeds=(), bits: bool = False) -> dict:
    """Every query of a prepared split against the originals, with these settings (over
    recipe.DEFAULTS and MATCH); shared: index each series' reference episode as shared
    material; speeds: verifier passes rescaled by these too; bits: record truth_bits."""
    s = recipe.DEFAULTS | recipe.MATCH | (settings or {})
    creators = creators_of(ctx, s, ctx["originals"])
    idx = recipe.index(creators, creators_of(ctx, s, ctx["refs"].values()) if shared else None, s)
    scored, ms = [], []
    for q in ctx["queries"]:
        vs = [result(ctx["fps"][a][q["id"]], "verifier", s, a) for a in (1.0, *speeds)]
        t = time.perf_counter()
        hits = recipe.verify(vs if speeds else vs[0], idx, s)
        ms.append((1000 * (time.perf_counter() - t), vs[0]["duration"]))
        out = score(q, hits, ctx["sets"])
        if bits and q["role"] == "original" and q["manipulation"] != "whole":
            out["bits"] = truth_bits(q, vs[0], creators[q["source"]])
        scored.append(out)
    return {"settings": {k: s[k] for k in s if k not in ("step",)} | {"step": round(s["step"], 4)}, "shared": shared,
            "speeds": list(speeds), "stop_windows": sum(idx["stop"].get(d, 0) for d in creators), "queries": scored,
            "match_ms": {"median_per_query": round(statistics.median(m for m, _ in ms), 1),
                         "per_minute_of_clip": round(sum(m for m, _ in ms) / sum(d for _, d in ms) * 60, 1)}}  # fmt: skip


def false_counts(ctx: dict, queries: list) -> dict:
    """False-match counts of one run: queries (excerpts) with a match, and pairs (whole
    recordings x originals), per kind of recording."""
    per_set = defaultdict(int)
    for n in ctx["originals"]:
        per_set[ctx["sets"][n]] += 1
    n_orig, out = len(ctx["originals"]), {}
    for role, kinds in (("unrelated", ("false",)), ("original", ("false",)), ("lookalike", ("lookalike", "false")), ("series", ("shared", "false"))):
        qs = [q for q in queries if q["role"] == role]
        ex = [q for q in qs if q["manipulation"] != "whole"] if role != "original" else []
        wh = [q for q in qs if q["manipulation"] == "whole"]
        pairs = sum(n_orig if role == "unrelated" else n_orig - 1 if role == "original" else per_set[q["set"]] for q in wh)
        out[role] = {"queries": [sum(any(q.get(k) for k in kinds) for q in ex), len(ex)],
                     "pairs": [sum(len(q.get(k, [])) for q in wh for k in kinds), pairs]}  # fmt: skip
    out["false_matches"] = sum(len(q.get("false", [])) for q in queries)  # every hit on an unrelated recording, any query
    out["branding"] = sum(bool(q.get("branding")) for q in queries)
    return out


# --- main ------------------------------------------------------------------------------


def test(split: str, out: Path, workers: int):
    ctx = prepare(split, workers, PASSES)
    rows, originals = ctx["rows"], ctx["originals"]
    print(f"{split}: {len(rows)} recordings, {len(originals)} originals, {len(ctx['queries'])} queries", flush=True)
    runs = {"fitted": run(ctx, bits=True), "step 0.5 s": run(ctx, {"step": 0.5}),
            "stop codes": run(ctx, {"stop_owners": recipe.STOP_OWNERS}, shared=True),
            "speed passes": run(ctx, speeds=PASSES), "segments": run(ctx, {"segments": REEDIT[0]})}  # fmt: skip
    for r in runs.values():
        r["false"] = false_counts(ctx, r["queries"])
    creators = creators_of(ctx, recipe.DEFAULTS, originals)
    minutes = sum(float(ctx["recs"][n]["duration"]) for n in originals) / 60
    n_codes = sum(len(c["codes"]) for c in creators.values())
    gen = lambda a: statistics.median(float(ctx["fps"][a][q["id"]]["seconds"]) for q in ctx["queries"] if q["manipulation"] == "excerpt30")  # noqa: E731
    report = {"split": split, "missing": sorted(r["name"] for r in corpus() if r["split"] == split and r["name"] not in ctx["sets"]),
              "versions": audio.versions(), "recipe": recipe.RECIPE, "defaults": recipe.DEFAULTS | {"step": round(recipe.DEFAULTS["step"], 4)},
              "match": recipe.MATCH, "speeds": list(PASSES), "stop_owners": recipe.STOP_OWNERS, "references": ctx["refs"],
              "counts": {role: sum(r["role"] == role for r in rows) for role in ("original", "unrelated", "lookalike", "series")},
              "hours": round(sum(r["duration"] for r in rows) / 3600, 2), "runs": runs,
              "volume": {"original_minutes": round(minutes, 1), "codes_per_minute": round(n_codes / minutes, 2),
                         "bytes_per_minute_codes": round(16 * n_codes / minutes, 1),
                         "bytes_per_minute_json": round(sum(len(json.dumps(c)) for c in creators.values()) / minutes, 1),
                         "skipped": {k: sum(c["skipped"][k] for c in creators.values()) for k in ("silent", "constant")},
                         "windows": n_codes + sum(sum(c["skipped"].values()) for c in creators.values())},
              "pass_seconds": {"speed 1": round(gen(1.0), 3), "per rescaled pass": round(statistics.mean(gen(a) for a in PASSES), 3)},
              "timing": timing([r for r in rows if r["role"] == "original"][:10])}  # fmt: skip
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


def found_cells(runs: dict, m: str) -> list[str]:
    cells = []
    for r in runs.values():
        qs = [q for q in r["queries"] if q["role"] == "original" and q["manipulation"] == m]
        cells.append(pct(sum(q["found"] for q in qs), len(qs)))
    return cells


def false_cells(f: dict) -> list[str]:
    return [pct(*f["unrelated"]["queries"]), pct(*f["unrelated"]["pairs"]), pct(*f["original"]["pairs"]),
            pct(*f["lookalike"]["queries"]), pct(*f["lookalike"]["pairs"]), pct(*f["series"]["queries"]), pct(*f["series"]["pairs"]),
            str(f["false_matches"])]  # fmt: skip


FALSE_HEAD = ("| run | unrelated: excerpts with a match | unrelated: pairs | originals: pairs with another original | "
              "look-alike: excerpts | look-alike: pairs | series: excerpts matching their series | series: pairs | false matches, all queries |")


def summary(r: dict) -> str:
    v, tm, runs = r["volume"], r["timing"], r["runs"]
    fit = runs["fitted"]
    L = [f"# Test mode: {r['split']} split", "",
         f"Recipe `{r['recipe']}`. Settings {r['defaults']}; match {r['match']}. {r['versions']['fpcalc']}; {r['versions']['ffmpeg'].split(' Copyright')[0]}.",
         f"{r['counts']['original']} originals, {r['counts']['unrelated']} unrelated recordings, {r['counts']['lookalike']} look-alikes "
         f"(other performances or readings of an original's piece), {r['counts']['series']} episodes of a series "
         f"({len(r['references'])} of them the series' reference, not queried); {r['hours']} h in all.",
         *([f"Left out, not downloaded (upload.wikimedia.org throttled this IP): {len(r['missing'])} recordings, "
            + ", ".join(r["missing"]) + "."] if r["missing"] else []),
         f"Found: the right recording, fitted offset within {OFFSET_OK:g} s of the truth (for re-edits, of one segment).", "",
         f"Storage: {v['codes_per_minute']} codes per minute, {v['bytes_per_minute_codes']:.0f} bytes per minute as 128-bit codes "
         f"({v['bytes_per_minute_json']:.0f} as JSON); {v['skipped']['silent']} silent and {v['skipped']['constant']} constant windows "
         f"skipped of {v['windows']}. Time, one process: creator {tm['creator_s_per_minute']} s per minute of audio, "
         f"verifier {tm['verifier_s_per_30s_clip']} s per 30 s clip (decode and fpcalc included).", "",
         "Runs: **fitted** (the settings above), **step 0.5 s** (coarser verifier step), **stop codes** (each series' reference "
         f"episode indexed as shared material, labelled shared_branding, and stored windows near it or near {r['stop_owners']} other "
         f"originals left out), **speed passes** (the clip also rescaled by {r['speeds']}), **segments** (up to {REEDIT[0]} "
         "lines per recording).", ""]  # fmt: skip
    L += ["## Found per manipulation", "", "| manipulation | " + " | ".join(runs) + " | right relationship | median offset error (s) | "
          "median coverage | median bits at the true place |", "|" + " --- |" * (len(runs) + 5)]  # fmt: skip
    for m in MANIPULATIONS:
        f = [q for q in fit["queries"] if q["role"] == "original" and q["manipulation"] == m and q["found"]]
        b = [q["bits"] for q in fit["queries"] if q["role"] == "original" and q["manipulation"] == m and q.get("bits") is not None]
        rel = sum(q["relationship"] == ("overlapping" if m == "reedit" else "contained_in") for q in f)
        med = lambda k: f"{statistics.median(q[k] for q in f):.2f}" if f else "–"  # noqa: E731
        L.append(f"| {m} | " + " | ".join(found_cells(runs, m)) + f" | {pct(rel, len(f))} | {med('offset_error')} | {med('coverage')} | "
                 + (f"{statistics.median(b):.0f}" if b else "–") + " |")  # fmt: skip
    L += ["", "Right relationship: contained_in, or overlapping for re-edits. Relationship, offset, coverage and bits: fitted run. "
          "Coverage: share of the clip's stretch of the original inside the matched range. Bits: Hamming distance of each stored "
          f"window to the clip's window at its true place (of 128; the tolerance is {r['match']['tolerance']}).", ""]  # fmt: skip
    L += ["## False matches", "", FALSE_HEAD, "|" + " --- |" * 9]
    L += [f"| {name} | " + " | ".join(false_cells(x["false"])) + " |" for name, x in runs.items()]
    L += ["", "Excerpts: two 30 s excerpts per recording. Pairs: each whole recording against every original (unrelated), "
          "every other original (originals), or the original(s) of its own set (look-alikes, series).", ""]  # fmt: skip
    bad = [(q["id"], q[k]) for q in fit["queries"] for k in ("false", "lookalike") if q.get(k)]
    if bad:
        L += ["False and look-alike matches, fitted run (query: matched recording, windows, relationship, density):", ""]
        L += [f"- {i}: " + "; ".join(", ".join(map(str, x)) for x in h) for i, h in bad] + [""]
    sc = runs["stop codes"]
    L += ["## Shared material (stop codes run)", "",
          f"References: {', '.join(r['references'].values()) or 'none'}. Stop windows left out of the index: {sc['stop_windows']}. "
          f"Queries with a shared_branding label: {sc['false']['branding']} (fitted run: {fit['false']['branding']}). "
          "Series excerpts matching their series' originals: "
          f"{pct(*sc['false']['series']['queries'])} with stop codes, {pct(*fit['false']['series']['queries'])} without.", ""]  # fmt: skip
    seg = [q for q in runs["segments"]["queries"] if q["manipulation"] == "reedit"]
    dist = [sum(q.get("segments_found", 0) == k for q in seg) for k in range(REEDIT[0] + 1)]
    L += ["## Re-edits, segments run", "", f"Segments found per re-edit ({REEDIT[0]} × {REEDIT[1]:g} s, reordered; {len(seg)} queries): "
          + ", ".join(f"{k}: {n}" for k, n in enumerate(dist)) + ". Reported segments at no true offset: "
          f"{sum(q.get('segments_false', 0) for q in seg)} in re-edits, "
          f"{sum(q.get('segments_false', 0) for q in runs['segments']['queries'] if q['manipulation'] != 'reedit')} in other queries.", ""]  # fmt: skip
    if r["pass_seconds"]:
        ps = r["pass_seconds"]
        L += ["## Speed passes", "", f"Each rescaled pass is another fpcalc run on the clip: median {ps['per rescaled pass']} s per 30 s clip "
              f"against {ps['speed 1']} s for the clip as it is (in the test pool, not one process), so {len(r['speeds'])} passes cost "
              f"about {1 + len(r['speeds'])}× the verifier time; match time is in the next table.", ""]  # fmt: skip
    L += ["## Match time", "", "| run | median per query (ms) | per minute of clip (ms) |", "| --- | --- | --- |"]
    L += [f"| {name} | {x['match_ms']['median_per_query']} | {x['match_ms']['per_minute_of_clip']} |" for name, x in runs.items()]
    return "\n".join(L) + "\n"

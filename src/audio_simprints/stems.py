"""Phase 4 experiment: stems. A real stem of a song (drums, bass or keys), alone or mixed
into an unrelated track, against (A) the song's full mix, and (B) demucs stems on both
sides: the full mix separated and indexed per stem, the clip separated and each of its
stems matched. Writes tests/corpus/report-stems/{report.json, summary.md}.

demucs is optional (pip install audio-simprints[stems]); its pretrained weights have no
clear licence (see THIRD-PARTY-NOTICES.md), so this is a research test only.
"""

import json
import random
import statistics
import tempfile
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from . import recipe
from .evaluate import OFFSET_OK, SR, cached, load, pct, result, rms, write_wav
from .testmode import corpus

KINDS = ("drums", "bass", "keys")
REPEATS = 2
SECONDS = 30.0
LEVELS = {"alone": None, "mix 0 dB": 0, "mix −6 dB": -6}  # stem level against the unrelated track's
ACTIVE = -40.0  # dBFS: a stem excerpt quieter than this is drawn again (the stem is silent there)
MODEL = "htdemucs"
PROCESSES, THREADS = 1, 10  # demucs on CPU here: one process of 10 threads did 84 s per minute of audio; 4 of 5 slowed each other to 135 (memory-bound)


def plan():
    rows = [r for r in corpus() if r["split"] == "stems" and r["path"].exists()]
    songs = {r["name"]: r for r in rows if r["role"] == "original"}
    stems = {(r["set"], r["name"].rsplit("--", 1)[1]): r for r in rows if r["role"] == "stem"}
    bgs = [r for r in corpus() if r["split"] == "test" and r["role"] == "unrelated" and r["source"] == "archive-netlabels" and r["path"].exists()]
    rng = random.Random("audio-simprints stems")
    queries = []
    for song in sorted(songs):
        dur = songs[song]["duration"]
        for k in KINDS:
            for i in range(REPEATS):
                for _ in range(10):
                    s = round(rng.uniform(0, dur - SECONDS - 0.5), 2)
                    if 20 * np.log10(rms(load(stems[song, k]["path"], s, SECONDS))) > ACTIVE:
                        break
                b = rng.choice(bgs)
                bs = round(rng.uniform(0, b["duration"] - SECONDS - 0.5), 2)
                for lv in LEVELS:
                    queries.append({"id": f"{song}__{k}__{i}__{lv}", "song": song, "kind": k, "level": lv, "start": s,
                                    "stem": str(stems[song, k]["path"]), "bg": [str(b["path"]), bs]})  # fmt: skip
    for b in bgs:  # the unrelated tracks alone: any match is false
        for i in range(REPEATS):
            queries.append({"id": f"{b['name']}__{i}__bg", "song": None, "kind": "unrelated", "level": "alone",
                            "start": None, "stem": str(b["path"]), "bg": None, "bs": round(rng.uniform(0, b["duration"] - SECONDS - 0.5), 2)})  # fmt: skip
    return songs, queries


def clip(q) -> np.ndarray:
    if q["song"] is None:
        return load(q["stem"], q["bs"], SECONDS)
    x = load(q["stem"], q["start"], SECONDS)
    if LEVELS[q["level"]] is None:
        return x
    b = load(q["bg"][0], q["bg"][1], SECONDS)
    n = min(len(x), len(b))
    x = x[:n] * rms(b[:n]) / rms(x[:n]) * 10 ** (LEVELS[q["level"]] / 20) + b[:n]
    return x / max(1.0, float(np.abs(x).max()))


class Separator:
    def __init__(self, threads: int | None = None):
        import torch

        if threads:
            torch.set_num_threads(threads)
        from demucs.apply import apply_model
        from demucs.pretrained import get_model

        self.torch, self.apply = torch, apply_model
        self.model = get_model(MODEL)
        self.model.eval()
        self.seconds = 0.0  # spent separating
        self.audio = 0.0  # seconds of audio separated

    def __call__(self, x: np.ndarray) -> dict:
        """(n, 2) float32 at SR -> {source: (n, 2)}."""
        t = time.perf_counter()
        with self.torch.no_grad():
            w = self.torch.from_numpy(np.ascontiguousarray(x.T))[None]
            ref = w.mean(0).mean(0)
            mean, std = ref.mean(), ref.std() + 1e-8
            out = self.apply(self.model, (w - mean) / std, device="cpu", progress=False)[0] * std + mean
        self.seconds += time.perf_counter() - t
        self.audio += len(x) / SR
        return {s: out[i].numpy().T for i, s in enumerate(self.model.sources)}


def separated(key: str, x_of, sep) -> dict:
    """Fingerprints of each demucs source of a signal, cached; x_of() gives the signal."""
    sources = ("drums", "bass", "other", "vocals")
    paths = {s: Path(".cache/eval") / f"{key}~{MODEL}-{s}.npz" for s in sources}
    if all(p.exists() for p in paths.values()):
        return {s: cached(f"{key}~{MODEL}-{s}", None) for s in sources}
    parts = sep()(x_of())
    out = {}
    with tempfile.TemporaryDirectory() as tmp:
        for s, y in parts.items():
            wav = Path(tmp) / f"{s}.wav"
            write_wav(wav, y / max(1.0, float(np.abs(y).max())))
            out[s] = cached(f"{key}~{MODEL}-{s}", lambda: wav)
    return out


_SEP = None


def _separate(job) -> tuple[float, float]:
    """In a worker: separate one signal into the cache; (seconds taken, seconds of audio)."""
    global _SEP
    key, x_of = job
    if _SEP is None:
        _SEP = Separator(THREADS)
    t, a = _SEP.seconds, _SEP.audio
    separated(key, x_of, lambda: _SEP)
    return _SEP.seconds - t, _SEP.audio - a


class _Mix:  # picklable signal makers for the pool
    def __init__(self, r):
        self.path, self.duration = str(r["path"]), r["duration"]

    def __call__(self):
        return load(self.path, 0, self.duration + 1)


class _Clip:
    def __init__(self, q):
        self.q = q

    def __call__(self):
        return clip(self.q)


def done(key) -> bool:
    return all((Path(".cache/eval") / f"{key}~{MODEL}-{s}.npz").exists() for s in ("drums", "bass", "other", "vocals"))


def found(q, hits) -> tuple[bool, list]:
    """(found, false hits): found is the right song with the offset within OFFSET_OK."""
    ok, false = False, []
    for h in hits:
        song = h["declaration"].split("|")[0]
        if song == q["song"] and abs(h["offset"] - q["start"]) <= OFFSET_OK:
            ok = True
        elif song != q["song"]:
            false.append([h["declaration"], h["windows"], h["density"]])
    return ok, false


def run(split_out: Path):
    songs, queries = plan()
    s = recipe.DEFAULTS | recipe.MATCH
    jobs = [(f"recordings/{n}", _Mix(r)) for n, r in songs.items()] + [(f"stems/{q['id']}", _Clip(q)) for q in queries if q["level"] != "alone" or q["song"] is None]
    todo = [j for j in jobs if not done(j[0])]
    sep_t = sep_a = 0.0
    if todo:
        print(f"separating {len(todo)} signals with demucs ({PROCESSES} processes)", flush=True)
        with Pool(PROCESSES) as pool:
            for i, (t, a) in enumerate(pool.imap_unordered(_separate, todo), 1):
                sep_t, sep_a = sep_t + t, sep_a + a
                if i % 20 == 0:
                    print(f"  {i}/{len(todo)}", flush=True)
        timing = Path(".cache/eval/stems-separation.json")  # kept, so a re-run from the cache still reports it
        timing.write_text(json.dumps({"seconds": sep_t, "audio": sep_a}))
    t = json.loads(Path(".cache/eval/stems-separation.json").read_text()) if Path(".cache/eval/stems-separation.json").exists() else {}
    sep_t, sep_a = t.get("seconds", 0.0), t.get("audio", 0.0)
    sep = lambda: None  # noqa: E731  everything is cached now
    mixes = {n: cached(f"recordings/{n}", lambda r=r: r["path"]) for n, r in songs.items()}
    idx_a = recipe.index({n: result(fp, "creator", s) for n, fp in mixes.items()}, None, s)
    dm = {n: separated(f"recordings/{n}", lambda r=r: load(r["path"], 0, r["duration"] + 1), sep) for n, r in songs.items()}
    idx_b = recipe.index({f"{n}|{src}": result(fp, "creator", s) for n, d in dm.items() for src, fp in d.items()}, None, s)
    rows, ms = [], {"A": [], "B": []}
    for q in queries:
        with tempfile.TemporaryDirectory() as tmp:
            wav = Path(tmp) / "clip.wav"
            fp = cached(f"stems/{q['id']}", lambda: (write_wav(wav, clip(q)), wav)[1])
        t = time.perf_counter()
        hits_a = recipe.verify(result(fp, "verifier", s), idx_a, s)
        ms["A"].append(1000 * (time.perf_counter() - t))
        hits_b = None
        if q["level"] != "alone" or q["song"] is None:
            parts = separated(f"stems/{q['id']}", None, sep)
            t = time.perf_counter()
            hits_b = [h for p in parts.values() for h in recipe.verify(result(p, "verifier", s), idx_b, s)]
            ms["B"].append(1000 * (time.perf_counter() - t))
        fa, xa = found(q, hits_a)
        fb, xb = found(q, hits_b) if hits_b is not None else (None, [])
        fc, xc = found(q, [h for h in hits_b if not h["declaration"].endswith("|drums")]) if hits_b is not None else (None, [])
        rows.append({"id": q["id"], "kind": q["kind"], "level": q["level"], "A": fa, "A_false": xa, "B": fb, "B_false": xb, "C": fc, "C_false": xc,
                     "B_sources": sorted({h["declaration"].split("|")[1] for h in hits_b or [] if h["declaration"].split("|")[0] == q["song"]})})  # fmt: skip
    r = {"recipe": recipe.RECIPE, "model": MODEL, "match": recipe.MATCH, "songs": len(songs),
         "song_minutes": round(sum(x["duration"] for x in songs.values()) / 60, 1), "queries": rows,
         "codes_per_minute": {"A": round(sum(len(result(fp, "creator", s)["codes"]) for fp in mixes.values()) / sum(x["duration"] for x in songs.values()) * 60, 2),
                              "B": round(sum(len(result(fp, "creator", s)["codes"]) for d in dm.values() for fp in d.values()) / sum(x["duration"] for x in songs.values()) * 60, 2)},
         "match_ms": {k: round(statistics.median(v), 1) for k, v in ms.items()},
         "separation_s_per_minute": round(sep_t / sep_a * 60, 2) if sep_a else None, "separation_threads": THREADS}  # fmt: skip
    split_out.mkdir(parents=True, exist_ok=True)
    (split_out / "report.json").write_text(json.dumps(r, indent=1, ensure_ascii=False), encoding="utf-8")
    (split_out / "summary.md").write_text(summary(r), encoding="utf-8")
    print(summary(r))


def pb(g, k="B") -> str:
    g = [x for x in g if x[k] is not None]
    return pct(sum(x[k] for x in g), len(g)) if g else "not run"


def pf(g, k) -> str:
    g = [x for x in g if x[k] is not None]
    return pct(sum(bool(x[k + "_false"]) for x in g), len(g))


def summary(r) -> str:
    q = r["queries"]
    L = [f"# Stems test (Phase 4)", "",
         f"Recipe `{r['recipe']}`, match {r['match']}. {r['songs']} songs ({r['song_minutes']} min), each with its full mix and real "
         f"drums, bass and keys stems (archive.org, CC BY). A query is {SECONDS:.0f} s of one stem at a random place where it plays, "
         f"{REPEATS} per song and stem: alone, or mixed over an unrelated netlabel track of the test split (stem at the track's "
         f"loudness, or 6 dB under it). Found: the right song, offset within {OFFSET_OK:g} s.", "",
         f"**A**: the query against the songs' full mixes. **B**: demucs ({r['model']}) on both sides: each full mix separated into "
         "drums, bass, other and vocals, each indexed; the query separated too, and each of its four parts matched. B is run on "
         "the mixed queries only. **C**: B with the songs' demucs drums stems left out of the index, a variant, not "
         "fitted.", "",
         "| stem | level | A: found | B: found | C: found |", "| --- | --- | --- | --- | --- |"]  # fmt: skip
    for k in KINDS:
        for lv in LEVELS:
            g = [x for x in q if x["kind"] == k and x["level"] == lv]
            L.append(f"| {k} | {lv} | {pct(sum(x['A'] for x in g), len(g))} | {pb(g)} | {pb(g, 'C')} |")
    for lv in LEVELS:
        g = [x for x in q if x["kind"] in KINDS and x["level"] == lv]
        L.append(f"| all | {lv} | {pct(sum(x['A'] for x in g), len(g))} | {pb(g)} | {pb(g, 'C')} |")
    st = [x for x in q if x["kind"] in KINDS]
    bg = [x for x in q if x["kind"] == "unrelated"]
    fb = [h[0].split("|")[1] for x in q for h in x["B_false"]]
    L += ["", "**False matches** (a hit on another song):", "", "| queries | A | B | C |", "| --- | --- | --- | --- |",
          f"| stem queries | {pf(st, 'A')} | {pf(st, 'B')} | {pf(st, 'C')} |",
          f"| unrelated tracks alone | {pf(bg, 'A')} | {pf(bg, 'B')} | {pf(bg, 'C')} |", "",
          f"B's false hits by demucs stem: " + ", ".join(f"{k} {fb.count(k)}" for k in ("drums", "bass", "other", "vocals")) + ".", ""]  # fmt: skip
    srcs = {}
    for x in st:
        if x["B"]:
            for s in x["B_sources"]:
                srcs.setdefault(x["kind"], {}).setdefault(s, 0)
                srcs[x["kind"]][s] += 1
    L += ["Demucs stems of the right song that B matched, per query stem: " + "; ".join(
        f"{k}: " + ", ".join(f"{s} {n}" for s, n in sorted(v.items(), key=lambda t: -t[1])) for k, v in srcs.items()) + ".", ""]
    L += [f"Cost: {r['codes_per_minute']['A']} codes per minute of song for A, {r['codes_per_minute']['B']} for B (four stems). "
          f"Median match time per query: {r['match_ms']['A']} ms (A), {r['match_ms']['B']} ms (B, four parts). "
          + (f"Separation: {r['separation_s_per_minute']} s per minute of audio in one process of {r['separation_threads']} CPU threads"
             + (f" ({PROCESSES} such processes ran at once)" if PROCESSES > 1 else "") + "." if r["separation_s_per_minute"] else "Separation: cached."), ""]  # fmt: skip
    return "\n".join(L)

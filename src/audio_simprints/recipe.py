"""The audio recipe: Chromaprint's raw stream cut into windows, each window one 128-bit
code (creator: a window every `hop` seconds; verifier: every `step`), codes compared
within a Hamming tolerance, then a time vote. RECIPE.md describes every step."""

import math
from fractions import Fraction

import numpy as np

from . import audio
from .audio import RATE

RECIPE = "audio-simprints/0.2"
FP_STEP = 1365  # samples between Chromaprint sub-fingerprints (frames of 4096 samples, a third apart)
FP_HOP = FP_STEP / RATE  # about 0.124 s
DEFAULTS = {
    "window": 5.0,  # seconds per code: four quarters of 1.25 s (0.1: 10 s)
    "hop": 2.5,  # creator: seconds between window starts (0.1: 5 s)
    "step": FP_HOP,  # verifier: seconds between window starts (one sub-fingerprint)
}
MATCH = {  # fitted on the tuning split: tests/corpus/tune-tuning/summary.md
    "tolerance": 28,  # bits (of 128) two codes may differ by (0.1: 20)
    "min_windows": 3,  # distinct original windows that must lie on one time line (M)
    "min_density": 0.25,  # share of the original's windows inside the matched range that are on the line
    "max_speed": 0.05,  # slopes tried: 1 +/- this (0.1: 0.1)
    "segments": 1,  # >1: also report further lines (re-edits), up to this many per recording
    "stop_owners": 0,  # >0: a stored window near codes of this many other recordings is a stop window
}
SILENT = -60.0  # dBFS: a window quieter than this (RMS) gets no code (-50 skipped -6 dB copies of quiet classical recordings)
CONSTANT = 1.0  # bits: a window whose sub-fingerprints change by fewer bits per step than this, on average, gets no code
SLOPES = np.round(np.arange(0.9, 1.1001, 0.005), 3)  # time vote: slopes tried (1 +/- 10%; video-simprints steps 0.02)
CONTEXT = 3.0  # seconds at the end of a recording no window can start in (Chromaprint's frame and filters, about 2.7 s)
STOP_OWNERS = 0  # stop_owners for test mode's stop-codes run; fitted on the tuning split (no value did better)


def version_string(s: dict) -> str:
    return RECIPE + (f";window={s['window']:g}" if s["window"] != DEFAULTS["window"] else "")


def window_of(version: str) -> float:
    if not version.startswith(RECIPE):
        raise ValueError(f"not an {RECIPE} result: {version!r}")
    opts = dict(x.split("=") for x in version.split(";")[1:])
    return float(opts.get("window", DEFAULTS["window"]))


# --- codes -----------------------------------------------------------------------------


def bounds(window: float) -> list[int]:
    """Quarter boundaries in sub-fingerprints from a window's first: sub-fingerprint r
    belongs to quarter floor(r * FP_HOP / (window / 4)). Exact (fractions), so every
    platform cuts the same."""
    w = Fraction(str(window))
    return [math.ceil(q * w / 4 * RATE / FP_STEP) for q in range(5)]


def creator_starts(n: int, s: dict) -> np.ndarray:
    """First sub-fingerprint of each creator window: the first at or after k * hop
    seconds, for every window that fits."""
    last = n - bounds(s["window"])[4]
    h = Fraction(str(s["hop"])) * RATE / FP_STEP
    return np.array([i for k in range(int(last / h) + 2) if (i := math.ceil(k * h)) <= last], np.int64)


def verifier_starts(n: int, s: dict) -> np.ndarray:
    return np.arange(0, n - bounds(s["window"])[4] + 1, max(1, round(s["step"] / FP_HOP)), dtype=np.int64)


def block_energy(pcm: np.ndarray) -> np.ndarray:
    """Sum of squares of each whole block of FP_STEP samples: block i starts where
    sub-fingerprint i does."""
    n = len(pcm) // FP_STEP
    return (np.asarray(pcm[: n * FP_STEP], np.int64).reshape(n, FP_STEP) ** 2).sum(1)


def codes_of(raw: np.ndarray, energy: np.ndarray, starts: np.ndarray, window: float) -> tuple[np.ndarray, np.ndarray]:
    """Per window start (in sub-fingerprints): the code as four uint32, one per quarter,
    each the bitwise majority of the quarter's sub-fingerprints (a tie gives 0); and why
    the window gets no code: "" (it does), "silent" or "constant"."""
    b = bounds(window)
    raw = np.asarray(raw, np.uint32)
    bits = ((raw[:, None] >> np.arange(32, dtype=np.uint32)) & 1).astype(np.int64)
    cum = np.vstack([np.zeros((1, 32), np.int64), np.cumsum(bits, 0)])
    major = np.stack([(cum[starts + b[q + 1]] - cum[starts + b[q]]) * 2 > b[q + 1] - b[q] for q in range(4)], 1)
    codes = (major.astype(np.uint64) << np.arange(32, dtype=np.uint64)).sum(2).astype(np.uint32)
    flips = np.r_[0, np.cumsum(np.bitwise_count(raw[1:] ^ raw[:-1]), dtype=np.int64)]
    change = (flips[starts + b[4] - 1] - flips[starts]) / (b[4] - 1)
    sq = np.r_[0, np.cumsum(energy, dtype=np.int64)]
    s0 = np.minimum(starts, len(energy))
    s1 = np.minimum(starts + b[4], len(energy))  # the window's blocks: as many as its sub-fingerprints
    db = 10 * np.log10((sq[s1] - sq[s0]) / np.maximum(s1 - s0, 1) / FP_STEP / 32768**2 + 1e-12)
    why = np.where(db < SILENT, "silent", np.where(change < CONSTANT, "constant", ""))
    return codes, why


def from_fingerprint(raw: np.ndarray, energy: np.ndarray, duration: float, role: str, settings: dict | None = None, speed: float = 1.0) -> dict:
    """generate() from a raw fingerprint, the block energies and duration of its samples.
    speed: the samples were rescaled by this factor (see rescale); starts are given in the
    clip's own time, so the time vote sees the clip's real speed."""
    if role not in ("creator", "verifier"):
        raise ValueError(f"role must be 'creator' or 'verifier', not {role!r}")
    s = DEFAULTS | (settings or {})
    starts = (creator_starts if role == "creator" else verifier_starts)(len(raw), s)
    codes, why = codes_of(raw, energy, starts, s["window"]) if len(starts) else (np.zeros((0, 4), np.uint32), np.array([]))
    keep = why == ""
    out = {"recipe_version": version_string(s), "role": role, "duration": round(duration / speed, 3),
           "hop": round(s["hop"] if role == "creator" else max(1, round(s["step"] / FP_HOP)) * FP_HOP / speed, 4),
           "codes": [{"start": round(int(i) * FP_HOP / speed, 3), "code": "".join(f"{int(v):08x}" for v in c)}
                     for i, c in zip(starts[keep], codes[keep])],
           "skipped": {"silent": int((why == "silent").sum()), "constant": int((why == "constant").sum())}}  # fmt: skip
    out["reason"] = None if out["codes"] else "shorter than one window" if not len(starts) else "every window skipped"
    return out | ({"speed": speed} if speed != 1.0 else {})


def generate(path, role: str = "creator", settings: dict | None = None) -> dict:
    """The codes of an audio file: creator (one window every `hop` seconds, to store with
    the declaration) or verifier (every `step`, for a clip being checked)."""
    return from_samples(audio.decode(path), role, settings)


def from_samples(pcm: np.ndarray, role: str, settings: dict | None = None, raw: np.ndarray | None = None) -> dict:
    """generate() from decoded samples (and their raw fingerprint, if already made)."""
    raw = audio.fingerprint(pcm) if raw is None else raw
    return from_fingerprint(raw, block_energy(pcm), len(pcm) / RATE, role, settings)


def rescale(pcm: np.ndarray, speed: float) -> np.ndarray:
    """Samples played `speed` times slower (pitch too): undoes a clip sped up by `speed`."""
    # ponytail: linear interpolation at 11,025 Hz; a proper resampler if the passes need cleaner chroma
    return np.interp(np.arange(0, len(pcm) - 1, 1 / speed), np.arange(len(pcm)), pcm).round().astype(np.int16)


def speed_passes(pcm: np.ndarray, speeds, settings: dict | None = None) -> list:
    """Verifier results of a clip as it is and rescaled by each of speeds, for verify()."""
    out = [from_samples(pcm, "verifier", settings)]
    for a in speeds:
        x = rescale(pcm, a)
        out.append(from_fingerprint(audio.fingerprint(x), block_energy(x), len(x) / RATE, "verifier", settings, a))
    return out


# --- matching --------------------------------------------------------------------------


def parse(r: dict) -> tuple[np.ndarray, np.ndarray]:
    """A generate() result -> (codes as (n, 2) uint64, start times)."""
    c = [x for x in r["codes"] if not x.get("stop")]
    codes = np.array([np.frombuffer(bytes.fromhex(x["code"]), ">u8") for x in c], np.uint64).reshape(-1, 2)
    return codes, np.array([x["start"] for x in c], float)


def near(q: np.ndarray, r: np.ndarray, t: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(i, j, distance) of every pair q[i], r[j] within t bits, in blocks of q to bound memory."""
    out = [np.zeros(0, int)] * 3
    for k in range(0, len(q), 2048):
        d = np.bitwise_count(q[k : k + 2048, None, :] ^ r[None, :, :]).sum(2)
        i, j = np.nonzero(d <= t)
        out = [np.r_[out[0], i + k], np.r_[out[1], j], np.r_[out[2], d[i, j]]]
    return tuple(out)


def time_vote(c: np.ndarray, t: np.ndarray, g: np.ndarray, q: np.ndarray, tol: float, slopes: np.ndarray = SLOPES):
    """The line t = a c + b with the highest score within tol seconds of it: per group g,
    the best quality q of its points on the line, summed. Returns (a, b, groups on the
    line, inlier mask), or None.

    For each slope, the offsets b = t - a c are put in bins of tol seconds; a candidate
    line spans two neighbouring bins (offsets within tol of their shared edge). The best
    candidate wins (ties: the slope nearer 1); its offset is then the median of its
    points' offsets. This is linear in the number of hits.

    From video-simprints 0.1 (recipe.time_vote), with changes: video counts distinct clip
    times, here g is the original window, so a finer verifier step does not inflate the
    count; lines are ranked by quality, not count, so a few hits off alignment (at a
    clip's ends) cannot tilt a line of exact ones; the tolerance is passed in (see
    decide); and offsets are binned instead of trying a line through every hit, whose
    cost grew with the square of the hits (whole recordings at a loose tolerance)."""
    if not len(c):
        return None
    n_s, n = len(slopes), len(c)
    off = t[None, :] - slopes[:, None] * c[None, :]  # slopes x hits
    k = np.floor(off / tol).astype(np.int64)
    gi = np.unique(g, return_inverse=True)[1]
    sl, pr = np.tile(np.repeat(np.arange(n_s), n), 2), np.r_[k.ravel(), k.ravel() - 1]  # each hit is in two candidates
    gg, qq = np.tile(gi, 2 * n_s), np.tile(q, 2 * n_s)
    o = np.lexsort((gg, pr, sl))
    sl, pr, gg, qq = sl[o], pr[o], gg[o], qq[o]
    first = np.flatnonzero(np.r_[True, (np.diff(sl) != 0) | (np.diff(pr) != 0) | (np.diff(gg) != 0)])
    best_q, sl, pr = np.maximum.reduceat(qq, first), sl[first], pr[first]  # per (slope, candidate, group)
    first = np.flatnonzero(np.r_[True, (np.diff(sl) != 0) | (np.diff(pr) != 0)])
    score, sl, pr = np.add.reduceat(best_q, first), sl[first], pr[first]  # per (slope, candidate)
    w = np.lexsort((np.abs(slopes[sl] - 1), -score))[0]
    o = off[sl[w]]
    inl = np.abs(o - (pr[w] + 1) * tol) <= tol
    b = float(np.median(o[inl]))
    inl = np.abs(o - b) <= tol
    return float(slopes[sl[w]]), b, len(np.unique(g[inl])), inl


def match(verifier: dict, creator: dict, settings: dict | None = None) -> dict:
    """How a clip (verifier result) relates to a recording (creator result): the windows
    on one time line, the matched range in each, the offset and speed of the line, and
    the relationship."""
    s = MATCH | (settings or {})
    check_windows(verifier, [creator])
    vq, vt = parse(verifier)
    cq, ct = parse(creator)
    qi, rj, dist = near(vq, cq, s["tolerance"])
    return decide(verifier, creator, vt[qi], ct[rj], rj, dist, s, ct)


def check_windows(verifier: dict, creators) -> float:
    w = window_of(verifier["recipe_version"])
    if any(window_of(c["recipe_version"]) != w for c in creators):
        raise ValueError("cannot match codes of different window lengths")
    return w


def index(declarations: dict, shared: dict | None = None, settings: dict | None = None) -> dict:
    """An in-memory index of {id: creator result}, for verify().

    shared: {id: creator result} of known shared material (intros, jingles, adverts). Its
    codes are indexed too, and matches to it come back labelled "shared_branding". A
    declaration's window that matches shared material, or (with stop_owners) the codes of
    that many other declarations, is a stop window: it is left out of the index."""
    s = MATCH | (settings or {})
    shared = {d: r for d, r in (shared or {}).items() if d not in declarations}
    ids = list(declarations) + list(shared)
    parsed = [parse((declarations | shared)[d]) for d in ids]
    codes = np.concatenate([c for c, _ in parsed]) if ids else np.zeros((0, 2), np.uint64)
    starts = np.concatenate([t for _, t in parsed]) if ids else np.zeros(0)
    owner = np.repeat(np.arange(len(ids)), [len(t) for _, t in parsed])
    is_shared = np.array([d in shared for d in ids], bool)
    stop = np.zeros(len(codes), bool)
    if shared or s["stop_owners"]:
        # ponytail: all pairs within the index, fine to some 10^4 windows; a code count table or LSH beyond
        i, j, _ = near(codes, codes, s["tolerance"])
        k = (owner[i] != owner[j]) & ~is_shared[owner[i]]
        stop[i[k & is_shared[owner[j]]]] = True
        if s["stop_owners"]:
            k &= ~is_shared[owner[j]]
            pairs = np.unique(np.c_[i[k], owner[j[k]]], axis=0)
            stop |= np.bincount(pairs[:, 0], minlength=len(codes)) >= s["stop_owners"] if len(pairs) else False
    keep = ~stop
    return {"declarations": declarations | shared, "ids": ids, "shared": set(shared),
            "codes": codes[keep], "starts": starts[keep], "owner": owner[keep],
            "stop": {d: int((stop & (owner == o)).sum()) for o, d in enumerate(ids)}}  # fmt: skip


def verify(clip, idx: dict, settings: dict | None = None) -> list:
    """A clip (a path, a verifier result, or a list of them, e.g. speed_passes()) against an
    index: one match() result, plus "declaration" (and "label" for shared material), per
    recording it matches, most windows first. With several passes, the best per recording."""
    s = MATCH | (settings or {})
    passes = clip if isinstance(clip, list) else [clip if isinstance(clip, dict) else generate(clip, "verifier", settings)]
    best = {}
    for v in passes:
        check_windows(v, idx["declarations"].values())
        vq, vt = parse(v)
        qi, rj, dist = near(vq, idx["codes"], s["tolerance"])
        for o in np.unique(idx["owner"][rj]):
            k = idx["owner"][rj] == o
            d = idx["ids"][o]
            r = decide(v, idx["declarations"][d], vt[qi[k]], idx["starts"][rj[k]], rj[k], dist[k], s, idx["starts"][idx["owner"] == o])
            if r["relationship"] != "none" and r["windows"] > best.get(d, {"windows": 0})["windows"]:
                best[d] = {"declaration": d} | ({"label": "shared_branding"} if d in idx.get("shared", ()) else {}) | r
    return sorted(best.values(), key=lambda r: -r["windows"])


def line_of(c, t, g, dist, s, slopes, tol, window, cs):
    """One time line over a recording's hits: (fields, windows on the line), or (None, windows on
    the best line) when it falls short of min_windows or min_density. cs: the
    original's window starts, for the density."""
    line = time_vote(c, t, g, s["tolerance"] + 1 - dist, tol, slopes)
    if line is None:
        return None, 0
    a, b, n, inl = line
    c, t, g, d = c[inl], t[inl], g[inl], dist[inl]
    c0, c1, o0, o1 = c.min(), c.max() + window, t.min(), t.max() + window
    density = n / max(1, int(((cs >= o0 - 1e-6) & (cs <= t.max() + 1e-6)).sum()))
    if n < s["min_windows"] or density < s["min_density"]:
        return None, n
    # Refit on each original window's closest hits (their mean clip time), weighted so
    # that windows matched only off alignment (at the clip's ends) barely count.
    best = np.array([(c[k].mean(), t[k][0], d[k][0]) for j in np.unique(g) for k in [(g == j) & (d == d[g == j].min())]])
    if len(best) > 1:
        a, b = (float(x) for x in np.polyfit(best[:, 0], best[:, 1], 1, w=1 / (1 + best[:, 2] - best[:, 2].min())))
    return {"windows": n, "clip": [round(c0, 2), round(c1, 2)], "original": [round(o0, 2), round(o1, 2)],
            "offset": round(b, 2) + 0.0, "slope": round(a, 4), "density": round(density, 3)}, n  # fmt: skip


def decide(verifier: dict, creator: dict, c: np.ndarray, t: np.ndarray, g: np.ndarray, dist: np.ndarray, s: dict, cs: np.ndarray) -> dict:
    """The time vote and result over one recording's hits: clip times c, original times
    t, original windows g and distances; cs, the original's window starts."""
    window = window_of(creator["recipe_version"])
    slopes = SLOPES[np.abs(SLOPES - 1) <= s["max_speed"] + 1e-9]
    # A hit off by k sub-fingerprints differs by a few bits per step, so a tolerance wider
    # than the verifier's own misalignment (half its step) lets edge hits tilt the line.
    tol = verifier["hop"] / 2 + FP_HOP
    segs, left, n_best = [], np.ones(len(c), bool), 0
    while len(segs) < max(1, s["segments"]) and left.any():
        seg, n = line_of(c[left], t[left], g[left], dist[left], s, slopes, tol, window, cs)
        n_best = max(n_best, n)
        if seg is None:
            break
        segs.append(seg)
        # drop every hit in this line's clip range, so the next line is another part of the clip
        lo, hi = seg["clip"][0], seg["clip"][1] - window
        left &= ~((c >= lo - tol) & (c <= hi + tol))
    if not segs:
        return {"relationship": "none", "windows": n_best}
    first = segs[0]
    (c0, c1), (o0, o1) = first["clip"], first["original"]
    edge = creator["hop"] + CONTEXT  # windows start every hop, so up to this much of each end is never matched
    whole_clip = c0 <= edge and c1 >= verifier["duration"] - edge
    whole_original = o0 <= edge and o1 >= creator["duration"] - edge
    rel = {(True, True): "identical", (True, False): "contained_in", (False, True): "contains"}.get((whole_clip, whole_original), "overlapping")
    out = {"relationship": rel} | first
    out["overlap_fraction"] = {"verifier": round(min(1, (c1 - c0) / verifier["duration"]), 4),
                               "candidate": round(min(1, (o1 - o0) / creator["duration"]), 4)}  # fmt: skip
    if s["segments"] > 1:
        out["segments"] = segs
    return out

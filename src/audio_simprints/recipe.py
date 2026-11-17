"""The audio recipe: Chromaprint's raw stream cut into windows, each window one 128-bit
code (creator: a window every `hop` seconds; verifier: every `step`), codes compared
within a Hamming tolerance, then a time vote. RECIPE.md describes every step."""

import math
from fractions import Fraction

import numpy as np

from . import audio
from .audio import RATE

RECIPE = "audio-simprints/0.1"
FP_STEP = 1365  # samples between Chromaprint sub-fingerprints (frames of 4096 samples, a third apart)
FP_HOP = FP_STEP / RATE  # about 0.124 s
DEFAULTS = {
    "window": 10.0,  # seconds per code: four quarters of 2.5 s
    "hop": 5.0,  # creator: seconds between window starts
    "step": FP_HOP,  # verifier: seconds between window starts (one sub-fingerprint)
}
MATCH = {  # starting values; fitted on the tuning split in Phase 3
    "tolerance": 20,  # bits (of 128) two codes may differ by
    "min_windows": 3,  # distinct original windows that must lie on one time line (M)
}
SILENT = -60.0  # dBFS: a window quieter than this (RMS) gets no code (-50 skipped -6 dB copies of quiet classical recordings)
CONSTANT = 1.0  # bits: a window whose sub-fingerprints change by fewer bits per step than this, on average, gets no code
SLOPES = np.round(np.arange(0.9, 1.1001, 0.005), 3)  # time vote: slopes tried (1 +/- 10%; video-simprints steps 0.02)
CONTEXT = 3.0  # seconds at the end of a recording no window can start in (Chromaprint's frame and filters, about 2.7 s)


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


def from_fingerprint(raw: np.ndarray, energy: np.ndarray, duration: float, role: str, settings: dict | None = None) -> dict:
    """generate() from a raw fingerprint, the block energies and duration of its samples."""
    if role not in ("creator", "verifier"):
        raise ValueError(f"role must be 'creator' or 'verifier', not {role!r}")
    s = DEFAULTS | (settings or {})
    starts = (creator_starts if role == "creator" else verifier_starts)(len(raw), s)
    codes, why = codes_of(raw, energy, starts, s["window"]) if len(starts) else (np.zeros((0, 4), np.uint32), np.array([]))
    keep = why == ""
    out = {"recipe_version": version_string(s), "role": role, "duration": round(duration, 3),
           "hop": round(s["hop"] if role == "creator" else max(1, round(s["step"] / FP_HOP)) * FP_HOP, 4),
           "codes": [{"start": round(int(i) * FP_HOP, 3), "code": "".join(f"{int(v):08x}" for v in c)}
                     for i, c in zip(starts[keep], codes[keep])],
           "skipped": {"silent": int((why == "silent").sum()), "constant": int((why == "constant").sum())}}  # fmt: skip
    out["reason"] = None if out["codes"] else "shorter than one window" if not len(starts) else "every window skipped"
    return out


def generate(path, role: str = "creator", settings: dict | None = None) -> dict:
    """The codes of an audio file: creator (one window every `hop` seconds, to store with
    the declaration) or verifier (every `step`, for a clip being checked)."""
    return from_samples(audio.decode(path), role, settings)


def from_samples(pcm: np.ndarray, role: str, settings: dict | None = None, raw: np.ndarray | None = None) -> dict:
    """generate() from decoded samples (and their raw fingerprint, if already made)."""
    raw = audio.fingerprint(pcm) if raw is None else raw
    return from_fingerprint(raw, block_energy(pcm), len(pcm) / RATE, role, settings)


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


def time_vote(c: np.ndarray, t: np.ndarray, g: np.ndarray, q: np.ndarray, tol: float):
    """The line t = a c + b with the highest score within tol seconds of it: per group g,
    the best quality q of its points on the line, summed. Returns (a, b, groups on the
    line, inlier mask), or None. Tried: each slope in SLOPES through each point.

    Copied from video-simprints 0.1 (recipe.time_vote), with three changes: video counts
    distinct clip times, here g is the original window, so a finer verifier step does
    not inflate the count; lines are ranked by quality, not count, so a few hits off
    alignment (at a clip's ends) cannot tilt a line of exact ones; and the tolerance is
    passed in (see match)."""
    if not len(c):
        return None
    # ponytail: (len(SLOPES) * P) x P matrix, fine to a few thousand hits; bin offsets first if queries get larger
    a = np.repeat(SLOPES, len(c))
    b = np.tile(t, len(SLOPES)) - a * np.tile(c, len(SLOPES))
    res = np.abs(t[None, :] - (a[:, None] * c[None, :] + b[:, None]))
    inl = res <= tol
    order = np.argsort(g, kind="stable")
    starts = np.flatnonzero(np.r_[True, np.diff(g[order]) != 0])
    score = np.maximum.reduceat(np.where(inl, q[None, :], 0)[:, order], starts, axis=1).sum(1)
    err = np.where(inl, res, 0).sum(1)
    best = np.lexsort((err, -score))[0]
    return float(a[best]), float(b[best]), len(np.unique(g[inl[best]])), inl[best]


def match(verifier: dict, creator: dict, settings: dict | None = None) -> dict:
    """How a clip (verifier result) relates to a recording (creator result): the windows
    on one time line, the matched range in each, the offset and speed of the line, and
    the relationship."""
    s = MATCH | (settings or {})
    check_windows(verifier, [creator])
    vq, vt = parse(verifier)
    cq, ct = parse(creator)
    qi, rj, dist = near(vq, cq, s["tolerance"])
    return decide(verifier, creator, vt[qi], ct[rj], rj, dist, s)


def check_windows(verifier: dict, creators) -> float:
    w = window_of(verifier["recipe_version"])
    if any(window_of(c["recipe_version"]) != w for c in creators):
        raise ValueError("cannot match codes of different window lengths")
    return w


def index(declarations: dict) -> dict:
    """An in-memory index of {id: creator result}, for verify()."""
    ids = list(declarations)
    parsed = [parse(declarations[d]) for d in ids]
    return {"declarations": declarations, "ids": ids,
            "codes": np.concatenate([c for c, _ in parsed]) if ids else np.zeros((0, 2), np.uint64),
            "starts": np.concatenate([t for _, t in parsed]) if ids else np.zeros(0),
            "owner": np.repeat(np.arange(len(ids)), [len(t) for _, t in parsed])}  # fmt: skip


def verify(clip, idx: dict, settings: dict | None = None) -> list:
    """A clip (a path, or a verifier result) against an index: one match() result, plus
    "declaration", per recording it matches, most windows first."""
    s = MATCH | (settings or {})
    v = clip if isinstance(clip, dict) else generate(clip, "verifier", settings)
    check_windows(v, idx["declarations"].values())
    vq, vt = parse(v)
    qi, rj, dist = near(vq, idx["codes"], s["tolerance"])
    out = []
    for o in np.unique(idx["owner"][rj]):
        k = idx["owner"][rj] == o
        d = idx["ids"][o]
        r = decide(v, idx["declarations"][d], vt[qi[k]], idx["starts"][rj[k]], rj[k], dist[k], s)
        if r["relationship"] != "none":
            out.append({"declaration": d} | r)
    return sorted(out, key=lambda r: -r["windows"])


def decide(verifier: dict, creator: dict, c: np.ndarray, t: np.ndarray, g: np.ndarray, dist: np.ndarray, s: dict) -> dict:
    """The time vote and result over one recording's hits: clip times c, original times
    t, original windows g and distances."""
    window = window_of(creator["recipe_version"])
    # A hit off by k sub-fingerprints differs by a few bits per step, so a tolerance wider
    # than the verifier's own misalignment (half its step) lets edge hits tilt the line.
    line = time_vote(c, t, g, s["tolerance"] + 1 - dist, verifier["hop"] / 2 + FP_HOP)
    if line is None or line[2] < s["min_windows"]:
        return {"relationship": "none", "windows": line[2] if line else 0}
    a, b, n, inl = line
    c, t, g, d = c[inl], t[inl], g[inl], dist[inl]
    c0, c1, o0, o1 = c.min(), c.max() + window, t.min(), t.max() + window
    # Refit on each original window's closest hits (their mean clip time), weighted so
    # that windows matched only off alignment (at the clip's ends) barely count.
    best = np.array([(c[k].mean(), t[k][0], d[k][0]) for j in np.unique(g) for k in [(g == j) & (d == d[g == j].min())]])
    if len(best) > 1:
        a, b = (float(x) for x in np.polyfit(best[:, 0], best[:, 1], 1, w=1 / (1 + best[:, 2] - best[:, 2].min())))
    edge = creator["hop"] + CONTEXT  # windows start every hop, so up to this much of each end is never matched
    whole_clip = c0 <= edge and c1 >= verifier["duration"] - edge
    whole_original = o0 <= edge and o1 >= creator["duration"] - edge
    rel = {(True, True): "identical", (True, False): "contained_in", (False, True): "contains"}.get((whole_clip, whole_original), "overlapping")
    return {"relationship": rel, "windows": n, "clip": [round(c0, 2), round(c1, 2)], "original": [round(o0, 2), round(o1, 2)],
            "offset": round(b, 2) + 0.0, "slope": round(a, 4),
            "overlap_fraction": {"verifier": round(min(1, (c1 - c0) / verifier["duration"]), 4),
                                 "candidate": round(min(1, (o1 - o0) / creator["duration"]), 4)}}  # fmt: skip

"""Fit the settings on the tuning split: window, hop, verifier step and tolerance on a grid,
then M (min_windows) and min_density over each grid point's hits; then, with the chosen
settings, the slope range, speed passes, stop codes and segments. Writes
tests/corpus/tune-<split>/report.json and summary.md. Choose on the tuning split only.

Rule: the highest mean found rate over the manipulations with no false match at all (no
query of any kind matching a recording outside its own set); ties go to fewer bytes per
minute, then larger M, larger density, the coarser step."""

import hashlib
import json
import statistics
from multiprocessing import Pool
from pathlib import Path

from . import recipe
from .testmode import CACHE
from .evaluate import MANIPULATIONS, REEDIT, creators_of, false_counts, pct, prepare, run

SHAPES = [(10, 5), (10, 2.5), (8, 4), (6, 3), (5, 2.5)]  # (window, hop) seconds
STEPS = [round(recipe.FP_HOP, 4), 0.5]
TOLERANCES = [12, 16, 20, 24, 28, 32, 36, 40]
MS = [1, 2, 3, 4, 5, 6, 7, 8, 10]
DENSITIES = [0.0, 0.25, 0.5, 0.75, 0.9, 1.0]
SPEED_SETS = [(), (0.98, 1.02), (0.96, 0.98, 1.02, 1.04), (0.95, 0.96, 0.97, 0.98, 0.99, 1.01, 1.02, 1.03, 1.04, 1.05)]
MAX_SPEEDS = [0.02, 0.05, 0.1]
STOPS = [0, 2, 3]
PROBE = {"min_windows": 1, "min_density": 0.0}  # report every line, decide afterwards

_ctx = None


def _init(split, speeds=()):
    global _ctx
    _ctx = prepare(split, 0, speeds)


def _cached_grid(cfg: tuple) -> dict:
    """A grid point's result, cached under .cache/tune by its settings and the plan."""
    plan = hashlib.sha1(json.dumps([q["id"] for q in _ctx["queries"]] + _ctx["originals"]).encode()).hexdigest()[:8]
    path = CACHE / "tune" / f"{_ctx['split']}-{plan}-{cfg[0][0]:g}-{cfg[0][1]:g}-{cfg[1]:g}-{cfg[2]}.json"
    if path.exists():
        return json.loads(path.read_text())
    g = _grid(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(g))
    print(f"  grid {cfg[0]} step {cfg[1]:g} tolerance {cfg[2]}: {g['match_ms']['median_per_query']} ms per query", flush=True)
    return g


def _experiment(job: tuple) -> tuple:
    """One run with the chosen settings, cached under .cache/tune like the grid points."""
    kind, x, settings, shared, speeds = job
    plan = hashlib.sha1(json.dumps([q["id"] for q in _ctx["queries"]] + _ctx["originals"]).encode()).hexdigest()[:8]
    key = hashlib.sha1(json.dumps([kind, x, settings, shared, list(speeds)], sort_keys=True).encode()).hexdigest()[:10]
    path = CACHE / "tune" / f"{_ctx['split']}-{plan}-exp-{key}.json"
    if path.exists():
        return kind, x, json.loads(path.read_text())
    r = run(_ctx, settings, shared=shared, speeds=speeds)
    r |= {"false": false_counts(_ctx, r["queries"])}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(r))
    print(f"  {kind} {x}: done", flush=True)
    return kind, x, r


def compact(queries: list) -> list:
    """Per query, what the M and density sweep needs: the found line's (windows, density)
    and the (windows, density) of every false and look-alike line."""
    return [{"m": q["manipulation"], "role": q["role"], "found": [q["windows"], q["density"]] if q["found"] else None,
             "false": [[x[1], x[3]] for x in q.get("false", [])], "lookalike": [[x[1], x[3]] for x in q.get("lookalike", [])]}
            for q in queries]  # fmt: skip


def _grid(cfg: tuple) -> dict:
    (w, h), step, t = cfg
    s = {"window": w, "hop": h, "step": step, "tolerance": t} | PROBE
    r = run(_ctx, s)
    creators = creators_of(_ctx, s, _ctx["originals"])
    minutes = sum(float(_ctx["recs"][n]["duration"]) for n in _ctx["originals"]) / 60
    return {"window": w, "hop": h, "step": step, "tolerance": t, "queries": compact(r["queries"]), "match_ms": r["match_ms"],
            "bytes_per_minute": round(16 * sum(len(c["codes"]) for c in creators.values()) / minutes, 1)}  # fmt: skip


def sweep(g: dict, m: int, d: float) -> dict:
    """Found rate per manipulation and false/look-alike counts of one grid point at M=m, density d."""
    ok = lambda x: x[0] >= m and x[1] >= d - 1e-9  # noqa: E731
    found = {}
    for k in MANIPULATIONS:
        qs = [q for q in g["queries"] if q["role"] == "original" and q["m"] == k]
        found[k] = sum(bool(q["found"]) and ok(q["found"]) for q in qs) / len(qs) if qs else 0.0
    return {"window": g["window"], "hop": g["hop"], "step": g["step"], "tolerance": g["tolerance"], "min_windows": m, "min_density": d,
            "mean_found": round(statistics.mean(found.values()), 4), "found": {k: round(v, 3) for k, v in found.items()},
            "false": sum(ok(x) for q in g["queries"] for x in q["false"]), "lookalike": sum(ok(x) for q in g["queries"] for x in q["lookalike"]),
            "bytes_per_minute": g["bytes_per_minute"], "match_ms": g["match_ms"]["median_per_query"]}  # fmt: skip


def choose(rows: list) -> dict:
    clean = [r for r in rows if r["false"] == 0]
    return max(clean, key=lambda r: (r["mean_found"], -r["bytes_per_minute"], r["min_windows"], r["min_density"], r["step"]))


def row_of(name, r: dict, f: dict, keys) -> str:
    cells = [pct(sum(q["found"] for q in r["queries"] if q["role"] == "original" and q["manipulation"] == k),
                 sum(q["role"] == "original" and q["manipulation"] == k for q in r["queries"])) for k in keys]  # fmt: skip
    mean = statistics.mean(
        sum(q["found"] for q in r["queries"] if q["role"] == "original" and q["manipulation"] == k)
        / max(1, sum(q["role"] == "original" and q["manipulation"] == k for q in r["queries"]))
        for k in MANIPULATIONS
    )
    return f"| {name} | " + " | ".join(cells) + f" | {mean:.3f} | {f['false_matches']} | {pct(*f['lookalike']['pairs'])} | {r['match_ms']['median_per_query']} |"


def tune(split: str, out: Path, workers: int):
    ctx = prepare(split, workers, sorted({a for s in SPEED_SETS for a in s}))
    print(f"{split}: {len(ctx['rows'])} recordings, {len(ctx['originals'])} originals, {len(ctx['queries'])} queries; grid ...", flush=True)
    cfgs = [(sh, st, t) for sh in SHAPES for st in STEPS for t in TOLERANCES]
    with Pool(workers, _init, (split,)) as pool:
        grid = list(pool.imap(_cached_grid, cfgs))
    rows = [sweep(g, m, d) for g in grid for m in MS for d in DENSITIES]
    best = choose(rows)
    chosen = {k: best[k] for k in ("window", "hop", "step", "tolerance", "min_windows", "min_density")}
    print("chosen:", chosen, flush=True)

    # With the chosen settings: slope range first (the others use the chosen range), then
    # speed passes, stop codes and segments, each run in its own worker.
    mean = lambda r: statistics.mean(  # noqa: E731
        sum(q["found"] for q in r["queries"] if q["role"] == "original" and q["manipulation"] == k)
        / max(1, sum(q["role"] == "original" and q["manipulation"] == k for q in r["queries"]))
        for k in MANIPULATIONS
    )
    experiments = {"max_speed": {}, "speeds": {}, "stop_owners": {}}
    all_speeds = sorted({a for sp in SPEED_SETS for a in sp})
    with Pool(min(workers, len(MAX_SPEEDS)), _init, (split,)) as pool:
        for kind, x, r in pool.imap(_experiment, [("max_speed", str(x), chosen | {"max_speed": x}, False, ()) for x in MAX_SPEEDS]):
            experiments[kind][x] = r
    picks = {k: v for k, v in experiments["max_speed"].items() if v["false"]["false_matches"] == 0}
    chosen["max_speed"] = float(max(picks or experiments["max_speed"], key=lambda k: (mean(experiments["max_speed"][k]), -float(k))))
    jobs = [("speeds", str(list(sp)), chosen, False, sp) for sp in SPEED_SETS]
    jobs += [("stop_owners", str(k), chosen | {"stop_owners": k}, True, ()) for k in STOPS]
    jobs += [("segments", "3", chosen | {"segments": REEDIT[0]}, False, ())]
    with Pool(min(workers, len(jobs)), _init, (split, all_speeds)) as pool:
        done = list(pool.imap_unordered(_experiment, jobs))
    seg = next(r for kind, _, r in done if kind == "segments")
    for kind, x, r in done:
        if kind != "segments":
            experiments[kind][x] = r
    experiments["speeds"] = {str(list(sp)): experiments["speeds"][str(list(sp))] for sp in SPEED_SETS}
    experiments["stop_owners"] = {str(k): experiments["stop_owners"][str(k)] for k in STOPS}
    speedy = ["speed+2", "speed-2", "speed+5", "speed-5"]
    n_speed = lambda r: sum(q["found"] for q in r["queries"] if q["manipulation"] in speedy)  # noqa: E731
    ok = {k: v for k, v in experiments["speeds"].items() if v["false"]["false_matches"] == 0}
    speeds = max(ok, key=lambda k: (n_speed(ok[k]), -len(json.loads(k))))
    st = experiments["stop_owners"]
    stop = min(st, key=lambda k: (st[k]["false"]["false_matches"] + st[k]["false"]["series"]["queries"][0], -mean(st[k]), int(k)))
    seg_q = [q for q in seg["queries"] if q["manipulation"] == "reedit"]

    report = {"split": split, "rule": __doc__.split("Rule: ")[1].strip(), "grid": {"shapes": SHAPES, "steps": STEPS, "tolerances": TOLERANCES,
              "min_windows": MS, "densities": DENSITIES}, "rows": rows, "chosen": chosen, "speeds": json.loads(speeds), "stop_owners": int(stop),
              "experiments": {k: {x: {"false": v["false"], "match_ms": v["match_ms"], "stop_windows": v["stop_windows"],
                                      "found": {m: [sum(q["found"] for q in v["queries"] if q["role"] == "original" and q["manipulation"] == m),
                                                    sum(q["role"] == "original" and q["manipulation"] == m for q in v["queries"])] for m in MANIPULATIONS}}
                                  for x, v in e.items()} for k, e in experiments.items()},
              "segments": {"found": [sum(q.get("segments_found", 0) == k for q in seg_q) for k in range(REEDIT[0] + 1)],
                           "false_in_reedits": sum(q.get("segments_false", 0) for q in seg_q),
                           "false_elsewhere": sum(q.get("segments_false", 0) for q in seg["queries"] if q["manipulation"] != "reedit")}}  # fmt: skip
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    (out / "summary.md").write_text(summary(report, experiments), encoding="utf-8")
    print((out / "summary.md").read_text(encoding="utf-8"))


def summary(r: dict, experiments: dict) -> str:
    rows, c = r["rows"], r["chosen"]
    L = [f"# Tuning: {r['split']} split", "", f"Rule: {r['rule']}", "",
         f"Chosen: window {c['window']:g} s, hop {c['hop']:g} s, step {c['step']:g} s, tolerance {c['tolerance']}, "
         f"M {c['min_windows']}, density {c['min_density']:g}, slopes 1 ± {c['max_speed']:g}; speed passes {r['speeds'] or 'none'}; "
         f"stop_owners {r['stop_owners']}.", "",
         f"Grid: (window, hop) {r['grid']['shapes']}, step {r['grid']['steps']}, tolerance {r['grid']['tolerances']}, "
         f"M {r['grid']['min_windows']}, density {r['grid']['densities']}: {len(rows)} settings. M and density are applied to each "
         "grid point's lines afterwards (the grid runs at M 1, density 0).", ""]  # fmt: skip
    keys = ["excerpt5", "excerpt10", "excerpt30", "phone", "noise-snr10", "speed+2", "tempo-5", "reedit"]
    head = "| window | hop | step | tolerance | M | density | " + " | ".join(keys) + " | mean found | false | look-alike | bytes/min | match ms |"
    fmt = lambda x: (f"| {x['window']:g} | {x['hop']:g} | {x['step']:g} | {x['tolerance']} | {x['min_windows']} | {x['min_density']:g} | "  # noqa: E731
                     + " | ".join(f"{x['found'][k]:.2f}" for k in keys) + f" | {x['mean_found']:.3f} | {x['false']} | {x['lookalike']} | "
                     f"{x['bytes_per_minute']:.0f} | {x['match_ms']} |")  # fmt: skip
    L += ["## Best with no false match, per (window, hop)", "", head, "|" + " --- |" * (len(keys) + 11)]
    for w, h in r["grid"]["shapes"]:
        clean = [x for x in rows if x["window"] == w and x["hop"] == h and x["false"] == 0]
        if clean:
            L.append(fmt(choose(clean)))
    L += ["", "## Recall against false matches, chosen window, hop and step", "",
          "Each tolerance at each M (density as chosen); found rates are shares of the queries.", "", head, "|" + " --- |" * (len(keys) + 11)]
    L += [fmt(x) for x in rows if (x["window"], x["hop"], x["step"], x["min_density"]) == (c["window"], c["hop"], c["step"], c["min_density"])]
    L += ["", "## Density, chosen window, hop, step and tolerance", "", head, "|" + " --- |" * (len(keys) + 11)]
    L += [fmt(x) for x in rows if (x["window"], x["hop"], x["step"], x["tolerance"]) == (c["window"], c["hop"], c["step"], c["tolerance"])]
    sk = ["speed+2", "speed-2", "speed+5", "speed-5", "tempo+5", "tempo-5", "excerpt30"]
    eh = "| | " + " | ".join(sk) + " | mean found | false matches | look-alike pairs | match ms |"
    for name, title in (("max_speed", "Slope range (1 ± x)"), ("speeds", "Speed passes (clip also rescaled by)"), ("stop_owners", "Stop codes (series references as shared material; stop_owners)")):
        L += ["", f"## {title}", "", eh, "|" + " --- |" * (len(sk) + 5)]
        L += [row_of(k, v, v["false"], sk) for k, v in experiments[name].items()]
    st = r["experiments"]["stop_owners"]
    L += ["", "Stop windows left out: " + ", ".join(f"{k}: {v['stop_windows']}" for k, v in st.items())
          + ". Series excerpts matching their series: " + ", ".join(f"{k}: {pct(*v['false']['series']['queries'])}" for k, v in st.items())
          + ". Queries with a shared_branding label: " + ", ".join(f"{k}: {v['false']['branding']}" for k, v in st.items()) + ".", ""]  # fmt: skip
    sg = r["segments"]
    L += ["## Segments (re-edits, chosen settings, up to 3 lines)", "",
          f"Segments found per re-edit: " + ", ".join(f"{k}: {n}" for k, n in enumerate(sg["found"]))
          + f". Reported segments at no true offset: {sg['false_in_reedits']} in re-edits, {sg['false_elsewhere']} elsewhere.", ""]  # fmt: skip
    return "\n".join(L) + "\n"

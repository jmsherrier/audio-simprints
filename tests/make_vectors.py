"""Make the test-vector audio (seeded, synthetic), its raw Chromaprint fingerprint and
the expected codes.

    python tests/make_vectors.py

Run only when the recipe version changes; commit the WAV files, the .raw files and
expected.json. Needs fpcalc on PATH.
"""

import json
import wave
from pathlib import Path

import numpy as np

from audio_simprints import audio, recipe

HERE = Path(__file__).parent / "vectors"
RATE = audio.RATE


def music(seconds: float, seed: int) -> np.ndarray:
    """Random notes of harmonic tones with decaying envelopes, a few at a time, with a
    little noise: enough chroma movement for Chromaprint."""
    rng = np.random.default_rng(seed)
    n = int(seconds * RATE)
    x = rng.normal(0, 0.003, n)
    t = 0.0
    while t < seconds:
        f, dur = 110 * 2 ** (rng.integers(0, 36) / 12), rng.uniform(0.15, 0.8)
        i, m = int(t * RATE), int(dur * RATE)
        s = np.arange(min(m, n - i)) / RATE
        tone = sum(np.sin(2 * np.pi * f * k * s) / k for k in range(1, 5)) * np.exp(-3 * s / dur)
        x[i : i + len(s)] += rng.uniform(0.05, 0.15) * tone
        t += rng.uniform(0.05, 0.3)
    return x


def write(path: Path, x: np.ndarray):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(np.clip(np.round(x * 32767), -32768, 32767).astype("<i2").tobytes())


def read(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as w:
        return np.frombuffer(w.readframes(w.getnframes()), "<i2")


def main():
    HERE.mkdir(exist_ok=True)
    tone = 0.2 * np.sin(2 * np.pi * 440 * np.arange(12 * RATE) / RATE)
    signals = {  # music, then 12 s of silence, then 12 s of one steady tone, then music again
        "music": np.concatenate([music(30, 1), np.zeros(12 * RATE), tone, music(20, 2)]),
        "other": music(40, 3),  # unrelated
    }
    expected = {}
    for name, x in signals.items():
        write(HERE / f"{name}.wav", x)
        pcm = read(HERE / f"{name}.wav")
        raw = audio.fingerprint(pcm)
        (HERE / f"{name}.raw").write_text(",".join(map(str, raw.tolist())) + "\n")
        expected[name] = {role: recipe.from_samples(pcm, role, raw=raw) for role in ("creator", "verifier")}
    expected["fpcalc"] = audio.versions()["fpcalc"]
    (HERE / "expected.json").write_text(json.dumps(expected, indent=1) + "\n")


if __name__ == "__main__":
    main()

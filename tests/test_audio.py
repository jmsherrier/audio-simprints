import json
import shutil
from pathlib import Path

import numpy as np
import pytest

from audio_simprints import audio, generate, match, recipe
from make_vectors import read

HERE = Path(__file__).parent / "vectors"
EXPECTED = json.loads((HERE / "expected.json").read_text())
FPCALC = shutil.which("fpcalc") is not None
FFMPEG = shutil.which("ffmpeg") is not None


def raw_of(name: str) -> np.ndarray:
    return np.array((HERE / f"{name}.raw").read_text().split(","), np.int64).astype(np.uint32)


def bits_apart(a: dict, b: dict) -> list[int]:
    return [bin(int(x["code"], 16) ^ int(y["code"], 16)).count("1") for x, y in zip(a["codes"], b["codes"])]


def test_quarters():
    assert recipe.bounds(10) == [0, 21, 41, 61, 81]


@pytest.mark.parametrize("name", ["music", "other"])
@pytest.mark.parametrize("role", ["creator", "verifier"])
def test_codes_from_raw_fingerprint(name, role):
    """Pure numpy from the committed raw fingerprint: exact on every platform."""
    assert recipe.from_fingerprint(raw_of(name), read(HERE / f"{name}.wav"), role) == EXPECTED[name][role]


def test_silent_and_constant_windows_are_skipped():
    assert EXPECTED["music"]["creator"]["skipped"] == {"silent": 1, "constant": 2}
    assert EXPECTED["other"]["creator"]["skipped"] == {"silent": 0, "constant": 0}


@pytest.mark.skipif(not FPCALC, reason="fpcalc not on PATH")
@pytest.mark.parametrize("name", ["music", "other"])
def test_fpcalc_reproduces_vector(name):
    """fpcalc on this platform against the committed fingerprint (made on Windows, 1.6.2).
    Prints the bit error rate; codes may differ by a few bits, not more."""
    pcm = read(HERE / f"{name}.wav")
    raw, ref = audio.fingerprint(pcm), raw_of(name)
    assert len(raw) == len(ref)
    print(f"\n{name}: {audio.versions()['fpcalc']}: raw identical={bool((raw == ref).all())}, "
          f"bit error rate={np.bitwise_count(raw ^ ref).sum() / (32 * len(ref)):.6f}")  # fmt: skip
    assert max(bits_apart(recipe.from_fingerprint(raw, pcm, "creator"), EXPECTED[name]["creator"])) <= 8


@pytest.mark.skipif(not FPCALC, reason="fpcalc not on PATH")
def test_misaligned_excerpt_is_found():
    pcm = read(HERE / "music.wav")
    start = 3.77  # not on the creator's 5 s grid
    clip = pcm[round(start * audio.RATE) : round((start + 24) * audio.RATE)]
    v = recipe.from_fingerprint(audio.fingerprint(clip), clip, "verifier")
    r = match(v, EXPECTED["music"]["creator"])
    assert r["relationship"] == "contained_in"
    assert abs(r["offset"] - start) < 0.2 and abs(r["slope"] - 1) < 0.02
    assert match(v, EXPECTED["other"]["creator"])["relationship"] == "none"


@pytest.mark.skipif(not (FPCALC and FFMPEG), reason="ffmpeg or fpcalc not on PATH")
def test_generate_whole_file_is_identical():
    c = generate(HERE / "other.wav")
    assert max(bits_apart(c, EXPECTED["other"]["creator"])) <= 8
    r = match(generate(HERE / "other.wav", "verifier", {"step": 0.5}), c)
    assert r["relationship"] == "identical" and r["windows"] == len(c["codes"])


def test_window_lengths_must_agree():
    v = EXPECTED["music"]["verifier"] | {"recipe_version": recipe.RECIPE + ";window=5"}
    with pytest.raises(ValueError):
        match(v, EXPECTED["music"]["creator"])

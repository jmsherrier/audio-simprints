"""Decoding with the system ffmpeg and raw fingerprints with the system fpcalc
(Chromaprint), both run as subprocesses. Neither is bundled."""

import shutil
import subprocess

import numpy as np

RATE = 11025  # Hz: Chromaprint's own working rate, so fpcalc does no resampling
FPCALC = ["-raw", "-plain", "-length", "0", "-algorithm", "2", "-format", "s16le", "-rate", str(RATE), "-channels", "1", "-"]


class AudioError(ValueError):
    """ffmpeg or fpcalc is missing, or cannot read the source."""


def tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise AudioError(f"{name} not found on PATH; install it (see README)")
    return path


def decode(path) -> np.ndarray:
    """The first audio stream as mono 16-bit samples at RATE (ffmpeg's default resampler)."""
    cmd = [tool("ffmpeg"), "-nostdin", "-v", "error", "-i", str(path), "-map", "0:a:0",
           "-ac", "1", "-ar", str(RATE), "-f", "s16le", "-"]  # fmt: skip
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode:
        raise AudioError(f"ffmpeg failed on {path}: {p.stderr.decode(errors='replace')[-500:]}")
    return np.frombuffer(p.stdout, "<i2")


def fingerprint(pcm: np.ndarray) -> np.ndarray:
    """Chromaprint's raw stream of 32-bit sub-fingerprints (algorithm 2, fpcalc's default),
    one per 1365 samples. Audio shorter than about 3 s has none."""
    p = subprocess.run([tool("fpcalc"), *FPCALC], input=np.asarray(pcm, "<i2").tobytes(), capture_output=True)
    out = p.stdout.strip()
    if p.returncode and (b"Empty fingerprint" in p.stderr or b"Not enough audio data" in p.stderr):  # too short
        return np.zeros(0, np.uint32)
    if p.returncode:
        raise AudioError(f"fpcalc failed: {p.stderr.decode(errors='replace')[-500:]}")
    return np.array(out.split(b","), np.int64).astype(np.uint32)


def versions() -> dict:
    """The first line of `ffmpeg -version` and `fpcalc -version`, for reports."""
    run = lambda name: subprocess.run([tool(name), "-version"], capture_output=True, text=True).stdout.split("\n")[0]  # noqa: E731
    return {"ffmpeg": run("ffmpeg"), "fpcalc": run("fpcalc")}

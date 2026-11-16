# audio-simprints

[![CI](https://github.com/jmsherrier/audio-simprints/actions/workflows/ci.yml/badge.svg)](https://github.com/jmsherrier/audio-simprints/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue)](pyproject.toml)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)
[![FFmpeg: system, not bundled](https://img.shields.io/badge/ffmpeg-system%2C%20not%20bundled-lightgrey)](THIRD-PARTY-NOTICES.md#ffmpeg-external-not-bundled)
[![Chromaprint fpcalc: system, not bundled](https://img.shields.io/badge/fpcalc-system%2C%20not%20bundled-lightgrey)](THIRD-PARTY-NOTICES.md#chromaprint-fpcalc-external-not-bundled)
[![Status: proof of concept](https://img.shields.io/badge/status-proof%20of%20concept-orange)](#status)

Granular audio codes ("audio facets"). A recording gets one 128-bit code for every
10 seconds of sound, a new one every 5 seconds. A clip found online is coded at a
fine step and its codes are compared with the stored ones. Matching codes must line
up in time. The answer says which recording the clip comes from, which part of it,
and at what offset and speed: "contained in, 47.3–77.3 s, speed 1.00".

The third member of a family with
[image-simprints](https://github.com/jmsherrier/image-simprints) and
[video-simprints](https://github.com/jmsherrier/video-simprints), with the same
`generate` / `match` shape and the same result fields.

<a id="status"></a>**Status:** proof of concept, recipe `audio-simprints/0.1`.
Treat codes as test data. The thresholds are starting values, not yet fitted.

## Design credit

The design is Sebastian Posth's (Liccium): Chromaprint's raw stream of 32-bit
sub-fingerprints, windows of 10 s every 5 s on the creator side, each window cut
into four quarters whose bitwise majorities make one 128-bit code; a verifier that
slides its windows at a fine step so misaligned excerpts still line up; and the
time vote of video-simprints to confirm a match.

## Install

Python 3.12 on Linux, macOS or Windows. Two system programs are run as
subprocesses; neither is bundled:

- **ffmpeg** decodes audio (`apt install ffmpeg`, `brew install ffmpeg`).
- **fpcalc** from [Chromaprint](https://github.com/acoustid/chromaprint) makes the
  raw fingerprints. Use the official 1.6.2 build from its
  [releases](https://github.com/acoustid/chromaprint/releases/tag/v1.6.2) and put
  it on `PATH`; [CI](.github/workflows/ci.yml) shows how, with SHA-256 checks.
  Ubuntu's `libchromaprint-tools` (1.5.1) also works; Chocolatey's package is
  version 1.1, too old.

```sh
pip install git+https://github.com/jmsherrier/audio-simprints
pip install -e ".[test]" && pytest     # from a checkout
```

## Use

```python
from audio_simprints import generate, match

creator = generate("song.flac", "creator")          # store this with the declaration (JSON)
verifier = generate("found_online.mp3", "verifier")  # the clip being checked
result = match(verifier, creator)
print(result["relationship"], result["original"], result["offset"], result["slope"])
```

The command line does the same:

```sh
audio-simprints generate tests/vectors/music.wav > music.json
ffmpeg -ss 3.77 -t 24 -i tests/vectors/music.wav -b:a 128k clip.mp3
audio-simprints match clip.mp3 music.json
```

prints

```json
[
 {
  "declaration": "music.json",
  "relationship": "contained_in",
  "windows": 3,
  "clip": [0.99, 21.27],
  "original": [5.08, 25.1],
  "offset": 3.76,
  "slope": 0.9998,
  "overlap_fraction": {"verifier": 0.8449, "candidate": 0.2707}
 }
]
```

`generate(path, role, settings)` returns `{recipe_version, role, duration, hop,
codes: [{start, code}], skipped: {silent, constant}, reason}`. `code` is 32 hex
characters; `start` is in seconds; `hop` is the seconds between window starts;
`reason` explains an empty list (shorter than one window, or every window
skipped).

`match(verifier, creator, settings)` returns:

- `relationship`: `identical` (the clip is the whole recording), `contained_in`
  (the clip is an excerpt of the recording), `contains` (the whole recording is
  inside a longer clip), `overlapping` (they share a stretch, neither is whole) or
  `none`. These are about time; audio has no picture to crop.
- `windows`: distinct stored windows on the time line (M counts these).
- `clip` and `original`: the matched range in each, in seconds. They are slightly
  shorter than the real overlap, because stored windows start only every 5 s.
- `offset` and `slope`: the line `original = slope × clip + offset`. `offset` is
  where the clip starts in the recording; `slope` is the fitted speed.
- `overlap_fraction`: `{verifier, candidate}`, the share of each that the matched
  range covers.

Settings and defaults: creator `window=10`, `hop=5`; verifier `step=0.124` (one
sub-fingerprint; `0.5` costs a quarter of the windows); match `tolerance=20` bits
of 128 and `min_windows=3` (M). [RECIPE.md](RECIPE.md) specifies every step.

## Limits

- Excerpts shorter than about 15 s are not found. A clip cut at a random point
  almost never contains a whole 10 s stored window, and the baseline needs whole
  windows.
- Speed changes are not measured yet. Expect trouble when the pitch moves:
  Chromaprint's chroma features move with it.
- There are no results on a corpus yet; they will come from test mode.

## Patents: not reviewed

Patents were not reviewed for this proof of concept, either way. Audio
fingerprinting has a dense patent history, including landmark (peak-pair) hashing
and Philips-style sub-fingerprints from band-energy differences. Check before any
commercial use.

## Documents

- [RECIPE.md](RECIPE.md): the recipe, precisely enough to reimplement.
- [CHANGELOG.md](CHANGELOG.md).
- [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md): dependencies, FFmpeg and
  Chromaprint.

Apache-2.0. © 2026 Joseph Sherrier.

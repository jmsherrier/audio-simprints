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
[Results](#results-baseline-test-split) are on a partial corpus.

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

## Results (baseline, test split)

From [`tests/corpus/report-test/summary.md`](tests/corpus/report-test/summary.md),
printed by `audio-simprints test --split test`. The settings are the starting values
above; nothing has been fitted yet (that is Phase 3, on the tuning split, whose
report is [`report-tuning`](tests/corpus/report-tuning/summary.md)).

The corpus is incomplete. upload.wikimedia.org throttled this machine for hours, so
52 Commons recordings of the test split (its 12 orchestral and chamber originals
and 40 unrelated recordings) are not in this run; the report lists them. What ran:
30 originals (4 classical piano, 10 LibriVox chapters, 10 netlabel tracks, 6 NASA
and JPL episodes), 60 unrelated recordings, 20 look-alikes and 12 other episodes
of a series, 20.93 h. Each original gets every manipulation twice, at random places
(60 queries per row). Found means the right recording, with a fitted offset within
2 s of the truth.

| manipulation (30 s unless named) | found, step 0.124 s | found, step 0.5 s | median offset error (s) |
| --- | --- | --- | --- |
| excerpt 5 s | 0% (0/60) | 0% (0/60) | – |
| excerpt 10 s | 0% (0/60) | 0% (0/60) | – |
| excerpt 30 s | 100% (60/60) | 100% (60/60) | 0.04 |
| excerpt 60 s | 100% (60/60) | 100% (60/60) | 0.03 |
| MP3 128k | 98% (59/60) | 98% (59/60) | 0.07 |
| MP3 64k | 100% (60/60) | 100% (60/60) | 0.04 |
| AAC 128k | 98% (59/60) | 98% (59/60) | 0.04 |
| Opus 32k | 98% (59/60) | 98% (59/60) | 0.04 |
| resample via 22.05 kHz | 100% (60/60) | 100% (60/60) | 0.04 |
| mono | 98% (59/60) | 98% (59/60) | 0.04 |
| volume +6 dB | 100% (60/60) | 100% (60/60) | 0.04 |
| volume −6 dB | 100% (60/60) | 100% (60/60) | 0.05 |
| phone band (300–3400 Hz, 8 kHz) | 30% (18/60) | 22% (13/60) | 0.15 |
| noise, SNR 20 dB | 98% (59/60) | 98% (59/60) | 0.05 |
| noise, SNR 10 dB | 98% (59/60) | 97% (58/60) | 0.04 |
| speed +2% (pitch moves) | 10% (6/60) | 8.3% (5/60) | 0.11 |
| speed −2% | 10% (6/60) | 6.7% (4/60) | 0.24 |
| speed ±5% | 0% (0/60 each) | 0% (0/60 each) | – |
| tempo +5% (pitch kept) | 97% (58/60) | 97% (58/60) | 0.26 |
| tempo −5% | 93% (56/60) | 88% (53/60) | 0.30 |
| under speech or music, −6 or −12 dB | 0% (0/60 each) | 0% (0/60 each) | – |
| re-edit (3 × 20 s, reordered) | 92% (55/60) | 88% (53/60) | 0.08 |
| soundtrack of an H.264/AAC video | 100% (60/60) | 98% (59/60) | 0.04 |

Found clips gave the right relationship in 96–100% of cases (`contained_in`;
`overlapping` for re-edits). The matched range covers a median 83% of a 30 s
clip's stretch of the original: stored windows start only every 5 s.

**False matches** (step 0.124 s; at 0.5 s: 4 unrelated pairs, the same look-alike):

| | queries (two 30 s excerpts each) | pairs (whole recording × original) |
| --- | --- | --- |
| unrelated recordings | 0% (0/120) | 0.3% (5/1800) |
| look-alikes (other performances or readings) | 0% (0/40) | 5.0% (1/20) |
| other episodes of a series (shared intro) | 0% (0/24) | 0% (0/24) |

No query matched a wrong recording. The 5 unrelated pairs are netlabel tracks
against netlabel originals, with 3–5 windows scattered over minutes; the look-alike
is two performances of the Moonlight Sonata meeting on 4 windows.

**Cost.** 11.72 codes per minute of audio: 188 bytes per minute as raw 128-bit
codes, 764 as JSON. One process makes creator codes at 0.067 s per minute of
audio and verifier codes at 0.158 s per 30 s clip, decode and fpcalc included.
Matching against the 30 originals takes a median 9.4 ms per query at step
0.124 s and 2.2 ms at 0.5 s.

## Test mode

```sh
audio-simprints fetch-corpus           # downloads the files in tests/corpus/manifest.csv
audio-simprints test --split tuning    # or test; writes tests/corpus/report-<split>/
```

The corpus is not in the repository. The manifest lists each file with its URL,
licence, credit and SHA-256: CC0, public domain or CC BY only, from Wikimedia
Commons, LibriVox, archive.org's netlabels collection, and the NASA, JPL and White
House series of video-simprints' corpus. Tuning and test use different sources,
pieces and readers. [`scripts/build_manifest.py`](scripts/build_manifest.py) chose
the files. `fetch-corpus` also fills in rows the builder left blank when Commons
was throttling.

## Limits

- Excerpts of 10 s or less are not found. A clip cut at a random point almost
  never holds a whole 10 s stored window, and the baseline needs whole windows.
- Speed changes that move the pitch are not found (10% at ±2%, none at ±5%).
  Chromaprint's chroma features move with the pitch. Tempo changes that keep the
  pitch are found.
- A recording mixed under speech or music, even 6 dB down, is not found: the
  foreground decides the codes.
- Phone-band audio is found about a third of the time.
- False matches are few (0.3% of unrelated pairs) but they are not zero. They are
  scattered hits that the slope search lined up.
- The test corpus is missing its orchestral and chamber music (see above), and has
  only 30 originals.

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

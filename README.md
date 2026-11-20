# audio-simprints

[![CI](https://github.com/jmsherrier/audio-simprints/actions/workflows/ci.yml/badge.svg)](https://github.com/jmsherrier/audio-simprints/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue)](pyproject.toml)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)
[![FFmpeg: system, not bundled](https://img.shields.io/badge/ffmpeg-system%2C%20not%20bundled-lightgrey)](THIRD-PARTY-NOTICES.md#ffmpeg-external-not-bundled)
[![Chromaprint fpcalc: system, not bundled](https://img.shields.io/badge/fpcalc-system%2C%20not%20bundled-lightgrey)](THIRD-PARTY-NOTICES.md#chromaprint-fpcalc-external-not-bundled)
[![Status: proof of concept](https://img.shields.io/badge/status-proof%20of%20concept-orange)](#status)

Granular audio codes ("audio facets"). A recording gets one 128-bit code for every
5 seconds of sound, a new one every 2.5 seconds. A clip found online is coded at a
fine step and its codes are compared with the stored ones. Matching codes must line
up in time. The answer says which recording the clip comes from, which part of it,
and at what offset and speed: "contained in, 47.3–77.3 s, speed 1.00".

The third member of a family with
[image-simprints](https://github.com/jmsherrier/image-simprints) and
[video-simprints](https://github.com/jmsherrier/video-simprints), with the same
`generate` / `match` shape and the same result fields.

<a id="status"></a>**Status:** proof of concept, recipe `audio-simprints/0.2`.
Treat codes as test data. The settings are fitted on the tuning split; on the test
split they still give a few false matches among netlabel (electronic) tracks (see
[Results](#results-test-split)). The corpus is partial.

## Design credit

The design is Sebastian Posth's (Liccium): Chromaprint's raw stream of 32-bit
sub-fingerprints, windows of 10 s every 5 s on the creator side, each window cut
into four quarters whose bitwise majorities make one 128-bit code; a verifier that
slides its windows at a fine step so misaligned excerpts still line up; and the
time vote of video-simprints to confirm a match. Recipe 0.2 keeps the design with
shorter windows (5 s every 2.5 s), chosen on the tuning split.

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
  "windows": 7,
  "clip": [1.24, 21.22],
  "original": [5.08, 25.06],
  "offset": 3.71,
  "slope": 1.0073,
  "density": 1.0,
  "overlap_fraction": {"verifier": 0.8325, "candidate": 0.27}
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
  shorter than the real overlap, because stored windows start only every 2.5 s.
- `offset` and `slope`: the line `original = slope × clip + offset`. `offset` is
  where the clip starts in the recording; `slope` is the fitted speed.
- `density`: the matched windows as a share of the stored windows that start in
  the matched original range.
- `overlap_fraction`: `{verifier, candidate}`, the share of each that the matched
  range covers.
- `segments` (with the `segments` setting above 1): every line found in the
  recording, for re-edits.

`index(declarations, shared)` and `verify(clip, idx)` check a clip against many
recordings. `shared` holds known shared material (intros, jingles); a match to it
comes back with `"label": "shared_branding"`, and declarations' windows that match
it are left out as stop codes. `speed_passes(pcm, speeds)` makes extra verifier
results from the clip rescaled by each speed; `verify` takes the list.

Settings and defaults, fitted on the tuning split
([`tune-tuning/summary.md`](tests/corpus/tune-tuning/summary.md)): creator
`window=5`, `hop=2.5`; verifier `step=0.124` (one sub-fingerprint; `0.5` costs a
quarter of the windows and match time); match `tolerance=32` bits of 128,
`min_windows=6` (M), `min_density=0.75`, `max_speed=0.05` (slopes tried),
`segments=1`, `stop_owners=0`. [RECIPE.md](RECIPE.md) specifies every step.

## Results (test split)

From [`tests/corpus/report-test/summary.md`](tests/corpus/report-test/summary.md),
printed by `audio-simprints test --split test`. The settings were chosen by
`audio-simprints tune` on the tuning split
([`tune-tuning/summary.md`](tests/corpus/tune-tuning/summary.md)); the test split
was not used to choose anything. The Phase 2 baseline (recipe 0.1: 10 s windows,
tolerance 20, M 3) is in the same file at commit `6633188`.

The corpus is incomplete. upload.wikimedia.org has throttled this machine since 16 November,
so 52 Commons recordings of the test split (its 12 orchestral and chamber originals
and 40 unrelated recordings) are not in this run; the report lists them. What ran:
30 originals (4 classical piano, 10 LibriVox chapters, 10 netlabel tracks, 6 NASA
and JPL episodes), 60 unrelated recordings, 20 look-alikes and 12 episodes of a
series (3 of them the series' reference), 20.93 h. Each original gets every
manipulation twice, at random places (60 queries per row). Found means the right
recording, with a fitted offset within 2 s of the truth (for re-edits, of one part).

| manipulation (30 s unless named) | found | found, step 0.5 s | found, 4 speed passes | baseline 0.1 | median bits at the true place |
| --- | --- | --- | --- | --- | --- |
| excerpt 5 s | 0% (0/60) | 0% (0/60) | 0% (0/60) | 0% | – |
| excerpt 10 s | 0% (0/60) | 0% (0/60) | 0% (0/60) | 0% | 4 |
| excerpt 30 s | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% | 5 |
| excerpt 60 s | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% | 6 |
| MP3 128k | 98% (59/60) | 98% (59/60) | 98% (59/60) | 98% | 5 |
| MP3 64k | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% | 5 |
| AAC 128k | 98% (59/60) | 98% (59/60) | 98% (59/60) | 98% | 5 |
| Opus 32k | 98% (59/60) | 98% (59/60) | 98% (59/60) | 98% | 6 |
| resample via 22.05 kHz | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% | 5 |
| mono | 98% (59/60) | 98% (59/60) | 98% (59/60) | 98% | 4 |
| volume +6 dB | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% | 5 |
| volume −6 dB | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% | 5 |
| phone band (300–3400 Hz, 8 kHz) | 70% (42/60) | 65% (39/60) | 70% (42/60) | 30% | 23 |
| noise, SNR 20 dB | 98% (59/60) | 98% (59/60) | 98% (59/60) | 98% | 5 |
| noise, SNR 10 dB | 100% (60/60) | 100% (60/60) | 98% (59/60) | 98% | 5 |
| speed +2% (pitch moves) | 78% (47/60) | 72% (43/60) | 98% (59/60) | 10% | 26 |
| speed −2% | 77% (46/60) | 68% (41/60) | 100% (60/60) | 10% | 26 |
| speed +5% | 1.7% (1/60) | 0% (0/60) | 87% (52/60) | 0% | 42 |
| speed −5% | 1.7% (1/60) | 1.7% (1/60) | 80% (48/60) | 0% | 42 |
| tempo +5% (pitch kept) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 97% | 14 |
| tempo −5% | 100% (60/60) | 100% (60/60) | 100% (60/60) | 93% | 15 |
| under speech, −6 dB | 1.7% (1/60) | 1.7% (1/60) | 1.7% (1/60) | 0% | 46 |
| under speech, −12 dB | 0% (0/60) | 0% (0/60) | 0% (0/60) | 0% | 52 |
| under music, −6 dB | 1.7% (1/60) | 1.7% (1/60) | 1.7% (1/60) | 0% | 51 |
| under music, −12 dB | 0% (0/60) | 0% (0/60) | 0% (0/60) | 0% | 59 |
| re-edit (3 × 20 s, reordered) | 87% (52/60) | 83% (50/60) | 97% (58/60) | 92% | 5 |
| soundtrack of an H.264/AAC video | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% | 5 |

Bits: the median Hamming distance (of 128) between a stored window and the clip's
window at its true place; the tolerance is 32, and 64 is chance. Found clips gave
the right relationship (`contained_in`; `overlapping` for re-edits) in 93–100% of
cases, except the single clips found at speed −5% and under speech at −6 dB. With
the `segments` option, 39 of 60 re-edits had all three parts found, 8 two, 6 one
and 7 none.

**False matches** (two 30 s excerpts per recording; pairs are whole recordings
against originals):

| run | unrelated: excerpts | unrelated: pairs | originals: pairs with another original | look-alike: excerpts | look-alike: pairs | series: excerpts matching their series | hits on unrelated recordings, all queries |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fitted | 2.5% (3/120) | 0.2% (4/1800) | 0.2% (2/870) | 2.5% (1/40) | 5.0% (1/20) | 0% (0/18) | 11 |
| step 0.5 s | 3.3% (4/120) | 0.2% (4/1800) | 0.1% (1/870) | 0% (0/40) | 0% (0/20) | 0% (0/18) | 9 |
| 4 speed passes | 3.3% (4/120) | 0.3% (6/1800) | 0.2% (2/870) | 2.5% (1/40) | 5.0% (1/20) | 0% (0/18) | 19 |

Baseline 0.1: 0 of 120 unrelated excerpts and 5 of 1800 unrelated pairs. On the
tuning split, which now has 6 netlabel originals and 20 unrelated netlabel tracks,
the fitted settings gave no false match. On the test split every false match in the
fitted run is netlabel music against one of two netlabel originals (6–18 windows),
including those two against each other. The look-alike that matches is another
recording of Für Elise. Shared series intros never matched, with or without stop
codes, so stop codes changed nothing here.

**Cost.** 23.56 codes per minute of audio: 377 bytes per minute as raw 128-bit
codes, 1518 as JSON (0.1: 188 and 764). One process makes creator codes at 0.044 s
per minute of audio and verifier codes at 0.115 s per 30 s clip, decode and fpcalc
included. Matching against the 30 originals takes a median 30.9 ms per query at
step 0.124 s, 6.9 ms at 0.5 s and 122.1 ms with 4 speed passes (each pass is also
another fpcalc run).

## Stems (Phase 4, optional)

Can a single stem, such as a song's bass line mixed into another track, be traced
back to the song? Twenty songs from archive.org (CC BY 3.0, 105.3 min) come with
their full mix and real drums, bass and keys stems. A query is 30 s of one stem,
either alone or mixed over an unrelated netlabel track. The stem is set at the
track's loudness (0 dB) or 6 dB below it. Each case has 40 queries.
**A** matches the query against the full mixes. **B** runs demucs (htdemucs) on
both sides: each full mix and each query is split into drums, bass, other and
vocals, and every part is matched against every part. **C** is B without the
songs' drums stems in the index. It is a variant, not a fitted setting.
Numbers: [`tests/corpus/report-stems/summary.md`](tests/corpus/report-stems/summary.md).

| stem | level | A: found | B: found | C: found |
| --- | --- | --- | --- | --- |
| drums | alone | 12% (5/40) | not run | not run |
| drums | mix 0 dB | 2.5% (1/40) | 28% (11/40) | 0% (0/40) |
| drums | mix −6 dB | 0% (0/40) | 12% (5/40) | 0% (0/40) |
| bass | alone | 5.0% (2/40) | not run | not run |
| bass | mix 0 dB | 0% (0/40) | 40% (16/40) | 40% (16/40) |
| bass | mix −6 dB | 0% (0/40) | 25% (10/40) | 25% (10/40) |
| keys | alone | 0% (0/40) | not run | not run |
| keys | mix 0 dB | 0% (0/40) | 18% (7/40) | 18% (7/40) |
| keys | mix −6 dB | 0% (0/40) | 10% (4/40) | 10% (4/40) |

| false matches (a hit on another song) | A | B | C |
| --- | --- | --- | --- |
| stem queries | 5.3% (19/360) | 38% (90/240) | 6.7% (16/240) |
| unrelated tracks alone | 3.3% (2/60) | 33% (20/60) | 6.7% (4/60) |

In short:
- A stem does not match its own full mix. That holds even when the stem is played
  alone (12% for drums, 0–5% for the others).
- Separating both sides helps. B finds 28% of stems mixed at 0 dB and 16% at −6 dB.
- B's drum stems make it unusable as it stands. B's false hits by demucs stem:
  drums 487, bass 5, other 5, vocals 10. Unrelated tracks hit the drums as well, so electronic
  drums look alike across songs, not only within this producer's work.
- C drops the drums index. False matches fall to 6.7%, and bass and keys are found
  as often as in B. Drums are then never found.

**Cost.** Four stems store 76.67 codes per minute of song, against 23.39 for the
mix. Matching takes a median 135.8 ms per query for B's four parts,
against 10.4 ms for A. Demucs separated 22.98 s per minute of audio in one process
of 10 CPU threads. That figure covers the second part of the run, which was mostly
30 s clips.

## Test mode

```sh
audio-simprints fetch-corpus           # downloads the files in tests/corpus/manifest.csv
audio-simprints test --split tuning    # or test; writes tests/corpus/report-<split>/
audio-simprints tune                   # fits the settings on the tuning split
audio-simprints stems                  # Phase 4, needs pip install ".[stems]"; writes report-stems/
```

The corpus is not in the repository. The manifest lists each file with its URL,
licence, credit and SHA-256: CC0, public domain or CC BY only, from Wikimedia
Commons, LibriVox, archive.org's netlabels collection and stems, and the NASA, JPL
and White House series of video-simprints' corpus. Tuning and test use different sources,
pieces and readers. [`scripts/build_manifest.py`](scripts/build_manifest.py) chose
the files. `fetch-corpus` also fills in rows the builder left blank when Commons
was throttling.

## Limits

- A few false matches among netlabel (electronic) tracks (above), even with
  netlabel music in the tuning split. Repetitive electronic music shares long
  stretches of near-identical codes.
- Excerpts of 10 s or less are not found. A 10 s clip holds at most three whole 5 s
  windows and M is 6, although its codes are close (4 bits). 5 s clips hold none.
- Re-edits of 20 s parts are found 87% of the time; each part holds barely M
  windows.
- Speed changes of 5% that move the pitch are found only with speed passes, which
  cost about 5× the verifier time and add false matches.
- A recording mixed under speech or music, even 6 dB down, is not found: the
  foreground decides the codes (46–59 bits apart).
- Phone-band audio is found seven times in ten.
- Storage is twice that of 0.1, because windows are half as long.
- The test corpus is missing its orchestral and chamber music, and has only 30
  originals.
- Stems (Phase 4) are a research test, not a feature:
  - All 20 stem songs come from one producer, mostly electronic pop, so variety
    is low.
  - The demucs weights have no clear licence (see
    [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md)).
  - Separation is far slower than fingerprinting.
  - Vocal stems were not queried; only drums, bass and keys were.

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

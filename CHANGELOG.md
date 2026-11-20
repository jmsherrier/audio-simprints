# Changelog

## 0.1.0 (2026-11-19)

### Stems test (Phase 4, optional)

- `audio-simprints stems`, which needs `pip install ".[stems]"`, adds demucs 4.1.0
  and torch 2.5.1. Torch 2.15.0 would not load under Windows Smart App Control.
  The htdemucs weights download to the Hugging Face cache, never to the
  repository, and their licence is not clear (THIRD-PARTY-NOTICES.md).
- A stems split of 20 archive.org songs (CC BY 3.0) with full mix and real drums,
  bass and keys stems (`build_manifest.py --add-stems 20`).
- Report: `tests/corpus/report-stems/`. It has three runs:
  - A: a stem against full mixes.
  - B: demucs on both sides.
  - C: B without the drums index.
- Results:
  - A finds almost nothing.
  - B finds 28% of stems mixed at 0 dB, but 38% of its stem queries also hit
    another song, nearly all on drums.
  - C keeps B's bass and keys rates with 6.7% false matches.

### Recipe 0.2 (Phase 3)

- Settings fitted on the tuning split (`audio-simprints tune`): windows of 5 s
  every 2.5 s (were 10 s every 5 s), tolerance 32 bits (was 20), M 6 (was 3), a new
  density check (`min_density` 0.75: matched windows as a share of the stored
  windows in the matched range) and slopes 1 ± 0.05 (were ± 0.1). Codes of 0.1 and
  0.2 do not mix.
- The time vote bins offsets per slope instead of trying a line through every hit;
  its cost was the square of the hits.
- Options: `segments` (several lines per recording, for re-edits); `index(...,
  shared)` with a `shared_branding` label and stop windows, and `stop_owners`;
  `speed_passes()` and `verify()` over several verifier passes.
- Test mode runs the fitted settings, step 0.5 s, stop codes, 4 speed passes and
  segments, and reports the Hamming distance at each clip's true place. Whole
  originals are also queried against the other originals, and one episode per
  series is kept as the series' reference.
- The tuning split gains 6 netlabel originals and 20 unrelated netlabel tracks
  (`build_manifest.py --add-netlabels tuning`, artists not in the test split). A
  first fit without them (tolerance 28, M 3, density 0.25) gave 38 false matches
  on the test split's netlabel music.
- `tune` caches each grid point and follow-up run under `.cache/tune/`.
- Test split, against 0.1: phone band 30% → 70%, speed ±2% 10% → 77–78%, re-edits
  92% → 87%. Unrelated recordings: 3 of 120 excerpts and 4 of 1800 whole-recording
  pairs matched (0.1: 0 and 5), all among netlabel tracks.

### Recipe 0.1 (Phases 1 and 2)

- Recipe `audio-simprints/0.1`, baseline: Chromaprint raw stream (fpcalc 1.6.2,
  fed samples decoded by ffmpeg at 11,025 Hz mono). Creator windows are 10 s every
  5 s; each becomes a 128-bit code from the bitwise majorities of its four
  quarters. Silent and constant windows are skipped. The verifier slides windows
  at one sub-fingerprint (or `step`), and matches go through a time vote copied
  from video-simprints 0.1.
- `generate(path, role)` and `match(verifier, creator)`; command line
  `audio-simprints generate` and `match`.
- Synthetic test vectors with committed raw fingerprints (exact on every
  platform) and fpcalc checks within a few bits.
- CI on Linux, macOS and Windows, with ffmpeg and the official fpcalc build
  (SHA-256 checked).
- `index()` and `verify()` over many recordings, as in video-simprints.
- Silence threshold −60 dBFS (was −50, which skipped quiet classical recordings
  turned down 6 dB).
- Test mode: `audio-simprints fetch-corpus` and `audio-simprints test --split
  tuning|test`, with 27 manipulations tied to their true time ranges, false matches
  against unrelated recordings, look-alikes and series episodes, storage, and time.
  The corpus manifest (250 files: Wikimedia Commons, LibriVox, archive.org
  netlabels, NASA/JPL/White House series) and the baseline reports for both splits.
  ccMixter was planned but its file server refuses scripts; FMA needs an account.
- fpcalc's "Not enough audio data" now counts as too short (no codes), like
  "Empty fingerprint".

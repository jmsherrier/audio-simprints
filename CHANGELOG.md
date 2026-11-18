# Changelog

## Unreleased

### Recipe 0.2 (Phase 3)

- Settings fitted on the tuning split (`audio-simprints tune`): windows of 5 s
  every 2.5 s (were 10 s every 5 s), tolerance 28 bits (was 20), M 3, a new
  density check (`min_density` 0.25: matched windows as a share of the stored
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
- Test split: phone band 30% → 72%, speed ±2% 10% → 78–83%, re-edits 92% → 98%;
  but 38 false matches (0.7% of unrelated pairs, was 0.3%), on netlabel electronic
  music, which the tuning split lacks.

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

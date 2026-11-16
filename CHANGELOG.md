# Changelog

## Unreleased

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

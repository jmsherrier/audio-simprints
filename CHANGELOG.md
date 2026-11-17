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

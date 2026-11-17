# Recipe `audio-simprints/0.1`

Enough to reimplement. Code: [`src/audio_simprints/recipe.py`](src/audio_simprints/recipe.py);
exact test vectors: [`tests/vectors`](tests/vectors).

## 1. Samples and raw fingerprint

1. Decode the first audio stream with ffmpeg to mono, 11,025 Hz, signed 16-bit:
   `ffmpeg -i IN -map 0:a:0 -ac 1 -ar 11025 -f s16le -` (default resampler).
2. Pipe the samples to Chromaprint's fpcalc:
   `fpcalc -raw -plain -length 0 -algorithm 2 -format s16le -rate 11025 -channels 1 -`.
   The output is the raw stream: one unsigned 32-bit sub-fingerprint `f[i]` per
   1365 samples (FP_HOP = 1365 / 11025 ≈ 0.1238 s). Sub-fingerprint `i` is placed at
   `i × FP_HOP` seconds. Audio shorter than about 3 s has none (fpcalc exits with 2,
   "Empty fingerprint").

Decoding is done by our ffmpeg, not fpcalc's built-in decoder, so that one decoder
is in play. At 11,025 Hz fpcalc does no resampling of its own.

## 2. Windows and codes

A window of `window` seconds (default 10) holds `n = ceil(window × 11025 / 1365)`
sub-fingerprints starting at index `s`. Sub-fingerprint `s + r` belongs to quarter
`floor(r × FP_HOP / (window / 4))`. The quarter boundaries are computed exactly, in
rationals: `b[q] = ceil(q × window / 4 × 11025 / 1365)`. For 10 s that gives
`[0, 21, 41, 61, 81]`, so the quarters hold 21, 20, 20 and 20 values.

For each quarter, bit `k` of its 32-bit value is 1 when more than half of the
quarter's sub-fingerprints have bit `k` set. A tie gives 0. The code is the four
quarter values in order, each as 8 lowercase hex digits (most significant first):
32 hex characters, 128 bits.

**Window starts.**

- Creator: for k = 0, 1, …, the first sub-fingerprint at or after `k × hop`
  seconds (`ceil(k × hop × 11025 / 1365)`, exact), while the whole window fits.
  The default hop is 5 s.
- Verifier: every `max(1, round(step / FP_HOP))` sub-fingerprints from 0, while the
  window fits. The default step is one sub-fingerprint.

`start` is the first sub-fingerprint's time, rounded to 3 decimals.

**Skipped windows.** A window gets no code if:

- *silent*: the RMS of its samples (`s × 1365` to `s × 1365 + window × 11025`) is
  below −60 dBFS; or
- *constant*: its sub-fingerprints change, on average, by fewer than 1.0 bits from
  one to the next (a steady tone, a hum, digital silence after Chromaprint's
  filters).

## 3. Matching

1. **Hits.** Every pair of a verifier code and a creator code within `tolerance`
   bits (default 20 of 128). Its quality is `tolerance + 1 − distance`.
2. **Time vote.** Lines `t = a·c + b`, with `c` the verifier start and `t` the
   creator start. The slopes tried are 0.900 to 1.100 in steps of 0.005, each
   through every hit. A hit is on a line when it lies within
   `verifier hop / 2 + FP_HOP` seconds of it. A line's score is the sum, over the
   creator windows with hits on it, of each window's best quality. The highest
   score wins; ties go to the smaller total residual.
3. **Decision.** A match needs at least `min_windows` (M, default 3) distinct
   creator windows on the line.
4. **Fit.** For each creator window on the line, take its lowest-distance hits and
   their mean clip time. Fit `t = slope · c + offset` to these by least squares,
   weighted `1 / (1 + distance − lowest distance)`. Skip the fit if there is only
   one window.
5. **Ranges.**
   - `clip` = [first verifier start on the line, last + window].
   - `original` = [first creator start on the line, last + window].
6. **Relationship.** A side counts as whole when its range starts within
   `creator hop + 3 s` of 0 and ends within that much of its duration. The 3 s
   allow for Chromaprint's frame and filter context, about 2.7 s, in which no
   window can start.
   - Both sides whole: `identical`.
   - Only the clip whole: `contained_in`.
   - Only the original whole: `contains`.
   - Neither: `overlapping`.

### Where the time vote comes from

The time vote is copied from video-simprints 0.1 (`recipe.time_vote`), not imported
from it. There are four changes:

- It counts creator windows, not clip times, so a finer verifier step does not
  inflate the count.
- It ranks lines by quality, not count. Hits a few sub-fingerprints off alignment
  occur at a clip's ends, and ranking by count let them tilt the line.
- The tolerance follows the verifier step. A hit a few sub-fingerprints off alignment
  differs by only several bits per step, which is still inside a 20-bit tolerance.
- Slopes are tried every 0.005 instead of 0.02, so a long clip at a changed speed
  stays within the tighter tolerance.

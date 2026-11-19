# Recipe `audio-simprints/0.2`

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

A window of `window` seconds (default 5; 10 in 0.1) holds `n = ceil(window × 11025 / 1365)`
sub-fingerprints starting at index `s`. Sub-fingerprint `s + r` belongs to quarter
`floor(r × FP_HOP / (window / 4))`. The quarter boundaries are computed exactly, in
rationals: `b[q] = ceil(q × window / 4 × 11025 / 1365)`. For 5 s that gives
`[0, 11, 21, 31, 41]`; for 10 s, `[0, 21, 41, 61, 81]`.

For each quarter, bit `k` of its 32-bit value is 1 when more than half of the
quarter's sub-fingerprints have bit `k` set. A tie gives 0. The code is the four
quarter values in order, each as 8 lowercase hex digits (most significant first):
32 hex characters, 128 bits.

**Window starts.**

- Creator: for k = 0, 1, …, the first sub-fingerprint at or after `k × hop`
  seconds (`ceil(k × hop × 11025 / 1365)`, exact), while the whole window fits.
  The default hop is 2.5 s (5 s in 0.1).
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
   bits (default 32). Its quality is `tolerance + 1 − distance`. Stop windows (below) are not in
   the index and give no hits.
2. **Time vote.** Lines `t = a·c + b`, with `c` the verifier start and `t` the
   creator start, for slopes `a` from `1 − max_speed` to `1 + max_speed` in steps of
   0.005. For each slope, the offsets `b = t − a·c` go into bins of `tol =
   verifier hop / 2 + FP_HOP` seconds. A candidate line covers two neighbouring bins:
   the hits within `tol` of their shared edge. Its score is the sum, over the creator
   windows with hits on it, of each window's best quality. The highest score wins;
   ties go to the slope nearer 1. The line's offset is then the median offset of its
   hits, and its hits are those within `tol` of it.
3. **Decision.** A match needs at least `min_windows` (M) distinct creator windows
   (default 6) on the line, and a density of at least `min_density` (default 0.75): those windows as a share of
   the creator windows that start inside the matched original range.
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
7. **Segments** (option `segments` > 1). After a line is accepted, every hit inside
   its clip range is dropped and the vote runs again, up to `segments` lines per
   recording. The result keeps the first line's fields and lists all of them under
   `segments`. This is for re-edits: parts of one recording in another order.

### Shared material and stop codes

`index(declarations, shared)` takes known shared material (intros, jingles,
adverts) as creator results. Its codes are indexed too, and a match to it comes back
with `"label": "shared_branding"`, so it is not read as a claim on a declaration. A
declaration's window within `tolerance` of a shared code is a stop window and is left
out of the index. With `stop_owners` = k > 0, so is a window within `tolerance` of
the codes of k or more other declarations.

### Speed passes

A speed change that moves the pitch moves Chromaprint's chroma features, so the codes
no longer match. `speed_passes(pcm, speeds)` makes extra verifier results from the
clip's samples rescaled by each speed (linear interpolation at 11,025 Hz, `rescale`),
with start times in the clip's own time. `verify` takes the list and keeps the best
match per recording. Each pass costs another fpcalc run and another match.

### Where the time vote comes from

The time vote started as a copy of video-simprints 0.1 (`recipe.time_vote`), not an
import. There are five changes:

- It counts creator windows, not clip times, so a finer verifier step does not
  inflate the count.
- It ranks lines by quality, not count. Hits a few sub-fingerprints off alignment
  occur at a clip's ends, and ranking by count let them tilt the line.
- The tolerance follows the verifier step. A hit a few sub-fingerprints off alignment
  differs by only several bits per step, which is still inside a 20-bit tolerance.
- Slopes are tried every 0.005 instead of 0.02, so a long clip at a changed speed
  stays within the tighter tolerance.
- Offsets are binned per slope instead of trying a line through every hit. The old
  way cost the square of the hits, which ran to hours and gigabytes for whole
  recordings at a loose tolerance.

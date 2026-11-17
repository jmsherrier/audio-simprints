# Test mode: tuning split

Recipe `audio-simprints/0.1`, match settings {'tolerance': 20, 'min_windows': 3}. fpcalc version 1.6.2 (FFmpeg Lavc62.11.100 Lavf62.3.100 SwR6.1.100); ffmpeg version 8.1.2-full_build-www.gyan.dev.
22 originals, 16 unrelated recordings, 11 look-alikes (other performances or readings of an original's piece), 6 other episodes of a series; 7.78 h in all.
Left out, not downloaded (upload.wikimedia.org throttled this IP): 21 recordings, chopin-12-tudes-op-10-no-1-in-c-major-waterfall-edward-neema, chopin-12-tudes-op-10-no-11-in-e-flat-major-arpeggio-edward-, chopin-12-tudes-op-10-no-12-in-c-minor-revolutionary-edward-, chopin-12-tudes-op-10-no-2-in-a-minor-chromatique-edward-nee, chopin-12-tudes-op-10-no-5-in-g-flat-major-black-keys-edward, chopin-12-tudes-op-25-no-12-in-c-minor-ocean-edward-neeman, chopin-12-tudes-op-25-no-8-in-d-flat-major-sixths-edward-nee, chopin-andantino-in-g-minor-b-117-aya-higuchi, chopin-cantabile-in-b-flat-major-b-84-aya-higuchi, chopin-mazurka-in-a-flat-major-b-85-edward-neeman, chopin-mazurka-in-b-flat-major-b-73-edward-neeman, chopin-mazurka-in-c-major-b-82-edward-neeman, chopin-mazurka-no-15-in-c-major-op-24-no-2-edward-neeman, chopin-mazurka-no-20-in-d-flat-major-op-30-no-3-edward-neema, chopin-mazurka-no-27-in-e-minor-op-41-no-2-edward-neeman, chopin-mazurka-no-34-in-c-major-op-56-no-2-xuan-he, chopin-mazurka-no-39-in-b-major-op-63-no-1-edward-neeman, chopin-mazurka-no-44-in-c-major-op-67-no-3-edward-neeman, chopin-mazurka-no-46-in-c-major-op-68-no-1-edward-neeman, chopin-mazurka-no-9-in-c-major-op-7-no-5-luis-sarro, chopin-waltz-no-15-in-e-major-b-44-olga-gurevich.
Found: the right recording, fitted offset within 2 s of the truth (for re-edits, of one segment).

Storage: 11.76 codes per minute, 188 bytes per minute as 128-bit codes (768 as JSON); 0 silent and 0 constant windows skipped of 2073. Time, one process: creator 0.104 s per minute of audio, verifier 0.176 s per 30 s clip (decode and fpcalc included).

## Found per manipulation

| manipulation | step 0.124 s | step 0.5 s | right relationship | median offset error (s) | median coverage | wrong recording |
| --- | --- | --- | --- | --- | --- | --- |
| excerpt5 | 0% (0/44) | 0% (0/44) | – | – | – | 0 |
| excerpt10 | 0% (0/44) | 0% (0/44) | – | – | – | 0 |
| excerpt30 | 100% (44/44) | 100% (44/44) | 100% (44/44) | 0.04 | 0.83 | 0 |
| excerpt60 | 100% (44/44) | 100% (44/44) | 100% (44/44) | 0.04 | 0.87 | 0 |
| mp3-128 | 100% (44/44) | 100% (44/44) | 100% (44/44) | 0.08 | 0.83 | 0 |
| mp3-64 | 100% (44/44) | 100% (44/44) | 100% (44/44) | 0.05 | 0.83 | 0 |
| aac-128 | 100% (44/44) | 100% (44/44) | 100% (44/44) | 0.06 | 0.82 | 0 |
| opus-32 | 100% (44/44) | 100% (44/44) | 100% (44/44) | 0.04 | 0.83 | 0 |
| resample-22k | 100% (44/44) | 100% (44/44) | 100% (44/44) | 0.05 | 0.83 | 0 |
| mono | 100% (44/44) | 100% (44/44) | 100% (44/44) | 0.04 | 0.83 | 0 |
| volume+6 | 100% (44/44) | 100% (44/44) | 100% (44/44) | 0.03 | 0.83 | 0 |
| volume-6 | 100% (44/44) | 100% (44/44) | 100% (44/44) | 0.04 | 0.83 | 0 |
| phone | 41% (18/44) | 32% (14/44) | 89% (16/18) | 0.17 | 0.75 | 0 |
| noise-snr20 | 100% (44/44) | 100% (44/44) | 100% (44/44) | 0.07 | 0.83 | 0 |
| noise-snr10 | 100% (44/44) | 98% (43/44) | 100% (44/44) | 0.04 | 0.83 | 0 |
| speed+2 | 11% (5/44) | 2.3% (1/44) | 80% (4/5) | 0.13 | 0.82 | 0 |
| speed-2 | 2.3% (1/44) | 2.3% (1/44) | 100% (1/1) | 0.11 | 0.68 | 0 |
| speed+5 | 0% (0/44) | 0% (0/44) | – | – | – | 0 |
| speed-5 | 0% (0/44) | 0% (0/44) | – | – | – | 0 |
| tempo+5 | 100% (44/44) | 98% (43/44) | 100% (44/44) | 0.31 | 0.79 | 0 |
| tempo-5 | 98% (43/44) | 95% (42/44) | 100% (43/43) | 0.28 | 0.85 | 0 |
| under-speech-6 | 0% (0/44) | 0% (0/44) | – | – | – | 0 |
| under-speech-12 | 0% (0/44) | 0% (0/44) | – | – | – | 0 |
| under-music-6 | 0% (0/44) | 0% (0/44) | – | – | – | 0 |
| under-music-12 | 0% (0/44) | 0% (0/44) | – | – | – | 0 |
| reedit | 95% (42/44) | 73% (32/44) | 100% (42/42) | 0.10 | 0.97 | 0 |
| video | 100% (44/44) | 100% (44/44) | 100% (44/44) | 0.04 | 0.83 | 0 |

Right relationship: contained_in, or overlapping for re-edits (no one stored stretch holds the whole clip). Relationship, offset, coverage and wrong-recording columns: step 0.124 s. Coverage: share of the clip's stretch of the original inside the matched range (stored windows start every 5 s, so the ends are missed).

## False matches

| step | unrelated: queries with a match | unrelated: pairs (whole recording × original) | look-alike: queries | look-alike: pairs | series episodes: queries matching their series (shared intro) | series: pairs | false matches of series queries |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.124 s | 0% (0/32) | 0% (0/352) | 0% (0/22) | 0% (0/11) | 0% (0/12) | 0% (0/10) | 0 |
| 0.5 s | 0% (0/32) | 0% (0/352) | 0% (0/22) | 9.1% (1/11) | 0% (0/12) | 0% (0/10) | 0 |

Pairs: for unrelated recordings, each whole recording against every original; for look-alikes and series episodes, each whole recording against the original(s) of its own set. Queries: two 30 s excerpts per recording.

## Match time

| step | median per query (ms) | per minute of clip (ms) |
| --- | --- | --- |
| 0.124 s | 7.4 | 18.9 |
| 0.5 s | 1.7 | 4.1 |

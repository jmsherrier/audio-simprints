# Test mode: tuning split

Recipe `audio-simprints/0.2`. Settings {'window': 5.0, 'hop': 2.5, 'step': 0.1238}; match {'tolerance': 28, 'min_windows': 3, 'min_density': 0.25, 'max_speed': 0.05, 'segments': 1, 'stop_owners': 0}. fpcalc version 1.6.2 (FFmpeg Lavc62.11.100 Lavf62.3.100 SwR6.1.100); ffmpeg version 8.1.2-full_build-www.gyan.dev.
22 originals, 16 unrelated recordings, 11 look-alikes (other performances or readings of an original's piece), 6 episodes of a series (2 of them the series' reference, not queried); 7.78 h in all.
Left out, not downloaded (upload.wikimedia.org throttled this IP): 21 recordings, chopin-12-tudes-op-10-no-1-in-c-major-waterfall-edward-neema, chopin-12-tudes-op-10-no-11-in-e-flat-major-arpeggio-edward-, chopin-12-tudes-op-10-no-12-in-c-minor-revolutionary-edward-, chopin-12-tudes-op-10-no-2-in-a-minor-chromatique-edward-nee, chopin-12-tudes-op-10-no-5-in-g-flat-major-black-keys-edward, chopin-12-tudes-op-25-no-12-in-c-minor-ocean-edward-neeman, chopin-12-tudes-op-25-no-8-in-d-flat-major-sixths-edward-nee, chopin-andantino-in-g-minor-b-117-aya-higuchi, chopin-cantabile-in-b-flat-major-b-84-aya-higuchi, chopin-mazurka-in-a-flat-major-b-85-edward-neeman, chopin-mazurka-in-b-flat-major-b-73-edward-neeman, chopin-mazurka-in-c-major-b-82-edward-neeman, chopin-mazurka-no-15-in-c-major-op-24-no-2-edward-neeman, chopin-mazurka-no-20-in-d-flat-major-op-30-no-3-edward-neema, chopin-mazurka-no-27-in-e-minor-op-41-no-2-edward-neeman, chopin-mazurka-no-34-in-c-major-op-56-no-2-xuan-he, chopin-mazurka-no-39-in-b-major-op-63-no-1-edward-neeman, chopin-mazurka-no-44-in-c-major-op-67-no-3-edward-neeman, chopin-mazurka-no-46-in-c-major-op-68-no-1-edward-neeman, chopin-mazurka-no-9-in-c-major-op-7-no-5-luis-sarro, chopin-waltz-no-15-in-e-major-b-44-olga-gurevich.
Found: the right recording, fitted offset within 2 s of the truth (for re-edits, of one segment).

Storage: 23.68 codes per minute, 379 bytes per minute as 128-bit codes (1526 as JSON); 0 silent and 0 constant windows skipped of 4176. Time, one process: creator 0.122 s per minute of audio, verifier 0.263 s per 30 s clip (decode and fpcalc included).

Runs: **fitted** (the settings above), **step 0.5 s** (coarser verifier step), **stop codes** (each series' reference episode indexed as shared material, labelled shared_branding, and stored windows near it or near 0 other originals left out), **speed passes** (the clip also rescaled by [0.96, 0.98, 1.02, 1.04]), **segments** (up to 3 lines per recording).

## Found per manipulation

| manipulation | fitted | step 0.5 s | stop codes | speed passes | segments | right relationship | median offset error (s) | median coverage | median bits at the true place |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| excerpt5 | 0% (0/44) | 0% (0/44) | 0% (0/44) | 0% (0/44) | 0% (0/44) | – | – | – | – |
| excerpt10 | 0% (0/44) | 0% (0/44) | 0% (0/44) | 0% (0/44) | 0% (0/44) | – | – | – | 4 |
| excerpt30 | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 0.03 | 0.83 | 4 |
| excerpt60 | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 0.03 | 0.92 | 5 |
| mp3-128 | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 0.04 | 0.83 | 5 |
| mp3-64 | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 0.03 | 0.83 | 5 |
| aac-128 | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 0.03 | 0.83 | 4 |
| opus-32 | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 0.02 | 0.83 | 5 |
| resample-22k | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 0.03 | 0.83 | 4 |
| mono | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 0.03 | 0.83 | 5 |
| volume+6 | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 0.03 | 0.83 | 4 |
| volume-6 | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 0.02 | 0.83 | 4 |
| phone | 98% (43/44) | 98% (43/44) | 98% (43/44) | 98% (43/44) | 98% (43/44) | 79% (34/43) | 0.07 | 0.83 | 20 |
| noise-snr20 | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 0.02 | 0.83 | 4 |
| noise-snr10 | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 0.02 | 0.83 | 6 |
| speed+2 | 66% (29/44) | 57% (25/44) | 66% (29/44) | 100% (44/44) | 66% (29/44) | 69% (20/29) | 0.12 | 0.81 | 30 |
| speed-2 | 77% (34/44) | 59% (26/44) | 77% (34/44) | 100% (44/44) | 77% (34/44) | 56% (19/34) | 0.08 | 0.77 | 30 |
| speed+5 | 18% (8/44) | 11% (5/44) | 18% (8/44) | 77% (34/44) | 18% (8/44) | 38% (3/8) | 0.30 | 0.67 | 40 |
| speed-5 | 2.3% (1/44) | 2.3% (1/44) | 2.3% (1/44) | 75% (33/44) | 2.3% (1/44) | 100% (1/1) | 0.07 | 0.79 | 40 |
| tempo+5 | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 0.17 | 0.87 | 14 |
| tempo-5 | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 0.18 | 0.88 | 15 |
| under-speech-6 | 0% (0/44) | 0% (0/44) | 0% (0/44) | 0% (0/44) | 0% (0/44) | – | – | – | 44 |
| under-speech-12 | 0% (0/44) | 0% (0/44) | 0% (0/44) | 0% (0/44) | 0% (0/44) | – | – | – | 51 |
| under-music-6 | 0% (0/44) | 0% (0/44) | 0% (0/44) | 0% (0/44) | 0% (0/44) | – | – | – | 45 |
| under-music-12 | 0% (0/44) | 0% (0/44) | 0% (0/44) | 0% (0/44) | 0% (0/44) | – | – | – | 50 |
| reedit | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 0.02 | 0.99 | 5 |
| video | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 100% (44/44) | 0.03 | 0.83 | 5 |

Right relationship: contained_in, or overlapping for re-edits. Relationship, offset, coverage and bits: fitted run. Coverage: share of the clip's stretch of the original inside the matched range. Bits: Hamming distance of each stored window to the clip's window at its true place (of 128; the tolerance is 28).

## False matches

| run | unrelated: excerpts with a match | unrelated: pairs | originals: pairs with another original | look-alike: excerpts | look-alike: pairs | series: excerpts matching their series | series: pairs | false matches, all queries |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fitted | 0% (0/32) | 0% (0/352) | 0% (0/462) | 14% (3/22) | 18% (2/11) | 0% (0/8) | 0% (0/7) | 0 |
| step 0.5 s | 0% (0/32) | 0% (0/352) | 0% (0/462) | 9.1% (2/22) | 18% (2/11) | 0% (0/8) | 0% (0/7) | 0 |
| stop codes | 0% (0/32) | 0% (0/352) | 0% (0/462) | 14% (3/22) | 18% (2/11) | 0% (0/8) | 0% (0/7) | 0 |
| speed passes | 0% (0/32) | 0.6% (2/352) | 0% (0/462) | 14% (3/22) | 18% (2/11) | 0% (0/8) | 14% (1/7) | 5 |
| segments | 0% (0/32) | 0% (0/352) | 0% (0/462) | 14% (3/22) | 18% (2/11) | 0% (0/8) | 0% (0/7) | 0 |

Excerpts: two 30 s excerpts per recording. Pairs: each whole recording against every original (unrelated), every other original (originals), or the original(s) of its own set (look-alikes, series).

False and look-alike matches, fitted run (query: matched recording, windows, relationship, density):

- gymnopedie-no-1-isrc-usuan1100787__excerpt30__0: erik-satie-gymnopedies-la-1-ere-lent-et-douloureux, 3, overlapping, 1.0
- gymnopedie-no-1__excerpt30__0: erik-satie-gymnopedies-la-1-ere-lent-et-douloureux, 3, overlapping, 1.0
- gymnopedie-no-1__excerpt30__1: erik-satie-gymnopedies-la-1-ere-lent-et-douloureux, 3, overlapping, 1.0
- gymnopedie-no-1__whole: erik-satie-gymnopedies-la-1-ere-lent-et-douloureux, 3, overlapping, 1.0
- chopin-minute-waltz__whole: chopin-waltz-no-6-in-d-flat-major-op-64-no-1-minute-olga-gur, 3, overlapping, 0.3

## Shared material (stop codes run)

References: nasa-twan-2017-08-18, wh-west-wing-week-2015-04-10. Stop windows left out of the index: 6. Queries with a shared_branding label: 0 (fitted run: 0). Series excerpts matching their series' originals: 0% (0/8) with stop codes, 0% (0/8) without.

## Re-edits, segments run

Segments found per re-edit (3 × 20 s, reordered; 44 queries): 0: 0, 1: 0, 2: 2, 3: 42. Reported segments at no true offset: 0 in re-edits, 2 in other queries.

## Speed passes

Each rescaled pass is another fpcalc run on the clip: median 1.166 s per 30 s clip against 1.111 s for the clip as it is (in the test pool, not one process), so 4 passes cost about 5× the verifier time; match time is in the next table.

## Match time

| run | median per query (ms) | per minute of clip (ms) |
| --- | --- | --- |
| fitted | 32.0 | 70.8 |
| step 0.5 s | 9.1 | 19.2 |
| stop codes | 33.1 | 73.9 |
| speed passes | 157.8 | 349.3 |
| segments | 32.5 | 72.2 |

# Test mode: tuning split

Recipe `audio-simprints/0.2`. Settings {'window': 5.0, 'hop': 2.5, 'step': 0.1238}; match {'tolerance': 32, 'min_windows': 6, 'min_density': 0.75, 'max_speed': 0.05, 'segments': 1, 'stop_owners': 0}. fpcalc version 1.6.2 (FFmpeg Lavc62.11.100 Lavf62.3.100 SwR6.1.100); ffmpeg version 8.1.2-full_build-www.gyan.dev.
28 originals, 36 unrelated recordings, 11 look-alikes (other performances or readings of an original's piece), 6 episodes of a series (2 of them the series' reference, not queried); 9.83 h in all.
Left out, not downloaded (upload.wikimedia.org throttled this IP): 21 recordings, chopin-12-tudes-op-10-no-1-in-c-major-waterfall-edward-neema, chopin-12-tudes-op-10-no-11-in-e-flat-major-arpeggio-edward-, chopin-12-tudes-op-10-no-12-in-c-minor-revolutionary-edward-, chopin-12-tudes-op-10-no-2-in-a-minor-chromatique-edward-nee, chopin-12-tudes-op-10-no-5-in-g-flat-major-black-keys-edward, chopin-12-tudes-op-25-no-12-in-c-minor-ocean-edward-neeman, chopin-12-tudes-op-25-no-8-in-d-flat-major-sixths-edward-nee, chopin-andantino-in-g-minor-b-117-aya-higuchi, chopin-cantabile-in-b-flat-major-b-84-aya-higuchi, chopin-mazurka-in-a-flat-major-b-85-edward-neeman, chopin-mazurka-in-b-flat-major-b-73-edward-neeman, chopin-mazurka-in-c-major-b-82-edward-neeman, chopin-mazurka-no-15-in-c-major-op-24-no-2-edward-neeman, chopin-mazurka-no-20-in-d-flat-major-op-30-no-3-edward-neema, chopin-mazurka-no-27-in-e-minor-op-41-no-2-edward-neeman, chopin-mazurka-no-34-in-c-major-op-56-no-2-xuan-he, chopin-mazurka-no-39-in-b-major-op-63-no-1-edward-neeman, chopin-mazurka-no-44-in-c-major-op-67-no-3-edward-neeman, chopin-mazurka-no-46-in-c-major-op-68-no-1-edward-neeman, chopin-mazurka-no-9-in-c-major-op-7-no-5-luis-sarro, chopin-waltz-no-15-in-e-major-b-44-olga-gurevich.
Found: the right recording, fitted offset within 2 s of the truth (for re-edits, of one segment).

Storage: 23.6 codes per minute, 378 bytes per minute as 128-bit codes (1523 as JSON); 0 silent and 6 constant windows skipped of 4598. Time, one process: creator 0.088 s per minute of audio, verifier 0.15 s per 30 s clip (decode and fpcalc included).

Runs: **fitted** (the settings above), **step 0.5 s** (coarser verifier step), **stop codes** (each series' reference episode indexed as shared material, labelled shared_branding, and stored windows near it or near 0 other originals left out), **speed passes** (the clip also rescaled by [0.96, 0.98, 1.02, 1.04]), **segments** (up to 3 lines per recording).

## Found per manipulation

| manipulation | fitted | step 0.5 s | stop codes | speed passes | segments | right relationship | median offset error (s) | median coverage | median bits at the true place |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| excerpt5 | 0% (0/56) | 0% (0/56) | 0% (0/56) | 0% (0/56) | 0% (0/56) | – | – | – | – |
| excerpt10 | 0% (0/56) | 0% (0/56) | 0% (0/56) | 0% (0/56) | 0% (0/56) | – | – | – | 4 |
| excerpt30 | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 0.03 | 0.83 | 4 |
| excerpt60 | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 0.03 | 0.92 | 5 |
| mp3-128 | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 0.03 | 0.83 | 4 |
| mp3-64 | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 0.02 | 0.83 | 4 |
| aac-128 | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 0.03 | 0.83 | 5 |
| opus-32 | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 0.03 | 0.83 | 5 |
| resample-22k | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 0.03 | 0.83 | 4 |
| mono | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 0.02 | 0.83 | 4 |
| volume+6 | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 0.03 | 0.83 | 4 |
| volume-6 | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 0.03 | 0.83 | 4 |
| phone | 82% (46/56) | 79% (44/56) | 82% (46/56) | 82% (46/56) | 82% (46/56) | 100% (46/46) | 0.08 | 0.83 | 20 |
| noise-snr20 | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 0.02 | 0.83 | 4 |
| noise-snr10 | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 0.03 | 0.83 | 6 |
| speed+2 | 64% (36/56) | 52% (29/56) | 64% (36/56) | 100% (56/56) | 64% (36/56) | 94% (34/36) | 0.10 | 0.82 | 28 |
| speed-2 | 70% (39/56) | 48% (27/56) | 70% (39/56) | 100% (56/56) | 70% (39/56) | 72% (28/39) | 0.09 | 0.85 | 30 |
| speed+5 | 12% (7/56) | 8.9% (5/56) | 12% (7/56) | 80% (45/56) | 12% (7/56) | 57% (4/7) | 0.22 | 0.80 | 39 |
| speed-5 | 7.1% (4/56) | 3.6% (2/56) | 7.1% (4/56) | 80% (45/56) | 7.1% (4/56) | 75% (3/4) | 0.23 | 0.79 | 41 |
| tempo+5 | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 0.17 | 0.87 | 14 |
| tempo-5 | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 98% (55/56) | 0.18 | 0.88 | 14 |
| under-speech-6 | 0% (0/56) | 0% (0/56) | 0% (0/56) | 1.8% (1/56) | 0% (0/56) | – | – | – | 45 |
| under-speech-12 | 0% (0/56) | 0% (0/56) | 0% (0/56) | 0% (0/56) | 0% (0/56) | – | – | – | 51 |
| under-music-6 | 0% (0/56) | 0% (0/56) | 0% (0/56) | 0% (0/56) | 0% (0/56) | – | – | – | 52 |
| under-music-12 | 0% (0/56) | 0% (0/56) | 0% (0/56) | 0% (0/56) | 0% (0/56) | – | – | – | 58 |
| reedit | 89% (50/56) | 89% (50/56) | 93% (52/56) | 96% (54/56) | 89% (50/56) | 100% (50/50) | 0.03 | 1.00 | 5 |
| video | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 100% (56/56) | 0.03 | 0.83 | 5 |

Right relationship: contained_in, or overlapping for re-edits. Relationship, offset, coverage and bits: fitted run. Coverage: share of the clip's stretch of the original inside the matched range. Bits: Hamming distance of each stored window to the clip's window at its true place (of 128; the tolerance is 32).

## False matches

| run | unrelated: excerpts with a match | unrelated: pairs | originals: pairs with another original | look-alike: excerpts | look-alike: pairs | series: excerpts matching their series | series: pairs | false matches, all queries |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fitted | 0% (0/72) | 0% (0/1008) | 0% (0/756) | 4.5% (1/22) | 0% (0/11) | 0% (0/8) | 0% (0/7) | 0 |
| step 0.5 s | 0% (0/72) | 0% (0/1008) | 0% (0/756) | 0% (0/22) | 0% (0/11) | 0% (0/8) | 0% (0/7) | 0 |
| stop codes | 0% (0/72) | 0% (0/1008) | 0% (0/756) | 4.5% (1/22) | 0% (0/11) | 0% (0/8) | 0% (0/7) | 0 |
| speed passes | 0% (0/72) | 0% (0/1008) | 0% (0/756) | 4.5% (1/22) | 0% (0/11) | 0% (0/8) | 0% (0/7) | 2 |
| segments | 0% (0/72) | 0% (0/1008) | 0% (0/756) | 4.5% (1/22) | 0% (0/11) | 0% (0/8) | 0% (0/7) | 0 |

Excerpts: two 30 s excerpts per recording. Pairs: each whole recording against every original (unrelated), every other original (originals), or the original(s) of its own set (look-alikes, series).

False and look-alike matches, fitted run (query: matched recording, windows, relationship, density):

- gymnopedie-no-1-isrc-usuan1100787__excerpt30__0: erik-satie-gymnopedies-la-1-ere-lent-et-douloureux, 6, contained_in, 0.75

## Shared material (stop codes run)

References: nasa-twan-2017-08-18, wh-west-wing-week-2015-04-10. Stop windows left out of the index: 80. Queries with a shared_branding label: 0 (fitted run: 0). Series excerpts matching their series' originals: 0% (0/8) with stop codes, 0% (0/8) without.

## Re-edits, segments run

Segments found per re-edit (3 × 20 s, reordered; 56 queries): 0: 6, 1: 6, 2: 2, 3: 42. Reported segments at no true offset: 0 in re-edits, 0 in other queries.

## Speed passes

Each rescaled pass is another fpcalc run on the clip: median 1.2 s per 30 s clip against 1.129 s for the clip as it is (in the test pool, not one process), so 4 passes cost about 5× the verifier time; match time is in the next table.

## Match time

| run | median per query (ms) | per minute of clip (ms) |
| --- | --- | --- |
| fitted | 87.2 | 176.0 |
| step 0.5 s | 28.4 | 52.4 |
| stop codes | 27.2 | 54.5 |
| speed passes | 85.2 | 191.7 |
| segments | 18.1 | 40.3 |

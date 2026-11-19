# Test mode: test split

Recipe `audio-simprints/0.2`. Settings {'window': 5.0, 'hop': 2.5, 'step': 0.1238}; match {'tolerance': 32, 'min_windows': 6, 'min_density': 0.75, 'max_speed': 0.05, 'segments': 1, 'stop_owners': 0}. fpcalc version 1.6.2 (FFmpeg Lavc62.11.100 Lavf62.3.100 SwR6.1.100); ffmpeg version 8.1.2-full_build-www.gyan.dev.
30 originals, 60 unrelated recordings, 20 look-alikes (other performances or readings of an original's piece), 12 episodes of a series (3 of them the series' reference, not queried); 20.93 h in all.
Left out, not downloaded (upload.wikimedia.org throttled this IP): 52 recordings, antonin-dvorak-symphony-no-9-in-e-minor-from-the-new-world-o, bach-j-s-goldberg-variations-bwv988-10-variation-9-canon-on-, bach-j-s-goldberg-variations-bwv988-10-variation-9-canon-on--2, bach-j-s-goldberg-variations-bwv988-17-variation-16-overture, bach-j-s-goldberg-variations-bwv988-18-variation-17-shelley-, bach-j-s-goldberg-variations-bwv988-20-variation-19-shelley-, bach-j-s-goldberg-variations-bwv988-24-variation-23-shelley-, bach-j-s-goldberg-variations-bwv988-25-variation-24-canon-on, bach-j-s-goldberg-variations-bwv988-29-variation-28-shelley-, bach-j-s-goldberg-variations-bwv988-30-variation-29-shelley-, bach-siloti-prelude-in-b-minor-j-s-bach-arranged-siloti-arra, beethoven-piano-sonata-no-28-in-a-major-op-101-ii-lebhaft-ma, beethoven-sonata-no-8-in-c-minor-pathetique-op-13-iii-rondo-, beethoven-stringquartetno-6inbflatmajorop-18-ludwigvanbeetho, brahms-symphony-no-4-in-e-minor-op-98-iii-allegro-giocoso, camille-saint-saens-cello-concerto-no-1-in-a-minor-op-33-i-a, charpentier-te-deum-prelude, chopin-mazurka-op-50-no-3, chopin-nocturne-op-37-no-1, chopin-polonaise-op-40-no-1, chopin-waltz-op-64-no-2-in-c-sharp-minor, concerto-grosso-in-g-major-hwv-314, franz-schubert-fantasy-in-c-major-op-15-d-760-wanderer-iv-al, frederic-chopin-piano-sonata-no-2-in-b-flat-minor-op35-iii-m, fugue-in-a-minor-b-144, haydn-stringquartetindmajorop-64-josephhaydn-stringquartetin, imslp348255-pmlp01555-mozart-29-3, johann-sebastian-bach-aria-variata-bwv-989-part-1-theme-and-, johann-sebastian-bach-fugue-in-a-minor-bwv-543-robert-k-bler, ludwig-van-beethoven-piano-concerto-no-1-in-c-major-op-15-ii, ludwig-van-beethoven-symphony-no-5-in-c-minor-op-67-i-allegr, mazurka-op-59-no-1-in-a-minor, mazurka-op-59-no-3-in-f-sharp-minor, mozart-concerto-no-1-in-f-major-ii-andante-mozart-european-a, mozart-symphony-no-19-in-e-flat-major-iii-menuetto-mozart-eu, mozart-symphony-no-34-c-major-ii-andante-di-molto-mozart-eur, muzio-clementi-sonata-in-g-minor-no-3-op-50-didone-abbandona, nocturne-b-108-in-c-minor, nocturne-op-55-no-2-in-e-flat-major, peer-gynt-suite-no-1-op-46-ii-aase-s-death, polonaiseb-6ing-sharpminor, prelude-op-28-no-6, robert-schumann-scenes-from-childhood-op-15-vii-dreaming, strauss-kaiserwalzer, symphony-no-35-in-d-haffner-k-385-iv-finale-presto-mozart-eu, tchaikovsky-symphony-no-3-in-d-major-iv-scherzo-allegro-vivo, the-modena-chamber-orchestra-vivaldi-s-bassoon-concerto-in-a, the-modena-chamber-orchestra-vivaldi-s-concerto-for-2-mandol, the-modena-chamber-orchestra-vivaldi-s-concerto-in-c-major-r, the-musopen-symphony-orchestra-mendelssohn-s-symphony-no-3-i, waltz-op-64-no-1-in-d-flat-major, wolfgang-amadeus-mozart-flute-concerto-in-g-major-k-313-i-al.
Found: the right recording, fitted offset within 2 s of the truth (for re-edits, of one segment).

Storage: 23.56 codes per minute, 377 bytes per minute as 128-bit codes (1518 as JSON); 25 silent and 25 constant windows skipped of 6930. Time, one process: creator 0.044 s per minute of audio, verifier 0.115 s per 30 s clip (decode and fpcalc included).

Runs: **fitted** (the settings above), **step 0.5 s** (coarser verifier step), **stop codes** (each series' reference episode indexed as shared material, labelled shared_branding, and stored windows near it or near 0 other originals left out), **speed passes** (the clip also rescaled by [0.96, 0.98, 1.02, 1.04]), **segments** (up to 3 lines per recording).

## Found per manipulation

| manipulation | fitted | step 0.5 s | stop codes | speed passes | segments | right relationship | median offset error (s) | median coverage | median bits at the true place |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| excerpt5 | 0% (0/60) | 0% (0/60) | 0% (0/60) | 0% (0/60) | 0% (0/60) | – | – | – | – |
| excerpt10 | 0% (0/60) | 0% (0/60) | 0% (0/60) | 0% (0/60) | 0% (0/60) | – | – | – | 4 |
| excerpt30 | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 0.02 | 0.83 | 5 |
| excerpt60 | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 98% (59/60) | 0.02 | 0.92 | 6 |
| mp3-128 | 98% (59/60) | 98% (59/60) | 97% (58/60) | 98% (59/60) | 98% (59/60) | 100% (59/59) | 0.03 | 0.83 | 5 |
| mp3-64 | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 0.02 | 0.83 | 5 |
| aac-128 | 98% (59/60) | 98% (59/60) | 98% (59/60) | 98% (59/60) | 98% (59/60) | 100% (59/59) | 0.03 | 0.83 | 5 |
| opus-32 | 98% (59/60) | 98% (59/60) | 98% (59/60) | 98% (59/60) | 98% (59/60) | 100% (59/59) | 0.02 | 0.83 | 6 |
| resample-22k | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 98% (59/60) | 0.03 | 0.83 | 5 |
| mono | 98% (59/60) | 98% (59/60) | 98% (59/60) | 98% (59/60) | 98% (59/60) | 100% (59/59) | 0.03 | 0.83 | 4 |
| volume+6 | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 98% (59/60) | 0.02 | 0.83 | 5 |
| volume-6 | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 0.03 | 0.83 | 5 |
| phone | 70% (42/60) | 65% (39/60) | 70% (42/60) | 70% (42/60) | 70% (42/60) | 98% (41/42) | 0.07 | 0.83 | 23 |
| noise-snr20 | 98% (59/60) | 98% (59/60) | 98% (59/60) | 98% (59/60) | 98% (59/60) | 100% (59/59) | 0.02 | 0.83 | 5 |
| noise-snr10 | 100% (60/60) | 100% (60/60) | 100% (60/60) | 98% (59/60) | 100% (60/60) | 97% (58/60) | 0.03 | 0.83 | 5 |
| speed+2 | 78% (47/60) | 72% (43/60) | 78% (47/60) | 98% (59/60) | 78% (47/60) | 96% (45/47) | 0.08 | 0.82 | 26 |
| speed-2 | 77% (46/60) | 68% (41/60) | 77% (46/60) | 100% (60/60) | 77% (46/60) | 93% (43/46) | 0.09 | 0.85 | 26 |
| speed+5 | 1.7% (1/60) | 0% (0/60) | 1.7% (1/60) | 87% (52/60) | 1.7% (1/60) | 100% (1/1) | 0.40 | 0.79 | 42 |
| speed-5 | 1.7% (1/60) | 1.7% (1/60) | 1.7% (1/60) | 80% (48/60) | 1.7% (1/60) | 0% (0/1) | 0.02 | 0.79 | 42 |
| tempo+5 | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 0.17 | 0.87 | 14 |
| tempo-5 | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 0.19 | 0.88 | 15 |
| under-speech-6 | 1.7% (1/60) | 1.7% (1/60) | 0% (0/60) | 1.7% (1/60) | 1.7% (1/60) | 0% (0/1) | 0.10 | 0.75 | 46 |
| under-speech-12 | 0% (0/60) | 0% (0/60) | 0% (0/60) | 0% (0/60) | 0% (0/60) | – | – | – | 52 |
| under-music-6 | 1.7% (1/60) | 1.7% (1/60) | 1.7% (1/60) | 1.7% (1/60) | 1.7% (1/60) | 100% (1/1) | 0.08 | 0.75 | 51 |
| under-music-12 | 0% (0/60) | 0% (0/60) | 0% (0/60) | 0% (0/60) | 0% (0/60) | – | – | – | 59 |
| reedit | 87% (52/60) | 83% (50/60) | 87% (52/60) | 97% (58/60) | 87% (52/60) | 100% (52/52) | 0.01 | 0.99 | 5 |
| video | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 0.03 | 0.83 | 5 |

Right relationship: contained_in, or overlapping for re-edits. Relationship, offset, coverage and bits: fitted run. Coverage: share of the clip's stretch of the original inside the matched range. Bits: Hamming distance of each stored window to the clip's window at its true place (of 128; the tolerance is 32).

## False matches

| run | unrelated: excerpts with a match | unrelated: pairs | originals: pairs with another original | look-alike: excerpts | look-alike: pairs | series: excerpts matching their series | series: pairs | false matches, all queries |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fitted | 2.5% (3/120) | 0.2% (4/1800) | 0.2% (2/870) | 2.5% (1/40) | 5.0% (1/20) | 0% (0/18) | 0% (0/18) | 11 |
| step 0.5 s | 3.3% (4/120) | 0.2% (4/1800) | 0.1% (1/870) | 0% (0/40) | 0% (0/20) | 0% (0/18) | 0% (0/18) | 9 |
| stop codes | 2.5% (3/120) | 0.2% (4/1800) | 0.2% (2/870) | 2.5% (1/40) | 5.0% (1/20) | 0% (0/18) | 0% (0/18) | 11 |
| speed passes | 3.3% (4/120) | 0.3% (6/1800) | 0.2% (2/870) | 2.5% (1/40) | 5.0% (1/20) | 0% (0/18) | 0% (0/18) | 19 |
| segments | 2.5% (3/120) | 0.2% (4/1800) | 0.2% (2/870) | 2.5% (1/40) | 5.0% (1/20) | 0% (0/18) | 0% (0/18) | 11 |

Excerpts: two 30 s excerpts per recording. Pairs: each whole recording against every original (unrelated), every other original (originals), or the original(s) of its own set (look-alikes, series).

False and look-alike matches, fitted run (query: matched recording, windows, relationship, density):

- audionautix-com-ccby-furelise__excerpt30__1: furelise, 7, contained_in, 0.778
- audionautix-com-ccby-furelise__whole: furelise, 8, overlapping, 0.8
- macho-alfa-el-pais-de-los-monos__whole: x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s, 7, overlapping, 1.0
- x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s__phone__0: macho-alfa-el-pais-de-los-monos, 6, overlapping, 1.0
- x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s__speed-5__0: macho-alfa-el-pais-de-los-monos, 6, overlapping, 1.0
- x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s__whole: macho-alfa-el-pais-de-los-monos, 7, overlapping, 0.875
- beat-doctor-tou269b__excerpt30__0: x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s, 8, contained_in, 1.0
- beat-doctor-tou269b__excerpt30__1: x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s, 10, contained_in, 1.0
- beat-doctor-tou269b__whole: macho-alfa-el-pais-de-los-monos, 6, overlapping, 0.857
- fm-dig019-04-fm-agrim-string-of-death-and-a-bitter-poison__whole: macho-alfa-el-pais-de-los-monos, 18, overlapping, 0.9
- blunderwood-01-geo-sync-deluxe__excerpt30__0: x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s, 7, contained_in, 0.778
- second-thought-christmaspart1__whole: x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s, 9, overlapping, 0.9
- risey-tou255b__whole: x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s, 6, overlapping, 0.857

## Shared material (stop codes run)

References: jpl-whats-up-2025-08, nasa-moment-aleksey-ovchinin, nasa-s2g-2015-10-16. Stop windows left out of the index: 193. Queries with a shared_branding label: 0 (fitted run: 0). Series excerpts matching their series' originals: 0% (0/18) with stop codes, 0% (0/18) without.

## Re-edits, segments run

Segments found per re-edit (3 × 20 s, reordered; 60 queries): 0: 7, 1: 6, 2: 8, 3: 39. Reported segments at no true offset: 1 in re-edits, 5 in other queries.

## Speed passes

Each rescaled pass is another fpcalc run on the clip: median 1.265 s per 30 s clip against 1.122 s for the clip as it is (in the test pool, not one process), so 4 passes cost about 5× the verifier time; match time is in the next table.

## Match time

| run | median per query (ms) | per minute of clip (ms) |
| --- | --- | --- |
| fitted | 30.9 | 73.6 |
| step 0.5 s | 6.9 | 16.1 |
| stop codes | 24.1 | 54.9 |
| speed passes | 122.1 | 284.0 |
| segments | 24.2 | 55.6 |

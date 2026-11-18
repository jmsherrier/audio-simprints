# Test mode: test split

Recipe `audio-simprints/0.2`. Settings {'window': 5.0, 'hop': 2.5, 'step': 0.1238}; match {'tolerance': 28, 'min_windows': 3, 'min_density': 0.25, 'max_speed': 0.05, 'segments': 1, 'stop_owners': 0}. fpcalc version 1.6.2 (FFmpeg Lavc62.11.100 Lavf62.3.100 SwR6.1.100); ffmpeg version 8.1.2-full_build-www.gyan.dev.
30 originals, 60 unrelated recordings, 20 look-alikes (other performances or readings of an original's piece), 12 episodes of a series (3 of them the series' reference, not queried); 20.93 h in all.
Left out, not downloaded (upload.wikimedia.org throttled this IP): 52 recordings, antonin-dvorak-symphony-no-9-in-e-minor-from-the-new-world-o, bach-j-s-goldberg-variations-bwv988-10-variation-9-canon-on-, bach-j-s-goldberg-variations-bwv988-10-variation-9-canon-on--2, bach-j-s-goldberg-variations-bwv988-17-variation-16-overture, bach-j-s-goldberg-variations-bwv988-18-variation-17-shelley-, bach-j-s-goldberg-variations-bwv988-20-variation-19-shelley-, bach-j-s-goldberg-variations-bwv988-24-variation-23-shelley-, bach-j-s-goldberg-variations-bwv988-25-variation-24-canon-on, bach-j-s-goldberg-variations-bwv988-29-variation-28-shelley-, bach-j-s-goldberg-variations-bwv988-30-variation-29-shelley-, bach-siloti-prelude-in-b-minor-j-s-bach-arranged-siloti-arra, beethoven-piano-sonata-no-28-in-a-major-op-101-ii-lebhaft-ma, beethoven-sonata-no-8-in-c-minor-pathetique-op-13-iii-rondo-, beethoven-stringquartetno-6inbflatmajorop-18-ludwigvanbeetho, brahms-symphony-no-4-in-e-minor-op-98-iii-allegro-giocoso, camille-saint-saens-cello-concerto-no-1-in-a-minor-op-33-i-a, charpentier-te-deum-prelude, chopin-mazurka-op-50-no-3, chopin-nocturne-op-37-no-1, chopin-polonaise-op-40-no-1, chopin-waltz-op-64-no-2-in-c-sharp-minor, concerto-grosso-in-g-major-hwv-314, franz-schubert-fantasy-in-c-major-op-15-d-760-wanderer-iv-al, frederic-chopin-piano-sonata-no-2-in-b-flat-minor-op35-iii-m, fugue-in-a-minor-b-144, haydn-stringquartetindmajorop-64-josephhaydn-stringquartetin, imslp348255-pmlp01555-mozart-29-3, johann-sebastian-bach-aria-variata-bwv-989-part-1-theme-and-, johann-sebastian-bach-fugue-in-a-minor-bwv-543-robert-k-bler, ludwig-van-beethoven-piano-concerto-no-1-in-c-major-op-15-ii, ludwig-van-beethoven-symphony-no-5-in-c-minor-op-67-i-allegr, mazurka-op-59-no-1-in-a-minor, mazurka-op-59-no-3-in-f-sharp-minor, mozart-concerto-no-1-in-f-major-ii-andante-mozart-european-a, mozart-symphony-no-19-in-e-flat-major-iii-menuetto-mozart-eu, mozart-symphony-no-34-c-major-ii-andante-di-molto-mozart-eur, muzio-clementi-sonata-in-g-minor-no-3-op-50-didone-abbandona, nocturne-b-108-in-c-minor, nocturne-op-55-no-2-in-e-flat-major, peer-gynt-suite-no-1-op-46-ii-aase-s-death, polonaiseb-6ing-sharpminor, prelude-op-28-no-6, robert-schumann-scenes-from-childhood-op-15-vii-dreaming, strauss-kaiserwalzer, symphony-no-35-in-d-haffner-k-385-iv-finale-presto-mozart-eu, tchaikovsky-symphony-no-3-in-d-major-iv-scherzo-allegro-vivo, the-modena-chamber-orchestra-vivaldi-s-bassoon-concerto-in-a, the-modena-chamber-orchestra-vivaldi-s-concerto-for-2-mandol, the-modena-chamber-orchestra-vivaldi-s-concerto-in-c-major-r, the-musopen-symphony-orchestra-mendelssohn-s-symphony-no-3-i, waltz-op-64-no-1-in-d-flat-major, wolfgang-amadeus-mozart-flute-concerto-in-g-major-k-313-i-al.
Found: the right recording, fitted offset within 2 s of the truth (for re-edits, of one segment).

Storage: 23.56 codes per minute, 377 bytes per minute as 128-bit codes (1518 as JSON); 25 silent and 25 constant windows skipped of 6930. Time, one process: creator 0.06 s per minute of audio, verifier 0.238 s per 30 s clip (decode and fpcalc included).

Runs: **fitted** (the settings above), **step 0.5 s** (coarser verifier step), **stop codes** (each series' reference episode indexed as shared material, labelled shared_branding, and stored windows near it or near 0 other originals left out), **speed passes** (the clip also rescaled by [0.96, 0.98, 1.02, 1.04]), **segments** (up to 3 lines per recording).

## Found per manipulation

| manipulation | fitted | step 0.5 s | stop codes | speed passes | segments | right relationship | median offset error (s) | median coverage | median bits at the true place |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| excerpt5 | 0% (0/60) | 0% (0/60) | 0% (0/60) | 0% (0/60) | 0% (0/60) | – | – | – | – |
| excerpt10 | 0% (0/60) | 0% (0/60) | 0% (0/60) | 0% (0/60) | 0% (0/60) | – | – | – | 4 |
| excerpt30 | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 0.02 | 0.83 | 5 |
| excerpt60 | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 98% (59/60) | 0.02 | 0.92 | 6 |
| mp3-128 | 98% (59/60) | 98% (59/60) | 98% (59/60) | 98% (59/60) | 98% (59/60) | 100% (59/59) | 0.03 | 0.83 | 5 |
| mp3-64 | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 0.02 | 0.83 | 5 |
| aac-128 | 98% (59/60) | 98% (59/60) | 98% (59/60) | 98% (59/60) | 98% (59/60) | 100% (59/59) | 0.03 | 0.83 | 5 |
| opus-32 | 98% (59/60) | 98% (59/60) | 98% (59/60) | 98% (59/60) | 98% (59/60) | 100% (59/59) | 0.02 | 0.83 | 6 |
| resample-22k | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 98% (59/60) | 0.03 | 0.83 | 5 |
| mono | 98% (59/60) | 98% (59/60) | 98% (59/60) | 98% (59/60) | 98% (59/60) | 100% (59/59) | 0.03 | 0.83 | 4 |
| volume+6 | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 98% (59/60) | 0.02 | 0.83 | 5 |
| volume-6 | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 0.03 | 0.83 | 5 |
| phone | 72% (43/60) | 68% (41/60) | 72% (43/60) | 72% (43/60) | 72% (43/60) | 86% (37/43) | 0.07 | 0.83 | 23 |
| noise-snr20 | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 98% (59/60) | 0.02 | 0.83 | 5 |
| noise-snr10 | 100% (60/60) | 100% (60/60) | 100% (60/60) | 98% (59/60) | 100% (60/60) | 97% (58/60) | 0.03 | 0.83 | 5 |
| speed+2 | 83% (50/60) | 77% (46/60) | 83% (50/60) | 100% (60/60) | 83% (50/60) | 84% (42/50) | 0.09 | 0.82 | 26 |
| speed-2 | 78% (47/60) | 77% (46/60) | 78% (47/60) | 100% (60/60) | 78% (47/60) | 74% (35/47) | 0.09 | 0.85 | 26 |
| speed+5 | 0% (0/60) | 0% (0/60) | 0% (0/60) | 87% (52/60) | 0% (0/60) | – | – | – | 42 |
| speed-5 | 5.0% (3/60) | 5.0% (3/60) | 5.0% (3/60) | 82% (49/60) | 5.0% (3/60) | 0% (0/3) | 0.32 | 0.70 | 42 |
| tempo+5 | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 0.17 | 0.87 | 14 |
| tempo-5 | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 0.19 | 0.88 | 15 |
| under-speech-6 | 1.7% (1/60) | 1.7% (1/60) | 1.7% (1/60) | 1.7% (1/60) | 1.7% (1/60) | 0% (0/1) | 0.10 | 0.67 | 46 |
| under-speech-12 | 0% (0/60) | 0% (0/60) | 0% (0/60) | 0% (0/60) | 0% (0/60) | – | – | – | 52 |
| under-music-6 | 1.7% (1/60) | 1.7% (1/60) | 1.7% (1/60) | 1.7% (1/60) | 1.7% (1/60) | 0% (0/1) | 0.10 | 0.58 | 51 |
| under-music-12 | 0% (0/60) | 0% (0/60) | 0% (0/60) | 0% (0/60) | 0% (0/60) | – | – | – | 59 |
| reedit | 98% (59/60) | 98% (59/60) | 98% (59/60) | 98% (59/60) | 98% (59/60) | 98% (58/59) | 0.01 | 0.98 | 5 |
| video | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 100% (60/60) | 0.03 | 0.83 | 5 |

Right relationship: contained_in, or overlapping for re-edits. Relationship, offset, coverage and bits: fitted run. Coverage: share of the clip's stretch of the original inside the matched range. Bits: Hamming distance of each stored window to the clip's window at its true place (of 128; the tolerance is 28).

## False matches

| run | unrelated: excerpts with a match | unrelated: pairs | originals: pairs with another original | look-alike: excerpts | look-alike: pairs | series: excerpts matching their series | series: pairs | false matches, all queries |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fitted | 4.2% (5/120) | 0.7% (13/1800) | 0.2% (2/870) | 5.0% (2/40) | 20% (4/20) | 0% (0/18) | 0% (0/18) | 38 |
| step 0.5 s | 2.5% (3/120) | 0.4% (7/1800) | 0.2% (2/870) | 7.5% (3/40) | 10% (2/20) | 0% (0/18) | 0% (0/18) | 22 |
| stop codes | 4.2% (5/120) | 0.7% (13/1800) | 0.2% (2/870) | 5.0% (2/40) | 20% (4/20) | 0% (0/18) | 0% (0/18) | 38 |
| speed passes | 8.3% (10/120) | 1.0% (18/1800) | 0.3% (3/870) | 5.0% (2/40) | 30% (6/20) | 0% (0/18) | 0% (0/18) | 71 |
| segments | 4.2% (5/120) | 0.7% (13/1800) | 0.2% (2/870) | 5.0% (2/40) | 20% (4/20) | 0% (0/18) | 0% (0/18) | 38 |

Excerpts: two 30 s excerpts per recording. Pairs: each whole recording against every original (unrelated), every other original (originals), or the original(s) of its own set (look-alikes, series).

False and look-alike matches, fitted run (query: matched recording, windows, relationship, density):

- moonlight-sonata__excerpt30__0: ludwig-van-beethoven-sonata-no-14-in-c-sharp-minor-moonlight, 6, contained_in, 0.6
- moonlight-sonata__whole: ludwig-van-beethoven-sonata-no-14-in-c-sharp-minor-moonlight, 31, overlapping, 0.304
- the-entertainer-by-scott-joplin-1902-ragtime-piano__whole: the-entertainer-scott-joplin, 11, overlapping, 0.297
- maple-leaf-rag-played-by-scott-joplin-1916-v2__whole: odyssey-butler-librivox, 3, overlapping, 1.0
- audionautix-com-ccby-furelise__excerpt30__1: furelise, 4, overlapping, 0.5
- christmas-carol-1111-librivox__whole: nasa-s2g-2017-01-06, 3, overlapping, 1.0
- moby-dick-librivox__under-music-12__0: macho-alfa-el-pais-de-los-monos, 3, overlapping, 0.429
- pollyanna-1-pc-librivox__mono__0: odyssey-butler-librivox, 3, overlapping, 1.0
- pollyanna-1-pc-librivox__volume+6__0: odyssey-butler-librivox, 3, overlapping, 1.0
- pollyanna-1-pc-librivox__under-music-6__0: x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s, 3, overlapping, 0.429
- mike-carrier-approachingyou__under-music-12__0: x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s, 4, overlapping, 1.0
- macho-alfa-el-pais-de-los-monos__whole: x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s, 5, overlapping, 1.0
- barfly-s-dreams-002-theoutrooftheintro__opus-32__1: x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s, 3, overlapping, 1.0
- barfly-s-dreams-002-theoutrooftheintro__noise-snr10__0: x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s, 3, overlapping, 1.0
- x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s__mp3-64__0: macho-alfa-el-pais-de-los-monos, 4, overlapping, 1.0
- x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s__mp3-64__1: macho-alfa-el-pais-de-los-monos, 5, overlapping, 1.0
- x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s__opus-32__1: macho-alfa-el-pais-de-los-monos, 4, overlapping, 1.0
- x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s__volume+6__0: macho-alfa-el-pais-de-los-monos, 4, overlapping, 1.0
- x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s__phone__0: macho-alfa-el-pais-de-los-monos, 3, overlapping, 1.0; barfly-s-dreams-002-theoutrooftheintro, 3, overlapping, 1.0
- x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s__noise-snr10__1: macho-alfa-el-pais-de-los-monos, 4, overlapping, 1.0
- x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s__speed+2__1: macho-alfa-el-pais-de-los-monos, 3, overlapping, 0.75
- x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s__reedit__1: macho-alfa-el-pais-de-los-monos, 4, overlapping, 1.0
- x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s__whole: macho-alfa-el-pais-de-los-monos, 4, overlapping, 0.571
- beat-doctor-tou269b__excerpt30__0: x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s, 7, overlapping, 1.0
- beat-doctor-tou269b__excerpt30__1: x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s, 8, contained_in, 1.0
- beat-doctor-tou269b__whole: macho-alfa-el-pais-de-los-monos, 3, overlapping, 1.0
- joanne-gabriel-01-the-planet__whole: barfly-s-dreams-002-theoutrooftheintro, 7, overlapping, 0.259
- fm-dig019-04-fm-agrim-string-of-death-and-a-bitter-poison__whole: macho-alfa-el-pais-de-los-monos, 14, overlapping, 0.778; x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s, 6, overlapping, 1.0
- blunderwood-01-geo-sync-deluxe__whole: x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s, 4, overlapping, 0.571
- winterstrand-01-winterstrand-process-reedit__excerpt30__0: barfly-s-dreams-002-theoutrooftheintro, 4, overlapping, 1.0
- winterstrand-01-winterstrand-process-reedit__whole: barfly-s-dreams-002-theoutrooftheintro, 4, overlapping, 1.0
- shoki-recordings-02-shoki009-bardo-boiler__whole: diana-fire-02-diana-fire-chotto-matte, 3, overlapping, 0.5
- litmus0001-anu014-litmus0001-001-pripyat__whole: barfly-s-dreams-002-theoutrooftheintro, 7, overlapping, 0.304
- second-thought-christmaspart1__excerpt30__1: x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s, 5, overlapping, 1.0
- second-thought-christmaspart1__whole: x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s, 9, overlapping, 0.9; macho-alfa-el-pais-de-los-monos, 3, overlapping, 0.75; barfly-s-dreams-002-theoutrooftheintro, 3, overlapping, 1.0
- risey-tou255b__excerpt30__1: x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s, 3, overlapping, 1.0
- risey-tou255b__whole: barfly-s-dreams-002-theoutrooftheintro, 3, overlapping, 0.75; x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s, 3, overlapping, 1.0

## Shared material (stop codes run)

References: jpl-whats-up-2025-08, nasa-moment-aleksey-ovchinin, nasa-s2g-2015-10-16. Stop windows left out of the index: 8. Queries with a shared_branding label: 0 (fitted run: 0). Series excerpts matching their series' originals: 0% (0/18) with stop codes, 0% (0/18) without.

## Re-edits, segments run

Segments found per re-edit (3 × 20 s, reordered; 60 queries): 0: 0, 1: 0, 2: 10, 3: 50. Reported segments at no true offset: 1 in re-edits, 7 in other queries.

## Speed passes

Each rescaled pass is another fpcalc run on the clip: median 1.265 s per 30 s clip against 1.122 s for the clip as it is (in the test pool, not one process), so 4 passes cost about 5× the verifier time; match time is in the next table.

## Match time

| run | median per query (ms) | per minute of clip (ms) |
| --- | --- | --- |
| fitted | 50.6 | 118.0 |
| step 0.5 s | 13.9 | 30.5 |
| stop codes | 51.9 | 120.1 |
| speed passes | 253.5 | 579.1 |
| segments | 51.2 | 118.5 |

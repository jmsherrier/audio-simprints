# Test mode: test split

Recipe `audio-simprints/0.1`, match settings {'tolerance': 20, 'min_windows': 3}. fpcalc version 1.6.2 (FFmpeg Lavc62.11.100 Lavf62.3.100 SwR6.1.100); ffmpeg version 8.1.2-full_build-www.gyan.dev.
30 originals, 60 unrelated recordings, 20 look-alikes (other performances or readings of an original's piece), 12 other episodes of a series; 20.93 h in all.
Left out, not downloaded (upload.wikimedia.org throttled this IP): 52 recordings, antonin-dvorak-symphony-no-9-in-e-minor-from-the-new-world-o, bach-j-s-goldberg-variations-bwv988-10-variation-9-canon-on-, bach-j-s-goldberg-variations-bwv988-10-variation-9-canon-on--2, bach-j-s-goldberg-variations-bwv988-17-variation-16-overture, bach-j-s-goldberg-variations-bwv988-18-variation-17-shelley-, bach-j-s-goldberg-variations-bwv988-20-variation-19-shelley-, bach-j-s-goldberg-variations-bwv988-24-variation-23-shelley-, bach-j-s-goldberg-variations-bwv988-25-variation-24-canon-on, bach-j-s-goldberg-variations-bwv988-29-variation-28-shelley-, bach-j-s-goldberg-variations-bwv988-30-variation-29-shelley-, bach-siloti-prelude-in-b-minor-j-s-bach-arranged-siloti-arra, beethoven-piano-sonata-no-28-in-a-major-op-101-ii-lebhaft-ma, beethoven-sonata-no-8-in-c-minor-pathetique-op-13-iii-rondo-, beethoven-stringquartetno-6inbflatmajorop-18-ludwigvanbeetho, brahms-symphony-no-4-in-e-minor-op-98-iii-allegro-giocoso, camille-saint-saens-cello-concerto-no-1-in-a-minor-op-33-i-a, charpentier-te-deum-prelude, chopin-mazurka-op-50-no-3, chopin-nocturne-op-37-no-1, chopin-polonaise-op-40-no-1, chopin-waltz-op-64-no-2-in-c-sharp-minor, concerto-grosso-in-g-major-hwv-314, franz-schubert-fantasy-in-c-major-op-15-d-760-wanderer-iv-al, frederic-chopin-piano-sonata-no-2-in-b-flat-minor-op35-iii-m, fugue-in-a-minor-b-144, haydn-stringquartetindmajorop-64-josephhaydn-stringquartetin, imslp348255-pmlp01555-mozart-29-3, johann-sebastian-bach-aria-variata-bwv-989-part-1-theme-and-, johann-sebastian-bach-fugue-in-a-minor-bwv-543-robert-k-bler, ludwig-van-beethoven-piano-concerto-no-1-in-c-major-op-15-ii, ludwig-van-beethoven-symphony-no-5-in-c-minor-op-67-i-allegr, mazurka-op-59-no-1-in-a-minor, mazurka-op-59-no-3-in-f-sharp-minor, mozart-concerto-no-1-in-f-major-ii-andante-mozart-european-a, mozart-symphony-no-19-in-e-flat-major-iii-menuetto-mozart-eu, mozart-symphony-no-34-c-major-ii-andante-di-molto-mozart-eur, muzio-clementi-sonata-in-g-minor-no-3-op-50-didone-abbandona, nocturne-b-108-in-c-minor, nocturne-op-55-no-2-in-e-flat-major, peer-gynt-suite-no-1-op-46-ii-aase-s-death, polonaiseb-6ing-sharpminor, prelude-op-28-no-6, robert-schumann-scenes-from-childhood-op-15-vii-dreaming, strauss-kaiserwalzer, symphony-no-35-in-d-haffner-k-385-iv-finale-presto-mozart-eu, tchaikovsky-symphony-no-3-in-d-major-iv-scherzo-allegro-vivo, the-modena-chamber-orchestra-vivaldi-s-bassoon-concerto-in-a, the-modena-chamber-orchestra-vivaldi-s-concerto-for-2-mandol, the-modena-chamber-orchestra-vivaldi-s-concerto-in-c-major-r, the-musopen-symphony-orchestra-mendelssohn-s-symphony-no-3-i, waltz-op-64-no-1-in-d-flat-major, wolfgang-amadeus-mozart-flute-concerto-in-g-major-k-313-i-al.
Found: the right recording, fitted offset within 2 s of the truth (for re-edits, of one segment).

Storage: 11.72 codes per minute, 188 bytes per minute as 128-bit codes (764 as JSON); 8 silent and 12 constant windows skipped of 3443. Time, one process: creator 0.067 s per minute of audio, verifier 0.158 s per 30 s clip (decode and fpcalc included).

## Found per manipulation

| manipulation | step 0.124 s | step 0.5 s | right relationship | median offset error (s) | median coverage | wrong recording |
| --- | --- | --- | --- | --- | --- | --- |
| excerpt5 | 0% (0/60) | 0% (0/60) | – | – | – | 0 |
| excerpt10 | 0% (0/60) | 0% (0/60) | – | – | – | 0 |
| excerpt30 | 100% (60/60) | 100% (60/60) | 100% (60/60) | 0.04 | 0.83 | 0 |
| excerpt60 | 100% (60/60) | 100% (60/60) | 98% (59/60) | 0.03 | 0.92 | 0 |
| mp3-128 | 98% (59/60) | 98% (59/60) | 100% (59/59) | 0.07 | 0.83 | 0 |
| mp3-64 | 100% (60/60) | 100% (60/60) | 100% (60/60) | 0.04 | 0.83 | 0 |
| aac-128 | 98% (59/60) | 98% (59/60) | 100% (59/59) | 0.04 | 0.83 | 0 |
| opus-32 | 98% (59/60) | 98% (59/60) | 100% (59/59) | 0.04 | 0.83 | 0 |
| resample-22k | 100% (60/60) | 100% (60/60) | 100% (60/60) | 0.04 | 0.83 | 0 |
| mono | 98% (59/60) | 98% (59/60) | 100% (59/59) | 0.04 | 0.83 | 0 |
| volume+6 | 100% (60/60) | 100% (60/60) | 100% (60/60) | 0.04 | 0.83 | 0 |
| volume-6 | 100% (60/60) | 100% (60/60) | 100% (60/60) | 0.05 | 0.83 | 0 |
| phone | 30% (18/60) | 22% (13/60) | 100% (18/18) | 0.15 | 0.83 | 0 |
| noise-snr20 | 98% (59/60) | 98% (59/60) | 100% (59/59) | 0.05 | 0.83 | 0 |
| noise-snr10 | 98% (59/60) | 97% (58/60) | 100% (59/59) | 0.04 | 0.83 | 0 |
| speed+2 | 10% (6/60) | 8.3% (5/60) | 83% (5/6) | 0.11 | 0.74 | 0 |
| speed-2 | 10% (6/60) | 6.7% (4/60) | 100% (6/6) | 0.24 | 0.77 | 0 |
| speed+5 | 0% (0/60) | 0% (0/60) | – | – | – | 0 |
| speed-5 | 0% (0/60) | 0% (0/60) | – | – | – | 0 |
| tempo+5 | 97% (58/60) | 97% (58/60) | 100% (58/58) | 0.26 | 0.79 | 0 |
| tempo-5 | 93% (56/60) | 88% (53/60) | 96% (54/56) | 0.30 | 0.70 | 0 |
| under-speech-6 | 0% (0/60) | 0% (0/60) | – | – | – | 0 |
| under-speech-12 | 0% (0/60) | 0% (0/60) | – | – | – | 0 |
| under-music-6 | 0% (0/60) | 0% (0/60) | – | – | – | 0 |
| under-music-12 | 0% (0/60) | 0% (0/60) | – | – | – | 0 |
| reedit | 92% (55/60) | 88% (53/60) | 96% (53/55) | 0.08 | 0.96 | 0 |
| video | 100% (60/60) | 98% (59/60) | 100% (60/60) | 0.04 | 0.83 | 0 |

Right relationship: contained_in, or overlapping for re-edits (no one stored stretch holds the whole clip). Relationship, offset, coverage and wrong-recording columns: step 0.124 s. Coverage: share of the clip's stretch of the original inside the matched range (stored windows start every 5 s, so the ends are missed).

## False matches

| step | unrelated: queries with a match | unrelated: pairs (whole recording × original) | look-alike: queries | look-alike: pairs | series episodes: queries matching their series (shared intro) | series: pairs | false matches of series queries |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.124 s | 0% (0/120) | 0.3% (5/1800) | 0% (0/40) | 5.0% (1/20) | 0% (0/24) | 0% (0/24) | 0 |
| 0.5 s | 0% (0/120) | 0.2% (4/1800) | 0% (0/40) | 5.0% (1/20) | 0% (0/24) | 0% (0/24) | 0 |

Pairs: for unrelated recordings, each whole recording against every original; for look-alikes and series episodes, each whole recording against the original(s) of its own set. Queries: two 30 s excerpts per recording.

False and look-alike matches at step 0.124 s (query: matched recording, windows, relationship):

- moonlight-sonata__whole: ludwig-van-beethoven-sonata-no-14-in-c-sharp-minor-moonlight, 4, overlapping
- beat-doctor-tou269b__whole: x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s, 3, overlapping
- joanne-gabriel-01-the-planet__whole: barfly-s-dreams-002-theoutrooftheintro, 3, overlapping
- fm-dig019-04-fm-agrim-string-of-death-and-a-bitter-poison__whole: macho-alfa-el-pais-de-los-monos, 5, overlapping
- litmus0001-anu014-litmus0001-001-pripyat__whole: barfly-s-dreams-002-theoutrooftheintro, 4, overlapping
- second-thought-christmaspart1__whole: x-died-enroute-y-records-03-athenian-mercurypunctured-lung-s, 3, contained_in

## Match time

| step | median per query (ms) | per minute of clip (ms) |
| --- | --- | --- |
| 0.124 s | 9.4 | 34.9 |
| 0.5 s | 2.2 | 6.5 |

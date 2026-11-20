# Stems test (Phase 4)

Recipe `audio-simprints/0.2`, match {'tolerance': 32, 'min_windows': 6, 'min_density': 0.75, 'max_speed': 0.05, 'segments': 1, 'stop_owners': 0}. 20 songs (105.3 min), each with its full mix and real drums, bass and keys stems (archive.org, CC BY). A query is 30 s of one stem at a random place where it plays, 2 per song and stem: alone, or mixed over an unrelated netlabel track of the test split (stem at the track's loudness, or 6 dB under it). Found: the right song, offset within 2 s.

**A**: the query against the songs' full mixes. **B**: demucs (htdemucs) on both sides: each full mix separated into drums, bass, other and vocals, each indexed; the query separated too, and each of its four parts matched. B is run on the mixed queries only. **C**: B with the songs' demucs drums stems left out of the index, a variant, not fitted.

| stem | level | A: found | B: found | C: found |
| --- | --- | --- | --- | --- |
| drums | alone | 12% (5/40) | not run | not run |
| drums | mix 0 dB | 2.5% (1/40) | 28% (11/40) | 0% (0/40) |
| drums | mix −6 dB | 0% (0/40) | 12% (5/40) | 0% (0/40) |
| bass | alone | 5.0% (2/40) | not run | not run |
| bass | mix 0 dB | 0% (0/40) | 40% (16/40) | 40% (16/40) |
| bass | mix −6 dB | 0% (0/40) | 25% (10/40) | 25% (10/40) |
| keys | alone | 0% (0/40) | not run | not run |
| keys | mix 0 dB | 0% (0/40) | 18% (7/40) | 18% (7/40) |
| keys | mix −6 dB | 0% (0/40) | 10% (4/40) | 10% (4/40) |
| all | alone | 5.8% (7/120) | not run | not run |
| all | mix 0 dB | 0.8% (1/120) | 28% (34/120) | 19% (23/120) |
| all | mix −6 dB | 0% (0/120) | 16% (19/120) | 12% (14/120) |

**False matches** (a hit on another song):

| queries | A | B | C |
| --- | --- | --- | --- |
| stem queries | 5.3% (19/360) | 38% (90/240) | 6.7% (16/240) |
| unrelated tracks alone | 3.3% (2/60) | 33% (20/60) | 6.7% (4/60) |

B's false hits by demucs stem: drums 487, bass 5, other 5, vocals 10.

Demucs stems of the right song that B matched, per query stem: drums: drums 16; bass: bass 24, other 2; keys: other 11.

Cost: 23.39 codes per minute of song for A, 76.67 for B (four stems). Median match time per query: 10.4 ms (A), 135.8 ms (B, four parts). Separation: 22.98 s per minute of audio in one process of 10 CPU threads.

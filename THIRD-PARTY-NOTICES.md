# Third-party notices

audio-simprints is Apache-2.0 and does not include the packages or programs below.
Versions are the pins in [`pyproject.toml`](pyproject.toml).

## Runtime

| package | version | licence | link |
| --- | --- | --- | --- |
| NumPy | 2.5.2 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 | [github.com/numpy/numpy](https://github.com/numpy/numpy) |

The NumPy wheels bundle other libraries (OpenBLAS, the gfortran runtime) under
their own licences, listed in the wheel's `LICENSE.txt`.

## FFmpeg (external, not bundled)

Decoding runs the system `ffmpeg` as a subprocess. Nothing of FFmpeg is
distributed with this package. Its licence is LGPL-2.1 or GPL, depending on how the
installed build was configured; codec patents (MP3, AAC) concern whoever installs
and runs it. Reports record the version used.

## Chromaprint fpcalc (external, not bundled)

Raw fingerprints come from the system `fpcalc`, Chromaprint's command-line tool,
run as a subprocess; samples go in on stdin and numbers come out on stdout.
Nothing of Chromaprint is distributed with this package, and no Chromaprint code
is linked into it. Chromaprint's own code is MIT, but it includes parts of FFmpeg,
so its authors say the whole is to be treated as **LGPL-2.1**
([LICENSE.md](https://github.com/acoustid/chromaprint/blob/v1.6.2/LICENSE.md)).
The official fpcalc binaries also link FFmpeg statically, and a binary carries the
licence of the FFT library it was built with (FFmpeg's on Linux and Windows,
Apple's vDSP on macOS). CI downloads the official 1.6.2 build from
[github.com/acoustid/chromaprint](https://github.com/acoustid/chromaprint/releases/tag/v1.6.2)
and checks its SHA-256. Reports record the version used.

## Optional: stems test (`pip install audio-simprints[stems]`)

Used only by `audio-simprints stems`, the Phase 4 experiment. Nothing here is needed
to make or match codes.

| package | version | licence | link |
| --- | --- | --- | --- |
| demucs | 4.1.0 | MIT (code) | [github.com/adefossez/demucs](https://github.com/adefossez/demucs) |
| PyTorch | 2.5.1 | BSD-3-Clause | [github.com/pytorch/pytorch](https://github.com/pytorch/pytorch) |

**demucs pretrained weights: licence not clear.** The `htdemucs` weights are
downloaded at run time from Hugging Face (`adefossez/HTDemucs`, file
`955717e8.safetensors`, SHA-256
`d9fa14133cfcc034a6758923bb3a8ca9f8dfd0b582134643bbf83f72c17576dd`) into the user's
cache, never into this repository. Neither that model card nor the original
facebookresearch repository states a licence for the weights. The maintained
repository's README says the licence of the weights "is not clear", because they were
trained on MUSDB18 (some of it usable for research only; parts CC BY-NC-SA) and 800
other songs. This test is research only; any product use would need the licence
settled first, or other weights.

## Tests only

| package | version | licence | link |
| --- | --- | --- | --- |
| pytest | 9.2.0 | MIT | [github.com/pytest-dev/pytest](https://github.com/pytest-dev/pytest) |

The test vectors in [`tests/vectors`](tests/vectors) are synthetic, made by
[`tests/make_vectors.py`](tests/make_vectors.py), and are Apache-2.0 like the code.

## Test corpus

The recordings are not in this repository and are not redistributed.
[`tests/corpus/manifest.csv`](tests/corpus/manifest.csv) lists each one with its URL,
licence, credit and SHA-256; `fetch-corpus` downloads them. Only CC0, public-domain and
CC BY files were chosen (no CC BY-SA, NC or ND).

- **Wikimedia Commons music**: Musopen recordings (public domain or CC0, a few CC BY)
  and other performances of the same pieces from Commons' per-work categories. Each
  row credits the file page and the performer as Commons gives them.
- **LibriVox** audiobooks on archive.org, public domain, read by LibriVox
  volunteers. Each row names the archive.org item.
- **archive.org netlabels** releases under CC BY 2.0, 2.5, 3.0 or 4.0, one track per
  artist. The licence is read from each item's own metadata. Each row credits the
  artist (as the item names it), the file and the archive.org item.
- **archive.org stems** (the `stems` split, Phase 4): songs with their full mix and
  stems, under CC BY 3.0, read from each item's metadata. The items give no artist
  name. Each row credits the file, the song title and the archive.org item.
- **NASA, JPL and White House** series (*This Week @NASA*, *Space to Ground*, JPL's
  *What's Up*, *A Moment with…*, *West Wing Week*) on Wikimedia Commons, public domain
  (works of the US government). These are the same rows as in video-simprints'
  corpus.

## Patents

Not reviewed. Audio fingerprinting has a dense patent history, including landmark
(peak-pair) hashing and Philips-style sub-fingerprints. Check before any
commercial use.

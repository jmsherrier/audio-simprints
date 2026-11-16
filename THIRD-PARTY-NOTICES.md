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

## Tests only

| package | version | licence | link |
| --- | --- | --- | --- |
| pytest | 9.2.0 | MIT | [github.com/pytest-dev/pytest](https://github.com/pytest-dev/pytest) |

The test vectors in [`tests/vectors`](tests/vectors) are synthetic, made by
[`tests/make_vectors.py`](tests/make_vectors.py), and are Apache-2.0 like the code.

## Patents

Not reviewed. Audio fingerprinting has a dense patent history, including landmark
(peak-pair) hashing and Philips-style sub-fingerprints. Check before any
commercial use.

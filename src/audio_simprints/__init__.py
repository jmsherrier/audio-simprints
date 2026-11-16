"""Granular audio codes: Chromaprint windows as 128-bit codes, matched within a Hamming tolerance, confirmed by a time vote."""

from .audio import AudioError
from .recipe import DEFAULTS, MATCH, RECIPE, generate, index, match, verify

__all__ = ["DEFAULTS", "MATCH", "RECIPE", "AudioError", "generate", "index", "match", "verify"]

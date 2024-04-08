"""
# 🏳️‍⚧️ Transdoc 🏳️‍⚧️

A simple tool for transforming Python docstrings by embedding results from
Python function calls.
"""
__all__ = [
    '__version__',
    'main',
    'transform',
    'Rule',
]

from .__consts import VERSION as __version__
from .__transformer import transform
from .__rule import Rule
from .__cli import main

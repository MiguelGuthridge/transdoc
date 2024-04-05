"""
# 🏳️‍⚧️ Transdoc 🏳️‍⚧️

A simple tool for transforming Python docstrings by embedding results from
Python function calls.
"""
__all__ = [
    'transform',
    'Rule',
]

from .__transformer import transform
from .__rule import Rule

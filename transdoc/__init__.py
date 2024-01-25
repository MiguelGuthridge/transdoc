"""
# Transdoc

A simple tool for rewriting Python docstrings.
"""
__all__ = [
    'transform',
    'Rule',
]

from .__transformer import transform
from .__rule import Rule

"""
# 🏳️‍⚧️ Transdoc 🏳️‍⚧️

A simple tool for transforming Python docstrings by embedding results from
Python function calls.
"""
__all__ = [
    'VERSION',
    'cli',
    'transform',
    'Rule',
]

from .__consts import VERSION
from .__transformer import transform
from .__rule import Rule
from .__cli import cli

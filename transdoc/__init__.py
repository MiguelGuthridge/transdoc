"""
# Transdoc

A simple tool for rewriting Python docstrings.
"""
__all__ = [
    'transform',
    'TransformErrorInfo',
    'CodePosition',
    'Rule',
]

from .__transformer import transform, TransformErrorInfo
from .__rule import Rule
from libcst.metadata import CodePosition

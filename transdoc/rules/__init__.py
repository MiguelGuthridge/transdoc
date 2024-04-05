"""
# Transdoc / Rules

This module contains definitions for some simple commonly-used rules.
"""
__all__ = [
    "file_contents",
    "attributes",
    "attributes_generator",
    "markdown_docs_link_generator",
]

from .__file_contents import file_contents
from .__attributes import attributes, attributes_generator
from .__markdown_docs_link import markdown_docs_link_generator

"""
Test module

This is to test Transdoc's rewriting of modules.

{{hi}}
"""


def function():
    """Here's a docstring {{hi}}"""


class Class:
    """Another docstring {{hi}}"""

    def example(self):
        """And another one {{hi}}"""

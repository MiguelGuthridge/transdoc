"""
# Transdoc / Rules / File contents

Rule for getting the contents of a file.
"""
from functools import cache


@cache
def file_contents(path: str) -> str:
    """
    Transdoc rule that evaluates to the contents of a file.

    This rule has simple cacheing to improve performance when used
    repeatedly.
    """
    with open(path, encoding='utf-8') as f:
        return f.read()

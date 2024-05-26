"""
# Transdoc / Tests / Rules / File Contents Test

Test cases for the `file_contents` rule.
"""
from transdoc import transform
from transdoc.rules import file_contents


def example():
    """
    {{file_contents[tests/data/example.txt]}}
    """


EXPECTED = '''
def example():
    """
    Example
    """
'''.removeprefix('\n')


def test_file_contents():
    assert transform(example, [file_contents]) == EXPECTED

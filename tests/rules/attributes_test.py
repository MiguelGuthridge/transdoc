"""
# Transdoc / Tests / Rules / Attributes Test

Test cases for Transdoc's built-in `attributes` rule.
"""
from transdoc import transform
from transdoc.rules import attributes


class Example:
    """
    {{attributes("tests.rules.attributes_test", "Example")}}
    """

    def __init__(self) -> None:
        pass

    def some_fn(self):
        pass


EXPECTED = '''
class Example:
    """
    * some_fn
    """

    def __init__(self) -> None:
        pass

    def some_fn(self):
        pass
'''.removeprefix('\n')


def test_attributes():
    assert transform(Example, [attributes]) == EXPECTED

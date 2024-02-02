"""
Tests / Parsing test

Tests for ensuring that parsing of docstrings works correctly.
"""
import importlib
from pathlib import Path
from transdoc import transform
from inspect import getsource


###############################################################################

# Some simple rules for testing

def hi():
    """Simple rule"""
    return "hi"


def hello(name: str):
    """Simple rule, accepting a parameter"""
    return f"hello, {name}"


###############################################################################


def test_no_transform():
    """Transdoc should leave functions that don't have transformations alone"""
    # Pylance yells about this but Mypy seems fine
    assert transform(test_no_transform, [hi]) \
        == getsource(test_no_transform)


def test_no_transform_braces():
    """
    Transdoc should leave functions that don't have transformations alone, even
    if they include {curly braces} in their docstring
    """
    assert transform(test_no_transform_braces, [hi]) \
        == getsource(test_no_transform_braces)


def test_no_transform_single_quote():
    "Transdoc should ignore single-quoted docstrings, {{hi}}"
    assert transform(test_no_transform_single_quote, [hi]) \
        == getsource(test_no_transform_single_quote)


###############################################################################


def fn_simple():
    """{{hi}}"""


fn_simple_result = "\n".join([
    'def fn_simple():',
    '    """hi"""',
    '',
])


def test_simple_transformation():
    """Test a simple transformation"""
    assert transform(fn_simple, [hi]) == fn_simple_result


###############################################################################


def fn_square_bracket():
    """{{hello[Miguel]}}"""


fn_square_bracket_result = \
    '''def fn_square_bracket():
    """hello, Miguel"""
'''


def test_square_bracket_syntax():
    """
    Test a transformation which provides a text argument using the square
    bracket syntax
    """
    assert transform(fn_square_bracket, [hello]) == fn_square_bracket_result


###############################################################################


def fn_square_bracket_braces():
    """{{hello[Miguel with {braces}]}}"""


fn_square_bracket_braces_result = \
    '''def fn_square_bracket_braces():
    """hello, Miguel with {braces}"""
'''


def test_square_bracket_syntax_with_braces():
    """
    Test a transformation which provides a text argument using the square
    bracket syntax, including {braces in the argument}
    """
    assert transform(fn_square_bracket_braces, [hello]) \
        == fn_square_bracket_braces_result


###############################################################################


def fn_call_simple():
    """{{hello("Miguel")}}"""


fn_call_simple_result = \
    '''def fn_call_simple():
    """hello, Miguel"""
'''


def test_transformation_function_call():
    """
    Test a transformation which provides arguments using the function-call
    syntax
    """
    assert transform(fn_call_simple, [hello]) == fn_call_simple_result


###############################################################################


def fn_call_kwargs():
    """{{hello(name="Miguel")}}"""


fn_call_kwargs_result = \
    '''def fn_call_kwargs():
    """hello, Miguel"""
'''


def test_transformation_function_call_kwargs():
    """
    Test a transformation which provides arguments using the function-call
    syntax, passing the argument as a kwarg.
    """
    assert transform(fn_call_kwargs, [hello]) \
        == fn_call_kwargs_result


###############################################################################


class Greeter:  # pragma: no cover
    """
    This class is useful for saying hi to people and stuff

    {{hi}}
    """

    def __init__(self, my_name: str) -> None:
        """
        Create a Greeter, which introduces itself to people

        {{hi}}
        """
        self.__my_name = my_name

    def say_hi(self, name: str) -> str:
        """
        Introduce this greeter to someone.

        {{hi}}
        """
        return f"Hi, {name}, I'm {self.__my_name}"


class_result = '\n'.join([
    'class Greeter:  # pragma: no cover',
    '    """',
    '    This class is useful for saying hi to people and stuff',
    '',
    '    hi',
    '    """',
    '',
    '    def __init__(self, my_name: str) -> None:',
    '        """',
    '        Create a Greeter, which introduces itself to people',
    '',
    '        hi',
    '        """',
    '        self.__my_name = my_name',
    '',
    '    def say_hi(self, name: str) -> str:',
    '        """',
    '        Introduce this greeter to someone.',
    '',
    '        hi',
    '        """',
    '        return f"Hi, {name}, I\'m {self.__my_name}"',
    '',
])


def test_transform_class():
    """
    Does Transdoc transform docstrings for classes and their methods correctly?
    """
    assert transform(Greeter, [hi]) == class_result


###############################################################################


def test_transform_module():
    """
    Can Transdoc transform entire modules?
    """
    mod_path = Path(__file__).parent.joinpath("data", "module.py")
    mod_txt = open(mod_path).read()

    assert transform(mod_txt, [hi]) == mod_txt.replace("{{hi}}", "hi")

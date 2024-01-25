"""
Tests / Parsing test

Tests for ensuring that parsing of docstrings works correctly.
"""
from transdoc import transform
from inspect import getsource


def hi():
    """Simple rule"""
    return "hi"


def hello(name: str):
    """Simple rule"""
    return f"hello, {name}"


def no_transformation():
    """hi"""


def transformation_hi():
    """{{hi}}"""


transformation_hi_result = \
    '''def transformation_hi():
    """hi"""
'''


def transformation_hello():
    """{{hello[Miguel]}}"""


transformation_hello_result = \
    '''def transformation_hello():
    """hello, Miguel"""
'''


def transformation_hello_call():
    """{{hello("Miguel")}}"""


transformation_hello_call_result = \
    '''def transformation_hello_call():
    """hello, Miguel"""
'''


def transformation_hello_call_kwargs():
    """{{hello(name="Miguel")}}"""


transformation_hello_call_kwargs_result = \
    '''def transformation_hello_call_kwargs():
    """hello, Miguel"""
'''


def test_no_transformation():
    # Pylance yells about this but Mypy seems fine
    assert transform(no_transformation, [hi]) == getsource(no_transformation)


def test_simple_transformation():
    assert transform(transformation_hi, [hi]) == transformation_hi_result


def test_transformation_square_bracket_syntax():
    assert transform(transformation_hello, [hello]) \
        == transformation_hello_result


def test_transformation_function_call():
    assert transform(transformation_hello_call, [hello]) \
        == transformation_hello_call_result


def test_transformation_function_call_kwargs():
    assert transform(transformation_hello_call_kwargs, [hello]) \
        == transformation_hello_call_kwargs_result

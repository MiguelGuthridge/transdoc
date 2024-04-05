"""
# Transdoc / Tests / Error test

Test cases for errors when transforming documentation.
"""
from transdoc import transform
from transdoc.errors import (
    TransformErrorInfo,
    TransdocNameError,
    TransdocSyntaxError,
    TransdocTransformationError,
)
from libcst.metadata import CodePosition
import jestspectation as expect


class EqualError(Exception):
    """
    An error where the == operator is implemented so we can test it easily
    """

    def __eq__(self, value: object) -> bool:
        return isinstance(value, EqualError) and value.args == self.args


def err(fn) -> list[TransformErrorInfo]:
    """
    Helper function to extract and unpack error information from
    transformation.
    """
    try:
        fn()
    except TransdocTransformationError as e:
        return list(e.args)

    assert False, "Transformation didn't produce error"


###############################################################################


def test_unknown_rule():
    """
    Is an error reported if an unknown rule is transformed?

    {{unknown}}
    """
    assert err(lambda: transform(test_unknown_rule, [])) == [
        expect.ObjectContainingItems({
            "position": CodePosition(5, 6),
            "error_info": expect.Any(TransdocNameError)
        }),
    ]


###############################################################################


def error_rule(value="Error"):
    """
    A rule that raises an exception
    """
    raise EqualError(value)


def test_rule_raises_standard():
    """
    Is an error reported if a rule raises an exception when processing?

    {{error_rule}}
    """
    assert err(lambda: transform(test_rule_raises_standard, [error_rule])) == [
        TransformErrorInfo(
            CodePosition(5, 6),
            EqualError("Error"),
        )
    ]


def test_rule_raises_string_arg():
    """
    Is an error reported if a rule raises an exception when processing?

    {{error_rule[Error message]}}
    """
    assert err(
        lambda: transform(test_rule_raises_string_arg, [error_rule])
    ) == [
        TransformErrorInfo(
            CodePosition(5, 6),
            EqualError("Error message"),
        )
    ]


def test_rule_raises_call_arg():
    """
    Is an error reported if a rule raises an exception when processing?

    {{error_rule("Error message")}}
    """
    assert err(lambda: transform(test_rule_raises_call_arg, [error_rule])) == [
        TransformErrorInfo(
            CodePosition(5, 6),
            EqualError("Error message"),
        )
    ]


###############################################################################


def test_rule_syntax_error():
    """
    Is an error reported if a rule contains invalid syntax?

    {{invalid syntax}}
    """
    assert err(lambda: transform(test_rule_syntax_error, [])) == [
        expect.ObjectContainingItems({
            "position": CodePosition(5, 6),
            "error_info": expect.Any(TransdocSyntaxError)
        }),
    ]


def test_unclosed_braces():
    """
    Is an error reported if a docstring contains an unclosed {{brace pair?
    """
    assert err(lambda: transform(test_unclosed_braces, [])) == [
        expect.ObjectContainingItems({
            "position": CodePosition(3, 63),
            "error_info": expect.Any(TransdocSyntaxError)
        }),
    ]

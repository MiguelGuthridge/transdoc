"""
# Transdoc / Tests / Error test

Test cases for errors when transforming documentation.
"""
from transdoc import transform, TransformErrorInfo, CodePosition
from transdoc.errors import TransdocNameError, TransdocSyntaxError
import jestspectation as expect


class EqualError(Exception):
    """
    An error where the == operator is implemented so we can test it easily
    """

    def __eq__(self, value: object) -> bool:
        return isinstance(value, EqualError) and value.args == self.args


def test_unknown_rule():
    """
    Is an error reported if an unknown rule is transformed?

    {{unknown}}
    """
    assert transform(test_unknown_rule, []) == [
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


def test_rule_raises_exception_standard():
    """
    Is an error reported if a rule raises an exception when processing?

    {{error_rule}}
    """
    assert transform(test_rule_raises_exception_standard, [error_rule]) == [
        TransformErrorInfo(
            CodePosition(5, 6),
            EqualError("Error"),
        )
    ]


def test_rule_raises_exception_string_arg():
    """
    Is an error reported if a rule raises an exception when processing?

    {{error_rule[Error message]}}
    """
    assert transform(test_rule_raises_exception_string_arg, [error_rule]) == [
        TransformErrorInfo(
            CodePosition(5, 6),
            EqualError("Error message"),
        )
    ]


def test_rule_raises_exception_call_arg():
    """
    Is an error reported if a rule raises an exception when processing?

    {{error_rule("Error message")}}
    """
    assert transform(test_rule_raises_exception_call_arg, [error_rule]) == [
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
    assert transform(test_rule_syntax_error, []) == [
        expect.ObjectContainingItems({
            "position": CodePosition(5, 6),
            "error_info": expect.Any(TransdocSyntaxError)
        }),
    ]


def test_unclosed_braces():
    """
    Is an error reported if a docstring contains an unclosed {{brace pair?
    """
    assert transform(test_unclosed_braces, []) == [
        expect.ObjectContainingItems({
            "position": CodePosition(3, 63),
            "error_info": expect.Any(TransdocSyntaxError)
        }),
    ]

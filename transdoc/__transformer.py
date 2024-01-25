"""
# Transdoc / transformer

Use libcst to rewrite docstrings.
"""
import inspect
from io import StringIO
from types import (
    FunctionType,
    ModuleType,
    MethodType,
    CodeType,
    TracebackType,
    FrameType,
)
from typing import Union
import libcst
from .__rule import Rule


# FIXME: This isn't especially safe - find a nicer type annotation to use
SourceObjectType = Union[
    FunctionType,
    ModuleType,
    MethodType,
    CodeType,
    TracebackType,
    FrameType,
    type,
]


class DocTransformer(libcst.CSTTransformer):
    """
    Rewrite documentation.
    """
    def __init__(self, rules: dict[str, Rule]) -> None:
        """
        Create an instance of the doc transformer module
        """
        self.__rules = rules

    def __report_error(self, msg: str, exc: Exception) -> None:
        """
        Report an error that occurred when processing a docstring

        TODO
        """

    def __eval_rule(self, rule: str) -> str:
        """
        Execute a command, alongside the given set of rules.
        """
        # if it's just a function name, evaluate it as a call with no arguments
        if rule.isidentifier():
            return self.__rules[rule]()
        # If it uses square brackets, then extract the contained string, and
        # pass that
        if rule.split('[')[0].isidentifier() and rule.endswith(']'):
            rule_name, *content = rule.split('[')
            content_str = '['.join(content).removesuffix(']')
            return self.__rules[rule_name](content_str)
        # Otherwise, it should be a regular function call
        # This calls `eval` with the rules dictionary set as the globals, since
        # otherwise it'd just be too complex to parse things.
        if rule.split('(')[0].isidentifier() and rule.endswith(')'):
            return eval(rule, self.__rules)

        # If we reach this point, it's not valid data, and we should give an
        # error
        # TODO: Make this nicer once we have better error reporting
        raise ValueError("Bad rule parsing")

    def __process_docstring(self, docstring: str) -> str:
        """
        Process the given docstring according to the rules of the
        DocTransformer.
        """
        new_doc = StringIO()
        cmd_buffer = StringIO()
        in_buffer = False
        brace_count = 0
        for c in docstring:
            if in_buffer:
                # FIXME: This assumes that all instances of `}}` close the
                # buffer, which isn't necessarily the case. This will break
                # function calls where nested dicts are used as arguments.
                if c == "}":
                    brace_count += 1
                    if brace_count == 2:
                        # End of command, let's execute it
                        cmd_buffer.seek(0)
                        new_doc.write(self.__eval_rule(cmd_buffer.read()))
                        cmd_buffer = StringIO()
                        in_buffer = False
                        brace_count = 0
                else:
                    # If we previously found a closing brace
                    if brace_count == 1:
                        cmd_buffer.write("}")
                    brace_count = 0
                    cmd_buffer.write(c)
            else:
                if c == "{":
                    brace_count += 1
                    if brace_count == 2:
                        in_buffer = True
                        brace_count = 0
                else:
                    # If we previously found a closing brace
                    if brace_count == 1:
                        new_doc.write("{")
                    brace_count = 0
                    new_doc.write(c)

        # TODO: if we're in a command, report an error, and also clean up extra
        # brace

        # Return the output
        new_doc.seek(0)
        return new_doc.read()

    def leave_SimpleString(
        self,
        original_node: libcst.SimpleString,
        updated_node: libcst.SimpleString,
    ) -> libcst.BaseExpression:
        """
        After visiting a string, check if it is a triple-quoted string. If so,
        apply formatting to it.

        Currently, I'm assuming that all triple-quoted strings are docstrings
        so that we can handle attribute docstrings (which otherwise don't work
        very nicely).
        """
        string = original_node.value
        if string.startswith('"""') or string.startswith("'''"):
            return updated_node.with_changes(
                value=self.__process_docstring(updated_node.value)
            )

        return updated_node


def make_rules_dict(rules: list[Rule]) -> dict[str, Rule]:
    """
    Convert a list of rule functions into a dictionary of functions
    """
    return {r.__name__: r for r in rules}


def transform(source: Union[str, SourceObjectType], rules: list[Rule]) -> str:
    """
    Transform a Python module by rewriting its documentation according to the
    given rules
    """
    if not isinstance(source, str):
        source = inspect.getsource(source)
    cst = libcst.parse_module(source)
    updated_cst = cst.visit(DocTransformer(make_rules_dict(rules)))
    return updated_cst.code

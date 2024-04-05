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
from typing import Union, Optional
import libcst as cst
from libcst.metadata import CodePosition, PositionProvider, MetadataWrapper

from .__rule import Rule
from .__collect_rules import collect_rules
from .errors import (
    TransdocTransformationError,
    TransformErrorInfo,
    TransdocSyntaxError,
    TransdocNameError,
)


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


class DocTransformer(cst.CSTTransformer):
    """
    Rewrite documentation.
    """
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, rules: dict[str, Rule]) -> None:
        """
        Create an instance of the doc transformer module
        """
        self.__rules = rules
        self.__errors: list[TransformErrorInfo] = []
        self.__current_node: Optional[cst.CSTNode] = None

    def get_errors(self) -> list[TransformErrorInfo]:
        return self.__errors

    def __get_position(
        self,
        offset: Optional[tuple[int, int]] = None,
    ) -> CodePosition:
        """
        Returns the position of the given node, for use with error reporting.
        """
        assert self.__current_node is not None
        position = self.get_metadata(
            PositionProvider,
            self.__current_node,
        ).start

        if offset is not None:
            line, column = offset

            if line:
                new_line = position.line + line
                new_col = column
            else:
                new_line = position.line
                new_col = position.column + column

            position = CodePosition(new_line, new_col)

        return position

    def __report_error(
        self,
        position: CodePosition,
        error_info: Exception,
    ):
        """
        Report an error
        """
        self.__errors.append(TransformErrorInfo(
            position,
            error_info,
        ))

    def __report_rule_if_unknown(self, rule_name: str, position: CodePosition):
        """
        Ensure a rule is known, and report an error if it is not.

        Return `True` if an error was reported.
        """
        if rule_name not in self.__rules:
            self.__report_error(
                position,
                TransdocNameError(f"unknown rule '{rule_name}'"),
            )
            return True
        return False

    def __eval_rule(self, rule: str, position: CodePosition) -> str:
        """
        Execute a command, alongside the given set of rules.
        """
        # if it's just a function name, evaluate it as a call with no arguments
        if rule.isidentifier():
            if self.__report_rule_if_unknown(rule, position):
                return ""
            try:
                return self.__rules[rule]()
            except Exception as e:
                self.__report_error(position, e)
                return ""
        # If it uses square brackets, then extract the contained string, and
        # pass that
        if rule.split('[')[0].isidentifier() and rule.endswith(']'):
            rule_name, *content = rule.split('[')
            content_str = '['.join(content).removesuffix(']')
            if self.__report_rule_if_unknown(rule_name, position):
                return ""
            try:
                return self.__rules[rule_name](content_str)
            except Exception as e:
                self.__report_error(position, e)
                return ""
        # Otherwise, it should be a regular function call
        # This calls `eval` with the rules dictionary set as the globals, since
        # otherwise it'd just be too complex to parse things.
        if rule.split('(')[0].isidentifier() and rule.endswith(')'):
            if self.__report_rule_if_unknown(rule.split('(')[0], position):
                return ""
            try:
                return eval(rule, self.__rules)
            except Exception as e:
                self.__report_error(position, e)
                return ""

        # If we reach this point, it's not valid data, and we should give an
        # error
        self.__report_error(
            position,
            TransdocSyntaxError(
                "unable to evaluate rule due to invalid syntax"
            ),
        )
        return ""

    def __process_docstring(self, docstring: str) -> str:
        """
        Process the given docstring according to the rules of the
        DocTransformer.
        """
        # This code is extremely yucky but I cannot be bothered to write a
        # nicer version of it
        # Perhaps I could use a state machine or something?
        new_doc = StringIO()
        cmd_buffer = StringIO()
        in_cmd_buffer = False
        brace_count = 0
        cmd_start_position: Optional[CodePosition] = None

        # Column offset starts at 3 to account for stripped out triple-quotes
        col_offset = 3
        line_offset = 0
        for c in docstring:
            if in_cmd_buffer:
                # FIXME: This assumes that all instances of `}}` close the
                # buffer, which isn't necessarily the case. This will break
                # function calls where nested dicts are used as arguments.
                if c == "}":
                    brace_count += 1
                    if brace_count == 2:
                        # End of command, let's execute it
                        cmd_buffer.seek(0)
                        assert cmd_start_position is not None
                        new_doc.write(self.__eval_rule(
                            cmd_buffer.read(),
                            cmd_start_position,
                        ))
                        cmd_buffer = StringIO()
                        in_cmd_buffer = False
                        cmd_start_position = None
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
                        cmd_start_position = self.__get_position((
                            line_offset,
                            col_offset + 1,
                        ))
                        in_cmd_buffer = True
                        brace_count = 0
                else:
                    # If we previously found a closing brace
                    if brace_count == 1:
                        new_doc.write("{")
                    brace_count = 0
                    new_doc.write(c)

            # Finally update the source position
            if c == '\n':
                line_offset += 1
                col_offset = 0
            else:
                col_offset += 1

        # TODO: if we're in a command, report an error, and also clean up extra
        # brace
        if in_cmd_buffer:
            assert cmd_start_position is not None
            self.__report_error(
                cmd_start_position,
                TransdocSyntaxError(
                    "unfinished command: are you missing a closing '}}'?"
                ),
            )

        # Return the output
        new_doc.seek(0)
        return new_doc.read()

    def leave_SimpleString(
        self,
        original_node: cst.SimpleString,
        updated_node: cst.SimpleString,
    ) -> cst.BaseExpression:
        """
        After visiting a string, check if it is a triple-quoted string. If so,
        apply formatting to it.

        Currently, I'm assuming that all triple-quoted strings are docstrings
        so that we can handle attribute docstrings (which otherwise don't work
        very nicely).
        """
        self.__current_node = original_node
        string = original_node.value
        if string.startswith('"""') or string.startswith("'''"):
            quote_type = string[0:3]

            processed = self.__process_docstring(updated_node.value[3:-3])

            return updated_node.with_changes(
                value=f"{quote_type}{processed}{quote_type}"
            )

        self.__current_node = None
        return updated_node


def make_rules_dict(rules: list[Rule]) -> dict[str, Rule]:
    """
    Convert a list of rule functions into a dictionary of functions
    """
    return {r.__name__: r for r in rules}


def transform(
    source: Union[str, SourceObjectType],
    rules: Union[list[Rule], dict[str, Rule], ModuleType],
) -> str:
    """
    Transform the Python code by rewriting its documentation according to the
    given rules.

    ## Args

    * `source` (`str | SourceObjectType`): source code to transform. If a
      Python code object is given, `inspect.getsource` will be used, meaning
      that an error will be given if source code is not available.

    * `rules` (`list[Rule] | dict[str, Rule] | ModuleRule`): a list of rules to
      apply, or a module containing these rules.

    ## Raises

    * `TransdocTransformationError`: collection of errors produced when
      performing the transformation.

    ## Returns

    * `str`: the transformed source code, with all rules applied.
    """
    if not isinstance(source, str):
        source = inspect.getsource(source)
    if isinstance(rules, ModuleType):
        rules = collect_rules(rules)
    elif isinstance(rules, list):
        rules = make_rules_dict(rules)
    parsed = MetadataWrapper(cst.parse_module(source))
    transformer = DocTransformer(rules)
    updated_cst = parsed.visit(transformer)

    errors = transformer.get_errors()
    if errors:
        raise TransdocTransformationError(*errors)

    return updated_cst.code

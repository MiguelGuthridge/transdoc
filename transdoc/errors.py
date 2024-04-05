"""
# Transdoc / Errors

Definitions for error classes used by Transdoc.
"""
from dataclasses import dataclass
from libcst.metadata import CodePosition


@dataclass
class TransformErrorInfo:
    """
    A simple wrapper class for information about an error that occurred
    during documentation transformation
    """
    position: CodePosition
    error_info: Exception


class TransdocTransformationError(Exception):
    """
    An exception containing information on all errors encountered whilst
    transforming the documentation.
    """

    def __init__(self, *errors: TransformErrorInfo) -> None:
        super().__init__(*errors)
        self.args: tuple[TransformErrorInfo, ...] = errors


class TransdocSyntaxError(SyntaxError):
    """Syntax error when transforming documentation"""


class TransdocNameError(NameError):
    """Name error when attempting to execute rule"""

"""
# Transdoc / Errors

Definitions for error classes used by Transdoc.
"""


# IDEA: Perhaps explore using exception groups to report all the errors?


class TransdocSyntaxError(SyntaxError):
    """Syntax error when transforming documentation"""


class TransdocNameError(NameError):
    """Name error when attempting to execute rule"""

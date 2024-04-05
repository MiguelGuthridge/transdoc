"""
# Transdoc / Errors

Definitions for error classes used by Transdoc.
"""


# IDEA: Perhaps explore using exception groups to report all the errors?
# This will probably require Python 3.11 though


class TransdocSyntaxError(SyntaxError):
    """Syntax error when transforming documentation"""


class TransdocNameError(NameError):
    """Name error when attempting to execute rule"""

"""
# Transdoc / rule

Type definition for Transdoc rules
"""
from typing import Callable


Rule = Callable[..., str]
"""
Rules are Python functions (potentially accepting arguments) which can be
called during compile time.
"""

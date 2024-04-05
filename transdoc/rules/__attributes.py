"""
# Transdoc / Rules / Attributes

Rule for listing the attributes of the given object.
"""
import importlib
from typing import Optional, Callable


def attributes_default_formatter(
    module: str,
    object: Optional[str],
    attribute: str,
) -> str:
    """
    Default formatter used by attributes rule.
    """
    return f"* {attribute}"


def attributes(
    module: str,
    object: Optional[str] = None,
    formatter: Callable[[str, Optional[str], str], str]
        = attributes_default_formatter,
) -> str:
    """
    Generate a list of attributes for an object.

    This imports the object from the given module before determining its
    attributes.

    ## Args

    * `module` (`str`): module to import.

    * `object` (`str`, optional): object to list attributes from. If not
      provided, attributes are listed from `module` instead. Defaults to
      `None`.

    * `formatter` (`(str, Optional[str], str) -> str`, optional): a function to
      format the documentation for the attribute. It should accept the
      module name (eg `"transdoc.errors"`), the object name (eg
      `"TransformErrorInfo"`), and the attribute name (eg `"position"`), and
      should return text that will be used in place of the object. This can be
      used to generate Markdown links, or do other useful things. By default,
      a bullet point followed by the name of the attribute will be provided,
      for example `"* position"`.
    """
    if object is None:
        data = importlib.import_module(module)
    else:
        mod = importlib.import_module(module)
        data = getattr(mod, object)

    return "\n".join(formatter(module, object, attr) for attr in dir(data))


# Sneaky little redefinition so we can use it in the function below
_attributes = attributes


def formatted_attributes_generator(
    formatter: Callable[[str, Optional[str], str], str]
) -> Callable[[str, Optional[str]], str]:
    """
    Generate an attributes rule that uses the given formatter.

    ## Usage

    This can be used in a list of rules as follows:

    ```py
    from transdoc.rules import formatted_attributes_generator

    def my_custom_formatter(mod, obj, attr):
        return f"{mod}.{obj}.{attr}"

    attributes = formatted_attributes_generator
    ```

    ## Args

    * `formatter` (`(str, Optional[str], str) -> str`): a function to
      format the documentation for the attribute. It should accept the
      module name (eg `"transdoc.errors"`), the object name (eg
      `"TransformErrorInfo"`), and the attribute name (eg `"position"`), and
      should return text that will be used in place of the object. This can be
      used to generate Markdown links, or do other useful things. By default,
      a bullet point followed by the name of the attribute will be provided,
      for example `"* position"`.

    ## Returns

    `Callable[[str, Optional[str]], str]`

    A Transdoc rule function that formats the list of attributes using
    `formatter`.
    """
    def attributes(module: str, object: Optional[str]) -> str:
        return _attributes(module, object, formatter)

    return attributes

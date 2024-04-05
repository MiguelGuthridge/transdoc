"""
# Transdoc / Rules / Attributes

Rule for listing the attributes of the given object.
"""
import importlib
from typing import Optional, Callable, Any


def attributes_default_filter(attr_name: str, attr_object: Any) -> bool:
    """
    Default filter used by attributes rule.

    Only keeps attrs where the name doesn't start with `_`.
    """
    return not attr_name.startswith('_')


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
    *,
    filter: Optional[Callable[[str, Any], bool]] = None,
    formatter: Optional[Callable[[str, Optional[str], str], str]]
        = None,
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

    ## Keyword args

    * `filter` (`(str, Any) -> bool`, optional): a function used to filter out
      unwanted attributes from the list. It should accept the name of the
      attribute, as well as a reference to it, then return `True` if the
      attribute should be included in the list, or `False` if it should be
      skipped. By default, this skips any attributes whose names start with an
      underscore (`_`).

    * `formatter` (`(str, Optional[str], str) -> str`, optional): a function to
      format the documentation for the attribute. It should accept the
      module name (eg `"transdoc.errors"`), the object name (eg
      `"TransformErrorInfo"`), and the attribute name (eg `"position"`), and
      should return text that will be used in place of the object. This can be
      used to generate Markdown links, or do other useful things. By default,
      a bullet point followed by the name of the attribute will be provided,
      for example `"* position"`.
    """
    if filter is None:
        filter = attributes_default_filter
    if formatter is None:
        formatter = attributes_default_formatter

    if object is None:
        data = importlib.import_module(module)
    else:
        mod = importlib.import_module(module)
        data = getattr(mod, object)

    return "\n".join(
        formatter(module, object, attr)
        for attr in dir(data)
        if filter(attr, getattr(data, attr))
    )


# Sneaky little redefinition so we can use it in the function below
_attributes = attributes


def attributes_generator(
    *,
    filter: Optional[Callable[[str, Any], bool]] = None,
    formatter: Optional[Callable[[str, Optional[str], str], str]] = None,
) -> Callable[[str, Optional[str]], str]:
    """
    Generate an attributes rule that uses the given formatter and/or filter.

    ## Usage

    This can be used in a list of rules as follows:

    ```py
    from transdoc.rules import attributes_generator

    def my_custom_formatter(mod, obj, attr):
        return f"{mod}.{obj}.{attr}"

    attributes = attributes_generator(formatter=my_custom_formatter)
    ```

    ## Keyword args

    * `filter` (`(str, Any) -> bool`, optional): a function used to filter out
      unwanted attributes from the list. It should accept the name of the
      attribute, as well as a reference to it, then return `True` if the
      attribute should be included in the list, or `False` if it should be
      skipped. By default, this skips any attributes whose names start with an
      underscore (`_`).

    * `formatter` (`(str, Optional[str], str) -> str`, optional): a function to
      format the documentation for the attribute. It should accept the
      module name (eg `"transdoc.errors"`), the object name (eg
      `"TransformErrorInfo"`), and the attribute name (eg `"position"`), and
      should return text that will be used in place of the object. This can be
      used to generate Markdown links, or do other useful things. By default,
      a bullet point followed by the name of the attribute will be provided,
      for example `"* position"`.

    ## Returns

    `Callable[[str, Optional[str]], str]`

    A Transdoc rule function that filters the list of attributes using
    `filter` and formats the list of attributes using `formatter`.
    """
    def attributes(module: str, object: Optional[str]) -> str:
        return _attributes(module, object, filter=filter, formatter=formatter)

    return attributes

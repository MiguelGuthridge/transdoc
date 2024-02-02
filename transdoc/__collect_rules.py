"""
# Transdoc / Collect rules

Code for collecting rules from a module.
"""
from types import ModuleType
from .__rule import Rule


def collect_rules(module: ModuleType) -> dict[str, Rule]:
    """
    Collect rules from the given module

    Items are considered to be rules if they are callable, and if there is an
    `__all__` attribute in the module, if they are contained within it.
    """
    items = getattr(module, "__all__", dir(module))

    collected_rules = {}

    for item_name in items:
        item = getattr(module, item_name)
        if callable(item):
            collected_rules[item_name] = item

    return collected_rules

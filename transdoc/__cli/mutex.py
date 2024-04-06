"""
# Transdoc / CLI / Mutex

Mutually exclusive option for Click argument parser.
"""
import click


class Mutex(click.Option):
    """
    Click option variant that is not required if another parameter is given.

    Adapted from https://stackoverflow.com/a/51235564/6335363 (CC BY-SA 4.0)
    """

    def __init__(self, *args, **kwargs) -> None:
        self.mutex_with: list = kwargs.pop("mutex_with")

        assert self.mutex_with, "'mutex_with' parameter required"
        kwargs["help"] = (
            kwargs.get("help", "")
            + "Option is mutually exclusive with "
            + ", ".join(self.mutex_with) + "."
        ).strip()
        super(Mutex, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        current_opt = self.name in opts
        for mutex_opt in self.mutex_with:
            if mutex_opt in opts:
                if current_opt:
                    raise click.UsageError(
                        f"Illegal usage: option '{self.name}' is mutually "
                        f"exclusive with option '{mutex_opt}'.",
                        ctx,
                    )
                else:
                    self.required = False
        return super(Mutex, self).handle_parse_result(ctx, opts, args)

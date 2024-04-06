"""
# Transdoc / CLI / Main

Main entrypoint to the Transdoc CLI.
"""
import importlib.util
import os
import sys
import click
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Literal, overload
from types import ModuleType
from traceback import print_exception
import importlib
from .mutex import Mutex

from transdoc import VERSION, transform
from transdoc.errors import TransdocTransformationError
from transdoc.__collect_rules import collect_rules


def display_error_list(errors: list[str]) -> int:
    """
    Display errors and exit the program
    """
    print(f"Transdoc - v{VERSION}", file=sys.stderr)
    print("Invalid command-line arguments", file=sys.stderr)
    for e in errors:
        print(e, file=sys.stderr)

    return 2


def load_rule_file(rule_file: Path) -> ModuleType:
    """
    Load a rule file given its path
    """
    # https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
    module_name = f"transdoc.rules_temp.{rule_file.name.removesuffix('.py')}"

    spec = importlib.util.spec_from_file_location(module_name, rule_file)
    if spec is None:
        raise ImportError(f"Import spec for rule file '{rule_file}' was None")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module

    if spec.loader is None:
        raise ImportError(f"Spec loader for rule file '{rule_file}' was None")

    # Any exceptions this raises get caught by the calling code
    spec.loader.exec_module(module)

    return module


def report_transformation_error(
    file: Path,
    errors: TransdocTransformationError
):
    print(f"!!! {file}", file=sys.stderr)
    for e in errors.args:
        pos = e.position
        print_exception(e.error_info)
        err_str = f"{type(e.error_info).__name__}: {e.error_info}"
        print(
            f"    {str(pos.line):>4}:{str(pos.column):<3} {err_str}",
            file=sys.stderr,
        )


@dataclass
class FileMapping:
    input: Path
    output: Optional[Path]
    transform: bool


@overload
def cli(
    input: Path,
    rule_file: Path,
    output: Path,
    *,
    force: bool = False,
) -> int:
    ...


@overload
def cli(
    input: Path,
    rule_file: Path,
    *,
    dryrun: Literal[True],
) -> int:
    ...


@click.command("transdoc")
@click.argument(
    'input',
    type=click.Path(exists=True, path_type=Path),
    # help='Path to the input file or directory',
)
@click.option(
    '-r',
    '--rule-file',
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help='Path to any Python file/module containing rules for Transdoc to use',
)
@click.option(
    '-o',
    '--output',
    type=click.Path(exists=False, path_type=Path),
    help='Path to the output file or directory',
    cls=Mutex,
    mutex_with=["dryrun"],
)
@click.option(
    '-d',
    '--dryrun',
    is_flag=True,
    help="Don't produce any output files",
)
@click.option(
    '-f',
    '--force',
    is_flag=True,
    help='Forcefully overwrite the output file/directory',
    cls=Mutex,
    mutex_with=["dryrun"],
)
@click.version_option(VERSION)
def cli(
    input: Path,
    rule_file: Path,
    output: Optional[Path] = None,
    *,
    dryrun: bool = False,
    force: bool = False,
) -> int:
    """
    Main entrypoint to the program.
    """
    errors: list[str] = []
    file_mappings: list[FileMapping] = []
    if input.is_dir():
        for dirpath, _, filenames in os.walk(input):
            for filename in filenames:
                in_file = Path(dirpath).joinpath(filename)
                if output is None:
                    out_file = None
                else:
                    out_file = output.joinpath(in_file.relative_to(input))
                perform_transformation = in_file.suffix == ".py"
                file_mappings.append(FileMapping(
                    in_file,
                    out_file,
                    perform_transformation,
                ))
    else:
        if not input.suffix == ".py":
            errors.append(f"Input file '{input}' must be a Python file")
        file_mappings.append(FileMapping(input, output, True))

    if not force and not dryrun:
        assert output is not None
        if output.exists():
            if output.is_dir() and len(os.listdir(output)):
                errors.append(
                    f"Output directory '{output}' exists and is not empty")
            else:
                errors.append(f"Output location '{output}' already exists")

    if rule_file.suffix != ".py":
        errors.append(f"Rule file '{rule_file}' must be a Python file")

    try:
        rules = collect_rules(load_rule_file(rule_file))
    except Exception as e:
        errors.append(
            f"Error when importing rule file '{rule_file}':\n    {e}")

    if len(errors):
        return display_error_list(errors)

    encountered_errors = False

    for mapping in file_mappings:
        if not mapping.transform:
            if not dryrun:
                # Just copy from the input to the output
                with open(mapping.input, 'rb') as in_file:
                    assert mapping.output is not None
                    mapping.output.parent.mkdir(parents=True, exist_ok=True)
                    with open(mapping.output, 'wb') as out_file:
                        out_file.write(in_file.read())
            continue

        # Open file
        with open(mapping.input, encoding='utf-8') as in_file:
            try:
                in_text = in_file.read()
            except Exception as e:
                # FIXME
                encountered_errors = True
                print(e)

        # Transform the data
        try:
            result = transform(in_text, rules)
        except TransdocTransformationError as e:
            report_transformation_error(mapping.input, e)
            encountered_errors = True
            continue

        if not dryrun:
            assert mapping.output is not None
            # Write the result
            mapping.output.parent.mkdir(parents=True, exist_ok=True)
            with open(mapping.output, "w", encoding='utf-8') as out_file:
                out_file.write(result)

    if encountered_errors:
        return 1

    return 0

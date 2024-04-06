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
from typing import NoReturn
from types import ModuleType
from traceback import print_exception
import importlib
from .mutex import Mutex

from transdoc import VERSION, transform
from transdoc.errors import TransdocTransformationError
from transdoc.__collect_rules import collect_rules


def error_and_exit(errors: list[str]) -> NoReturn:
    """
    Display errors and exit the program
    """
    print(f"Transdoc - v{VERSION}", file=sys.stderr)
    print("Invalid command-line arguments", file=sys.stderr)
    for e in errors:
        print(e, file=sys.stderr)

    exit(2)


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
    output: Path
    transform: bool


@click.command()
@click.argument(
    'input',
    type=click.Path(exists=True, path_type=Path),
    # help='Path to the input file or directory',
)
@click.option(
    '-r',
    '--rule',
    type=click.Path(exists=True, path_type=Path),
    help='Path(s) to any Python files/modules containing rules for Transdoc',
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
def transdoc(input: Path, rule: Path, output: Path, dryrun: bool, force: bool):
    """
    Main entrypoint to the program.
    """
    errors: list[str] = []
    file_mappings: list[FileMapping] = []
    if input.is_dir():
        for dirpath, _, filenames in os.walk(input):
            for filename in filenames:
                in_file = Path(dirpath).joinpath(filename)
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
        if output.exists():
            if output.is_dir() and len(os.listdir(output)):
                errors.append(
                    f"Output directory '{output}' exists and is not empty")
            else:
                errors.append(f"Output location '{output}' already exists")

    if rule.suffix != ".py":
        errors.append(f"Rule file '{rule}' must be a Python file")

    try:
        rules = collect_rules(load_rule_file(rule))
    except Exception as e:
        errors.append(f"Error when importing rule file '{rule}':\n    {e}")

    if len(errors):
        error_and_exit(errors)

    encountered_errors = False

    for mapping in file_mappings:
        # Open file
        with open(mapping.input, encoding='utf-8') as in_file:
            in_text = in_file.read()

        # Transform the data
        try:
            result = transform(in_text, rules)
        except TransdocTransformationError as e:
            report_transformation_error(mapping.input, e)
            encountered_errors = True
            continue

        if not dryrun:
            # Write the result
            mapping.output.parent.mkdir(parents=True, exist_ok=True)
            with open(mapping.output, "w", encoding='utf-8') as out_file:
                out_file.write(result)

    if encountered_errors:
        exit(1)

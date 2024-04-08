"""
# Transdoc / CLI / Main

Main entrypoint to the Transdoc CLI.
"""
import click
from pathlib import Path
from typing import Optional
from .mutex import Mutex
from .main import main

from transdoc.__consts import VERSION


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
    return main(input, rule_file, output, dryrun=dryrun, force=force)

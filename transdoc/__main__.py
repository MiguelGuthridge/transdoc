"""
# Transdoc / main

Main entry-point to the transdoc executable.

Usage: transdoc [path] -o [output path] -r [path to rules module]
"""
from .__cli import cli


if __name__ == '__main__':
    cli()

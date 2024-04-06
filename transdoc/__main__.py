"""
# Transdoc / main

Main entry-point to the transdoc executable.

Usage: transdoc [path] -o [output path] -r [path to rules module]
"""
from .cli import transdoc


if __name__ == '__main__':
    transdoc()

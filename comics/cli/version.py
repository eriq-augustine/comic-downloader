"""
Get the version of this package.
"""

import argparse
import sys

import comics
import comics.cli.parser

def run_cli(args: argparse.Namespace) -> int:
    """ Run the CLI. """

    print(f"v{comics.__version__}")
    return 0

def main() -> int:
    """ Get a parser, parse the args, and call run. """

    return run_cli(_get_parser().parse_args())

def _get_parser() -> argparse.ArgumentParser:
    """ Get the parser. """

    return comics.cli.parser.get_parser(__doc__.strip(),
        include_net = False,
    )

if (__name__ == '__main__'):
    sys.exit(main())

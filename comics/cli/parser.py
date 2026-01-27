"""
Customize an argument parser.
"""

import argparse
import typing

import edq.core.argparser

import comics

CONFIG_FILENAME: str = 'comics-downloader.json'

def get_parser(description: str,
        include_net: bool = True,
        ) -> argparse.ArgumentParser:
    """
    Get an argument parser specialized for LMS Toolkit.
    """

    config_options = {
        'config_filename': CONFIG_FILENAME,
    }

    parser = edq.core.argparser.get_default_parser(
            description,
            version = f"v{comics.__version__}",
            include_net = include_net,
            config_options = config_options,
    )

    return typing.cast(argparse.ArgumentParser, parser)

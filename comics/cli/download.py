"""
Download comics by URL.
"""

import argparse
import sys

import edq.net.request

import comics.cli.parser
import comics.download

def run_cli(args: argparse.Namespace) -> int:
    """ Run the CLI. """

    # Set the HTTP timeout.
    edq.net.request._module_makerequest_options = {
        'timeout': 5.0,
    }

    total_missing_count = 0
    total_chapter_errors = 0

    for url in args.urls:
        result = comics.download.download(url, args.out_dir, dry_run = args.dry_run)

        print(result.comic)
        print("    Chapters:")

        missing_images = 0
        chapter_errors = 0

        for chapter_download_result in result.chapter_download_results:
            missing_images += chapter_download_result.missing_count()

            if (chapter_download_result.has_error()):
                chapter_errors += 1

            print(f"        {chapter_download_result}")
            for image_download_result in chapter_download_result.image_results:
                if (image_download_result.has_error()):
                    print(f"            {image_download_result.image} - {image_download_result.error_text()}")

        print(f"    Missing Count: {missing_images}, Chapter Errors: {chapter_errors}")

        total_missing_count += missing_images
        total_chapter_errors += chapter_errors

    print(f"\nTotal Missing Count: {total_missing_count}, Total Chapter Errors: {total_chapter_errors}")

    return min((total_missing_count + total_chapter_errors), 100)

def main() -> int:
    """ Get a parser, parse the args, and call run. """

    return run_cli(_get_parser().parse_args())

def _get_parser() -> argparse.ArgumentParser:
    """ Get the parser. """

    parser = comics.cli.parser.get_parser(__doc__.strip(),
        include_net = True,
    )

    parser.add_argument('urls', metavar = 'URLS',
        type = str, nargs = '+',
        help = 'URLs to download.',
    )

    parser.add_argument('--out-dir', dest = 'out_dir',
        action = 'store', type = str, default = '.',
        help = "Where the comics will be downloaded to (default: %(default)s).",
    )

    parser.add_argument('--dry-run', dest = 'dry_run',
        action = 'store_true', default = False,
        help = "Don't download anything (default: %(default)s).",
    )

    return parser

if (__name__ == '__main__'):
    sys.exit(main())

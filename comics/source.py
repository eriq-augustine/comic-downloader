import typing
import urllib.parse

import edq.util.pyimport

import comics.model

KNOWN_SOURCE_MODULES: typing.List[str] = [
    'comics.sources.coffeemanga_to',
]
"""
Source modules that we already know about.
Must have `get_urls()` and `get_source(url)` functions.
"""

_known_sources_loaded: bool = False  # pylint: disable=invalid-name

_sources: typing.Dict[str, comics.model.ComicSource] = {}

def lookup(url: str) -> typing.Union[comics.model.ComicSource, None]:
    """ Try to find a comic's source according to it's model. """

    if (not url.startswith('http')):
        url = f"http://{url}"

    parts = urllib.parse.urlparse(url)
    key = parts.hostname

    if (key is None):
        return None

    return _sources.get(key, None)

def register(url: str, source: comics.model.ComicSource) -> None:
    """ Register a source. """

    if (not url.startswith('http')):
        url = f"http://{url}"

    parts = urllib.parse.urlparse(url)
    key = parts.hostname

    if (key is None):
        raise ValueError(f"Unable to parse hostname from URL: '{url}'.")

    existing_source = _sources.get(key, None)
    if (existing_source is not None):
        raise ValueError(f"Cannot register source ('{source}'), found an existing source ('{existing_source}') at URL: '{url}'.")

    _sources[key] = source

def _register_known_sources() -> None:
    """ Register sources we already know about. """

    global _known_sources_loaded  # pylint: disable=global-statement

    if (_known_sources_loaded):
        return

    for known_source_module in KNOWN_SOURCE_MODULES:
        source_module = edq.util.pyimport.import_name(known_source_module)

        for url in source_module.get_urls():
            source = source_module.get_source(url)
            register(url, source)

    _known_sources_loaded = True

_register_known_sources()

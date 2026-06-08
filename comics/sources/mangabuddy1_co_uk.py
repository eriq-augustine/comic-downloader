import json
import re
import typing
import urllib.parse

import bs4
import edq.net.request
import edq.util.dirent
import edq.util.json

import comics.model

NAME: str = 'mangabuddy1.co_uk'
URLS: typing.List[str] = [
    'https://mangabuddy1.co.uk',
]

class ComicSource(comics.model.ComicSource):
    """ A source for mangabuddy.com. """

    def __init__(self) -> None:
        super().__init__(NAME)

    def get_info_from_url(self, url: str) -> comics.model.ComicInfo:
        _, text = edq.net.request.make_get(url, retries = self.retries)

        document = bs4.BeautifulSoup(text, 'html.parser')

        comic_data = None
        for script in document.select('script'):
            if (script.get('src', None) is not None):
                continue

            contents = script.get_text()

            if ('slug_hash:' not in contents):
                continue

            contents = re.sub(r'\s+', ' ', contents, flags = re.DOTALL)
            contents = re.sub(r'^[^{]+{', '{', contents)
            contents = re.sub(r'}[^}]+$', '}', contents)

            comic_data = edq.util.json.loads(contents)

        if (comic_data is None):
            raise ValueError(f"Unable to parse comic info from: '{url}'.")

        name = comic_data['title']
        source_id = comic_data['slug']

        # Fetch chapters.
        url_parts = urllib.parse.urlparse(url)
        chapters_url = f"{url_parts.scheme}://{url_parts.netloc}/get-chapter-list?slug={source_id}"
        _, raw_chapter_data = edq.net.request.make_get(chapters_url, retries = self.retries)
        chapters_data = edq.util.json.loads(raw_chapter_data)

        chapters = []
        for (i, chapter) in enumerate(reversed(chapters_data['data'])):
            chapters.append(comics.model.ComicChapter(
                url = f"{url_parts.scheme}://{url_parts.netloc}/series/{source_id}/{chapter['chapter_slug']}",
                index = i,
                source_id = chapter['chapter_slug'],
                name = chapter['chapter_name'],
            ))

        return comics.model.ComicInfo(url, name = name, source_id = source_id, chapters = chapters)

    def get_chapter_images(self, comic: comics.model.ComicInfo, chapter: comics.model.ComicChapter) -> typing.List[comics.model.ComicImage]:
        _, text = edq.net.request.make_get(chapter.url, retries = self.retries)

        document = bs4.BeautifulSoup(text, 'html.parser')

        images = []
        for (i, image) in enumerate(document.select('img[data-src]')):
            images.append(comics.model.ComicImage(image.get('data-src'), index = i))

        return images

def get_urls() -> typing.List[str]:
    """ Get URLs handled by these sources. """

    return URLS

def get_source(url: str) -> comics.model.ComicSource:
    """ Get a source for the given URL. """

    return ComicSource()

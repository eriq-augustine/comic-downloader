import re
import typing

import bs4
import edq.net.request
import edq.util.dirent

import comics.model

NAME: str = 'mangabuddy.com'
URLS: typing.List[str] = [
    'https://mangabuddy.com',
]

class ComicSource(comics.model.ComicSource):
    """ A source for mangabuddy.com. """

    def __init__(self) -> None:
        super().__init__(NAME)

    def get_info_from_url(self, url: str) -> comics.model.ComicInfo:
        _, text = edq.net.request.make_get(url, retries = self.retries)

        document = bs4.BeautifulSoup(text, 'html.parser')

        name = document.select('.book-info .name h1')[0].get_text()
        chapters = []

        # Note that chapters are provided in reverse order.
        for (i, element) in enumerate(reversed(document.select('ul.chapter-list > li > a'))):
            link = element.get('href', None)
            if (link is None):
                raise ValueError("Unable to locate chapter link.")

            chapter_name = element.get('title', None)
            if (chapter_name is not None):
                chapter_name = str(chapter_name)

            link = str(link)
            chapters.append(comics.model.ComicChapter(
                url = 'https://mangabuddy.com' + link,
                index = i,
                source_id = link,
                name = chapter_name,
            ))

        return comics.model.ComicInfo(url, name, chapters = chapters)

    def get_chapter_images(self, comic: comics.model.ComicInfo, chapter: comics.model.ComicChapter) -> typing.List[comics.model.ComicImage]:
        _, text = edq.net.request.make_get(chapter.url, retries = self.retries)

        match = re.search(r"\s*var\s+chapImages\s*=\s*'([^']+)'\s*", text)
        if (match is None):
            raise ValueError("Failed to parse out image data structure.")

        links = match.group(1).split(',')

        images = []
        for (i, link) in enumerate(links):
            images.append(comics.model.ComicImage(link, index = i))

        return images

def get_urls() -> typing.List[str]:
    """ Get URLs handled by these sources. """

    return URLS

def get_source(url: str) -> comics.model.ComicSource:
    """ Get a source for the given URL. """

    return ComicSource()

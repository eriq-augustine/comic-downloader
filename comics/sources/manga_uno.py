import typing

import edq.net.request
import edq.util.json

import comics.model

NAME: str = 'manga.uno'
URLS: typing.List[str] = [
    'https://manga.uno',
]

HEADERS: typing.Dict[str, str] = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:157.0) Gecko/20100101 Firefox/157.0',
}

class ComicSource(comics.model.ComicSource):
    """ A source for manga.uno. """

    def __init__(self) -> None:
        super().__init__(NAME)

    def get_info_from_url(self, url: str) -> comics.model.ComicInfo:
        slug = url.replace('https://manga.uno/m/', '')

        info_url = f"https://manga.uno/api/manga/{slug}"

        _, text = edq.net.request.make_get(info_url, retries = self.retries, headers = HEADERS)
        data = edq.util.json.loads(text)

        chapters = []
        for (i, chapter_info) in enumerate(reversed(data['chapters'])):
            name = None
            try:
                number = float(chapter_info['chapter_number'])
                if (number == int(number)):
                    name = f"Chapter {int(number):03d}"
                else:
                    name = f"Chapter {number:07.3f}"
            except ValueError:
                pass

            chapters.append(comics.model.ComicChapter(
                url = f"https://manga.uno/r/{data['manga']['slug']}/{chapter_info['id']}",
                index = i,
                source_id = str(chapter_info['id']),
                name = name,
            ))

        return comics.model.ComicInfo(url, name = data['manga']['title'], source_id = data['manga']['id'], chapters = chapters)

    def get_chapter_images(self, comic: comics.model.ComicInfo, chapter: comics.model.ComicChapter) -> typing.List[comics.model.ComicImage]:
        url = f"https://manga.uno/api/chapter/{chapter.source_id}"

        _, text = edq.net.request.make_get(url, retries = self.retries, headers = HEADERS)
        data = edq.util.json.loads(text)

        images = []
        for (i, image_url) in enumerate(data['pages']):
            images.append(comics.model.ComicImage(image_url, index = i))

        return images

def get_urls() -> typing.List[str]:
    """ Get URLs handled by these sources. """

    return URLS

def get_source(url: str) -> comics.model.ComicSource:
    """ Get a source for the given URL. """

    return ComicSource()

import json
import re
import typing

import bs4
import edq.net.request
import edq.util.dirent

import comics.model

NAME: str = 'coffeemanga.to.'
URLS: typing.List[str] = [
    'https://coffeemanga.to',
]

USER_AGENT: str = 'Mozilla/5.0 (X11; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0'

class ComicSource(comics.model.ComicSource):
    """ A source for coffeemanga.to. """

    def __init__(self) -> None:
        super().__init__(NAME)

    def get_info_from_url(self, url: str) -> comics.model.ComicInfo:
        _, text = edq.net.request.make_get(url, retries = self.retries)

        document = bs4.BeautifulSoup(text, 'html.parser')

        name = document.select('h1')[0].get_text()
        chapters = None
        next_action = None

        # Several script tags have information we need.
        for script_tag in document.select('script'):
            text = str(script_tag)

            if ('imagesCount' in text):
                chapters = self._parse_chapters_from_script(url, script_tag.get_text())
                continue

            match = re.search(r'src="(/_next/static/chunks/app/.*/series/.*/page-.*\.js)"', text)
            if (match is not None):
                next_action = self._fetch_next_action(match.group(1))
                continue

        if (next_action is None):
            raise ValueError("Unable to locate next_action information.")

        if (chapters is None):
            raise ValueError("Unable to locate chapter information.")

        return comics.model.ComicInfo(url, name, chapters = chapters, next_action = next_action)

    def _fetch_next_action(self, url_path: str) -> str:
        """ Make a request and collect the next action value. """

        url = f"https://coffeemanga.to{url_path}"

        _, text = edq.net.request.make_get(url, retries = self.retries)

        match = re.search(r'\("(\w+)",[^"]*callServer[^"]*"getChapterImages"\)', text)
        if (match is None):
            raise ValueError("Could not locate next action in text.")

        return match.group(1)

    def _parse_chapters_from_script(self, url: str, text: str) -> typing.List[comics.model.ComicChapter]:
        """ Parse chapter information out of a script tag. """

        matches = re.findall(r'\\"chapter\\":(\{[^\}]+\})', text)
        if ((matches is None) or (len(matches) == 0)):
            raise ValueError("Unable to parse out chapters.")

        chapters = []
        for (i, match) in enumerate(reversed(matches)):
            # Convert the JSON string to a JSON object.
            text = json.loads(f'"{match}"')
            data = json.loads(text)

            chapters.append(comics.model.ComicChapter(
                url = url,
                index = i,
                source_id = data['id'],
                name = str(data['chap']),
            ))

        return chapters

    def get_chapter_images(self, comic: comics.model.ComicInfo, chapter: comics.model.ComicChapter) -> typing.List[comics.model.ComicImage]:
        payload = f"[{chapter.source_id}]".encode(edq.util.dirent.DEFAULT_ENCODING)
        headers = {
            'Content-Type': 'text/plain;charset=UTF-8',
            'User-Agent': USER_AGENT,
            'Next-Action': comic.extra_info['next_action'],
        }

        _, text = edq.net.request.make_post(comic.url, data = payload, headers = headers, retries = self.retries)

        match = re.search(r'\s*1:(\[.+\])\s*', text)
        if (match is None):
            raise ValueError("Failed to parse out image data structure.")

        data = json.loads(match.group(1))

        images = []
        for (i, row) in enumerate(data):
            images.append(comics.model.ComicImage(row['src'], index = i))

        return images

def get_urls() -> typing.List[str]:
    """ Get URLs handled by these sources. """

    return URLS

def get_source(url: str) -> comics.model.ComicSource:
    """ Get a source for the given URL. """

    return ComicSource()

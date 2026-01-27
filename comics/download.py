import logging
import os
import typing

import edq.net.request
import edq.util.dirent

import comics.model
import comics.source

_logger = logging.getLogger(__name__)

def download(
        comic_url: str,
        base_dir: str,
        stop_on_chapter_error: bool = False,
        overwrite: bool = False,
        dry_run: bool = False,
        ) -> comics.model.DownloadResult:
    """ Download a comic by URL. """

    _logger.info("Fetching comic for '%s'.", comic_url)

    source = comics.source.lookup(comic_url)
    if (source is None):
        raise ValueError(f"Could not find a matching source for '{comic_url}'.")

    comic = source.get_info_from_url(comic_url)

    comic_out_dir = os.path.join(base_dir, comic.name)
    if (not dry_run):
        edq.util.dirent.mkdir(comic_out_dir)

    _logger.info("Downloading '%s' to '%s'.", comic, comic_out_dir)

    chapter_download_results: typing.List[comics.model.ChapterDownloadResult] = []

    for chapter in comic.chapters:
        _logger.info("Fetching images for '%s' chapter '%s'.", comic, chapter)

        chapter_out_dir = os.path.join(comic_out_dir, str(chapter))
        if (not dry_run):
            edq.util.dirent.mkdir(chapter_out_dir)

        chapter_download_result = comics.model.ChapterDownloadResult(chapter, chapter_out_dir)
        chapter_download_results.append(chapter_download_result)

        try:
            images = source.get_chapter_images(comic, chapter)
        except Exception as ex:
            _logger.error("Failed for get images for '%s' chapter '%s'.", comic, chapter, exc_info = ex)
            chapter_download_result.error = "Failed to fetch chapter images."
            chapter_download_result.exception = ex

            if (stop_on_chapter_error):
                raise ex

            continue

        _logger.debug("Downloading images for '%s' chapter '%s' to '%s'.", comic, chapter, chapter_out_dir)

        wait_required = False
        for image in images:
            out_path = os.path.join(chapter_out_dir, str(image))

            image_download_result = comics.model.ImageDownloadResult(image, out_path)
            chapter_download_result.image_results.append(image_download_result)

            if (wait_required):
                source.image_wait()

            wait_required = False

            _logger.debug("Downloading image to '%s'.", out_path)

            if ((not overwrite) and os.path.exists(out_path)):
                _logger.debug("Image already exists, skipping: '%s'.", out_path)
                image_download_result.already_exists = True
                continue

            if (dry_run):
                continue

            try:
                response, _ = edq.net.request.make_get(image.url, retries = comics.model.DEFAULT_RETRIES)
                image_download_result.downloaded = True
                wait_required = True
            except Exception as ex:
                _logger.error("Failed for get image: '%s'.", image.url, exc_info = ex)
                image_download_result.error = 'Failed to fetch image.'
                image_download_result.exception = ex

                if (stop_on_chapter_error):
                    raise ex

                continue

            edq.util.dirent.write_file_bytes(out_path, response.content)

    return comics.model.DownloadResult(comic, comic_out_dir, chapter_download_results)

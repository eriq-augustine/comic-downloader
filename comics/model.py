import abc
import os
import time
import typing

DEFAULT_IMAGE_WAIT_SECS: float = 0.25

DEFAULT_RETRIES: int = 3

class ComicImage:
    """ Information about an image that appears in a comic chapter. """

    def __init__(self,
            url: str,
            extension: typing.Union[str, None] = None,
            index: int = 0,
            source_id: typing.Union[str, None] = None,
            name: typing.Union[str, None] = None,
            ) -> None:
        self.url: str = url
        """
        URL that points to this image.
        """

        if (extension is None):
            extension = os.path.splitext(url)[-1]

        self.extension: str = extension
        """ The file extension for this image. """

        self.index: int = index
        """
        The ordering for this image within the chapter (according to the source).
        """

        self.source_id: typing.Union[str, None] = source_id
        """ An ID for this image provided by the source. """

        self.name: typing.Union[str, None] = name
        """
        The name of this image (if provided).
        Should not include file extension.
        """

    def __repr__(self) -> str:
        if (self.name is not None):
            return f"{self.name}{self.extension}"

        if (self.source_id is not None):
            return f"{self.source_id}{self.extension}"

        return f"{self.index:03d}{self.extension}"

class ImageDownloadResult:
    """ Information about an image's download status. """

    def __init__(self,
            image: ComicImage,
            out_path: str,
            downloaded: bool = False,
            already_exists: bool = False,
            error: typing.Union[str, None] = None,
            exception: typing.Union[Exception, None] = None,
            ) -> None:
        self.image: ComicImage = image
        """ The target of the download. """

        self.out_path: str = out_path
        """ Where the image was written. """

        self.downloaded: bool = downloaded
        """ If the image was actually downloaded. """

        self.already_exists: bool = already_exists
        """ If the image already exists. """

        self.error: typing.Union[str, None] = error
        """ A text describing any error that occurred. """

        self.exception: typing.Union[Exception, None] = exception
        """ Any exception that was thrown. """

    def has_error(self) -> bool:
        """ Check if this image download had any type of error. """

        return ((self.error is not None) or (self.exception is not None))

    def error_text(self) -> str:
        """ Get a textual representation of the error for this download, or an empty string if there was no error. """

        if ((self.error is not None) or (self.exception is not None)):
            return f"{self.error} - {self.exception}"

        if (self.error is not None):
            return self.error

        if (self.exception is not None):
            return str(self.exception)

        return ''

class ComicChapter:
    """ Information about a comic's chapter. """

    def __init__(self,
            url: str,
            index: int = 0,
            source_id: typing.Union[str, None] = None,
            name: typing.Union[str, None] = None,
            ) -> None:
        self.url: str = url
        """
        URL that points to this chapter.
        For some sources, this could point to the comic (and not a specific chapter).
        """

        self.index: int = 0
        """
        The ordering for this chapter within the comic (according to the source).
        In an ideal world, this would indicate the reading order,
        but not all sources are well organized.
        """

        self.source_id: typing.Union[str, None] = source_id
        """ An ID for this chapter provided by the source. """

        self.name: typing.Union[str, None] = name
        """ The name of this chapter (if provided). """

    def __repr__(self) -> str:
        if (self.name is not None):
            return self.name

        if (self.source_id is not None):
            return self.source_id

        return f"{self.index:03d}"

class ChapterDownloadResult:
    """ Information about a chapter's download status. """

    def __init__(self,
            chapter: ComicChapter,
            out_path: str,
            image_results: typing.Union[typing.List[ImageDownloadResult], None] = None,
            error: typing.Union[str, None] = None,
            exception: typing.Union[Exception, None] = None,
            ) -> None:
        self.chapter: ComicChapter = chapter
        """ The target of the download. """

        self.out_path: str = out_path
        """ Where the chapter is downloaded to. """

        if (image_results is None):
            image_results = []

        self.image_results: typing.List[ImageDownloadResult] = image_results
        """ The image download results. """

        self.error: typing.Union[str, None] = error
        """ A text describing any error that occurred. """

        self.exception: typing.Union[Exception, None] = exception
        """ Any exception that was thrown. """

    def missing_count(self) -> int:
        """ Get a count of the images that are missing (not downloaded or pre-existing). """

        count = 0
        for image_result in self.image_results:
            if (image_result.downloaded or image_result.already_exists):
                count += 1

        return (len(self.image_results) - count)

    def has_error(self) -> bool:
        """ Check if this image download had any type of error. """

        return ((self.error is not None) or (self.exception is not None))

    def error_text(self) -> str:
        """ Get a textual representation of the error for this download, or an empty string if there was no error. """

        if ((self.error is not None) or (self.exception is not None)):
            return f"{self.error} - {self.exception}"

        if (self.error is not None):
            return self.error

        if (self.exception is not None):
            return str(self.exception)

        return ''

    def __repr__(self) -> str:
        if (self.has_error()):
            return f"{self.chapter} - Error: {self.error_text()}"

        downloaded = 0
        errors = 0
        already_exists = 0

        for image_result in self.image_results:
            if (image_result.downloaded):
                downloaded += 1

            if (image_result.has_error()):
                errors += 1

            if (image_result.already_exists):
                already_exists += 1

        return f"{self.chapter} - Images: {len(self.image_results)}, Downloads: {downloaded}, Errors: {errors}, Already Exists: {already_exists}"

class ComicInfo:
    """ Information about a comic for the purposes of downloading. """

    def __init__(self,
            url: str,
            name: str,
            source_id: typing.Union[str, None] = None,
            chapters: typing.Union[typing.List[ComicChapter], None] = None,
            **kwargs: typing.Any) -> None:
        self.url = url
        """ The URL of this comic in the source. """

        self.name: str = name
        """ The name of this comic (if provided). """

        self.source_id: typing.Union[str, None] = source_id
        """ An ID for this comic provided by the source. """

        if (chapters is None):
            chapters = []

        self.chapters: typing.List[ComicChapter] = chapters
        """ The chapters for this comic. """

        self.extra_info: typing.Dict[str, typing.Any] = kwargs
        """ Any additional info set by the source. """

    def __repr__(self) -> str:
        text = self.name

        if (self.source_id is not None):
            text += f" ({self.source_id})"

        return text

class DownloadResult:
    """ The result of downloading a comic. """

    def __init__(self,
            comic: ComicInfo,
            out_dir: str,
            chapter_download_results: typing.List[ChapterDownloadResult],
            ) -> None:
        self.comic: ComicInfo = comic
        """ The target comic. """

        self.out_dir: str = out_dir
        """ The directory this comic was downloaded to. """

        self.chapter_download_results: typing.List[ChapterDownloadResult] = chapter_download_results
        """
        Information about the status of images for each chapter.
        """

class ComicSource(abc.ABC):
    """ An abstraction for a source that comics can be download from. """

    def __init__(self,
            name: str,
            image_wait_secs: float = DEFAULT_IMAGE_WAIT_SECS,
            retries: int = DEFAULT_RETRIES,
            ) -> None:
        self.name = name
        """ A display name for this source. """

        self.image_wait_secs: float = image_wait_secs
        """ How long to wait between image requests. """

        self.retries: int = retries
        """ The number of times to retry a request. """

    def __repr__(self) -> str:
        return self.name

    def image_wait(self) -> None:
        """ A courtesy wait between downloading images. """

        time.sleep(self.image_wait_secs)

    @abc.abstractmethod
    def get_info_from_url(self, url: str) -> ComicInfo:
        """ Get a comic's info from the URL for the comic. """

    @abc.abstractmethod
    def get_chapter_images(self, comic: ComicInfo, chapter: ComicChapter) -> typing.List[ComicImage]:
        """ Get the images that make up a chapter. """

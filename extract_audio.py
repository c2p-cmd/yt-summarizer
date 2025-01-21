from logging import getLogger
from typing import Generator, Optional
from models import YTResult
import yt_dlp

logger = getLogger(__name__)


def __get_audio(result: YTResult) -> Optional[YTResult]:
    try:
        with open(f"output/{result.id}.m4a", "rb") as f:
            return result
    except FileNotFoundError:
        return None


def __my_hook(d):
    if d["status"] == "error":
        logger.info("Error downloading video")
    elif d["status"] == "downloading":
        downloaded_bytes = d.get("downloaded_bytes", 0)
        total_bytes_estimate = d.get("total_bytes_estimate", 1)
        percent = downloaded_bytes / total_bytes_estimate * 100
        logger.info(f"Downloaded {percent:.2f}%")
    elif d["status"] == "finished":
        logger.info("Download finished")


def __get_options():
    return {
        "format": "m4a/bestaudio/best",
        "outtmpl": "output/%(id)s.%(ext)s",
        "progress_hooks": [__my_hook],
    }


def extract_info(link: str) -> YTResult:
    with yt_dlp.YoutubeDL(__get_options()) as ydl:
        info = ydl.extract_info(link, download=False)
        info_dict = ydl.sanitize_info(info)

        return YTResult(
            id=info_dict["id"],
            title=info_dict["title"],
            thumbnail_link=info_dict["thumbnail"],
            uploader=info_dict["uploader"],
        )


def simple_download_audio_from_youtube(link: str) -> YTResult:
    with yt_dlp.YoutubeDL(__get_options()) as ydl:
        info = ydl.extract_info(link, download=False)
        info_dict = ydl.sanitize_info(info)

        res = YTResult(
            id=info_dict["id"],
            title=info_dict["title"],
            thumbnail_link=info_dict["thumbnail"],
            uploader=info_dict["uploader"],
        )

        local_link = __get_audio(res)
        if local_link:
            return res

        error_code = ydl.download([link])

        res.error_code = error_code
        return res


def download_audio_from_youtube(link: str) -> Generator[YTResult, None, None]:
    with yt_dlp.YoutubeDL(__get_options()) as ydl:
        info = ydl.extract_info(link, download=False)
        info_dict = ydl.sanitize_info(info)

        # Yield video metadata
        yield YTResult(
            id=info_dict["id"],
            title=info_dict["title"],
            thumbnail_link=info_dict["thumbnail"],
            uploader=info_dict["uploader"],
        )

        # Start downloading and yield progress updates
        error_code = ydl.download([link])

        yield YTResult(
            id=info_dict["id"],
            title=info_dict["title"],
            thumbnail_link=info_dict["thumbnail"],
            uploader=info_dict["uploader"],
            error_code=error_code,
        )


# Example Usage
if __name__ == "__main__":
    yt_link = "https://www.youtube.com/watch?v=vf7bI5nZyi8"
    for update in download_audio_from_youtube(yt_link):
        logger.info(f"Video Info: {update}")

from pydantic import BaseModel
from typing import Generator, Optional
import yt_dlp


class YTRequest(BaseModel):
    link: str


class YTResult(BaseModel):
    id: str
    title: str
    thumbnail_link: str
    uploader: str
    error_code: Optional[int] = None


def __my_hook(d):
    if d["status"] == "error":
        print("Error downloading video")
    elif d["status"] == "downloading":
        downloaded_bytes = d.get("downloaded_bytes", 0)
        total_bytes_estimate = d.get("total_bytes_estimate", 1)
        percent = downloaded_bytes / total_bytes_estimate * 100
        print(f"Downloaded {percent:.2f}%")
    elif d["status"] == "finished":
        print("Download finished")


def __get_options():
    return {
        "format": "m4a/bestaudio/best",
        "outtmpl": "output/%(title)s.%(ext)s",
        "progress_hooks": [__my_hook],
    }


def simple_download_audio_from_youtube(link: str) -> YTResult:
    with yt_dlp.YoutubeDL(__get_options()) as ydl:
        info = ydl.extract_info(link, download=True)
        info_dict = ydl.sanitize_info(info)
        error_code = ydl.download([link])

        return YTResult(
            id=info_dict["id"],
            title=info_dict["title"],
            thumbnail_link=info_dict["thumbnail"],
            uploader=info_dict["uploader"],
            error_code=error_code,
        )


def download_audio_from_youtube(
    link: str,
) -> Generator[YTResult, None, None]:
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
    link = "https://www.youtube.com/watch?v=vf7bI5nZyi8"
    for update in download_audio_from_youtube(link):
        print(f"Video Info: {update}")

from typing import Optional

from pydantic import BaseModel, Field


class YTRequest(BaseModel):
    yt_link: str = Field(description="The YouTube video link to be processed")


class YTResult(BaseModel):
    id: str = Field(description="The YouTube video ID")
    title: str = Field(description="The YouTube video title")
    thumbnail_link: str = Field(description="The YouTube video thumbnail link")
    uploader: str = Field(description="The YouTube video uploader")
    error_code: Optional[int] = Field(description="The error code if any", default=None)

    def get_local_file_path(self) -> str:
        return f"output/{self.id}.m4a"


class YTResultWithTranscript(YTResult):
    transcript: str = Field(description="The YouTube video transcript")

    def model_outputs(self) -> list:
        return [
            self.id,
            self.title,
            self.thumbnail_link,
            self.uploader,
            self.transcript,
        ]

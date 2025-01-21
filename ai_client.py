from dotenv import load_dotenv
import os
import google.generativeai as genai
from typing import Generator
from logging import getLogger

logger = getLogger(__name__)


class Gemini:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key is None:
            raise ValueError("GEMINI_API_KEY is not set in the environment variables")
        genai.configure(api_key=api_key)

        # Create the model
        self.generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=self.generation_config,
        )

    def generate_text(
        self, local_file: str, id: str, uploader: str
    ) -> Generator[str, None, None]:
        responses = self.model.generate_content(
            [
                {
                    "role": "user",
                    "parts": [
                        self.__upload_to_gemini(
                            id=id, path=local_file, mime_type="audio/m4a"
                        ),
                        f"""
Summarize the audio's content to sound like a podcast.\n
Add fun facts to the summary too.\n
The uploader of the audio is the following: {uploader}\n
Add a nice title to the summary too.\n
""",
                    ],
                },
            ],
            stream=True,
        )
        for response in responses:
            yield response.text

    def __upload_to_gemini(self, id: str, path: str, mime_type=None) -> str:
        """Uploads the given file to Gemini.

        See https://ai.google.dev/gemini-api/docs/prompting_with_media
        """
        file = genai.upload_file(
            path,
            mime_type=mime_type,
        )
        logger.info(f"Uploaded file '{file.display_name}' as: {file.uri}")
        return file


if __name__ == "__main__":
    from extract_audio import simple_download_audio_from_youtube

    gemini = Gemini()
    yt_link = input("Enter YouTube link: ")
    yt_res = simple_download_audio_from_youtube(yt_link)

    for chunk in gemini.generate_text(
        yt_res.get_local_file_path(), yt_res.id, yt_res.uploader
    ):
        print(chunk)

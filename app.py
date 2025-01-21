from ai_client import Gemini
from extract_audio import simple_download_audio_from_youtube
from models import YTResultWithTranscript
import gradio as gr

gemini = Gemini()


def summarize_audio(youtube_link: str):
    yt_res = simple_download_audio_from_youtube(youtube_link)
    yt_transcript = YTResultWithTranscript(
        **yt_res.model_dump(), transcript="This is a transcript of the audio."
    )
    for chunk in gemini.generate_text(
        yt_res.get_local_file_path(),
        yt_res.id,
        yt_res.uploader,
    ):
        yt_transcript.transcript += chunk
        yield yt_transcript.model_dump().values()


demo = gr.Interface(
    fn=summarize_audio,
    inputs="text",
    outputs=[
        # id
        gr.Textbox(),
        # title
        gr.Textbox(),
        # thumbnail_link
        gr.Image(type='filepath'),
        # uploader
        gr.Textbox(),
        # error_code
        gr.Textbox(),
        # transcript
        gr.TextArea(),
    ],
    title="Summarize Audio",
    description="Summarize the content of an audio from a YouTube link.",
)

demo.launch()

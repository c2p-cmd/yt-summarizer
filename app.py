from ai_client import Gemini
from extract_audio import simple_download_audio_from_youtube
from models import YTResultWithTranscript
import gradio as gr
import os

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
        yield yt_transcript.model_outputs()


demo = gr.Interface(
    fn=summarize_audio,
    inputs=gr.Textbox(label="YouTube Link"),
    outputs=[
        gr.Textbox(lines=1, label="ID"),
        # title
        gr.Textbox(lines=1, label="Title"),
        # thumbnail_link
        gr.Image(label="Thumbnail Link", type='filepath', show_download_button=True),
        # uploader
        gr.Textbox(lines=1, label="Uploader"),
        # transcript
        gr.Markdown(label="Transcript", show_copy_button=True),
    ],
    title="Summarize Audio",
    description="Summarize the content of an audio from a YouTube link.",
    flagging_mode="never",
    api_name="summarize",
)


def auth_handler(usr, pwd) -> bool:
    username = os.environ.get("USERNAME")
    password = os.environ.get("PASSWORD")
    return usr == username and pwd == password


demo.launch(auth=auth_handler, pwa=True)

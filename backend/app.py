from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from extract_audio import (
    simple_download_audio_from_youtube,
    download_audio_from_youtube,
    YTResult,
    YTRequest,
)
from gemini import Gemini
import logging

app = FastAPI()
gemini = Gemini()


# health check at /
@app.get("/")
def read_root():
    return {"status": "ok"}


# POST /download
@app.post("/simple_summary")
def extract_audio_from_youtube(request: YTRequest) -> JSONResponse:
    try:
        res = simple_download_audio_from_youtube(request.link)
        error = res.error_code
        if error != 0:
            return JSONResponse(
                status_code=400, content={"error": "Failed to download audio"}
            )
        summary = gemini.generate_text(f"output/{res.title}.m4a")
        return JSONResponse(
            status_code=200,
            content={
                "info": res.model_dump(),
                "summary": summary,
            },
        )
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


# POST /summarize
@app.post("/summarize")
def summarize(link: str) -> StreamingResponse:
    try:
        res = None
        error = None

        # Download audio from YouTube
        for response in download_audio_from_youtube(link):
            if isinstance(response, YTResult):
                res = response
            else:
                error = response
        
        if error != 0 or not res:
            logging.error("Error downloading audio from YouTube")
            return JSONResponse(
                status_code=400, content={"error": "Failed to download audio"}
            )

        file_path = f"output/{res.title}.m4a"
        # Define the streaming generator
        def gemini_stream():
            try:
                for chunk in gemini.generate_text_streaming(file_path):
                    yield chunk
            except Exception as e:
                logging.error(f"Error in Gemini streaming: {e}")
                yield f"Error: {str(e)}\n"

        return StreamingResponse(gemini_stream(), media_type="text/plain")
    except Exception as e:
        logging.error(f"Unexpected error in /summarize: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True, workers=2)

from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from extract_audio import (
    simple_download_audio_from_youtube,
    download_audio_from_youtube,
    YTRequest,
)
from gemini import Gemini
import logging

logger = logging.getLogger(__name__)

app = FastAPI()
gemini = Gemini()


# health check at /
@app.get("/")
def read_root():
    return {
        "status": "ok",
    }


# POST /download
@app.post("/simple_summary")
def extract_audio_from_youtube(request: YTRequest) -> JSONResponse:
    try:
        res = simple_download_audio_from_youtube(request.link)
        error = res.error_code
        if error != 0:
            return JSONResponse(
                status_code=400,
                content={
                    "error": f"Failed to download audio with error code: {error}",
                },
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
        return JSONResponse(
            status_code=400,
            content={
                "error": str(e),
            },
        )


# POST /summarize
@app.post("/summarize")
def summarize(req: YTRequest) -> StreamingResponse:
    try:
        print(req)
        res = None
        error = None

        # Download audio from YouTube
        for response in download_audio_from_youtube(req.link):
            res = response
            error = res.error_code

        if error is not None and error != 0 or res is None:
            logger.error("Error downloading audio from YouTube")
            return JSONResponse(
                status_code=400, content={"error": "Failed to download audio"}
            )

        file_path = f"output/audio.m4a"

        # Define the streaming generator
        def gemini_stream():
            try:
                for chunk in gemini.generate_text_streaming(local_file=file_path, id=res.id):
                    yield chunk
            except Exception as e:
                logger.error(f"Error in Gemini streaming: {e}")
                yield f"Error: {str(e)}\n"

        return StreamingResponse(gemini_stream(), media_type="text/plain")
    except Exception as e:
        print(f"Unexpected error in /summarize: {e}")
        logger.error(f"Unexpected error in /summarize: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


if __name__ == "__main__":
    import sys
    import uvicorn

    # provide mode as argument: python app.py debug
    if len(sys.argv) <= 1:
        logger.error("Provide mode as argument: python app.py debug")
        sys.exit(-1)

    arg = sys.argv[1].lower()
    if arg == "debug" or arg == "prod":
        debug = arg == "debug"
        logger.info(f"Starting server in arg mode")
        uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=debug, workers=2)
    else:
        logger.error("Invalid mode argument, give either 'debug' or 'prod'")
        sys.exit(-1)

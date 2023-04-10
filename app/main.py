import json
import os

import uvicorn
from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional
import whisper
from speech_processing.audio import make_srt_subtitles
from pathlib import Path
from os.path import dirname, abspath, join as join_path, splitext
import shutil
from dotenv import load_dotenv
import time

load_dotenv()

DOWNLOAD_DIR = 'download'
ABS_DIR = dirname(abspath(__file__))
PROJECT_DIR_TO_DOWNLOAD_FILE = join_path(ABS_DIR, DOWNLOAD_DIR)
print(PROJECT_DIR_TO_DOWNLOAD_FILE)
ALLOWED_EXTENSIONS = {'mp3', 'flac', 'wav'}

app = FastAPI()
app.mount("/files", StaticFiles(directory=PROJECT_DIR_TO_DOWNLOAD_FILE), name="files")
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.get("/")
async def root():
    return {"message": "SubLan API"}


@app.get('/get-subtitles-file')
async def get_file():
    file_path = f'{PROJECT_DIR_TO_DOWNLOAD_FILE}/subtitles.srt'
    return FileResponse(file_path)


@app.post('/download-subtitle')
async def download_subtitle(request: Request, file: UploadFile = File(), model_type: str = "tiny",
                            timestamps: Optional[str] = Form("False"), file_name: str = "subtitles",
                            file_type: str = "srt"):
    start_time = time.time()
    # file extension processing
    if not allowed_file(file.filename):
        return {"error": "Invalid file extension"}
    file_extension = splitext(file.filename)[1]
    audio_file_url = f"audio{file_extension}"
    ##

    # file server processing
    try:
        with open(join_path(PROJECT_DIR_TO_DOWNLOAD_FILE, audio_file_url), 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
    except:
        print("error")
        pass
    ##

    # Load the model and transcribe the audio
    audio_file = whisper.load_audio(join_path(PROJECT_DIR_TO_DOWNLOAD_FILE, audio_file_url))
    model = whisper.load_model(model_type.lower())
    result = model.transcribe(audio=audio_file, fp16=False)
    ##

    # Create the subtitle file
    subtitle_file = join_path(PROJECT_DIR_TO_DOWNLOAD_FILE, f"{file_name}.{file_type}")
    transcribe = ""
    if file_type == "srt":
        with open(subtitle_file, "w", encoding='utf-8') as f:
            if timestamps:
                tmp = make_srt_subtitles(result["segments"])
                transcribe = tmp
                f.write(tmp)
            else:
                transcribe = result["text"]
                f.write(result["text"])
    elif file_type == "txt":
        with open(subtitle_file, "w", encoding='utf-8') as f:
            transcribe = result["text"]
            f.write(result["text"])

    else:
        raise TypeError("Invalid file type")
    print("It takes %s seconds" % (time.time() - start_time))
    return JSONResponse({
        "text": result["text"],
        "transcribe": transcribe
    })


if __name__ == "__main__":
    PORT = 3000 if not os.getenv("PORT") else int(os.getenv("PORT"))
    print(f"Server is running on port: {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)

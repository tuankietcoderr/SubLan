import uvicorn
from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import whisper
from speech_processing.audio import make_srt_subtitles
from pathlib import Path
from os.path import dirname, abspath, join as join_path, splitext
import shutil
from pydantic import BaseModel

import time
app = FastAPI()

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

DOWNLOAD_DIR = 'download'
ABS_DIR = dirname(abspath(__file__))
PROJECT_DIR_TO_DOWNLOAD_FILE = join_path(ABS_DIR, DOWNLOAD_DIR)

ALLOWED_EXTENSIONS = {'mp3', 'flac', 'wav'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.get("/")
async def root():
    return {"message": "SubLan API"}


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
    model = whisper.load_model(model_type)
    result = model.transcribe(audio=audio_file, fp16=False)
    ##

    # Create the subtitle file
    subtitle_file = join_path(PROJECT_DIR_TO_DOWNLOAD_FILE,f"{file_name}.{file_type}")
    if file_type == "srt":
        with open(subtitle_file, "w", encoding='utf-8') as f:
            if timestamps:
                f.write(make_srt_subtitles(result["segments"]))
            else:
                f.write(result["text"])
    elif file_type == "txt":
        with open(subtitle_file, "w", encoding='utf-8') as f:
                f.write(result["text"])
    else:
        raise TypeError("Invalid file type")

    # Create a streaming response with the file
    path = Path(subtitle_file)
    media_type = "application/octet-stream"
    response = StreamingResponse(path.open('rb'), media_type=media_type,
                                 headers={'Content-Disposition': f'attachment;filename={file_name}.{file_type}'})
    print("It takes %s seconds" % (time.time() - start_time))
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
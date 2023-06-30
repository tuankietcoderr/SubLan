import os
import uvicorn
from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from speech_processing.audio import speech_processing
from os.path import join as join_path, splitext
from constants.directory import PROJECT_DIR_TO_DOWNLOAD_FILE, YOUTUBE_DOWNLOAD_FILE_NAME, ALLOWED_EXTENSIONS
import shutil
from dotenv import load_dotenv
from pytube import YouTube
import moviepy.editor as mp
from enum import Enum
import warnings
warnings.filterwarnings("ignore")

load_dotenv()

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


class FileType(str, Enum):
    srt = "srt"
    txt = "txt"


class ModelType(str, Enum):
    tiny = "tiny"
    base = "base"
    small = "small"
    medium = "medium"
    # Higher CPU
    large = "large"
    large_v2 = "large-v2"


@app.post('/download-subtitle-by-file')
async def download_subtitle_by_file(file: UploadFile = File(),
                                    model_type: ModelType = Query(ModelType.tiny, title="Model type"),
                                    timestamps: bool = True, file_name: str = "subtitles",
                                    file_type: FileType = Query(FileType.srt, title="File type")):
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
            buffer.close()
    except FileNotFoundError as e:
        print(e)
        raise
    ##
    try:
        result, transcribe, transcribe_arr = speech_processing(model_type=model_type, timestamps=timestamps, file_type=file_type,
                                               file_name=file_name, audio_path=audio_file_url)
        return JSONResponse({
            "text": result["text"],
            "transcribe": transcribe,
            "language": result["language"],
            "transcribe_arr": transcribe_arr
        })
    except OSError as e:
        print(e)
        raise


@app.post("/youtube-to-mp3")
async def youtube_to_mp3(youtube_url: str):
    try:
        # Download the video using pytube
        youtube = YouTube(youtube_url)
        video = youtube.streams.get_lowest_resolution()
        file_size = video.filesize_mb
        print(file_size)
        # Check the video size
        if file_size > 20:
            raise JSONResponse({
                "message": "File too large, must be less then 10MB!"
            })
        # download it to local
        video.download()

        # Convert the video to audio using moviepy
        video_path = video.default_filename
        clip = mp.VideoFileClip(video_path)
        clip.audio.write_audiofile(join_path(PROJECT_DIR_TO_DOWNLOAD_FILE, YOUTUBE_DOWNLOAD_FILE_NAME))

        # Delete the video file
        clip.close()
        os.remove(video_path)
        return JSONResponse({
            "message": "Upload successfully!",
            "file_url": "/files/" + YOUTUBE_DOWNLOAD_FILE_NAME
        })
    except OSError as e:
        print(e)
        raise


@app.get("/download-subtitle-by-youtube-url")
async def download_subtitle_by_file(model_type: ModelType = Query(ModelType.tiny, title="Model type"),
                                    file_name: str = "subtitles",
                                    file_type: FileType = Query(FileType.srt, title="File type"),
                                    timestamps: bool = True):
    # Load the model and transcribe the audio
    result, transcribe, transcribe_arr = speech_processing(model_type=model_type, file_type=file_type, timestamps=timestamps,
                                           file_name=file_name, audio_path=YOUTUBE_DOWNLOAD_FILE_NAME)
    return JSONResponse({
        "text": result["text"],
        "transcribe": transcribe,
        "language": result["language"],
        "transcribe_arr": transcribe_arr
    })


if __name__ == "__main__":
    PORT = 8000 if not os.getenv("PORT") else int(os.getenv("PORT"))
    print(f"Server is running on port: {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)

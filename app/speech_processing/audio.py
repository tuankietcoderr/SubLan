from datetime import timedelta
import srt
import whisper
from os.path import dirname, abspath, join as join_path

DOWNLOAD_DIR = 'download'
ABS_DIR = dirname(abspath(__file__))
PROJECT_DIR_TO_DOWNLOAD_FILE = join_path(ABS_DIR, DOWNLOAD_DIR).replace("\\speech_processing", "")
ALLOWED_EXTENSIONS = {'mp3', 'flac', 'wav'}
YOUTUBE_DOWNLOAD_FILE_NAME = "youtube_download.mp3"


def transcribe_time_stamps(segments: list):
    string = ""
    for seg in segments:
        string += " ".join([str(seg["start"]), "->", str(seg["end"]), ": ", seg["text"].strip(), "\n"])
    return string


def make_srt_subtitles(segments: list):
    subtitles = []
    for i, seg in enumerate(segments, start=1):
        start_time = seg["start"]
        end_time = seg["end"]
        text = seg["text"].strip()

        subtitle = srt.Subtitle(
            index=i,
            start=timedelta(seconds=start_time),
            end=timedelta(seconds=end_time),
            content=text
        )
        subtitles.append(subtitle)

    return srt.compose(subtitles)


def speech_processing(audio_path: str, model_type: str, file_type: str, file_name: str, timestamps: bool):
    audio_file = whisper.load_audio(join_path(PROJECT_DIR_TO_DOWNLOAD_FILE, audio_path))
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
                f.close()
            else:
                transcribe = result["text"]
                f.write(result["text"])
                f.close()
    elif file_type == "txt":
        with open(subtitle_file, "w", encoding='utf-8') as f:
            transcribe = result["text"]
            f.write(result["text"])
            f.close()

    else:
        raise TypeError("Invalid file type")

    return result, transcribe

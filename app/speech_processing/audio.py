from datetime import timedelta, datetime
import srt


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
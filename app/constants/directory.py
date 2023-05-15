from os.path import dirname, abspath, join as join_path

DOWNLOAD_DIR = 'download'
MODEL_DIR = 'tmp'
ABS_DIR = dirname(abspath(__file__))
PROJECT_DIR_TO_DOWNLOAD_FILE = join_path(ABS_DIR, DOWNLOAD_DIR).replace("\\constants","").replace("/constants","")
PROJECT_DIR_TO_MODEL = join_path(ABS_DIR, MODEL_DIR).replace("\\constants","").replace("/constants","")
ALLOWED_EXTENSIONS = {'mp3', 'flac', 'wav'}
YOUTUBE_DOWNLOAD_FILE_NAME = "youtube_download.mp3"

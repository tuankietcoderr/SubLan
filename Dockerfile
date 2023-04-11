FROM python:3.9
RUN apt-get update && apt-get install -y \
ffmpeg
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
RUN python3.9 app/load_model.py
CMD ["python3.9", "app/main.py"]
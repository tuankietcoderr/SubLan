FROM python:3.9-slim-buster
RUN apt-get update && apt-get install -y \
ffmpeg
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
RUN ls -la /code/app
RUN python app/load_model.py
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
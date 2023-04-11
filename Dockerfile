FROM python:3.9-slim-buster
RUN apt-get update && apt-get install -y \
ffmpeg
ENV APP_HOME /code
COPY ./requirements.txt /code/requirements.txt
ENV PORT 8000
WORKDIR $APP_HOME
COPY . ./
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
RUN ls -la ./
RUN echo $PORT
RUN python app/load_model.py
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", $PORT]
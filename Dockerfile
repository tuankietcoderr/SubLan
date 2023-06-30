FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9
RUN apt-get update && apt-get install -y ffmpeg
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install --upgrade --no-deps --force-reinstall git+https://github.com/openai/whisper.git
COPY ./app /code/app
RUN python app/load_model.py
EXPOSE 8000
CMD ["python", "-W", "ignore", "./app/main.py"]
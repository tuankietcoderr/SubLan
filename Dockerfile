FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9
RUN apt-get update && apt-get install -y ffmpeg
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
RUN python app/load_model.py
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
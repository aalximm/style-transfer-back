FROM python:3.8-slim-buster

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c",  "celery -A celery_worker worker --loglevel=info -P eventlet --uid=nobody --concurrency=2 --max-memory-per-child=20000 & waitress-serve --port=8000 --call flaskr:create_app"]

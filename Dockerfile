FROM python:3.8-slim-buster

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD [ "python3", "-m" , "flask", "--app", "flaskr", "run", "--host=0.0.0.0", "--port=8000"]
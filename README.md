# Backend part of Style Transfer App

## Stack

Flask, Celery, onnx

## What are inside of project?

This project contains:
 - pretrained m=odels `/assets/stylemodels/`
 - stlyle representation for each model `/static/images/`
 - flask app with 3 endpoints
 - celery worker
## Usage

There is a docker-compose file wich contains this application and redis database

```
docker-compose up --build
```

Redis runs on 6379 port, app on 8000 port

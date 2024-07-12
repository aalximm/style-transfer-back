import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from flaskr import create_app


flask_app = create_app()
celery_app = flask_app.extensions["celery"]

if __name__ == "__main__":
    celery_app.start()

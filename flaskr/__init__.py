import os

import yaml
from celery import Celery, Task, shared_task
from celery.result import AsyncResult
from flask import Flask, request, make_response, Response
from flask_cors import CORS

from flaskr.image_generator.ImageConverter import reduce_quality
from flaskr.image_generator.StylerService import StylerService

STYLE_FILE_KEY = 'style'
CONTENT_FILE_KEY = 'content'

styler: StylerService = None


def celery_init_app(app: Flask) -> Celery:
	class FlaskTask(Task):
		def __call__(self, *args: object, **kwargs: object) -> object:
			with app.app_context():
				return self.run(*args, **kwargs)

	celery_app_local = Celery(app.name, task_cls=FlaskTask)
	celery_app_local.config_from_object(app.config["CELERY"])
	celery_app_local.set_default()
	app.extensions["celery"] = celery_app_local
	return celery_app_local


def create_app():
	global styler
	from .image_generator.StylerService import StylerService

	static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static")
	# create and configure the app
	app = Flask(__name__, static_folder=static_folder)

	with open(os.path.join('app.yaml')) as config_file:
		config = yaml.safe_load(config_file)

	app.config.update(config)
	app.config.from_prefixed_env()
	app.config.from_mapping(
		CELERY=dict(
			broker_url=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379"),
			result_backend=os.getenv("CELERY_BACKEND_URL", "redis://localhost:6379"),
			task_ignore_result=True,
			broker_connection_retry_on_startup=True
		),
	)

	CORS(app)

	if styler is None:
		styler = StylerService(app)

	celery_init_app(app)

	@app.get("/image-styler/styles")
	def get_styles():
		global styler
		styles = styler.get_styles()
		response = make_response(styles)

		del styles

		return response, 200

	@app.post("/image-styler/upload")
	def upload_image():
		content_image_bytes = request.files['content'].read()
		style_key = request.form.get("style")

		max_size = app.config["images"]["max_size"]
		task = style_image_task.delay(content_image_bytes, style_key, max_size)

		return {"task_id": task.id}, 200

	@app.get("/image-styler/result/<task_id>")
	def get_result(task_id: str):
		result = AsyncResult(task_id, app=app.extensions["celery"])

		if not result.ready():
			return Response(status=202)

		if result.status == 'FAILURE':
			result.forget()
			return Response(status=500)

		generated_image_bytes = result.result
		result.forget()

		response = make_response(generated_image_bytes)
		response.headers.set('Content-Type', 'image/jpeg')

		return response

	return app


@shared_task(ignore_result=False)
def style_image_task(content_image_bytes: bytes, style_key: str, max_size: int) -> bytes:
	from .image_generator import ImageConverter
	global styler

	image = ImageConverter.bytes_to_image(content_image_bytes)
	del content_image_bytes

	image = ImageConverter.reduce_quality(image, max_size)

	generated_image = styler.style_image(image, style_key)
	del image

	generated_image_bytes = ImageConverter.image_to_bytes(generated_image)
	del generated_image

	return generated_image_bytes

if __name__ == "__main__":
	flask_app = create_app()
	flask_app.run(debug=True)

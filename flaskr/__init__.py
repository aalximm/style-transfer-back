import os

import yaml
from flask import Flask, request, make_response
from flask_cors import CORS

from flaskr.image_generator.ImageConverter import reduce_quality
from flaskr.image_generator.StylerService import StylerService

STYLE_FILE_KEY = 'style'
CONTENT_FILE_KEY = 'content'


styler: StylerService = None


def create_app():
	global styler
	from .image_generator.StylerService import StylerService

	static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static")
	# create and configure the app
	app = Flask(__name__, static_folder=static_folder)

	with open(os.path.join('app.yaml')) as config_file:
		config = yaml.safe_load(config_file)

	app.config.update(config)

	CORS(app)

	if styler is None:
		styler = StylerService(app)

	@app.get("/image-styler/styles")
	def get_styles():
		global styler
		styles = styler.get_styles()
		response = make_response(styles)

		return response, 200

	@app.post("/image-styler/forward/upload")
	async def upload_image():
		global styler
		from .image_generator import ImageConverter

		content_image_bytes = request.files['content'].read()
		style_key = request.form.get("style")

		image = ImageConverter.bytes_to_image(content_image_bytes)

		max_size = app.config["images"]["max_size"]
		image = ImageConverter.reduce_quality(image, max_size)

		generated_image = await styler.style_image(image, style_key)
		# generated_image = image
		generated_image_bytes = ImageConverter.image_to_bytes(generated_image)
		response = make_response(generated_image_bytes)

		response.headers.set('Content-Type', 'image/jpeg')

		return response, 200

	return app


if __name__ == "__main__":
	create_app()

import os
import uuid

from flask import Flask, request, g, make_response

STYLE_FILE_KEY = 'style'
CONTENT_FILE_KEY = 'content'

image_generator_instance = None


def create_app():
	global image_generator_instance
	from .image_generator import ImageGenerator
	# create and configure the app
	app = Flask(__name__)

	if image_generator_instance is None:
		image_generator_instance = ImageGenerator.ImageGenerator()

	@app.post("/image-generator/upload")
	async def upload_images():
		global image_generator_instance
		from .image_generator import ImageProcessor

		if STYLE_FILE_KEY not in request.files or CONTENT_FILE_KEY not in request.files:
			return "No file part", 400

		# session_id = str(uuid.uuid4())

		style_image = request.files[STYLE_FILE_KEY].read()
		content_image = request.files[CONTENT_FILE_KEY].read()
		# style_image.save(os.path.join('uploads', 'style', f"{session_id}.jpg"))
		# content_image.save(os.path.join('uploads', 'content', f"{session_id}.jpg"))

		generated_image = image_generator_instance.generate_image(content_image, style_image)

		response = make_response(generated_image)
		response.headers.set('Content-Type', 'image/jpeg')

		return response, 200

	return app

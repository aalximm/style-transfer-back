from typing import Dict, Union, Callable

import PIL.Image
import numpy as np
import onnxruntime
from PIL.Image import Image
from celery import shared_task
from flask import url_for
from onnxruntime import InferenceSession

from flaskr.image_generator.ImageConverter import image_to_normalized_array, normalized_array_to_image


class StylerService:
	def __init__(self, app):
		self.models: Dict[str, Dict[str, Union[Callable[[], InferenceSession], str]]] = {}

		for model_data in app.config["models"]:
			def get_session(model_path=model_data["model_path"]):
				return onnxruntime.InferenceSession(model_path, providers=["CPUExecutionProvider"])

			self.models[model_data["key"]] = {
				"model": get_session,
				"description": model_data["description"],
				"name": model_data["name"],
				"image_name": model_data["image_name"]
			}
			print(f"Model {model_data['key']} loaded successful")

	def get_styles(self):
		return [
			{
				"style_key": name,
				"description": self.models[name]["description"],
				"name": self.models[name]["name"],
				"image_url": url_for('static', filename=self.models[name]["image_name"])
			}
			for name in self.models.keys()
		]

	def style_image(self, image: Image, style: str) -> Image:
		if style not in self.models.keys():
			raise KeyError

		image_array = image_to_normalized_array(image)
		del image

		image_array = np.expand_dims(image_array, axis=0)

		session = self.models[style]["model"]()
		model_inputs = {
			session.get_inputs()[0].name: image_array
		}

		output_image = session.run(["result"], model_inputs)[0]
		del image_array, session

		output_image = normalized_array_to_image(output_image)

		return output_image

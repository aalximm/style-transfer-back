from typing import Dict, Union, Callable

import numpy as np
import onnxruntime
from PIL.Image import Image
from flask import url_for
from onnxruntime import InferenceSession

from flaskr.image_generator.ImageConverter import image_to_normalized_array, normalized_array_to_image


class StylerService:
	def __init__(self, app):
		self.models: Dict[str, Dict[str, Union[InferenceSession, str]]] = {}

		for model_data in app.config["models"]:
			self.models[model_data["key"]] = {
				"model": onnxruntime.InferenceSession(model_data["model_path"], providers=["CPUExecutionProvider"]),
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

	async def style_image(self, image: Image, style: str) -> Image:
		if style not in self.models.keys():
			raise KeyError

		image_array = image_to_normalized_array(image)
		image_array = np.expand_dims(image_array, axis=0)

		session = self.models[style]["model"]
		model_inputs = {
			session.get_inputs()[0].name: image_array
		}

		output_image = session.run(["result"], model_inputs)
		output_image = output_image[0]

		output_image = normalized_array_to_image(output_image)

		return output_image

import math

import numpy as np
from PIL import Image, ExifTags
import io

mean = np.array([0.485, 0.456, 0.406]).reshape(3, 1, 1)
std = np.array([0.229, 0.224, 0.225]).reshape(3, 1, 1)


def image_to_normalized_array(image: Image.Image) -> np.ndarray:
	if image.mode == 'RGBA':
		image = image.convert('RGB')

	image_array = np.array(image).astype(np.float32)
	image_array = np.transpose(image_array, (2, 0, 1))

	image_array /= 255.0

	normalized_image_array = (image_array - mean) / std

	return normalized_image_array.astype(np.float32)


def normalized_array_to_image(normalized_array: np.ndarray) -> Image.Image:
	normalized_array = np.squeeze(normalized_array, axis=0)
	image_array = (normalized_array * std) + mean
	image_array = image_array.transpose(1, 2, 0)
	image_array = (image_array * 255.0).astype(np.uint8)

	image = Image.fromarray(image_array)

	return image


def bytes_to_image(image_bytes: bytes) -> Image.Image:
	image = Image.open(io.BytesIO(image_bytes))\

	# Обработка EXIF-данных для правильной ориентации
	try:
		for orientation in ExifTags.TAGS.keys():
			if ExifTags.TAGS[orientation] == 'Orientation':
				break
		exif = image._getexif()
		if exif is not None:
			exif = dict(exif.items())
			orientation = exif.get(orientation)

			if orientation == 3:
				image = image.rotate(180, expand=True)
			elif orientation == 6:
				image = image.rotate(270, expand=True)
			elif orientation == 8:
				image = image.rotate(90, expand=True)
	except (AttributeError, KeyError, IndexError):
		pass

	return image




def image_to_bytes(image: Image.Image) -> bytes:
	buffer = io.BytesIO()
	image.save(buffer, format="JPEG")
	return buffer.getvalue()


def reduce_quality(image: Image.Image, max_size: int) -> Image.Image:
	h, w = image.height, image.width

	ratio = math.sqrt(h * w / max_size)

	if ratio <= 1:
		return image

	# Resize the image to the target dimensions without maintaining the aspect ratio
	target_width = math.floor(w / ratio)
	target_height = math.floor(h / ratio)
	resized_image = image.resize((target_width, target_height))

	return resized_image

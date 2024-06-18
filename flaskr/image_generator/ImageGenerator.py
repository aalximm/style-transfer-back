import torch
from flask import g

from . import FeatureExtractor
from . import ImageProcessor


class ImageGenerator:
	def __init__(self):
		self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
		self.feature_extractor = FeatureExtractor.FeatureExtractor().to(self.device)

		self.alpha = 1e-3
		self.content_wl = torch.tensor([0, 0, 0, 1], device=self.device)
		self.style_wl = torch.tensor([1 / 5, 1 / 5, 1 / 5, 1 / 5, 1 / 5], device=self.device)
		self.deep = 5

		self.lr = 5e-2

		self.quality_dict = {
			'normal': {
				'iterations': 100,
				'lr': 5e-2
			}
		}

	def generate_image(self, content_image, style_image, quality='normal'):
		content_image = ImageProcessor.bytes_to_tensor(content_image)
		style_image = ImageProcessor.bytes_to_tensor(style_image)

		generated_image = self._generate_image(
			content_image,
			style_image,
			iterations=self.quality_dict[quality]['iterations'],
			lr=self.quality_dict[quality]['lr']
		)

		generated_image = ImageProcessor.tensor_to_bytes(generated_image)
		return generated_image

	def loss_fn(self, generated_image_features, content_features, style_features):
		content_loss = torch.zeros(1, device=self.device)
		style_loss = torch.zeros(1, device=self.device)

		for i in range(len(content_features)):
			if i >= len(self.content_wl) or self.content_wl[i] == 0:
				continue

			content_loss += torch.mean((generated_image_features[0][i] - content_features[i]) ** 2) * self.content_wl[
				i] / 2

		for i in range(len(style_features)):
			if self.style_wl[i] == 0:
				continue

			style_loss += torch.mean((generated_image_features[1][i] - style_features[i]) ** 2) * self.style_wl[i] / 2

		return self.alpha * content_loss + style_loss

	def _generate_image(self, content_image, style_image, iterations, lr):
		if self.device == 'cuda':
			torch.cuda.empty_cache()

		content_image = content_image.to(self.device)
		style_image = style_image.to(self.device)

		content_features = self.feature_extractor.extract_content_features(content_image, max_layers=self.deep)
		style_features = self.feature_extractor.extract_style_features(style_image, max_layers=self.deep)

		generated_image = content_image.clone()
		generated_image.requires_grad = True
		optimizer = torch.optim.Adam([generated_image], lr=lr)

		for i in range(iterations):
			optimizer.zero_grad()

			generated_image_features = self.feature_extractor.extract_features(generated_image, max_layers=self.deep)

			loss = self.loss_fn(generated_image_features, content_features, style_features)

			loss.backward()
			optimizer.step()

		return generated_image.detach().cpu()

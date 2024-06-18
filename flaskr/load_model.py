import os.path

import torch
import torchvision

ASSETS_PATH = 'assets'


def load_model():
	vgg19 = torchvision.models.vgg19(weights=torchvision.models.VGG19_Weights.DEFAULT)
	vgg19 = vgg19.features
	vgg19.eval()
	for param in vgg19.parameters():
		param.requires_grad = False

	torch.save(vgg19, os.path.join(os.path.realpath(__file__), '..', '..', ASSETS_PATH, 'vgg19.model'))


if __name__ == "__main__":
	load_model()

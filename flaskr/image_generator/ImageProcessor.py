import torchvision.io
import torchvision.transforms.v2 as tt
import torch

_IMAGE_MEAN = [0.485, 0.456, 0.406]
_IMAGE_STD = [0.229, 0.224, 0.225]
_IMAGE_SIZE = 224

TRANSFORMS = tt.Compose([
	tt.ToImage(),
	tt.Resize(256, antialias=True),
	tt.CenterCrop(_IMAGE_SIZE),
	tt.ToDtype(dtype=torch.float32, scale=True),
	tt.Normalize(mean=_IMAGE_MEAN, std=_IMAGE_STD, inplace=True)
])


def _denorm(image_tensor):
	return (image_tensor.permute(1, 2, 0) * torch.tensor(_IMAGE_STD) + torch.tensor(_IMAGE_MEAN)).permute(2, 1, 0)


def bytes_to_tensor(image):
	# print(image)
	image = torch.tensor(list(image), dtype=torch.uint8, device='cpu')
	image = torchvision.io.decode_image(image)
	image = TRANSFORMS(image)
	return image


def tensor_to_bytes(image):
	image = _denorm(image)
	image = image * 255
	image = image.to(dtype=torch.uint8).transpose(1, 2)
	image = torchvision.io.encode_jpeg(image).tolist()
	return bytes(image)

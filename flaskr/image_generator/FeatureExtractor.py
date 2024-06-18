import math
import os.path

import torch
import torchvision
from torch import nn

from flaskr.load_model import ASSETS_PATH


def get_gram(x):
    c, h, w = x.size()
    x = x.view(c, h * w)
    return x @ x.T / c / math.sqrt(h * w)


class FeatureExtractor(nn.Module):
    def __init__(self):
        super(FeatureExtractor, self).__init__()

        self.layers = torch.load(os.path.join(ASSETS_PATH, "vgg19.model"))

        for param in self.layers.parameters():
            param.requires_grad = False

    def extract_features(self, x, max_layers=None):
        style_features = []
        content_features = []

        x = x.unsqueeze(0)

        for i, layer in enumerate(self.layers):
            if max_layers and len(content_features) >= max_layers:
                break

            x = layer(x)

            if isinstance(layer, nn.ReLU):
                content_features.append(x[0])

                style_feature = get_gram(x[0])
                style_features.append(style_feature)

        return content_features, style_features

    def extract_style_features(self, x, max_layers=None):
        style_features = []

        x = x.unsqueeze(0)

        for i, layer in enumerate(self.layers):
            if max_layers and len(style_features) >= max_layers:
                break

            x = layer(x)

            if isinstance(layer, nn.ReLU):
                style_feature = get_gram(x[0])
                style_features.append(style_feature)

        return style_features

    def extract_content_features(self, x, max_layers=None):
        content_features = []

        x = x.unsqueeze(0)

        for i, layer in enumerate(self.layers):
            if max_layers and len(content_features) >= max_layers:
                break

            x = layer(x)

            if isinstance(layer, nn.ReLU):
                content_features.append(x[0])

        return content_features

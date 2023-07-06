# Copyright 2020 Toyota Research Institute.  All rights reserved.

import torch.nn as nn
import numpy as np
import torch.nn.functional as F
from functools import partial
import torch
# DNet decoder
# from packnet_sfm.networks.layers.Dnet.DNet_decoder import DepthDecoder
# Monodepth2 decoder
# from packnet_sfm.networks.layers.resnet.depth_decoder import DepthDecoder
# ECA_Dnet_decoder
from packnet_sfm.networks.layers.Dnet.ECA_dnet_decoder import ECADnet_DepthDecoder
from packnet_sfm.networks.layers.resnet.layers import disp_to_depth
from packnet_sfm.networks.layers.repvgg.RepVGG_encoder import RepVGGencoder
import packnet_sfm.networks.layers.repvgg.RepVGG as RepVGG
########################################################################################################################

class DepthRepVGGNet(nn.Module):
    """
    Inverse depth network based on the ResNet architecture.

    Parameters
    ----------
    version : str
        Has a XY format, where:
        X is the number of residual layers [18, 34, 50] and
        Y is an optional ImageNet pretrained flag added by the "pt" suffix
        Example: "18pt" initializes a pretrained ResNet18, and "34" initializes a ResNet34 from scratch
    kwargs : dict
        Extra parameters
    """
    def __init__(self, version=None, **kwargs):
        super().__init__()
        assert version is not None, "DispResNet needs a version"

        num_layers = int(version[:2])       # First two characters are the number of layers
        if version[2:] == 'np': #
            pretrained = 'np'
        elif version[2:] == 'pt':
            pretrained = 'pt'
            # If the last characters are "pt", use ImageNet original pretraining
        else:
            pretrained = False
        assert num_layers in [18, 34, 50], 'ResNet version {} not available'.format(num_layers)
        
        self.num_ch_enc = np.array([48, 48, 96, 192, 1280])
        self.encoder = RepVGGencoder(pretrained=pretrained)
        self.decoder = ECADnet_DepthDecoder(num_ch_enc=self.num_ch_enc)
        self.scale_inv_depth = partial(disp_to_depth, min_depth=0.1, max_depth=80.0)

        
    def forward(self, x):
        """
        Runs the network and returns inverse depth maps
        (4 scales if training and 1 if not).
        """
        x = self.encoder(x)
        x = self.decoder(x)
        disps = [x[('disp', i)] for i in range(4)]
        d_disp_0 = disps[0]

        if self.training:
            return [self.scale_inv_depth(d)[0] for d in disps]
        else:
            # return F.interpolate(self.scale_inv_depth(d_disp_0)[0], scale_factor=0.5)
            return self.scale_inv_depth(disps[0])[0]

########################################################################################################################

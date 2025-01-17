# Copyright Niantic 2019. Patent Pending. All rights reserved.
#
# This software is licensed under the terms of the Monodepth2 licence
# which allows for non-commercial use only, the full terms of which are made
# available in the LICENSE file.

from __future__ import absolute_import, division, print_function

import numpy as np

import packnet_sfm.networks.layers.repvgg.RepVGG as RepVGG
import torch
import torch.nn as nn
import torchvision.models as models
import torch.utils.model_zoo as model_zoo
import torch.utils.checkpoint as checkpoint

class RepVGGencoder(nn.Module):
    """Pytorch module for a resnet encoder
    """
    def __init__(self, pretrained):
        super(RepVGGencoder, self).__init__()
        self.encoder = RepVGG.create_RepVGG_A0(deploy=False)
        print('----- RepVGG -----')
        if pretrained == 'pt':
            self.encoder.load_state_dict(
                torch.load('/home/seok436/packnet-sfm-master/configs/RepVGG-A0-train.pth'))
            print('RepVGG pretrained model loaded!')

    def forward(self, input_image):
        self.features = []
        x = (input_image - 0.45) / 0.225
        out = self.encoder.stage0(x)
        self.features.append(out)
        for stage in (self.encoder.stage1, self.encoder.stage2, self.encoder.stage3, self.encoder.stage4):
            for block in stage:
                if self.encoder.use_checkpoint:
                    out = checkpoint.checkpoint(block, out)
                else:
                    out = block(out)
            self.features.append(out)
        return self.features

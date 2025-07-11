# Copyright 2025, Maxime Burchi.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# PyTorch
import torch
import torch.nn as nn

# NeuralNets
from nnet import modules
from nnet import distributions

class RewardNetwork(nn.Module):

    def __init__(
        self, 
        hidden_size=512, 
        act_fun=nn.SiLU, 
        num_mlp_layers=5, 
        feat_size=32*32+512, 
        weight_init="dreamerv3_normal", 
        bias_init="zeros", 
        norm={"class": "LayerNorm", "params": {"eps": 1e-3}}, 
        bins=255, 
        dist_weight_init="zeros", 
        dist_bias_init="zeros"
    ):
        super(RewardNetwork, self).__init__()

        self.mlp = modules.MultiLayerPerceptron(dim_input=feat_size, dim_layers=[hidden_size for _ in range(num_mlp_layers)], act_fun=act_fun, weight_init=weight_init, bias_init=bias_init, norm=norm, bias=norm is None)
        self.linear_proj = modules.Linear(hidden_size, bins, weight_init=dist_weight_init, bias_init=dist_bias_init)

    def forward(self, x):

        # MLP Layers
        x = self.mlp(x)

        # Output Proj
        x = self.linear_proj(x)

        # Discrete SymLog Distribution
        reward_dist = distributions.SymLogDiscreteDist(logits=x, reinterpreted_batch_ndims=1, low=-20, high=20)

        return reward_dist
    
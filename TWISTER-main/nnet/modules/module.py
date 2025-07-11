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

# Other
from collections import OrderedDict

class Module(nn.Module):

    def __init__(self):
        super(Module, self).__init__()
        self.modules_buffer = OrderedDict()
        self.device = torch.device("cpu")
        self.reset_losses()
        self.reset_infos()
        self.reset_metrics()

    def add_loss(self, name, loss, weight=1.0):

        """ Add module loss to model total loss during forward_model """

        self.added_losses[name] = {"loss": loss, "weight": weight}

    def add_info(self, name, info):

        """ Add module info to model infos during forward_model """

        self.infos[name] = info

    def add_metric(self, name, metric):

        """ Add module metric to model metrics during forward_model """

        self.added_metrics[name] = metric

    def reset_losses(self):
        self.added_losses = OrderedDict()

    def reset_infos(self):
        self.infos = OrderedDict()

    def reset_metrics(self):
        self.added_metrics = OrderedDict()

    def register_module_buffer(self, name, module, require_grad=False, training=False):

        """ Register a module as buffer (requires_grad = False, training = False) """
        
        # Set require grad
        if require_grad is not None:
            self.set_require_grad(module, require_grad)

        # Set training mode
        if training is not None:
            module.train(training)
            
        self.modules_buffer[name] = module
        object.__setattr__(self, name, module)

    def set_require_grad(self, networks, require_grad=True):

        if not isinstance(networks, list):
            networks = [networks]

        for network in networks:
            if network != None:
                network.requires_grad_(require_grad)

    def to(self, device):

        # Set device
        self.device = device

        for module in self.children():
            module.to(device=self.device)

        # Set modules buffer to device
        for key, value in self.modules_buffer.items():
            self.modules_buffer[key] = value.to(device=self.device)

        return super(Module, self).to(device)

    def transfer_to_device(self, struct, device=None):

        # Load Batch elt to model device
        if isinstance(struct, dict):
            return {key: self.transfer_to_device(value, device=device) for key, value in struct.items()}
        elif isinstance(struct, list):
            return [self.transfer_to_device(value, device=device) for value in struct]
        elif isinstance(struct, tuple):
            return tuple([self.transfer_to_device(value, device=device) for value in struct])
        elif isinstance(struct, torch.Tensor) or isinstance(struct, nn.Module):
            return struct.to(device if device != None else self.device)
        elif struct is None:
            return struct
        else:
            raise Exception("Incorrect struct type: {}. Must be dict, list module, tensor or None.".format(type(struct)))
        
    def add_frozen(self, name, module, persistent=True):

        """ add frozen module (requires_grad==False) to state dict, add to module buffer if persistent==False """

        # Set Require Grad to False
        self.set_require_grad(module, False)

        # Add to Modules to include in state_dict
        if persistent:
            self.add_module(name, module)

        # Add to Modules Buffer
        else:
            self.modules_buffer[name] = module
            object.__setattr__(self, name, module)



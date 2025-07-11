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

###############################################################################
# Collate Functions
###############################################################################

class CollateDefault(nn.Module):

    def __init__(self):
        super(CollateDefault, self).__init__()

    def forward(self, samples):
        return samples

class CollateFn(nn.Module):

    """ Collate samples to List / Dict

    Args:
        - inputs_params_: List / Dict of collate param for inputs
        - targets_params: List / Dict of collate param for targets

    Collate Params Dict:
        - axis: axis to select samples

    """

    def __init__(self, inputs_params=[{"axis": 0}], targets_params=[{"axis": 1}]):
        super(CollateFn, self).__init__()

        assert isinstance(inputs_params, dict) or isinstance(inputs_params, list) or isinstance(inputs_params, tuple)
        self.inputs_params = inputs_params
        assert isinstance(targets_params, dict) or isinstance(targets_params, list) or isinstance(targets_params, tuple)
        self.targets_params = targets_params

    def forward(self, samples):

        return {"inputs": self.collate(samples, self.inputs_params), "targets": self.collate(samples, self.targets_params)}

    def collate(self, samples, collate_params):

        # Collate as Dict
        if isinstance(collate_params, dict):
            collates = {}
            for name, params in collate_params.items():

                # Select
                collate = [sample[params["axis"]] for sample in samples]

                # Stack
                collate = torch.stack(collate, axis=0)

                # Append
                collates[name] = collate

        # Collate as List
        elif isinstance(collate_params, list):
            collates = []
            for params in collate_params:

                # Select
                collate = [sample[params["axis"]] for sample in samples]

                # Stack
                collate = torch.stack(collate, axis=0)

                # Append
                collates.append(collate)
                
        # Collate as Tuple
        elif isinstance(collate_params, tuple):
            collates = []
            for params in collate_params:

                # Select
                collate = [sample[params["axis"]] for sample in samples]

                # Stack
                collate = torch.stack(collate, axis=0)

                # Append
                collates.append(collate)
            collates = tuple(collates)

        # Convert single elt struct to item for easy unpack
        collates = collates[0] if len(collates) == 1 else collates

        return collates
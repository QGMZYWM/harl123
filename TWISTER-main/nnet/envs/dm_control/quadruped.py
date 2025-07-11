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

# NeuralNets
from nnet.envs import dm_control

class Quadruped(dm_control.DeepMindControlEnv):

    """
    
    Quadruped

    quadruped     walk
    quadruped     run
    quadruped     escape
    quadruped     fetch
    
    """

    def __init__(
            self, 
            img_size=(64, 64), 
            history_frames=1, 
            episode_saving_path=None, 
            task="run", 
            action_repeat=1
        ):

        assert task in ["walk", "run"]
        super(Quadruped, self).__init__(
            domain="quadruped", 
            task=task, 
            img_size=img_size, 
            history_frames=history_frames, 
            episode_saving_path=episode_saving_path, 
            action_repeat=action_repeat, 
            camera_id=2
        )

        self.num_actions = 12
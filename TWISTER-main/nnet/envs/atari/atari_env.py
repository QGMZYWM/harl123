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
import torchvision

# NeuralNets
from nnet.structs import AttrDict

# Gym
import gym.envs.atari
import gym.wrappers

# Other
import os
import datetime

class AtariEnv:
    
    """

    Atari 100k 26:
        1: alien
        2: amidar
        3: assault
        4: asterix
        5: bank_heist
        6: battle_zone
        7: boxing
        8: breakout
        9: chopper_command
        10: crazy_climber
        11: demon_attack
        12: freeway
        13: frostbite
        14: gopher
        15: hero
        16: jamesbond
        17: kangaroo
        18: krull
        19: kung_fu_master
        20: ms_pacman
        21: pong
        22: private_eye
        23: qbert
        24: road_runner
        25: seaquest
        26: up_n_down
    
    """

    def obs_space(self):

        if self.grayscale_obs:
            return (["image", (1 * self.history_frames, self.img_size[0], self.img_size[1]), torch.uint8],)
        else:
            return (["image", (3 * self.history_frames, self.img_size[0], self.img_size[1]), torch.uint8],)

    def __init__(
            self, 
            game, 
            img_size=(64, 64), 
            action_repeat=4, 
            history_frames=1, 
            seed=None, 
            repeat_action_probability=0.0, 
            episode_saving_path=None, 
            noop_max=30, 
            terminal_on_life_loss=False, 
            grayscale_obs=False, 
            full_action_space=False
        ):

        # Params
        self.img_size = img_size
        self.grayscale_obs = grayscale_obs
        self.terminal_on_life_loss = terminal_on_life_loss

        # Env
        self.env = gym.envs.atari.AtariEnv(game=game, obs_type='image', frameskip=1, repeat_action_probability=repeat_action_probability, full_action_space=full_action_space)

        # Avoid unnecessary rendering in inner env.
        self.env._get_obs = lambda: None

        # Tell wrapper that the inner env has no action repeat.
        self.env.spec = gym.envs.registration.EnvSpec('NoFrameskip-v0')

        # Standard Preprocessing
        self.env = gym.wrappers.AtariPreprocessing(env=self.env, noop_max=noop_max, frame_skip=action_repeat, screen_size=img_size[0], terminal_on_life_loss=terminal_on_life_loss, grayscale_obs=grayscale_obs)

        # Params
        self.episode_saving_path = episode_saving_path
        if self.episode_saving_path is not None:
            if not os.path.isdir(self.episode_saving_path):
                os.makedirs(self.episode_saving_path, exist_ok=True)
        self.grayscale_obs = grayscale_obs
        self.action_repeat = action_repeat
        self.history_frames = history_frames

        # Set Seed
        self.seed(seed)

        # Default Action Space
        self.num_actions = self.env.action_space.n

        # FPS
        self.fps = 60.0 / self.action_repeat

    def seed(self, seed):
        if seed:
            self.env.seed(seed)

    def sample(self):

        return torch.nn.functional.one_hot(torch.randint(low=0, high=self.num_actions, size=()), num_classes=self.num_actions).type(torch.float32)

    def preprocess(self, state, reward, done):

        # To tensor
        state = torch.tensor(state) 

        # (C, H, W)
        if self.grayscale_obs:
            state = state.unsqueeze(dim=0)
        else:
            state = state.permute(2, 0, 1)

        # Reward
        reward = torch.tensor(reward, dtype=torch.float32)

        # Done
        done = torch.tensor(done, dtype=torch.float32)

        # Is_last
        if self.terminal_on_life_loss:
            is_last = torch.tensor(self.env.env.ale.game_over(), dtype=torch.float32)
        else:
            is_last = done

        return state, reward, done, is_last

    def reset(self):

        # Reset
        state, _, _, _ = self.preprocess(self.env.reset(), 0, 0)
        
        # Episode videos
        if self.episode_saving_path is not None:
            self.episode_video = []
            self.episode_video_pre = []

        # Repeat history frames along channels
        if self.history_frames > 1:
            self.history = state.repeat(self.history_frames, 1, 1)

        # No history frames
        else:
            self.history = state

        # Episode Score
        self.episode_score = 0.0

        # Reward
        reward = torch.tensor(0.0, dtype=torch.float32)

        # Done
        done = torch.tensor(False, dtype=torch.float32)

        # Is_last
        is_last = torch.tensor(False, dtype=torch.float32)

        # Is First
        is_first = torch.tensor(True, dtype=torch.float32)

        return AttrDict(state=self.history, reward=reward, done=done, is_first=is_first, is_last=is_last)

    def step(self, action):

        # Env Step
        state, reward, done, infos = self.env.step(action.item())

        # Update Episode Score
        self.episode_score += reward

        # Add to video
        if self.episode_saving_path is not None:
            self.episode_video.append(torch.tensor(self.env.env._get_image()))
            self.episode_video_pre.append(torch.tensor(state))

        # Save Episode
        if done and self.episode_saving_path is not None:

            # Stack videos
            self.episode_video = torch.stack(self.episode_video, dim=0)
            self.episode_video_pre = torch.stack(self.episode_video_pre, dim=0)

            # Datetime
            date_time_score = str(datetime.datetime.now()).replace(" ", "_") + "_" + str(self.episode_score)

            # Save Videos
            torchvision.io.write_video(filename=os.path.join(self.episode_saving_path, "{}.mp4".format(date_time_score)), video_array=self.episode_video, fps=self.fps, video_codec="libx264")
            torchvision.io.write_video(filename=os.path.join(self.episode_saving_path, "{}_pre.mp4".format(date_time_score)), video_array=self.episode_video_pre.unsqueeze(dim=-1).repeat(1, 1, 1, 3) if self.grayscale_obs else self.episode_video_pre, fps=self.fps, video_codec="libx264")

        # Preprocessing
        state, reward, done, is_last = self.preprocess(state, reward, done)

        # Is First
        is_first = torch.tensor(False, dtype=torch.float32)

        # Concat history frames along channels
        if self.history_frames > 1:
            if self.grayscale_obs:
                self.history = torch.cat([self.history[1:], state], dim=0)
            else:
                self.history = torch.cat([self.history[3:], state], dim=0)

        # No history frames
        else:
            self.history = state

        return AttrDict(state=self.history, reward=reward, done=done, is_first=is_first, is_last=is_last)
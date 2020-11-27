from numpy.core.defchararray import index, replace
from mazemap import Action, Mode
import numpy as np
from numpy import random

# Basic encap for a episode, which stands for a snapshot of a game state
class Episode:
    def __init__(self, curr_state, next_state, action, reward, mode):
        self._curr_state = curr_state
        self._next_state = next_state
        self._action = action
        self._reward = reward
        self._mode = mode

    def get_curr_state(self):
        return self._curr_state

    def get_next_state(self):
        return self._next_state

    def get_action(self):
        return self._action

    def get_reward(self):
        return self._reward

    def get_mode(self):
        return self._mode

# The official name for this is "Experience Buffer"
# Experience buffer is another concept beyond the vanilla implementation of reinforce learning,
# which means it's not required for a basic reinforce learning.
#
# Experience buffer can help our model to learn better
# by randomly sampling input and target from previous training episode


class ReplyBuffer:
    def __init__(self, model, state_size, max_buffer=1000, gamma=0.9):
        # Set up basic parameter for a experience buffer
        self.model = model
        self.max_buffer = max_buffer
        self.gamma = gamma
        self.state_size = state_size

        self.buffer = []
        self.num_actions = len(Action)

    # Log the new episode into a list
    def log(self, episode: Episode):
        if len(self.buffer) > self.max_buffer:
            del self.buffer[0]
        self.buffer.append(episode)

    def predict(self, state):
        return self.model.predict(state)[0]

    def change_gamme(self, new_val):
        self.gamma = new_val

    def sampling(self, sample_size):
        buffer_size = len(self.buffer)
        # If the no enough data in the buffer, then it will shrink the sample size
        # to use as much data as possible
        sample_size = min(sample_size, buffer_size)

        inputs = np.zeros((sample_size, self.state_size))
        outputs = np.zeros((sample_size, self.num_actions))

        samples = random.choice(buffer_size, sample_size, replace=False)
        for idx, sample_idx in enumerate(samples):
            episode = self.buffer[sample_idx]
            inputs[idx] = episode.get_curr_state()
            outputs[idx] = self.predict(episode.get_curr_state())

            # Apply Q-learning update rule:
            # Q(s, a) = r + gamma * max Q(s', a')
            # r stands for immediate reward at that state
            # gamma is discount rate

            # This is for Q(s', a')
            Q_sa_prev = np.max(self.predict(episode.get_next_state()))
            action_idx = int(episode.get_action())
            if episode.get_mode() == Mode.END:
                outputs[idx, action_idx] = episode.get_reward()
            else:
                outputs[idx, action_idx] = episode.get_reward() + self.gamma * Q_sa_prev

        return inputs, outputs

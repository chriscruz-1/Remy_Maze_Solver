from mazemap import Action

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

class ReplyBuffer:
    def __init__(self, model, max_buffer = 100, gamma=0.9):
        # Set up basic parameter for a experience buffer
        self.model = model
        self.max_buffer = max_buffer
        self.gamma = gamma


        self.buffer = []
        self.num_actions = len(Action)

    def log(self, episode: Episode):
        if len(self.buffer) > self.max_buffer:
            del self.buffer[0]
        self.buffer.append(episode)

    def predict(self, state):
        return self.model.predict(state)[0]

    # def 
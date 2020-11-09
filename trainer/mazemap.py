import numpy as np
from enum import Enum

class Mode(Enum):
    VALID = 0
    INVALID = 1
    VISITED = 2
    END = 4
    TERMINATED = 5

class Action(Enum):
    LEFT = 0
    UP = 1
    RIGHT = 2
    DOWN = 3
    # JUMP = 4

class MazeMap:
    def __init__(self, map, start=(0, 0), end=None):
        self.maze = np.array(map)
        self.height, self.width = self.maze.shape

        # Mark the start position and end position
        self.start = start
        self.end = (self.height - 1, self.width - 1) if end == None else end

        # Mark the current location of our agent.
        self.curr_loc = start

        # Set up state map, which will record the reward
        # And will be used in training process
        self.state = np.copy(self.maze)

        # Set up total reward and termination bound
        self.tol_reward = 0
        self.reward_lower_bound = -100
        # self.reward_upper_bound = 100

        # Set up visited set.
        self.visited = set()
        self.visited.add(self.start)

    # A simple helper function to get the dimension of map
    def dime(self):
        return (self.height, self.width)

    # Determine whether there is a path based on 
    # the difference from current row and col
    def _is_path(self, drow = 0, dcol = 0):
        curr_row, curr_col = self.curr_loc
        return (self.maze[curr_row + drow, curr_col + dcol] == 0)

    def _is_wall(self, drow = 0, dcol = 0):
        return not self._is_path(drow, dcol)

    # Calculate all possible and valid operation based on the current location
    def get_valid_actions(self):
        curr_row, curr_col = self.curr_loc
        actions = []

        if curr_row - 1 >= 0 and self._is_path(-1):
            actions.append(Action.UP)
        
        if curr_row + 1 < self.height and self._is_path(1):
            actions.append(Action.DOWN)
        
        if curr_col - 1 >= 0 and self._is_path(dcol= -1):
            actions.append(Action.LEFT)

        if curr_col + 1 < self.width and self._is_path(dcol= 1):
            actions.append(Action.RIGHT)

        # Jump action is not handled yet
        return actions

    # Apply the action based on the current location
    # Returen the new location of our agent.
    def _apply_action(self, action: Action):
        curr_row, curr_col = self.curr_loc

        if action == Action.LEFT:
            curr_row -= 1
        elif action == Action.UP:
            curr_col -= 1
        elif action == Action.RIGHT:
            curr_col += 1
        elif action == Action.DOWN:
            curr_row += 1

        return (curr_row, curr_col)

    # Calculate the reward based on different situations.
    def cal_reward(self, action: Action):
        valid_actions = self.get_valid_actions()

        if not action in valid_actions:
            return (-10, Mode.INVALID)
        else:
            next_loc = self._apply_action(action)
            if next_loc == self.end:
                return (10, Mode.END)
            elif next_loc in self.visited:
                return (-1, Mode.VISITED)
            else:
                return (-0.5, Mode.VALID)

    # Get the current map and location of agent
    def observe(self, mark_visited=False):
        curr_row, curr_col = self.curr_loc
        canvas = np.copy(self.maze)

        # Use number 0.6 to mark visited cell
        if mark_visited:
            for pos in self.visited:
                canvas[pos[0], pos[1]] = 0.6
        
        # Use 0.3 to mark position of agent
        canvas[curr_row, curr_col] = 0.3

        # Use 0.9 to mark position of end
        canvas[self.end[0], self.end[1]] = 0.9
        return canvas.reshape(1, -1)
    
    # This function is basically identical to the observe.
    # Only used for visualization game process.
    def get_map_for_draw(self, mark_visited=True):
        curr_row, curr_col = self.curr_loc
        canvas = np.copy(self.maze)

        reverse_v = np.vectorize(lambda x: 1.0 if x == 0 else 0.0)
        canvas = reverse_v(canvas)

        # Use number 0.6 to mark visited cell
        if mark_visited:
            for pos in self.visited:
                canvas[pos[0], pos[1]] = 0.6
        
        # Use 0.3 to mark position of agent
        canvas[curr_row, curr_col] = 0.3

        # Use 0.9 to mark position of end
        canvas[self.end[0], self.end[1]] = 0.9
        return canvas

    def act(self, action: Action):
        reward, mode = self.cal_reward(action)

        self.tol_reward += reward

        if mode != Mode.INVALID:
            self.curr_loc = self._apply_action(action)
            self.visited.add(self.curr_loc)

            if mode == Mode.END:
                return self.observe(), reward, mode

            if self.tol_reward <= self.reward_lower_bound:
                mode = Mode.TERMINATED

        return self.observe(), reward, mode
            
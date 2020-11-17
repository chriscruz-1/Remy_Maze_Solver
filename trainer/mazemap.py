import numpy as np
from enum import Enum

class Mode(Enum):
    VALID = 0
    INVALID = 1
    VISITED = 2
    PREVIOUS = 3
    END = 4
    TERMINATED = 5
    VISITED_PENALTY = 6

    def __int__(self):
        return self.value

class Action(Enum):
    LEFT = 0
    UP = 1
    RIGHT = 2
    DOWN = 3
    # JUMP = 4

    def __int__(self):
        return self.value

class MazeMap:
    def __init__(self, map, start=(0, 0), end=None):
        self.maze = np.array(map)
        self.height, self.width = self.maze.shape

        # Mark the start position and end position
        self.start = start
        self.end = (self.height - 1, self.width - 1) if end == None else end

        # Mark the current location of our agent.
        self.curr_loc = start
        self.prev_loc = None

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

        # Counter to penalize agent if it only stays on visited cells
        self.visit_in_row = 0


    def get_state_size(self):
        return len(self.state.flatten())

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
            curr_col -= 1
        elif action == Action.RIGHT:
            curr_col += 1
        elif action == Action.UP:
            curr_row -= 1
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
            elif next_loc in self.visited and self.visit_in_row > 10:
                # agent stuck looping on visited cells, penalize
                return (-15, Mode.VISITED_PENALTY)
            elif next_loc == self.prev_loc:
                return(-5, Mode.PREVIOUS)
            elif next_loc in self.visited:
                return (-1, Mode.VISITED)
            else:
                return (-0.5, Mode.VALID)

    # Get the current map and location of agent
    def observe(self, mark_visited=False, reshape=True):
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
        if reshape:
            return canvas.reshape(1, -1)
        return canvas
    
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
            self.prev_loc = self.curr_loc
            self.curr_loc = self._apply_action(action)
            self.visited.add(self.curr_loc)

            if mode == Mode.VISITED or mode == Mode.PREVIOUS or mode == Mode.VISITED_PENALTY:
                self.visit_in_row += 1
            else:
                self.visit_in_row = 0

            if mode == Mode.END:
                return self.observe(), reward, mode

            if self.tol_reward <= self.reward_lower_bound:
                mode = Mode.TERMINATED

        return self.observe(), reward, mode
            
    def print_maze(self,mouse_char='mm',end_char='E',wall_char='██',empty_char='  ',edge_char='░'):
        canvas = self.observe(reshape=False)
        width, height = canvas.shape
        # Print maze top boundary
        print(edge_char * (2* len(canvas) + 2))
        for j in range(height):
            # Print maze left boundary
            print(edge_char, end = '')
            for i in range(width):
                # Print maze contents row by row
                if canvas[j][i] == .3:
                    print(mouse_char + '', end = '')
                elif canvas[j][i] == 1:
                    print(wall_char + '', end = '')
                elif canvas[j][i] == 0:
                    print(empty_char + '', end = '')
                elif canvas[j][i] == .9:
                    print(end_char*2 + '', end = '')
                else:
                    print(str(canvas[i][j])*2 + '', end = '')
            # Print maze right boundary
            print(edge_char)
        # Print maze bottom boundary
        print(edge_char * (2* len(canvas) + 2))

    def path_to_end(self):
        # Get observed copy of maze
        canvas = self.observe(reshape=False)
        # Initialize arrays for BFS
        queue = []
        visited = set()
        dist = [[np.Inf] * self.width for i in range(self.height)]
        prev_cell = [[False] * self.width for i in range(self.height)]

        # Add current location initial point
        row,col = self.curr_loc
        visited.add(self.curr_loc);
        dist[col][row] = 0;
        queue.append(self.curr_loc);

        found = False
        # Iterate through queue until exit is found
        while len(queue) > 0:
            if found:
                break
            row,col = queue.pop(0)
            cell_list = []

            # Add unvisited neighbors to queue
            if row != self.width - 1:
                cell_list.append((row + 1, col))

            if row > 0:
                cell_list.append((row - 1, col))

            if col != self.height - 1:
                cell_list.append((row, col + 1))

            if col > 0:
                cell_list.append((row, col - 1))

            for cell in cell_list:
                if cell not in visited:
                    if canvas[cell] != 1:
                        #print("adding cell", cell)
                        # Add new cell to visited set
                        visited.add(cell)
                        #print(col,row)
                        # Calculate distance from starting point
                        dist[cell[1]][cell[0]] = dist[col][row] + 1
                        prev_cell[cell[1]][cell[0]] = (row,col)
                        queue.append(cell)
                        #print("value at cell:", canvas[cell])
                        # If we find the exit, we are done
                        if canvas[cell] == 0.9:
                            found = True
                            #print("found exit at ", cell)
                            break

        # Retrieve shortest path by going backwards through the previous cell array
        shortest_path = []
        distance = dist[cell[1]][cell[0]]
        cur_cell = cell
        while cur_cell != self.curr_loc:
            shortest_path.insert(0, cur_cell)
            cur_cell = prev_cell[cur_cell[1]][cur_cell[0]]

        return shortest_path, distance

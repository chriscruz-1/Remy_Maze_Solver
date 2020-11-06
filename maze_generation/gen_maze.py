import random
from time import perf_counter 
import hashlib
#random.seed(126)

class maze_class:
	def __init__(self, dim, max_cluster_size):
   		self.dimension = dim
   		self.max_cluster_size = max_cluster_size
   		self.points_list = []
   		self.maze = []
   		self.validated = False
   		self.empty_points = [] # List containing points in the maze that do not contain walls
   		self.valid = []
   		self.invalid = []
   		self.init_maze()

	def init_maze(self):
		# Initialize point list
		for i in range(self.dimension):
			for j in range(self.dimension):
				self.points_list.append((i,j))

		#print(self.points_list)


		# Initialize self.maze
		
		# Add self.dimensions to self.maze
		for i in range(self.dimension):
			self.maze.append([])
		#print(self.maze)

		# Assign all initial points to 0
		for i in range(self.dimension):
			for j in range(self.dimension):
				self.maze[i].append(0)

	def build_maze(self):
		# Get random points from point list
		for num in range(self.dimension**2):
			index = random.randint(0, len(self.points_list) - 1)
			cur_point = self.points_list.pop(index)
			# Check if we can place this point as a wall in the maze
			can_place = validate_point(cur_point, self.maze, self.max_cluster_size)
			if can_place:
				# If so, place wall, otherwise continue
				i = cur_point[0]
				j = cur_point[1]
				self.maze[i][j] = 1
			else:
				self.empty_points.append(cur_point)

	def find_connected(self, point):
		connected = []
		# Store the type of data we are looking for (i.e. wall or no wall)
		i = point[0]
		j = point[1]
		find_type = self.maze[i][j]

		connected.append(point)
		idx = 0

		# BFS on points of the same type as the intiial point until all connected points are found
		while idx < len(connected):
			cur_point = connected[idx]
			i = cur_point[0]
			j = cur_point[1]

			try:
				if self.maze[i+1][j] == find_type:
					if (i+1,j) not in connected:
						connected.append((i+1,j))
			except:
				pass
			try:
				if self.maze[i][j+1] == find_type:
					if (i,j+1) not in connected:
						connected.append((i,j+1))
			except:
				pass
			try:
				if self.maze[i-1][j] == find_type:
					if i - 1 >= 0:
						if (i-1,j) not in connected:
							connected.append((i-1,j))
			except:
				pass
			try:
				if self.maze[i][j-1] == find_type:
					if j - 1 >= 0:
						if (i,j-1) not in connected:
							connected.append((i,j-1))
			except:
				pass
			idx += 1
		return connected

	def get_valid_empty(self, points):
		# Get a list of empty spaces that are valid (able to be reached from any other valid point in the maze)
		points = set(points)

		# Store a list of all connected graphs
		connected_graphs = []

		# Iterate through all points and find their full graphs
		while len(points) > 0:
			cur_point = points.pop()
			connected = self.find_connected(cur_point)
			first = True
			for item in connected:
				if item == cur_point:
					continue
				# Remove found points from point list
				points.remove(item)
			print(len(points)) 
			# Add new graph to graph list
			connected_graphs.append(connected)

		# Find largest graph - this will be our traverable maze
		max_len = 0	
		max_idx = 0
		cur_idx = 0
		for graph in connected_graphs:
			cur_len = len(graph)
			if cur_len > max_len:
				max_len = cur_len
				max_idx = cur_idx 
			cur_idx += 1

		# Set the largest graph to our valid set
		valid = connected_graphs.pop(max_idx)

		# Set the smaller graphs to be part of the invalid set
		invalid = []
		for item in connected_graphs:
			invalid += item

		self.valid = valid
		self.invalid = invalid
		self.validated = True

	def fill_invalid(self):
		# Fill invaid empty spaces with walls

		# If we haven't found valid and invalid empty spaces already, do it now
		if not self.validated:
			self.get_valid_empty(self.empty_points)

		print(self.invalid)

		# Fill invalid spaces
		for point in self.invalid:
			print(point)
			i = point[0]
			j = point[1]
			self.maze[i][j] = 1
		#print("filled invalid")

	def place_special(self, amount, char):
		# Randomly place 'amount' amount of special characters in valid locations

		# If we haven't found valid and invalid empty spaces already, do it now
		if not self.validated:
			self.get_valid_empty(self.empty_points)

		# Get random points from valid point list
		for num in range(amount):
			index = random.randint(0, len(self.valid) - 1)

			# Place special point
			cur_point = self.valid.pop(index)
			i = cur_point[0]
			j = cur_point[1]
			self.maze[i][j] = char
		#print('char:',char)
		#print('placed special')

	def get_hash(self):
		# Convert maze to str then hash
		expanded_maze = []
		for array in self.maze:
			expanded_maze += array
		expanded_maze = [str(val) for val in expanded_maze]
		maze_str = "".join(expanded_maze).encode('utf-8')

		# Hash maze
		k = hashlib.md5()
		k.update(maze_str)
		return k.hexdigest()

	def maze_to_csv(self):
		# Convert each row in the maze into a csv row and return
		output = ""
		for row in self.maze:
			row = [str(val) for val in row]
			new_row = ",".join(row)
			new_row += '\n'
			output += new_row
		return output


def analyze_adjacent(index,maze):
	i = index[0]
	j = index[1]
	has_wall = []
	has_edge_point = False
	# Check if point has adjacent walls

	# Top wall edge case
	if i != 0:
		if maze[i - 1][j] == 1:
			has_wall.append((i - 1, j))
		# Top left edge case
		if j != 0:
			if maze[i - 1][j - 1] == 1:
				has_wall.append((i - 1, j - 1))
		# Top right edge case
		if j != len(maze) - 1:
			if maze[i - 1][j + 1] == 1:
				has_wall.append((i - 1, j + 1))
	else:
		has_edge_point = True

	# Bottom wall edge case
	if i != len(maze) - 1:
		if maze[i + 1][j] == 1:
			has_wall.append((i + 1, j))
		# Bottom left edge case
		if j != 0:
			if maze[i + 1][j - 1] == 1:
				has_wall.append((i + 1, j - 1))
		# Bottom right edge case
		if j != len(maze) - 1:
			if maze[i + 1][j + 1] == 1:
				has_wall.append((i + 1, j + 1))
	else:
		has_edge_point = True
	# Left wall edge case
	if j != 0:
		if maze[i][j - 1] == 1:
			has_wall.append((i, j - 1))
	else:
		has_edge_point = True

	# Right wall edge case
	if j != len(maze) - 1:
		if maze[i][j + 1] == 1:
			has_wall.append((i, j + 1))
	else:
		has_edge_point = True

	# Return the list of adjacent points and whether or not the maze edge was reached
	if len(has_wall) > 0:
		return (has_wall, has_edge_point)
	else:
		return (None, has_edge_point)

def validate_point(index,maze, max_cluster_size = None):
	# Store list of points to check for walls, starting with the given point
	to_check = [index]
	# Maintain a list of already checked points so we don't infinite loop
	# There's probably a better way of  doing this
	already_checked = [] 
	edge_touch_count = 0
	while len(to_check) > 0:
		# Grab first point from queue
		cur_point = to_check.pop(0)
		if cur_point in already_checked:
			continue
		# Get adjacent walls for point and add to check list
		new_points = analyze_adjacent(cur_point,maze)
		if new_points[0]:
			for point in new_points[0]:
				to_check.append(point)
		# Add completed point to the checked list
		already_checked.append(cur_point)
		# If we are touching two maze edges then we've formed an impassable wall
		# Point is invalid
		if new_points[1] == True:
			edge_touch_count += 1
		if edge_touch_count > 1:
			return False
		# If the wall cluster is too big, do not place
		if max_cluster_size:
			if len(already_checked) >= max_cluster_size:
				return False
	
	return True

def print_maze(maze,pretty=False,wall_char='██',empty_char='  ',edge_char='░'):
	if pretty:
		# Print maze top boundary
		print(edge_char * (2* len(maze) + 2))
		for j in range(len(maze)):
			# Print maze left boundary
			print(edge_char, end = '')
			for i in range(len(maze)):
				# Print maze contents row by row
				if maze[i][j] == 1:
					print(wall_char + '', end = '')
				elif maze[i][j] == 0:
					print(empty_char + '', end = '')
				else:
					print(maze[i][j]*2 + '', end = '')
			# Print maze right boundary
			print(edge_char)
		# Print maze bottom boundary
		print(edge_char * (2* len(maze) + 2))

	else:
		for row in maze:
			print(row)




if __name__ == "__main__":
	start = perf_counter()  

	maze = maze_class(dim = 25, max_cluster_size = 10)
	maze.build_maze()

	# Check maze initialization
	#print_maze(maze.maze)
	#print("\n\n------------------------------\n\n")



	end = perf_counter()  

	print_maze(maze.maze,pretty=True)

	maze.fill_invalid()
	print_maze(maze.maze,pretty=True)

	maze.place_special(3,'C')
	print_maze(maze.maze,pretty=True)

	maze.place_special(3,'T')
	print_maze(maze.maze,pretty=True)

	print("Took",end - start, "seconds")
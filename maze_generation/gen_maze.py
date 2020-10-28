import random
from time import perf_counter 

#random.seed(126)


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
				else:
					print(empty_char + '', end = '')
			# Print maze right boundary
			print(edge_char)
		# Print maze bottom boundary
		print(edge_char * (2* len(maze) + 2))

	else:
		for row in maze:
			print(row)

start = perf_counter()  

dimension = 10

points_list = []

# Initialize point list
for i in range(dimension):
	for j in range(dimension):
		points_list.append((i,j))

print(points_list)


# Initialize maze
maze = []

# Add dimensions to maze
for i in range(dimension):
	maze.append([])
print(maze)

# Assign all initial points to 0
for i in range(dimension):
	for j in range(dimension):
		maze[i].append(0)

# Check maze initialization
print_maze(maze)
print("\n\n------------------------------\n\n")

# Get random points from point list
for num in range(dimension**2):
	index = random.randint(0, len(points_list) - 1)
	cur_point = points_list.pop(index)
	# Check if we can place this point as a wall in the maze
	can_place = validate_point(cur_point, maze, max_cluster_size=10)
	if can_place:
		# If so, place wall, otherwise continue
		i = cur_point[0]
		j = cur_point[1]
		maze[i][j] = 1

end = perf_counter()  

print_maze(maze,pretty=True)

print("Took",end - start, "seconds")

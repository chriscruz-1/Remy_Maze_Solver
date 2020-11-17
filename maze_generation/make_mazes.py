import gen_maze
import os
from time import perf_counter 

num = int(input("How many mazes do you want? (might be less due to hash collisions)"))
dim = int(input("What dimension?"))
flags = input("Any flags? (y/n)")
fill_invalid = 0
max_cluster_size = 10
do_print = False

if flags == 'y':
	do_print = input("Print mazes? (y/n)")
	if do_print == 'n':
		do_print = False
	max_cluster_size = int(input("Max cluster size? (num)"))
	fill_invalid = input("Fill invalid? (y/n)")

print("ok...")
start = perf_counter()  

maze_hashes = set()

if not os.path.exists('Maze Output'):
    os.makedirs('Maze Output')

base_path = "./Maze Output/"

# Attempt to generate num mazes 
for i in range(num):
	# Generate maze of dimension dim * dim and build
	maze = gen_maze.maze_class(dim = dim, max_cluster_size = max_cluster_size)
	maze.build_maze()

	# Print maze if applicable
	if do_print:
		gen_maze.print_maze(maze.maze,pretty=True)

	# Fill unreachable cells if applicable
	if fill_invalid:
		maze.fill_invalid()

	# Hash maze to ensure it's not a duplicate
	cur_hash = maze.get_hash()
	if cur_hash not in maze_hashes:
		maze_hashes.add(cur_hash)

		# If not, convert it to a csv and write to file
		data = maze.maze_to_csv()
		file_path = base_path + "m" + str(len(maze_hashes)) + ".csv"
		f = open(file_path, "w")
		f.write(data)
		f.close()
	else:
		print('Hash collision')

end = perf_counter()  
print("Generated", len(maze_hashes), "mazes in", end - start, "sec")

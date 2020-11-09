# This is not a correct or well-format unit test
# Just some simple testings.

from mazemap import MazeMap
from mazemap import Action
import numpy as np
from utils import show_map, update_map
import matplotlib.pyplot as plt

maze_test = np.array([
    [ 0., 1., 0., 0., 0., 0., 0., 0. ],
    [ 0., 0., 0., 1., 1., 0., 1., 0. ],
    [ 1., 1., 1., 0., 0., 0., 1., 0. ],
    [ 0., 0., 0., 0., 1., 1., 0., 0. ],
    [ 0., 1., 1., 1., 0., 0., 0., 1. ],
    [ 0., 1., 0., 0., 0., 0., 0., 1. ],
    [ 0., 0., 0., 1., 0., 0., 0., 1. ],
    [ 0., 0., 0., 1., 0., 0., 0., 0. ],
])

# def invert(x):
#     return 0 if x == 1 else 1

# invert_v = np.vectorize(invert)

# for row in invert_v(maze_test):
#     print('[', end=' ')
#     for index, col in enumerate(row):
#         if index == len(row) - 1:
#             print(col, end=' ')
#         else:
#             print(col, end=', ')
#     print(']', end=',\n')

def test_map_draw():
    maze_map = MazeMap(maze_test)
    map_img = show_map(maze_map)

    plt.pause(1)
    maze_map.act(Action.DOWN)
    update_map(map_img, maze_map)

    plt.pause(1)
    maze_map.act(Action.RIGHT)
    update_map(map_img, maze_map)

    plt.show()

# test_map_draw()
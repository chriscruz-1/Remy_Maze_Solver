# This is not a correct or well-format unit test
# Just some simple testings.
import sys
from keras.engine.training import Model
from mazemap import MazeMap, Mode
from mazemap import Action
import numpy as np
from utils import show_map, update_map, build_model
import matplotlib.pyplot as plt
import pandas as pd

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

def to_float(x):
    return x.astype(float)

df = pd.read_csv('./mazes/m10.csv', header=None)
df = df.apply(to_float)
maze_test = df.values


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

def play():
    try:
        model = build_model(maze_test)
        model.load_weights('maze_model.h5')

        maze_map = MazeMap(maze_test)
        maze_img = show_map(maze_map)

        game_over = False
        state = maze_map.observe()

        while not game_over:
            plt.pause(0.5)
            valid_actions = maze_map.get_valid_actions()

            if not valid_actions: break
            action = np.argmax(model.predict(state))
            state, reward, mode = maze_map.act(action)
            update_map(maze_img, maze_map)

            if mode == Mode.TERMINATED:
                print('Terminated')
                game_over = True
            elif mode == Mode.END:
                print('Reach the End')
                game_over = True
            elif mode == Mode.INVALID:
                print(f'Attemped Invalid Move {Action(action)}')

        plt.show()
    except KeyboardInterrupt:
        print("Force Quit the Game!")
        exit(1)

play()
# test_map_draw()
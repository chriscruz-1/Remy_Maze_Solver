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
import tensorflow as tf

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

df = pd.read_csv('./mazes/m1.csv', header=None)
df = df.apply(to_float)
maze_test = df.values

# Enable GPU memory auto resize, in case your get error due to GPU occupied by other applications
physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)

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
        maze_map.reset((1, 7))
        maze_img = show_map(maze_map)

        game_over = False
        state = maze_map.observe()

        while not game_over:
            plt.pause(0.5)
            valid_actions = maze_map.get_valid_actions()
            # print('valid: ', valid_actions)
            if not valid_actions: break

            # for index, pred in enumerate(model.predict(state)):
            #     print('index = ', index, end=', ')
            #     print('Action = ', Action(index), end=', ')
            #     print('pred = ', pred, end='..... One loop end\n')

            possible_move = [ pred if Action(index) in valid_actions else sys.float_info.min for index, pred in enumerate(model.predict(state)[0]) ]
            # print(possible_move)
            action = np.argmax(possible_move)
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
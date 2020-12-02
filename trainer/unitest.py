# This is not a correct or well-format unit test
# Just some simple testings.
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import argparse

from mazemap import MazeMap, Mode, Action
from utils import show_map, update_map, build_model, load_csv

def test_map_draw(maze):
    maze_map = MazeMap(maze)
    map_img = show_map(maze_map)

    plt.pause(1)
    maze_map.act(Action.DOWN)
    update_map(map_img, maze_map)

    plt.pause(1)
    maze_map.act(Action.RIGHT)
    update_map(map_img, maze_map)

    plt.show()

def play(maze, model_path):
    # Enable GPU memory auto resize, in case your get error due to GPU occupied by other applications
    physical_devices = tf.config.list_physical_devices('GPU')
    tf.config.experimental.set_memory_growth(physical_devices[0], True)

    try:
        model = build_model(maze)
        model.load_weights(model_path)

        maze_map = MazeMap(maze)
        maze_img = show_map(maze_map)

        game_over = False
        state = maze_map.observe()

        while not game_over:
            plt.pause(0.2)
            valid_actions = maze_map.get_valid_actions()

            if not valid_actions: break

            possible_move = [ pred if Action(index) in valid_actions else -sys.float_info.max for index, pred in enumerate(model.predict(state)[0]) ]
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--func_name', default='play', type=str, 
                        help='The test function you want to run.')
    parser.add_argument('--wkdir', default='./mazes', type=str,
                        help='The working directory of your input file. Default value will be provided if None')
    parser.add_argument('--filename', default='m1.csv', type=str,
                        help='The filename of your input file.')
    parser.add_argument('--model', default="maze_model.h5", type=str)
    
    args = parser.parse_args()

    wkdir = args.wkdir
    filename = args.filename
    file_path = os.path.join(wkdir, filename)

    input_file = load_csv(file_path)

    func_name = args.func_name

    if func_name == 'play':
        play(input_file, args.model)
    elif func_name == 'test_map_draw':
        test_map_draw(input_file)

# play()
# test_map_draw()
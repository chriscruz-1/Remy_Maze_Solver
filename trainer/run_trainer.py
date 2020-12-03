from utils import build_model, load_csv
from replay import Episode, ReplyBuffer
import numpy as np
from mazemap import Action, MazeMap, Mode
import tensorflowjs as tfjs
import tensorflow as tf
import pandas as pd
import math
import random
import os
import argparse
from time import perf_counter

# maze_test = np.array([
#     [ 0., 1., 0., 0., 0., 0., 0., 0. ],
#     [ 0., 0., 0., 1., 1., 0., 1., 0. ],
#     [ 1., 1., 1., 0., 0., 0., 1., 0. ],
#     [ 0., 0., 0., 0., 1., 1., 0., 0. ],
#     [ 0., 1., 1., 1., 0., 0., 0., 1. ],
#     [ 0., 1., 0., 0., 0., 0., 0., 1. ],
#     [ 0., 0., 0., 1., 0., 0., 0., 1. ],
#     [ 0., 0., 0., 1., 0., 0., 0., 0. ],
# ])

def load_mazes(directory='./mazes/', num_mazes=10):
    mazes = []
    cur_count = 0
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            filepath = os.path.join(directory, filename)
            # print(filepath)

            # Read csv into np array, then convert to MazeMap
            cur_maze = load_csv(filepath)
            mazes.append(MazeMap(cur_maze, name=filename))
        cur_count += 1

        if cur_count == num_mazes:
            break
    return mazes

# df = pd.read_csv('./mazes/m1.csv', header=None)
# df = df.apply(to_float)
# maze_test = df.values

# Enable GPU memory auto resize, in case your get error due to GPU occupied by other applications
physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)

def start_train(model,
                maze: MazeMap, 
                num_epoch = 15000, 
                max_buffer = 1000, 
                sample_size = 50,
                gamma = 0.9,
                load_path = None,
                save_path = None):
    global epsilon

    if save_path == None:
        save_path = 'maze_model.h5'

    if load_path != None:
        print(f'Load weight from ./models_h5/{load_path}')
        model.load_weights('./models_h5/' + load_path)

    maze_map = maze

    replay_buf: ReplyBuffer = ReplyBuffer(model, maze_map.get_state_size(), max_buffer, gamma)

    history = []
    loss = 0.0
    hsize = maze.get_state_size() // 2
    win_rate = 0.0
    total_time = 0

    # Run training epoch
    for epoch in range(num_epoch):
        loss = 0.0
        is_over = False
        epoch_start = perf_counter()

        if epoch % 2 == 1 and win_rate < 0.8:
            # Randomly pick a start, can improve the performance sometimes.
            # No guarantee.
            point = random.choice(maze_map.free)
            maze_map.reset(point)
        else:
            maze_map.reset()

        curr_state = maze_map.observe()

        num_episode = 0

        while not is_over:
            valid_actions = maze_map.get_valid_actions()

            if len(valid_actions) == 0:
                break

            # Explore
            action = np.random.choice(valid_actions)
            if np.random.rand() > epsilon:
                # Exploit
                action = np.argmax(replay_buf.predict(curr_state))

            prev_state = curr_state
            curr_state, reward, mode = maze_map.act(action)

            if mode == Mode.END:
                history.append(1)
                is_over = True
            elif mode == Mode.TERMINATED:
                history.append(0)
                is_over = True
            else:
                is_over = False

            # maze_map.print_maze(mouse_char=':>')

            episode = Episode(prev_state, curr_state, action, reward, mode)
            replay_buf.log(episode)
            num_episode += 1

            inputs, outputs = replay_buf.sampling(sample_size)
            train_history = model.fit(inputs, outputs, epochs=20, batch_size=64, verbose=0)
            loss = train_history.history['loss'][-1]
        
        win_rate = np.sum(np.array(history)) / len(history) if len(history) < hsize else np.sum(np.array(history[-hsize:])) / hsize
        new_epsilon = (math.exp(-win_rate)) * 0.9 / ((win_rate + 1) ** 4)
        epsilon = new_epsilon
        #  if new_epsilon < epsilon else epsilon
        
        epoch_end = perf_counter()
        epoch_time = epoch_end - epoch_start
        total_time += epoch_time
        print(f'Epoch {epoch}/{num_epoch} | Loss: {loss:.2f} | Episodes: {num_episode} | Win Count: {np.sum(np.array(history))} | \nWin Rate: {win_rate:.3f} | Epoch Time: {epoch_time:.2f}s | Total Time: {total_time:.2f}s | Epsilon: {epsilon:.2f}')
        
        if win_rate == 1.0:
            print('Reach 100% win rate')
            break

        if epoch % 15 == 0:
            h5file = "./models_h5/" + save_path
            model.save_weights(h5file + '.h5', overwrite=True)
            tfjs.converters.save_keras_model(model, './models_json/' + save_path)
            
            print(f'Saved model in {save_path}')


    h5file = "./models_h5/" + save_path
    model.save_weights(h5file + '.h5', overwrite=True)        
    tfjs.converters.save_keras_model(model, './models_json/' + save_path)
    print(f'Saved model in {save_path}')

# This hyperparamter is used to control the ratio of exploration and exploitation
epsilon = 0.9

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--wkdir', default='./mazes', type=str,
                        help='The working directory of your input file. Default value will be provided if None')
    parser.add_argument('--filename', default='m1.csv', type=str,
                        help='The filename of your input file.')
    parser.add_argument('--load_path', default=None, type=str,
                        help='Provide the path of model file to resume last training.')
    parser.add_argument('--save_path', default=None, type=str,
                        help='Provide the path of model file to be saved for future use.')
    parser.add_argument('--log_time', default=False, type=bool,
                        help='Whether log the training time of each map.')                
    
    args = parser.parse_args()

    wkdir = args.wkdir
    filename = args.filename
    file_path = os.path.join(wkdir, filename)

    input_file = load_csv(file_path)
    maze_map = MazeMap(input_file, name=filename)
    model = build_model(maze_map._maze)
    print(f"Start map {maze_map.name}")


    # Currently we only train on the one map. 
    # since multiple map won't be a good choice based on our current implementation
    start_train(model, maze_map, 10000, 8 * maze_map.get_state_size(), load_path=args.load_path, save_path=args.save_path)
    print(f"Finished training map {maze_map.name}")


# maze_map = MazeMap(maze_test)
# mazes = load_mazes()
# model = build_model(mazes[0]._maze)

# for index, maze_map in enumerate(mazes):
#     if index == 0:
#         print(f"Start map {maze_map.name}")
#         maze_map.print_maze(mouse_char=':>')
#         start_train(model, maze_map, 20000, 8 * maze_map.get_state_size())
#         print(f"Finished training map {maze_map.name}")

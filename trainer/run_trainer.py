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
        print(f'Load weight from {load_path}')
        model.load_weights(load_path)

    maze_map = maze

    replay_buf: ReplyBuffer = ReplyBuffer(model, maze_map.get_state_size(), max_buffer, gamma)

    history = []
    loss = 0.0
    hsize = maze.get_state_size() // 2

    # Run training epoch
    for epoch in range(num_epoch):
        if epoch == 250:
            epsilon = 0.8

        loss = 0.
        is_over = False

        if epoch != 0:
            point = random.choice(maze_map.free)
            maze_map.reset(point)

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

        print(f'Epoch {epoch}/{num_epoch} | Loss: {loss:.2f} | Episodes: {num_episode} | Win Count: {np.sum(np.array(history))} | Win Rate: {win_rate}')

        new_epsilon = (math.exp(-win_rate)) * 0.9 / ((win_rate + 1) ** 4)
        epsilon = new_epsilon if new_epsilon < epsilon else epsilon
        
        if win_rate == 1.0:
            print('Reach 100% win rate')
            break

        if epoch % 15 == 0:
            h5file = save_path
            model.save_weights(h5file, overwrite=True)
            tfjs.converters.save_keras_model(model, './')
            
            print(f'Saved model in {save_path}')


    h5file = save_path
    model.save_weights(h5file, overwrite=True)        
    tfjs.converters.save_keras_model(model, './')
    print(f'Saved model in {save_path}')

# This hyperparamter is used to control the ratio of exploration and exploitation
epsilon = 0.9

# maze_map = MazeMap(maze_test)
mazes = load_mazes()
model = build_model(mazes[0]._maze)

for index, maze_map in enumerate(mazes):
    if index == 0:
        print(f"Start map {maze_map.name}")
        start_train(model, maze_map, 400, 8 * maze_map.get_state_size())
        print(f"Finished training map {maze_map.name}")

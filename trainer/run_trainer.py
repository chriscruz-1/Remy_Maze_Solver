from replay import Episode, ReplyBuffer
from keras.models import Sequential
from keras.layers.core import Dense
# from keras.optimizers import SGD , Adam, RMSprop
from keras.layers.advanced_activations import PReLU
import numpy as np
from mazemap import Action, MazeMap, Mode
import json

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

# This model structure is identical to this article
# https://www.samyzaf.com/ML/rl/qmaze.html
# TODO: Our next goal is to test out whether there is other suitable model structure
def build_model(maze, lr=0.001):
    model = Sequential()
    model.add(Dense(maze.size, input_shape=(maze.size,)))
    model.add(PReLU())
    model.add(Dense(maze.size))
    model.add(PReLU())
    model.add(Dense(len(Action)))
    model.compile(optimizer='adam', loss='mse')
    return model

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
        save_path = 'maze_model'

    if load_path != None:
        print(f'Load weight from {load_path}')
        model.load_weights(load_path)

    maze_map = MazeMap(maze)

    replay_buf: ReplyBuffer = ReplyBuffer(model, maze_map.get_state_size(), max_buffer, gamma)

    history = []
    loss = 0
    hsize = maze.get_state_size // 2

    # Run training epoch
    for epoch in range(num_epoch):
        loss = 0.
        is_over = False

        curr_state = maze.observe()

        num_episode = 0

        while not is_over:
            valid_actions = maze.get_valid_actions()

            if len(valid_actions) == 0:
                break

            # Explore
            action = np.random.choice(valid_actions)
            if np.random.rand() > epsilon:
                # Exploit
                action = np.argmax(replay_buf.predict(curr_state))

            prev_state = curr_state
            curr_state, reward, mode = maze.act(action)

            if mode == Mode.END:
                history.append(1)
                is_over = True
            elif mode == Mode.TERMINATED:
                history.append(0)
                is_over = True
            else:
                is_over = False

            episode = Episode(prev_state, curr_state, action, reward, mode)
            replay_buf.log(episode)
            num_episode += 1

            inputs, outputs = replay_buf.sampling(sample_size)
            train_history = model.fit(inputs, outputs, epochs=8, batch_size=16, verbose=0)
            loss = train_history.history['loss']
        
        win_rate = 0.0 if len(history) < hsize else np.sum(np.array(history[-hsize:])) / len(hsize)

        print(f'Epoch {epoch}/{num_epoch} | Loss: {loss:.2f} | Episodes: {num_episode} | Win Count: {np.sum(np.array(history))} | Win Rate: {win_rate}')

        if win_rate > 0.9:
            epsilon = 0.05
        
        if win_rate == 1.0:
            print('Reach 100% win rate')
            break

        if epoch % 10 == 0:
            with open(save_path + '.json', "w") as outfile:
                json.dump(model.to_json(), outfile)


    with open(save_path + '.json', "w") as outfile:
        json.dump(model.to_json(), outfile)




# This hyperparamter is used to control the ratio of exploration and exploitation
epsilon = 0.1
maze_map = MazeMap(maze_test)
model = build_model(maze_test)
start_train(model, maze_map, 1000, 8 * maze_map.get_state_size())

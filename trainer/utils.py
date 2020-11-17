from matplotlib.image import AxesImage
import matplotlib.pyplot as plt
import numpy as np
from mazemap import Action, MazeMap
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
# from keras.optimizers import SGD , Adam, RMSprop
from tensorflow.keras.layers import PReLU

# This function is used to visualize the game process by using matplot
# Credits to https://www.samyzaf.com/ML/rl/qmaze.html
# Some tweaks are applied.
def show_map(maze_map: MazeMap):
    plt.grid('on')
    height, width = maze_map.dime()
    ax = plt.gca()
    ax.set_xticks(np.arange(0.5, height, 1))
    ax.set_yticks(np.arange(0.5, width, 1))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    canvas = maze_map.get_map_for_draw(True)
    img = plt.imshow(canvas, interpolation='none', cmap='gray')
    return img

def update_map(img, maze_map):
    img.set_data(maze_map.get_map_for_draw(True))
    plt.draw()

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

def build_model_reduced(maze, lr=0.001):
    model = Sequential()
    model.add(Dense(maze.size/4, input_shape=(maze.size,)))
    model.add(PReLU())
    model.add(Dense(maze.size/8))
    model.add(PReLU())
    model.add(Dense(len(Action)))
    model.compile(optimizer='adam', loss='mse')
    return model
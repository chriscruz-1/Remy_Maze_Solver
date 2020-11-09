from matplotlib.image import AxesImage
import matplotlib.pyplot as plt
import numpy as np
from mazemap import MazeMap

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
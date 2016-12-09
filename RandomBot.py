import hlt
import random
import numpy as np


myID, game_map = hlt.get_init()
hlt.send_init("RandomPythonBot")

while True:
    game_map.get_frame()
    moves = [hlt.Move(x, y, random.choice(range(5)))
             for (x, y) in np.transpose(np.where(game_map.owners == myID))]
    hlt.send_frame(moves)

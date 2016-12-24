import hlt
import random
import numpy as np


game_map = hlt.GameMap()
hlt.send_init("RandomNumpyBot")


while True:
    game_map.get_frame()
    owned_locs = np.transpose(np.where(game_map.owners == game_map.my_id))
    moves = [hlt.Move(x, y, random.choice(range(5)))
             for (x, y) in owned_locs]
    hlt.send_frame(moves)

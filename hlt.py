"""
A Python-based Halite starter-bot framework.
A barebones, numpy-inspired fork of erdman's hlt.py that focuses on
assembling prod, strn and owner numpy matrices as quickly as possible.
Moves are tuples of x, y and dir, where dir behaves as in the
base starter.

GameMap.prod and GameMap.strn are the production and strength respectively.
GameMap.owner contains the each cell's owner.
"""

import sys
import numpy as np
from collections import namedtuple


Move = namedtuple('Move', 'x y dir')


class GameMap:
    """Hold prod, strn and owners as separate x*y numpy matrices
    and update on each new frame.
    """

    def __init__(self, size_string, prod_string, my_id):
        self.width, self.height = tuple(map(int, size_string.split()))
        self.my_id = my_id

        prod = [int(p) for p in prod_string.split()]
        self.prod = np.array(prod, dtype=int).reshape((self.height, self.width)).T

        self.get_frame()

    def get_frame(self, map_string=None):
        if map_string is None:
            map_string = get_string()

        split_string = map_string.split()
        owners = np.zeros(self.width * self.height, dtype=int)

        ctr, strloc = 0, 0
        while ctr < self.width * self.height:
            increment = int(split_string[strloc])
            owner_id = int(split_string[strloc + 1])
            owners[ctr:(ctr + increment)] = owner_id
            ctr += increment
            strloc += 2
        self.owners = owners.reshape((self.height, self.width)).T

        strn = [int(s) for s in split_string[strloc:]]
        self.strn = np.array(strn, dtype=int).reshape((self.height, self.width)).T


def send_string(s):
    sys.stdout.write(s)
    sys.stdout.write('\n')
    sys.stdout.flush()


def get_string():
    return sys.stdin.readline().rstrip('\n')


def get_init():
    my_id = int(get_string())
    m = GameMap(get_string(), get_string(), my_id)
    return my_id, m


def send_init(name):
    send_string(name)


def send_frame(moves):
    send_string(' '.join(str(move.x) + ' ' + str(move.y) + ' ' + str(move.dir)
                         for move in moves))

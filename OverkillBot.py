"""
Implementation of @nmalaguti's OverkillBot in the numpy paradigm.

Extends the base GameMap with new derived features and methods making
use of numpy ndarray math and scipy filters.
"""


import hlt
import numpy as np
from hlt import Move
from scipy.ndimage.filters import generic_filter


BIGINT = 99999


class ImprovedGameMap(hlt.GameMap):
    """Adds enough jank to make OverkillBot possible."""
    def __init__(self):
        super().__init__()  # Runs the GameMap base init

        # More effective to calculate distances and neighbours up
        # front and forever in the 15 seconds of init.
        self.dists = self.get_distances(self.width, self.height)
        self.nbrs = self.get_neighbours(self.width, self.height)

    def update(self):
        """Derive everything that changes per frame."""
        # Boolean arrays for owned, blank and enemy cells
        self.owned = self.owners == self.my_id
        self.blank = self.owners == 0
        self.enemy = np.ones_like(self.owned) - self.owned - self.blank

        # The heuristics for OverkillBot, calculated for every square
        # with numpy array arithmetic
        self.splash_dmg = self.plus_filter(self.strn * self.enemy, sum)
        self.heuristic = self.prod / np.maximum(1, self.strn)
        self.heuristic += self.splash_dmg
        self.heuristic[self.owned] = -1

        # Calculate the border cells using scipy filters
        self.border = self.plus_filter(self.enemy + self.blank, max) * self.owned

        # Get an iterable array of coordinate pairs of all the Trues in owned
        self.owned_locs = np.transpose(np.nonzero(self.owned))

    def path_towards(self, x, y, tx, ty):
        """For an owned cell at x, y, and a target cell at tx, ty,
        return the cardinal direction to move along.
        Moves along the shortest nonzero cardinal first.
        """
        dists = np.array([
            (y - ty) % self.height,
            (tx - x) % self.width,
            (ty - y) % self.height,
            (x - tx) % self.width
        ])
        dists[dists == 0] = BIGINT
        distorder = np.argsort(dists)
        return distorder[0] + 1

    @staticmethod
    def get_distances(w, h):
        """Populate a 4-dimensional np.ndarray where:
            arr[x, y, a, b]
        yields the shortest distance between (x, y) and (a, b).
        Indexing as:
            arr[x, y]
        yields a 2D array of the distances from (x, y) to every
        other cell.
        Would love to hear a more elegant way to calculate this!
        """
        base_dists = np.zeros((w, h), dtype=int)
        all_dists = np.zeros((w, h, w, h), dtype=int)

        for x in range(w):
            for y in range(h):
                min_x = min((x - 0) % w, (0 - x) % w)
                min_y = min((y - 0) % h, (0 - y) % h)
                base_dists[x, y] = max(min_x + min_y, 1)

        for x in range(w):
            for y in range(h):
                all_dists[x, y] = np.roll(np.roll(base_dists, x, 0), y, 1)

        return all_dists

    @staticmethod
    def get_neighbours(w, h):
        """Populate a dictionary keyed by all (x, y) where the
        elements are the neighbours of that cell ordered N, E, S, W.
        """
        def get_local_nbrs(x, y):
            return [(x, (y - 1) % h),
                    ((x + 1) % w, y),
                    (x, (y + 1) % h),
                    ((x - 1) % w, y)]

        nbrs = {(x, y): get_local_nbrs(x, y)
                for x in range(w) for y in range(h)}

        return nbrs

    @staticmethod
    def plus_filter(X, f):
        """Scans a +-shaped filter over the input matrix X, applies
        the reducer function f and returns a new matrix with the same
        dimensions of X containing the reduced values.
        This kind of technique is useful for a tonne of stuff, and
        very efficient.
        """
        footprint = np.array([[0, 1, 0],
                              [1, 1, 1],
                              [0, 1, 0]])
        proc = generic_filter(X, f, footprint=footprint, mode='wrap')
        return proc


def get_move(x, y, gmap):
    # If on the border, hit the neighbour with the highest heuristic
    if gmap.border[x, y]:
        heur_vals = [gmap.heuristic[nx, ny]
                     for (nx, ny) in gmap.nbrs[x, y]]
        ni = np.argmax(heur_vals)
        nx, ny = gmap.nbrs[x, y][ni]

        # ...if strong enough to capture it
        if gmap.strn[nx, ny] > gmap.strn[x, y]:
            return Move(x, y, 0)
        else:
            return Move(x, y, ni + 1)

    # Stay if not at least 5x stronger than the production value
    if gmap.strn[x, y] < (gmap.prod[x, y] * 5):
        return Move(x, y, 0)

    # Else find the closest border square
    dist_to_brdr = np.zeros_like(gmap.prod)
    dist_to_brdr.fill(BIGINT)
    dist_to_brdr[np.nonzero(gmap.border)] = \
        gmap.dists[x, y][np.nonzero(gmap.border)]

    # ..and move towards it
    tx, ty = np.unravel_index(dist_to_brdr.argmin(), dist_to_brdr.shape)
    direction = gmap.path_towards(x, y, tx, ty)
    return Move(x, y, direction)


game_map = ImprovedGameMap()
hlt.send_init("OverkillNumpyBot")


while True:
    game_map.get_frame()
    game_map.update()
    moves = [get_move(x, y, game_map) for (x, y) in game_map.owned_locs]
    hlt.send_frame(moves)

import hlt
import numpy as np
from hlt import Move
from scipy.ndimage.filters import generic_filter


BIGINT = 99999


class ImprovedGameMap(hlt.GameMap):

    def __init__(self):
        super().__init__()
        self.dists = self.get_distances(self.width, self.height)
        self.nbrs = self.get_neighbours(self.width, self.height)
        self.turn = -1

    def update(self):
        self.owned = self.owners == self.my_id
        self.blank = self.owners == 0
        self.enemy = np.ones_like(self.owners) - self.owned - self.blank

        self.splash_dmg = self.plus_filter(self.strn * self.enemy, sum)
        self.heuristic = self.prod / np.maximum(1, self.strn)
        self.heuristic += self.splash_dmg
        self.heuristic[np.nonzero(self.owned)] = -1

        self.border = self.plus_filter(self.enemy + self.blank, max) * self.owned

        self.owned_locs = np.transpose(np.nonzero(self.owned))

        self.turn += 1

    def path_towards(self, x, y, tx, ty):
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
        """Todo: explain."""
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
        """Apply function f on matrix X with a plus-shaped filter
        accounting for edge wrapping.
        """
        footprint = np.array([[0, 1, 0],
                              [1, 1, 1],
                              [0, 1, 0]])
        proc = generic_filter(X, f,
                              footprint=footprint,
                              mode='wrap')
        return proc


def get_move(x, y, game_map):
    if game_map.border[x, y]:
        heur_vals = [game_map.heuristic[nx, ny]
                     for (nx, ny) in game_map.nbrs[x, y]]
        ni = np.argmax(heur_vals)
        nx, ny = game_map.nbrs[x, y][ni]

        if game_map.strn[nx, ny] > game_map.strn[x, y]:
            return Move(x, y, 0)
        else:
            return Move(x, y, ni + 1)

    if game_map.strn[x, y] < (game_map.prod[x, y] * 5):
        return Move(x, y, 0)

    dist_to_brdr = np.zeros_like(game_map.prod)
    dist_to_brdr.fill(BIGINT)
    dist_to_brdr[np.nonzero(game_map.border)] = game_map.dists[x, y][np.nonzero(game_map.border)]

    tx, ty = np.unravel_index(dist_to_brdr.argmin(), dist_to_brdr.shape)

    direction = game_map.path_towards(x, y, tx, ty)

    return Move(x, y, direction)


game_map = ImprovedGameMap()
hlt.send_init("HumptyNumpy")


while True:
    game_map.get_frame()
    game_map.update()

    moves = [get_move(x, y, game_map) for (x, y) in game_map.owned_locs]

    hlt.send_frame(moves)

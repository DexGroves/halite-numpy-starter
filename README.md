# halite-numpy-starter
Alternative Halite starter package for Python3.

A barebones, numpy-inspired fork of [erdman](https://github.com/erdman/alt-python3-halite-starter)'s hlt.py that focuses on
minimally assembling the game state as production, strength and owner numpy matrices as quickly as possible. This all gets jammed in `GameMap` as `.prod`, `.strn` and `.owner`.

Moves are tuples of x, y and dir, where dir behaves as in the base starter.

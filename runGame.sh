#!/bin/bash

if hash python3 2>/dev/null; then
    halite -d "30 30" "python3 RandomBot.py"  "python3 RandomBot.py"

else
    halite -d "30 30" "python RandomBot.py" "python RandomBot.py"
fi

#!/bin/bash

# Generate a random minute (0 to 59)
MINUTE=$((RANDOM % 60))

# Generate a random hour (13 to 15)
HOUR=$((RANDOM % 3 + 13))

# Sleep until the random time
at -M $HOUR:$MINUTE <<END
python3 /home/ubuntu/fruits_jb_scraper/monster/monster_usa.py
END

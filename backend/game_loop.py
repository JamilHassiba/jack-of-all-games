"""Background tick loop driving every active game's state machine."""

import time
import traceback

from registry import rooms

TICK_RATE = 1 / 30  # 30 ticks per second


def game_loop():
    last_time = time.time()
    TICK_RATE = 1/30  # 30 ticks/sec
    while True:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time

        try:
            for room_id, room in rooms.items():
                room.game.Update(dt)  # pass delta time in seconds
        except Exception as e:
            print("Error in game loop:", e)
            traceback.print_exc()

        time.sleep(TICK_RATE)


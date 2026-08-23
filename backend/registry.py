"""In-memory server state shared across routes and socket handlers.

Note: this lives in process memory, so it resets on restart and does not
survive multiple worker processes.
"""

rooms = {}                    # room_id -> Room
socketio_connected = {}       # sid -> Room
sid_player_obj_mapping = {}   # sid -> player object, needed to handle leaving rooms
socketio_rooms = []           # room ids seen by socket layer

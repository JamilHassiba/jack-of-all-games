"""Shared validation for socket handlers."""

from registry import rooms


# Validates to check whether the user is in a room, and that the room exists
# Returns true/false
def socket_validate(session):
    room_id = session.get("room") # User must be in a backend room
    if not room_id: print("Tried to connect frontend room - user is not in a backend room yet"); return False

    # Room must exist
    room = rooms.get(room_id)
    if not room: print("Tried to connect frontend room - backend room no longer exists"); return False

    return True


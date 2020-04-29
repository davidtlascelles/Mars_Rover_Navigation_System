import time

from Communication_Dispatch import CommunicationDispatch
from Database import Database
from Pathfinder import PathFinder
from Vector_Handler import Vector
from Onboard_Systems_Interface import DriveInterface


def wait_for_comms_activity():
    COMM_CHECK_INTERVAL = 5
    activity = Comms_object.activity()
    while activity is False:
        time.sleep(COMM_CHECK_INTERVAL)
        activity = Comms_object.activity()
    return


def wait_for_downlink(obj, step):
    if step == 1:
        sender = "mission control"
    elif step == 2:
        sender = "mps orbiter"
    else:
        obj.activity()
        return obj.downlink_topography()
    obj.activity()
    point = obj.downlink_coordinates(sender)
    if point is None:
        obj.activity()
        point = obj.downlink_coordinates(sender)
    return point


Pathfinder_object = PathFinder()
Database_object = Database()
Comms_object = CommunicationDispatch()

# Wait until mission control sends destination coordinates to trigger autonomous navigation
destination = wait_for_downlink(Comms_object, 1)

# Requesting current coordinates
Comms_object.get_current_coordinates()

# Waiting for current coordinate response from orbiter
current_coordinates = wait_for_downlink(Comms_object, 2)

Drive_object = DriveInterface(Database_object, Comms_object, current_coordinates, destination)

# Creates heading vector for topography
v = Vector(current_coordinates, destination, False)

# Sends vector to orbiter, requesting topology
Comms_object.get_topography(v.vector)
wait_for_downlink(Comms_object, 3)

# Begin pathfinding search for preliminary route
Pathfinder_object.pathfind(Database_object, Drive_object, Comms_object, current_coordinates, destination)

import time

import Communication_Dispatch
import Database
import Pathfinder
import Vector_Handler


def wait_for_comms_activity():
    COMM_CHECK_INTERVAL = 5
    activity = Comms_object.activity()
    while activity is False:
        time.sleep(COMM_CHECK_INTERVAL)
        activity = Comms_object.activity()
    return


def get_downlink(obj, step):
    if step == 1:
        sender = "mission control"
    elif step == 2:
        sender = "mps orbiter"
    else:
        wait_for_comms_activity()
        print("Topography downlink requested from mps orbiter")
        return obj.downlink_topography()
    wait_for_comms_activity()
    print("Coordinate downlink requested from", sender)
    point = obj.downlink_coordinates(sender)
    if point is None:
        wait_for_comms_activity()
        point = obj.downlink_coordinates(sender)
    return point


Comms_object = Communication_Dispatch.CommunicationDispatch()

destination = get_downlink(Comms_object, 1)

Comms_object.request_current_coordinates()

current_coordinates = get_downlink(Comms_object, 2)

Vector_object = Vector_Handler.VectorHandler()
vector = Vector_object.make_vector(current_coordinates, destination, True)

Comms_object.uplink_vector(vector)

topo_map = get_downlink(Comms_object, 3)

Pathfinder_object = Pathfinder.PathFinder()
Pathfinder_object.topography = topo_map

Database_object = Database.Database()

# Clears tables from database file for testing new routes
Database_object.delete_all_rows('waypoints')
Database_object.delete_all_rows('checkpoints')

Pathfinder_object.pathfind(Database_object, Vector_object, current_coordinates, destination)
print("Preliminary route established")
# rover_position = (1068, 873, 1101.01) # Pathfind failure

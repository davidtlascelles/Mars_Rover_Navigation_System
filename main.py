import time

import Communication_Dispatch
import Database
import Pathfinder
import Vector_Handler
import Onboard_Systems_Interface


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

# Wait until mission control sends destination coordinates to trigger autonomous navigation
destination = wait_for_downlink(Comms_object, 1)

# Requesting current coordinates
Comms_object.request_current_coordinates()

# Waiting for current coordinate response from orbiter
current_coordinates = wait_for_downlink(Comms_object, 2)

# Creates heading vector for topography
Vector_object = Vector_Handler.VectorHandler()
vector = Vector_object.make_vector(current_coordinates, destination, True)

# Sends vector to orbiter, requesting topology
Comms_object.uplink_vector(vector)

# Waiting for topology map response from orbiter
topo_map = wait_for_downlink(Comms_object, 3)

# Load topology map into pathfinding system
Pathfinder_object = Pathfinder.PathFinder()
Pathfinder_object.topography = topo_map

# Establish waypoint/checkpoint database object
Database_object = Database.Database()

# Clears tables from database file for testing new routes
Database_object.delete_all_rows('waypoints')
Database_object.delete_all_rows('checkpoints')

# Begin pathfinding search for preliminary route
Pathfinder_object.pathfind(Database_object, Vector_object, current_coordinates, destination)
print("Preliminary route established")
Comms_object.uplink_rover_status("SUCCESS")

# Generate vectors between waypoints
    ## Probably a method in Vector Handler will work? Should vectors be stored in DB or passed right away to Drive?

# Pass downrange vector to imaging system
Onboard_Systems_Interface.sensor_orientation(Database_object, Vector_object, Pathfinder_object)
# Wait for hazard detection for high resolution waypoints

# Start Driving



# rover_position = (1068, 873, 1101.01) # Pathfind failure

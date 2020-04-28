# import time
#
# import Communication_Dispatch
# import Database
# import Onboard_Systems_Interface
# import Pathfinder
# import Vector_Handler
#
#
# def wait_for_downlink(step):
#     comms = Communication_Dispatch.CommunicationDispatch()
#     if step == 1:
#         sender = "mission control"
#     elif step == 2:
#         sender = "mps orbiter"
#     else:
#         comms.wait_for_comms_activity()
#         return comms.downlink_topography()
#     comms.wait_for_comms_activity()
#     point = comms.downlink_coordinates(sender)
#     if point is None:
#         comms.wait_for_comms_activity()
#         point = comms.downlink_coordinates(sender)
#     return point
#
#
# comms = Communication_Dispatch.CommunicationDispatch()
#
# # Wait until mission control sends destination coordinates to trigger autonomous navigation
# destination = wait_for_downlink(1)
# print(destination)
# # Requesting current coordinates
# comms.request_current_coordinates()
#
# # Waiting for current coordinate response from orbiter
# current_coordinates = wait_for_downlink(2)
# print(current_coordinates)
# # Creates heading vector for topography
# v = Vector_Handler.Vector(current_coordinates, destination, False)
#
# # Sends vector to orbiter, requesting topology
# comms.get_topography(v.vector)
#
# # Waiting for topology map response from orbiter
# topo_map = wait_for_downlink(3)
#
# # Load topology map into pathfinding system
# Pathfinder_object = Pathfinder.PathFinder()
# Pathfinder_object.topography = topo_map
#
# # Establish waypoint/checkpoint database object
# Database_object = Database.Database()
#
# # Clears tables from database file for testing new routes
# Database_object.delete_all_rows('waypoints')
# Database_object.delete_all_rows('checkpoints')
# Database_object.delete_all_rows('traversed')
#
# # Begin pathfinding search for preliminary route
# Pathfinder_object.pathfind(Database_object, current_coordinates, destination)
#
# # Generate vectors between waypoints
# # Probably a method in Vector Handler will work? Should vectors be stored in DB or passed right away to Drive?
#
# # Pass downrange vector to imaging system
# # Onboard_Systems_Interface.sensor_orientation(Database_object, Pathfinder_object)
# # Wait for hazard detection for high resolution waypoints
#
# # Start Driving
#
#
# # rover_position = (1068, 873, 1101.01) # Pathfind failure






#WORKING
import time

import Communication_Dispatch
import Database
import Onboard_Systems_Interface
import Pathfinder
import Vector_Handler


def wait_for_comms_activity():
    COMM_CHECK_INTERVAL = 5
    activity = comms.activity()
    while activity is False:
        time.sleep(COMM_CHECK_INTERVAL)
        activity = comms.activity()
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


comms = Communication_Dispatch.CommunicationDispatch()

# Wait until mission control sends destination coordinates to trigger autonomous navigation
destination = wait_for_downlink(comms, 1)
# Requesting current coordinates
comms.get_current_coordinates()

# Waiting for current coordinate response from orbiter
current_coordinates = wait_for_downlink(comms, 2)

# Creates heading vector for topography
v = Vector_Handler.Vector(current_coordinates, destination, False)

# Sends vector to orbiter, requesting topology
comms.get_topography(v.vector)
wait_for_downlink(comms, 3)
# Load topology map into pathfinding system
Pathfinder_object = Pathfinder.PathFinder()

# Establish waypoint/checkpoint database object
Database_object = Database.Database()

# Clears tables from database file for testing new routes
Database_object.delete_all_rows('waypoints')
Database_object.delete_all_rows('checkpoints')
Database_object.delete_all_rows('traversed')

# Begin pathfinding search for preliminary route
Pathfinder_object.pathfind(Database_object, current_coordinates, destination)

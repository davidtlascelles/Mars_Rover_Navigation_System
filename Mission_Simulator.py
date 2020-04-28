# import os
# import shutil
# import time
# import Database
# import Communication_Dispatch
#
# def unwrap_message():
#     with open(os.path.join(location, 'uplink.txt'), "r") as file:
#         message = file.readlines()
#         file.close()
#         print("opening uplink", message)
#         os.remove(os.path.join(location, 'uplink.txt'))
#         recipient = message[0].strip()
#         packet = message[2].strip()
#         return recipient, packet
#
# def distpatch_decider():
#     recipient, packet = unwrap_message()
#     if recipient == "mission control":
#         if packet == "('NO_COORDS', 'Downlink Failure; no coordinates in packet')":
#             create_start_coords(start)
#             return True
#
#     else:
#         if packet == "Requesting Current Coordinates":
#             create_start_coords(start)
#             return True
#         coordinate_topography()
#         return True
#
#
# def activity(activity_type):
#     name = f"{activity_type}.txt"
#     file = None
#     while file is None:
#         try:
#             with open(os.path.join(location, name), "r") as file:
#                 pass
#         except FileNotFoundError:
#             time.sleep(FILE_CHECK_INTERVAL)
#             print("no activity")
#         if file is not None:
#             file.close()
#             return#
#

#
# comms = Communication_Dispatch.CommunicationDispatch()
# create_destination_coords(end)
#
# # Start Coordinates
# activity("uplink")
# distpatch_decider()
# while distpatch_decider() is not True:
#     activity("uplink")
#     distpatch_decider()
#
# # Topography
# activity("uplink")
# distpatch_decider()
# while distpatch_decider() is not True:
#     activity("uplink")
#     distpatch_decider()
#
# db = Database.Database()
# while current != end:
#     size = db.get_table_size("waypoints")
#
#     # Find visited number of current coordinate
#     visited_count = db.get_visited_count(current)
#
#     i = 1
#     # Look for next highest visited number
#     next_point = db.select_point_by_visited(visited_count + i)
#     while next_point is None:
#         i += 1
#         next_point = db.select_point_by_visited(visited_count + i)
#     activity("downlink")
#     unwrap_message()
#     get_current_coords(next_point)
#
#

import os
import shutil
import time

location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
filepath = os.path.join(location, 'downlink.txt')


def unwrap_message():
    file = None
    while file is None:
        try:
            with open(os.path.join(location, 'uplink.txt'), "r") as file:
                message = file.readlines()
                file.close()
                print("opening uplink", message)
                os.remove(os.path.join(location, 'uplink.txt'))
                recipient = message[0].strip()
                packet = message[2].strip()
                return recipient, packet
        except FileNotFoundError:
            time.sleep(FILE_CHECK_INTERVAL)

def coordinate_topography():
    src_file = os.path.join(location, "coordinate_topography_map_downlink.txt")
    dup = src_file + ".dup"
    shutil.copy(src_file, dup)

    dst_file = os.path.join(location, "coordinate_topography_map_downlink.txt.dup")
    new_dst_file_name = os.path.join(location, "downlink.txt")
    print("sending downlink topo")
    os.rename(dst_file, new_dst_file_name)


def create_start_coords(start_coords):
    line1 = "navigation\n"
    line2 = "coordinates\n"
    line3 = "mps orbiter\n"
    line4 = str(start_coords)
    message = [line1, line2, line3, line4]
    print("sending downlink", message)
    f = open("downlink.txt", "w")
    f.writelines(message)
    f.close()
    return


def get_current_coords(coords):
    line1 = "navigation\n"
    line2 = "coordinates\n"
    line3 = "mps orbiter\n"
    line4 = str(coords)
    message = [line1, line2, line3, line4]
    print("sending downlink", message)
    f = open("downlink.txt", "w")
    f.writelines(message)
    f.close()
    return


def create_destination_coords(end_coords):
    line1 = "navigation\n"
    line2 = "coordinates\n"
    line3 = "mission control\n"
    line4 = str(end_coords)
    message = [line1, line2, line3, line4]
    print("sending downlink", message)
    f = open("downlink.txt", "w")
    f.writelines(message)
    f.close()
    return

FILE_CHECK_INTERVAL = 5
start = current = (1328, 823, 1101.89)
end = (749, 574, 1117.56)

create_destination_coords(end)
recipient, packet = unwrap_message()

while packet != "Mission Success; Destination reached successfully":
    if packet == "Requesting Current Coordinates":
        create_start_coords(start)
    elif packet[0] == "[":
        coordinate_topography()

    recipient, packet = unwrap_message()


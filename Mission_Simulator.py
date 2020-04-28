import os
import shutil
import time
import Database

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
                rcpt = message[0].strip()
                pckt = message[2].strip()
                return rcpt, pckt
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
start = (1328, 823, 1101.89)
end = (749, 574, 1117.56)

db = Database.Database()

create_destination_coords(end)
recipient, packet = unwrap_message()

visited = 0
while packet != "Mission Success; Destination reached successfully":
    if packet == "Requesting Current Coordinates":
        if db.get_table_size("traversed") == 0:
            get_current_coords(start)
        else:
            coords = db.select_point_by_visited(visited)
            while coords is None:
                visited += 1
                coords = db.select_point_by_visited(visited)
            get_current_coords(coords)
    elif packet[0] == "[":
        coordinate_topography()

    recipient, packet = unwrap_message()


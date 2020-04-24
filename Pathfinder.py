import Vector_Handler
import Database
import os


def unwrap_topology():
    topography_map = []

    with open(os.path.join(location, 'coordinate_topography_map.txt'), "r") as file:
        line = file.readline()
        split_line = line.split("], [")
        for s_line in split_line:
            s_line = s_line.rstrip(']')
            s_line = s_line.lstrip('[')
            unwrapped = s_line.split(',')
            row = []
            for z in unwrapped:
                row.append(float(z))
            topography_map.append(row)
    return topography_map


def cardinal(direction):
    if direction["theta"] == "N":
        heading = 2
    if direction["theta"] == "NW":
        heading = 3
    if direction["theta"] == "W":
        heading = 4
    if direction["theta"] == "SW":
        heading = 5
    if direction["theta"] == "S":
        heading = 6
    if direction["theta"] == "SE":
        heading = 7
    if direction["theta"] == "E":
        heading = 0
    if direction["theta"] == "NE":
        heading = 1

    return heading


def travel_direction(heading, start):
    matrix = unwrap_topology()
    MAX_DELTA_Z = .2

    #              E  0   NE  1    N  2    NW  3    W   4    SW   5    S   6   SE   7
    transforms = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]

    for i in range(2):
        if i == 0:
            new_x = start[0] + transforms[heading][0]
            new_y = start[1] + transforms[heading][1]
            next_move = (new_x, new_y, matrix[new_x][new_y])
            if abs(next_move[2] - start[2]) < MAX_DELTA_Z:
                return next_move

        new_x_right = start[0] + transforms[(heading + i) % 7][0]
        new_y_right = start[1] + transforms[(heading + i) % 7][1]
        next_move_right = (new_x_right, new_y_right, matrix[new_x_right][new_y_right])

        new_x_left = start[0] + transforms[(heading - i) % 7][0]
        new_y_left = start[1] + transforms[(heading - i) % 7][1]
        next_move_left = (new_x_left, new_y_left, matrix[new_x_left][new_y_left])

        right_delta_z = abs(next_move_right[2] - start[2])
        left_delta_z = abs(next_move_left[2] - start[2])
        if right_delta_z <= left_delta_z and right_delta_z < MAX_DELTA_Z:
            return next_move_right
        elif left_delta_z < right_delta_z and left_delta_z < MAX_DELTA_Z:
            return next_move_left
        else:
            print("backtracking")


def pathfind(start, end):
    if start == end:
        return

    vector = Vector_Handler.transform(start, end)
    heading = cardinal(Vector_Handler.angle(vector, True, True))

    travel = travel_direction(heading, start)
    new_point = travel[0], travel[1], travel[2]
    print(new_point)

    new_vector = Vector_Handler.transform(new_point, end)
    new_direction = Vector_Handler.angle(new_vector, True, True)["theta"]
    new_distance = Vector_Handler.magnitude(new_vector)

    db_point = (new_point[0], new_point[1], new_point[2], new_distance, new_direction)
    Database.create_waypoint(conn, db_point)

    pathfind(travel, end)





location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
name = "waypoint.db"
database = os.path.join(location, name)

conn = Database.create_connection(database)

rover_position = [1413, 638, 1097.26]
destination = [749, 574, 1117.56]

pathfind(rover_position, destination)

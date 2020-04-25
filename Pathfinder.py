import os

import Database
import Vector_Handler


def unwrap_topology():
    """
    Reads coordinate_topography_map.txt and unwraps it into a 2D array of z values
    :return: 2D array of z values
    """
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


def travel_direction(heading, start):
    """
    Finds a valid direction to travel
    :param heading: Cardinal direction towards target (integer)
    :param start: Current coordinate
    :return: Next coordinate
    """
    for i in range(2):
        if i == 0:
            point = safe_travel_options(start, heading)
            if point is not None:
                print(point)
                return point
        else:
            right = safe_travel_options(start, (heading + i) % 7)
            left = safe_travel_options(start, (heading - i) % 7)

            if right and left is not None:
                if right <= left:
                    point = right
                if left < right:
                    point = left
                print(point)
                return point
            elif right is not None and left is None:
                print(right)
                return right
            elif left is not None and right is None:
                print(left)
                return left

    print("backtracking")


def safe_travel_options(start, direction):
    """
    Finds a safe gradient in adjacent cells defined by direction parameter.
    MAX_DELTA_Z defines the acceptable height change
    :param start: Current coordinate
    :param direction: Cardinal direction (integer)
    :return: Next coordinate
    """
    matrix = unwrap_topology()
    MAX_DELTA_Z = .2

    #              E  0   NE  1    N  2    NW  3    W   4    SW   5    S   6   SE   7
    transforms = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]

    # Uses direction parameter to choose which transform to do on the start coordinate
    new_x = start[0] + transforms[direction][0]
    new_y = start[1] + transforms[direction][1]
    next_move = (new_x, new_y, matrix[new_x][new_y])

    # finds absolute value of height difference to next cell
    if abs(next_move[2] - start[2]) < MAX_DELTA_Z:
        return next_move


def safe_travel_options_counter(start):
    """
    Finds how many safe directions of travel are available at a particular spot
    :param start: Current coordinate
    :return: Number of safe options up to 8
    """
    matrix = unwrap_topology()
    MAX_DELTA_Z = .2

    #              E  0   NE  1    N  2    NW  3    W   4    SW   5    S   6   SE   7
    transforms = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]

    count = 0
    for i, direction in enumerate(transforms):
        check_x = start[0] + transforms[i][0]
        check_y = start[1] + transforms[i][1]
        check_move = (check_x, check_y, matrix[check_x][check_y])

        if abs(check_move[2] - start[2]) < MAX_DELTA_Z:
            count += 1
    return count


def pathfind(start, end):
    if start == end:
        return

    vector = Vector_Handler.make_vector(start, end)
    heading = Vector_Handler.cardinal_heading(vector)

    new_distance = Vector_Handler.magnitude(vector)
    new_direction = None
    new_point = end

    if new_distance > 1.5:
        travel = travel_direction(heading, start)
        new_point = (travel[0], travel[1], travel[2])
        new_vector = Vector_Handler.make_vector(new_point, end)
        new_direction = Vector_Handler.cardinal_heading(new_vector)
        new_distance = Vector_Handler.magnitude(new_vector)

    db_point = (new_point[0], new_point[1], new_point[2], new_distance, new_direction)

    with connection:
        Database.create_waypoint(connection, db_point)

        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM checkpoints;")
        if cursor.fetchall()[0][0] == 0:
            db_checkpoint = (new_point[0], new_point[1], safe_travel_options_counter(new_point))
            Database.create_checkpoint(connection, db_checkpoint)

    if new_point == end:
        return
    pathfind(travel, end)


# Finds current directory
location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
# name of DB file
file_name = "waypoint.db"
# creates filepath from current directory and file name
database_filepath = os.path.join(location, file_name)

# Establishes a connection to the DB, creates a connection object
connection = Database.create_connection(database_filepath)

rover_position = (1413, 638, 1097.26)
destination = (862, 771, 1109.11)
# destination = (1402, 637, 1097.7) # Works
# destination = (749, 574, 1117.56)

# Clears tables from database file for testing new routes
Database.delete_all_rows(connection, 'waypoints')
Database.delete_all_rows(connection, 'checkpoints')

pathfind(rover_position, destination)

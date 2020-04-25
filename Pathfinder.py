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


def travel_direction(connection, heading, start):
    """
    Finds a valid direction to travel
    :param connection: Connection object
    :param heading: Cardinal direction towards target (integer)
    :param start: Current coordinate
    :return: Next coordinate
    """
    i = 0
    while i < 4:
        if i == 0:
            point = safe_travel_options(connection, start, heading)
            i += 1
            if point is not None:
                return point
        elif i < 4:
            right = safe_travel_options(connection, start, (heading + i) % 7)
            left = safe_travel_options(connection, start, (heading - i) % 7)

            i += 1
            if right and left is not None:
                if right <= left:
                    point = right
                if left < right:
                    point = left
                return point
            elif right is not None and left is None:
                return right
            elif left is not None and right is None:
                return left
            if i == 4:
                backtrack(connection, start)
                count = Database.table_size(connection, 'checkpoints')
                checkpoint_coordinate = Database.select_point_by_key(connection, count, 'checkpoints')
                return travel_direction(connection, heading, checkpoint_coordinate)


def safe_travel_options(connection, start, direction):
    """
    Finds a safe gradient in adjacent cells defined by direction parameter.
    MAX_DELTA_Z defines the acceptable height change
    :param connection: Connection object
    :param start: Current coordinate
    :param direction: Cardinal direction (integer)
    :return: Next coordinate
    """
    matrix = Global_Map
    MAX_DELTA_Z = .2

    #              E  0   NE  1    N  2    NW  3    W   4    SW   5    S   6   SE   7
    transforms = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]

    # Uses direction parameter to choose which transform to do on the start coordinate
    new_x = start[0] + transforms[direction][0]
    new_y = start[1] + transforms[direction][1]
    next_move = (new_x, new_y, matrix[new_x][new_y])

    # Checks if path has been visited
    path_is_new = new_path(connection, next_move)

    # finds absolute value of height difference to next cell
    if abs(next_move[2] - start[2]) < MAX_DELTA_Z and path_is_new:
        return next_move


def safe_travel_options_counter(start, direction):
    """
    Finds how many safe directions of travel are available at a particular spot
    :param start: Current coordinate (tuple)
    :param direction: Cardinal direction heading (integer)
    :return: Number of safe options up to 5
    """
    matrix = Global_Map
    MAX_DELTA_Z = .2

    #              E  0   NE  1    N  2    NW  3    W   4    SW   5    S   6   SE   7
    transforms = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]

    count = 0
    i = 0
    while i <= 3:
        if i == 0:
            check_x = start[0] + transforms[direction][0]
            check_y = start[1] + transforms[direction][1]
            check_move = (check_x, check_y, matrix[check_x][check_y])

            if abs(check_move[2] - start[2]) < MAX_DELTA_Z:
                count += 1
            i += 1
        else:
            check_x_left = start[0] + transforms[(direction + i) % 7][0]
            check_y_left = start[1] + transforms[(direction + i) % 7][1]
            check_move_left = (check_x_left, check_y_left, matrix[check_x_left][check_y_left])

            if abs(check_move_left[2] - start[2]) < MAX_DELTA_Z:
                count += 1

            check_x_right = start[0] + transforms[(direction - i) % 7][0]
            check_y_right = start[1] + transforms[(direction - i) % 7][1]
            check_move_right = (check_x_right, check_y_right, matrix[check_x_right][check_y_right])

            if abs(check_move_right[2] - start[2]) < MAX_DELTA_Z:
                count += 1
            i += 1

    return count


def pathfind(start, end, connection, count):
    vector = Vector_Handler.make_vector(start, end)
    heading = Vector_Handler.cardinal_heading(vector)

    new_distance = Vector_Handler.magnitude(vector)
    new_direction = None
    new_point = end

    if new_distance > 1.5:
        new_point = travel_direction(connection, heading, start)
        print(f"Traveling, {new_point}")

        new_vector = Vector_Handler.make_vector(new_point, end)
        new_direction = Vector_Handler.cardinal_heading(new_vector)
        new_distance = Vector_Handler.magnitude(new_vector)

    count += 1
    db_point = (new_point[0], new_point[1], new_point[2], new_distance, new_direction, count)

    with connection:
        Database.create_waypoint(connection, db_point)

        checkpoint(connection, new_point, heading)

    if new_point == end:
        return

    pathfind(new_point, end, connection, count)


def checkpoint(connection, point, heading):
    """
    Logs checkpoints if defined minimum distance and safe topography requirement is met
    :param connection: Connection object
    :param point: Current location of rover (tuple)
    :param heading: Cardinal direction heading (integer)
    """
    MIN_DISTANCE = 15
    SAFE_TOPOGRAPHY = 4

    # Checks if checkpoints database is empty for first checkpoint
    if Database.table_size(connection, 'checkpoints') == 0:
        db_checkpoint = (point[0], point[1], safe_travel_options_counter(point, heading))
        Database.create_checkpoint(connection, db_checkpoint)
    else:
        # Find distance since last checkpoint
        count = Database.table_size(connection, 'checkpoints')
        last_checkpoint_coordinate = Database.select_point_by_key(connection, count, 'checkpoints')
        vector = Vector_Handler.make_vector(last_checkpoint_coordinate, point)
        distance_between_checkpoints = Vector_Handler.magnitude(vector)

        if distance_between_checkpoints > MIN_DISTANCE:
            # Finds how many safe travel options there are at the current coordinate
            safe_options = safe_travel_options_counter(point, heading)

            # If checkpoint is sufficiently far from last checkpoint and the area is relatively
            # flat (many travel options are available), log checkpoint to database
            if safe_options >= SAFE_TOPOGRAPHY:
                db_checkpoint = (point[0], point[1], safe_options)
                Database.create_checkpoint(connection, db_checkpoint)


def backtrack(connection, point):
    # Find key of last checkpoint
    count = Database.table_size(connection, 'checkpoints')
    # Look up checkpoint coordinates with key
    last_checkpoint_coordinate = Database.select_point_by_key(connection, count, 'checkpoints')
    # Loop up number of safe options at last checkpoint
    safe_options = Database.select_point_by_key(connection, count, 'checkpoints', True)[3]

    if point == last_checkpoint_coordinate:
        print("Returned to checkpoint", last_checkpoint_coordinate)
        Database.delete_point(connection, count, 'checkpoints')
        return

    # Determine if checkpoint is exhausted of safe options
    if safe_options < 2:
        # Delete last checkpoint from database
        Database.delete_point(connection, count, 'checkpoints')
        # Set last checkpoint as invalid coordinates
        Global_Map[last_checkpoint_coordinate[0]][last_checkpoint_coordinate[1]] = float('inf')

        # Find next checkpoint
        count = Database.table_size(connection, 'checkpoints')
        last_checkpoint_coordinate = Database.select_point_by_key(connection, count, 'checkpoints')
        safe_options = Database.select_point_by_key(connection, count, 'checkpoints', True)[3]

    point = backtrack_segment(connection, point, last_checkpoint_coordinate)

    Database.update_value(connection, count, 'checkpoints', 'safe_options', safe_options - 1)
    return


def backtrack_segment(connection, current, end):
    # Backtracking logic
    # Find visited number of current coordinate
    if current == end:
        return end

    visited_count = Database.get_visited_count(connection, current)

    i = 1
    # Look for next lowest visited number
    next_point = Database.select_point_by_visited(connection, visited_count - i)
    while next_point is None:
        i += 1
        next_point = Database.select_point_by_visited(connection, visited_count - i)

    print(f"Backtracking to, {next_point}")

    Database.delete_point(connection, current, 'waypoints')
    Global_Map[current[0]][current[1]] = float('inf')

    backtrack_segment(connection, next_point, end)


def new_path(connection, point):
    if Database.select_point_by_key(connection, point, 'waypoints') is None:
        return True
    return False


# Finds current directory
location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
# name of DB file
file_name = "waypoint.db"
# creates filepath from current directory and file name
database_filepath = os.path.join(location, file_name)

# Opens a global topology map to be modified by backtrack function
Global_Map = unwrap_topology()

# Establishes a connection to the DB, creates a connection object
conn = Database.create_connection(database_filepath)


#rover_position = (1068, 873, 1101.01) # Pathfind failure
rover_position = (1328, 823, 1101.89)
destination = (749, 574, 1117.56)

# Clears tables from database file for testing new routes
Database.delete_all_rows(conn, 'waypoints')
Database.delete_all_rows(conn, 'checkpoints')

c = 0
pathfind(rover_position, destination, conn, c)

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
    elif direction["theta"] == "NW":
        heading = 3
    elif direction["theta"] == "W":
        heading = 4
    elif direction["theta"] == "SW":
        heading = 5
    elif direction["theta"] == "S":
        heading = 6
    elif direction["theta"] == "SE":
        heading = 7
    elif direction["theta"] == "E":
        heading = 0
    elif direction["theta"] == "NE":
        heading = 1
    else:
        return
    return heading


def travel_direction(heading, start):
    for i in range(2):
        if i == 0:
            point = safe_travel_options(start, heading)
            if point is not None:
                return point
        else:
            right = safe_travel_options(start, (heading + i) % 7)
            left = safe_travel_options(start, (heading - i) % 7)

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

        if i == 2:
            print("backtracking")


def safe_travel_options(start, direction):
    matrix = unwrap_topology()
    MAX_DELTA_Z = .2

    #              E  0   NE  1    N  2    NW  3    W   4    SW   5    S   6   SE   7
    transforms = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]

    new_x = start[0] + transforms[direction][0]
    new_y = start[1] + transforms[direction][1]
    next_move = (new_x, new_y, matrix[new_x][new_y])

    if abs(next_move[2] - start[2]) < MAX_DELTA_Z:
        return next_move


def safe_travel_options_counter(start):
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

    vector = Vector_Handler.transform(start, end)
    heading = cardinal(Vector_Handler.angle(vector, True, True))

    new_distance = Vector_Handler.magnitude(vector)
    new_direction = None
    new_point = end

    if new_distance > 1.5:
        travel = travel_direction(heading, start)
        new_point = (travel[0], travel[1], travel[2])
        new_vector = Vector_Handler.transform(new_point, end)
        new_direction = Vector_Handler.angle(new_vector, True, True)["theta"]
        new_distance = Vector_Handler.magnitude(new_vector)

    db_point = (new_point[0], new_point[1], new_point[2], new_distance, new_direction)

    with conn:
        Database.create_waypoint(conn, db_point)

        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM checkpoints;")
        if cursor.fetchall()[0][0] == 0:
            db_checkpoint = (new_point[0], new_point[1], safe_travel_options_counter(new_point))
            Database.create_checkpoint(conn, db_checkpoint)

    if new_point == end:
        return
    pathfind(travel, end)


location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
name = "waypoint.db"
database = os.path.join(location, name)

conn = Database.create_connection(database)

rover_position = (1413, 638, 1097.26)
destination = (1402, 637, 1097.7)
# destination = (749, 574, 1117.56)

pathfind(rover_position, destination)

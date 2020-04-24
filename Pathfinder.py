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


def pathfind(start, end):
    if start == end:
        return
    MAX_DELTA_Z = .2
    matrix = unwrap_topology()
    vector = Vector_Handler.transform(start, end)
    direction = Vector_Handler.angle(vector, True, True)

    transformed_coordinates = []
    #              E  0   NE  1    N  2    NW  3    W   4    SW   5    S   6   SE   7
    transforms = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
    for transformation in transforms:
        new_x = start[0] + transformation[0]
        new_y = start[1] + transformation[1]
        new_point = (new_x, new_y, matrix[new_x][new_y])
        transformed_coordinates.append(new_point)

    #print("Remaining: ", Vector_Handler.magnitude(vector))

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

    if abs(transformed_coordinates[heading][2] - start[2]) < MAX_DELTA_Z:
        print(transformed_coordinates[heading])
        point = (transformed_coordinates[heading][0], transformed_coordinates[heading][1],
                 transformed_coordinates[heading][2], Vector_Handler.magnitude(vector), direction["theta"])
        Database.create_waypoint(conn, point)
        pathfind(transformed_coordinates[heading], end)

    else:
        forward_right = (heading + 1) % 7
        forward_left = (heading - 1) % 7
        fr = abs(transformed_coordinates[forward_right][2] - start[2])
        fl = abs(transformed_coordinates[forward_left][2] - start[2])
        if fr <= fl and fr < MAX_DELTA_Z:
            print(transformed_coordinates[forward_right])
            point = (transformed_coordinates[forward_right][0], transformed_coordinates[forward_right][1],
                     transformed_coordinates[forward_right][2], Vector_Handler.magnitude(vector), direction["theta"])
            Database.create_waypoint(conn, point)
            pathfind(transformed_coordinates[forward_right], end)
        elif fl < fr and fl < MAX_DELTA_Z:
            print(transformed_coordinates[forward_left])
            point = (transformed_coordinates[forward_left][0], transformed_coordinates[forward_left][1],
                     transformed_coordinates[forward_left][2], Vector_Handler.magnitude(vector), direction["theta"])
            Database.create_waypoint(conn, point)
            pathfind(transformed_coordinates[forward_left], end)

        else:
            right = (heading + 2) % 7
            left = (heading - 2) % 7
            r = abs(transformed_coordinates[right][2] - start[2])
            l = abs(transformed_coordinates[left][2] - start[2])
            if r <= l and r < MAX_DELTA_Z:
                print(transformed_coordinates[right])
                point = (transformed_coordinates[right][0], transformed_coordinates[right][1],
                         transformed_coordinates[right][2], Vector_Handler.magnitude(vector), direction["theta"])
                Database.create_waypoint(conn, point)
                pathfind(transformed_coordinates[right], end)
            elif l < r and l < MAX_DELTA_Z:
                print(transformed_coordinates[left])
                point = (transformed_coordinates[left][0], transformed_coordinates[left][1],
                         transformed_coordinates[left][2], Vector_Handler.magnitude(vector), direction["theta"])
                Database.create_waypoint(conn, point)
                pathfind(transformed_coordinates[left], end)

            else:
                back_right = (heading + 3) % 7
                back_left = (heading - 3) % 7
                br = abs(transformed_coordinates[back_right][2] - start[2])
                bl = abs(transformed_coordinates[back_left][2] - start[2])
                if br <= bl and br < MAX_DELTA_Z:
                    print(transformed_coordinates[back_right])
                    point = (transformed_coordinates[back_right][0], transformed_coordinates[back_right][1],
                             transformed_coordinates[back_right][2], Vector_Handler.magnitude(vector), direction["theta"])
                    Database.create_waypoint(conn, point)
                    pathfind(transformed_coordinates[back_right], end)
                elif bl < br and bl < MAX_DELTA_Z:
                    print(transformed_coordinates[back_left])
                    point = (transformed_coordinates[back_left][0], transformed_coordinates[back_left][1],
                             transformed_coordinates[back_left][2], Vector_Handler.magnitude(vector),
                             direction["theta"])
                    Database.create_waypoint(conn, point)
                    pathfind(transformed_coordinates[back_left], end)
                else:
                    print("backtracking")


location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
name = "waypoint.db"
database = os.path.join(location, name)

conn = Database.create_connection(database)

rover_position = [1413, 638, 1097.26]
destination = [749, 574, 1117.56]

pathfind(rover_position, destination)

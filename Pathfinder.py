import os


class PathFinder:

    def __init__(self):
        # Opens a global topology map to be modified by backtrack function
        self.Global_Map = self.__unwrap_topology()
        self.visited_count = 0

    @staticmethod
    def __unwrap_topology():
        """
        Reads coordinate_topography_map.txt and unwraps it into a 2D array of z values
        :return: 2D array of z values
        """
        # Finds current directory
        location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
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

    def travel_direction(self, db, heading, start):
        """
        Finds a valid direction to travel
        :param db: Database object
        :param heading: Cardinal direction towards target (integer)
        :param start: Current coordinate
        :return: Next coordinate
        """
        i = 0
        point = None
        while i < 4:
            if i == 0:
                point = self.safe_travel_options(db, start, heading)
                i += 1
                if point is not None:
                    return point
            elif i < 4:
                right = self.safe_travel_options(db, start, (heading + i) % 7)
                left = self.safe_travel_options(db, start, (heading - i) % 7)

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
                    self.backtrack(db, start)
                    count = db.get_table_size('checkpoints')
                    checkpoint_coordinate = db.select_point_by_key(count, 'checkpoints')
                    return self.travel_direction(db, heading, checkpoint_coordinate)

    def safe_travel_options(self, db, start, direction):
        """
        Finds a safe gradient in adjacent cells defined by direction parameter.
        MAX_DELTA_Z defines the acceptable height change
        :param db: Database object
        :param start: Current coordinate
        :param direction: Cardinal direction (integer)
        :return: Next coordinate
        """
        matrix = self.Global_Map
        MAX_DELTA_Z = .2

        #              E  0   NE  1    N  2    NW  3    W   4    SW   5    S   6   SE   7
        transforms = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]

        # Uses direction parameter to choose which transform to do on the start coordinate
        new_x = start[0] + transforms[direction][0]
        new_y = start[1] + transforms[direction][1]
        next_move = (new_x, new_y, matrix[new_x][new_y])

        # Checks if path has been visited
        path_is_new = self.__new_path(db, next_move)

        # finds absolute value of height difference to next cell
        if abs(next_move[2] - start[2]) < MAX_DELTA_Z and path_is_new:
            return next_move

    def safe_travel_options_counter(self, start, direction):
        """
        Finds how many safe directions of travel are available at a particular spot
        :param start: Current coordinate (tuple)
        :param direction: Cardinal direction heading (integer)
        :return: Number of safe options up to 5
        """
        matrix = self.Global_Map
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

    def pathfind(self, db, v, start, end):
        vector = v.make_vector(start, end)
        heading = v.heading(vector)

        new_distance = v.magnitude(vector)
        new_direction = None
        new_point = end

        if new_distance > 1.5:
            new_point = self.travel_direction(db, heading, start)
            # print(f"Traveling, {new_point}")

            new_vector = v.make_vector(new_point, end)
            new_direction = v.heading(new_vector)
            new_distance = v.magnitude(new_vector)

        self.visited_count += 1
        db_point = (new_point[0], new_point[1], new_point[2], new_distance, new_direction, self.visited_count)

        db.create_waypoint(db_point)
        self.checkpoint(db, v, new_point, heading)

        if new_point == end:
            return

        self.pathfind(db, v, new_point, end)

    def checkpoint(self, db, v, point, heading):
        """
        Logs checkpoints if defined minimum distance and safe topography requirement is met
        :param db: Database object
        :param v: VectorHandler object
        :param point: Current location of rover (tuple)
        :param heading: Cardinal direction heading (integer)
        """
        MIN_DISTANCE = 15
        SAFE_TOPOGRAPHY = 4

        # Checks if checkpoints database is empty for first checkpoint
        if db.get_table_size('checkpoints') == 0:
            db_checkpoint = (point[0], point[1], self.safe_travel_options_counter(point, heading))
            db.create_checkpoint(db_checkpoint)
        else:
            # Find distance since last checkpoint
            count = db.get_table_size('checkpoints')
            last_checkpoint_coordinate = db.select_point_by_key(count, 'checkpoints')
            vector = v.make_vector(last_checkpoint_coordinate, point)
            distance_between_checkpoints = v.magnitude(vector)

            if distance_between_checkpoints > MIN_DISTANCE:
                # Finds how many safe travel options there are at the current coordinate
                safe_options = self.safe_travel_options_counter(point, heading)

                # If checkpoint is sufficiently far from last checkpoint and the area is relatively
                # flat (many travel options are available), log checkpoint to database
                if safe_options >= SAFE_TOPOGRAPHY:
                    db_checkpoint = (point[0], point[1], safe_options)
                    db.create_checkpoint(db_checkpoint)

    def backtrack(self, db, point):
        # Find key of last checkpoint
        count = db.get_table_size('checkpoints')
        # Look up checkpoint coordinates with key
        last_checkpoint_coordinate = db.select_point_by_key(count, 'checkpoints')
        # Loop up number of safe options at last checkpoint
        safe_options = db.select_point_by_key(count, 'checkpoints', True)[3]

        if point == last_checkpoint_coordinate:
            # print("Returned to checkpoint", last_checkpoint_coordinate)
            db.delete_point(count, 'checkpoints')
            return

        # Determine if checkpoint is exhausted of safe options
        if safe_options < 2:
            # Delete last checkpoint from database
            db.delete_point(count, 'checkpoints')
            # Set last checkpoint as invalid coordinates
            self.Global_Map[last_checkpoint_coordinate[0]][last_checkpoint_coordinate[1]] = float('inf')

            # Find next checkpoint
            count = db.get_table_size('checkpoints')
            last_checkpoint_coordinate = db.select_point_by_key(count, 'checkpoints')
            safe_options = db.select_point_by_key(count, 'checkpoints', True)[3]

        self.__backtrack_segment(db, point, last_checkpoint_coordinate)

        db.update_value(count, 'checkpoints', 'safe_options', safe_options - 1)
        return

    def __backtrack_segment(self, db, current, end):
        # Backtracking logic
        # Find visited number of current coordinate
        if current == end:
            return end

        visited_count = db.get_visited_count(current)

        i = 1
        # Look for next lowest visited number
        next_point = db.select_point_by_visited(visited_count - i)
        while next_point is None:
            i += 1
            next_point = db.select_point_by_visited(visited_count - i)

        # print(f"Backtracking to, {next_point}")

        db.delete_point(current, 'waypoints')
        self.Global_Map[current[0]][current[1]] = float('inf')

        self.__backtrack_segment(db, next_point, end)

    @staticmethod
    def __new_path(db, point):
        if db.select_point_by_key(point, 'waypoints') is None:
            return True
        return False

from Vector_Handler import Vector


class PathFinder:
    # Maximum tolerance for adjacent coordinate elevation change to determine safe travel
    MAX_DELTA_Z = 0.2

    # Minimum tolerance for determining if checkpoints are sufficiently
    # far from each other to allow successful backtracking
    MIN_DISTANCE_FROM_PREV_CHECKPOINT = 15

    # Threshold for the number of adjacent coordinates with safe topography. (Max 7)
    # Lower numbers allow more uneven terrain at a checkpoint.
    SAFE_TOPOGRAPHY_THRESHOLD = 5

    # Used for checking points around a coordinate. Private variable. Do not change.
    #                     E  0   NE  1    N  2    NW  3    W   4    SW   5    S   6   SE   7
    __transforms = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]

    topography = None

    def __init__(self):
        self.new_waypoint = None
        self.current_coordinate = None
        self.visited_count = 0

    def travel_direction(self, db, comms, heading):
        """
        Finds a valid direction to travel
        :param db: Database object
        :param heading: Cardinal direction towards target (integer)
        :return: Next coordinate
        """
        i = 0
        point = None
        while i < 4:
            if i == 0:
                # Determines if the current forward heading has safe terrain to traverse
                point = self.safe_travel_options(db, heading)
                i += 1
                if point is not None:
                    return point
            elif i < 4:
                # Progressively check terrain to the left and right of the rover for safe terrain to traverse
                right = self.safe_travel_options(db, (heading + i) % 7)
                left = self.safe_travel_options(db, (heading - i) % 7)

                i += 1
                # Favor left or right by picking minimum elevation change
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
                # If there is no safe terrain in any direction, backtrack to the last checkpoint
                if i == 4:
                    comms.uplink_rover_status("BACKTRACK")
                    self.backtrack(db)
                    # Recheck for next viable path
                    return self.travel_direction(db, comms, heading)

    def safe_travel_options(self, db, direction):
        """
        Finds a safe gradient in adjacent cells defined by direction parameter.
        MAX_DELTA_Z is defined in the class, and represents the elevation change tolerance
        :param db: Database object
        :param direction: Cardinal direction (integer)
        :return: Next coordinate
        """
        # Uses direction parameter to choose which transform to perform on the current waypoint
        new_x = int(self.new_waypoint[0] + self.__transforms[direction][0])
        new_y = int(self.new_waypoint[1] + self.__transforms[direction][1])
        next_move = (new_x, new_y, self.topography[new_x][new_y])

        # Checks if path has been visited to prevent backtracking loop
        path_is_new = self.__new_path(db, next_move)

        # Find absolute value of height elevation change from current waypoint to transformed (adjacent) waypoint
        if abs(next_move[2] - self.new_waypoint[2]) < self.MAX_DELTA_Z and path_is_new:
            return next_move

    def safe_travel_options_counter(self, direction):
        """
        Finds how many safe directions of travel are available at a particular spot. Used when making a
        checkpoint to make sure the checkpoint is in a relatively safe terrain environment.
        MAX_DELTA_Z is defined in the class, and represents the elevation change tolerance
        :param direction: Cardinal direction heading (integer)
        :return: Number of safe options up to 7
        """
        count = 0

        # Check for safe terrain in every direction except opposite from
        # heading, accumulate number of safe terrain options
        for i in range(4):
            if i == 0:
                check_x = self.new_waypoint[0] + self.__transforms[direction][0]
                check_y = self.new_waypoint[1] + self.__transforms[direction][1]
                check_move = (check_x, check_y, self.topography[check_x][check_y])

                if abs(check_move[2] - self.new_waypoint[2]) < self.MAX_DELTA_Z:
                    count += 1
                i += 1
            else:
                check_x_left = self.new_waypoint[0] + self.__transforms[(direction + i) % 7][0]
                check_y_left = self.new_waypoint[1] + self.__transforms[(direction + i) % 7][1]
                check_move_left = (check_x_left, check_y_left, self.topography[check_x_left][check_y_left])

                if abs(check_move_left[2] - self.new_waypoint[2]) < self.MAX_DELTA_Z:
                    count += 1

                check_x_right = self.new_waypoint[0] + self.__transforms[(direction - i) % 7][0]
                check_y_right = self.new_waypoint[1] + self.__transforms[(direction - i) % 7][1]
                check_move_right = (check_x_right, check_y_right, self.topography[check_x_right][check_y_right])

                if abs(check_move_right[2] - self.new_waypoint[2]) < self.MAX_DELTA_Z:
                    count += 1
                i += 1

        return count

    def pathfind(self, db, dr, comms, start, end):
        """
        Core pathfinding logic
        :param db: Database object
        :param start: Current coordinates
        :param end: Destination coordinates
        """
        self.new_waypoint = start
        vector = Vector(start, end, False)
        heading = vector.cardinal_heading

        new_point = end

        # When not next to destination endpoint
        if vector.magnitude > 1.5:
            # Gets the next waypoint favoring the heading
            new_point = self.travel_direction(db, comms, vector.cardinal_heading)
            # print(f"Waypoint, {new_point}")

            # From the new waypoint, recalculate distance from destination and heading
            vector.set_start(new_point)

        self.visited_count += 1
        # Adds the new waypoint to the database
        db_point = (new_point[0], new_point[1], new_point[2],
                    vector.magnitude, vector.cardinal_heading, self.visited_count)

        # Creates a new checkpoint from the new waypoint
        db.create_waypoint(db_point)
        self.checkpoint(db, new_point, heading)
        self.new_waypoint = new_point
        if new_point == end:
            comms.uplink_rover_status("GO_PATH")
            dr.drive()
            print("out of drive")
            return

        try:
            # Loops, finds next waypoint
            self.pathfind(db, dr, comms, new_point, end)
        except RecursionError:
            print()
            comms.uplink_rover_status("NO_PATH")
        return

    def checkpoint(self, db, point, heading):
        """
        Logs checkpoints if defined minimum distance and safe topography requirement is met
        :param db: Database object
        :param point: Current location of rover (tuple)
        :param heading: Cardinal direction heading (integer)
        """
        count = db.get_table_size('checkpoints')
        # Checks if checkpoints database is empty for first checkpoint
        if count == 0:
            db_checkpoint = (point[0], point[1], self.safe_travel_options_counter(heading))
            db.create_checkpoint(db_checkpoint)
        else:
            # Find distance since last checkpoint
            last_checkpoint_coordinate = db.select_point_by_key(count, 'checkpoints')
            checkpoint_vector = Vector(point, last_checkpoint_coordinate, False)
            distance_between_checkpoints = checkpoint_vector.magnitude

            if distance_between_checkpoints > self.MIN_DISTANCE_FROM_PREV_CHECKPOINT:
                # Finds how many safe travel options there are at the current coordinate
                safe_options = self.safe_travel_options_counter(heading)

                # If checkpoint is sufficiently far from last checkpoint and the area is relatively
                # flat (many travel options are available), log checkpoint to database
                if safe_options >= self.SAFE_TOPOGRAPHY_THRESHOLD:
                    db_checkpoint = (point[0], point[1], safe_options)
                    db.create_checkpoint(db_checkpoint)

    def backtrack(self, db):
        """
        Core backtracking logic
        :param db: Database object
        """
        # Find key of last checkpoint
        count = db.get_table_size('checkpoints')
        # Look up checkpoint coordinates with key
        last_checkpoint_coordinate = db.select_point_by_key(count, 'checkpoints')
        # Loop up number of safe options at last checkpoint
        safe_options = db.select_point_by_key(count, 'checkpoints', True)[3]

        if self.new_waypoint == last_checkpoint_coordinate:
            # print("Returned to checkpoint", last_checkpoint_coordinate)
            db.delete_point(count, 'checkpoints')
            return

        # Determine if checkpoint is exhausted of safe options
        if safe_options < 2:
            # Delete last checkpoint from database
            db.delete_point(count, 'checkpoints')
            # Set last checkpoint as invalid coordinates
            self.topography[int(last_checkpoint_coordinate[0])][int(last_checkpoint_coordinate[1])] = float('inf')

            # Find next checkpoint
            count = db.get_table_size('checkpoints')
            last_checkpoint_coordinate = db.select_point_by_key(count, 'checkpoints')
            safe_options = db.select_point_by_key(count, 'checkpoints', True)[3]

        self.__backtrack_segment(db, last_checkpoint_coordinate)

        db.update_value(count, 'checkpoints', 'safe_options', safe_options - 1)
        return

    def __backtrack_segment(self, db, last_checkpoint):
        """
        Gets waypoints in reverse order from database, deletes them, and makes the coordinate unreachable.
        When backtracking is complete, return coordinates of the last checkpoint.
        :param db: Database object
        :param last_checkpoint: Coordinates of last checkpoint from database
        :return Coordinates of the last checkpoint
        """
        if self.new_waypoint == last_checkpoint:
            return last_checkpoint

        # Find visited number of current coordinate
        visited_count = db.get_visited_count(self.new_waypoint)

        i = 1
        # Look for next lowest visited number
        next_point = db.select_point_by_visited(visited_count - i)
        while next_point is None:
            i += 1
            next_point = db.select_point_by_visited(visited_count - i)

        # print(f"Backtracking, {next_point}")

        # Delete waypoint from database
        db.delete_point(self.new_waypoint, 'waypoints')
        # Make waypoint unreachable during this pathfinding session
        self.topography[int(self.new_waypoint[0])][int(self.new_waypoint[1])] = float('inf')
        # Keep backtracking
        self.new_waypoint = next_point
        self.__backtrack_segment(db, last_checkpoint)

    @staticmethod
    def __new_path(db, point):
        """
        Querys database for a specific point, returns true if the waypoint coordinate is new
        :param db: Database object
        :param point: Coordinate waypoint
        :return: Boolean value for new coordinate status
        """
        if db.select_point_by_key(point, 'waypoints') is None:
            return True
        return False

    @classmethod
    def set_MAX_DELTA_Z(cls, tolerance):
        """
        Adjusts maximum tolerance for adjacent coordinate elevation change to determine safe travel. Lower is safer
        :param tolerance: Tolerance value in meters
        """
        cls.MAX_DELTA_Z = tolerance
        return

    @classmethod
    def set_MIN_DISTANCE_FROM_PREV_CHECKPOINT(cls, tolerance):
        """
        Adjusts minimum tolerance for determining if checkpoints are sufficiently far from each other to
        allow successful backtracking. Avoid low values to reduce pathfinding compute time.
        :param tolerance: Tolerance value in meters
        :return:
        """
        cls.MIN_DISTANCE_FROM_PREV_CHECKPOINT = tolerance
        return

    @classmethod
    def set_SAFE_TOPOGRAPHY_THRESHOLD(cls, threshold):
        """
        Adjusts threshold for the number of adjacent coordinates with safe topography.
        Avoid lower numbers to avoid more uneven terrain at a checkpoint.
        :param threshold: Threshold of safe adjacent points (Max 7)
        """
        cls.SAFE_TOPOGRAPHY_THRESHOLD = threshold
        return

    @classmethod
    def set_topography(cls, topo_map):
        cls.topography = topo_map
        return





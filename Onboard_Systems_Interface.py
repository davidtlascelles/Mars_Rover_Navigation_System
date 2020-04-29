import time
from Vector_Handler import Vector


class DriveInterface:

    def __init__(self, database_object, comms_object, start, end):
        self.db = database_object
        self.comms = comms_object
        self.destination_coordinate = end
        self.starting_coordinate = start
        self.current_coordinate = start

        self.vector_buffer = []

    def drive_buffer(self, done=False, initialize=False):
        if done is False:
            start = self.current_coordinate

            if initialize is True:
                next_waypoint = self.db.select_point_by_visited(1)
                v = Vector(start, next_waypoint)
                self.vector_buffer.append((v.vector, v))
                start = next_waypoint

            distance = 0

            while distance < 10:
                visited = self.db.get_visited_count(start) + 1
                next_waypoint = self.db.select_point_by_visited(visited)
                while next_waypoint is None:
                    visited += 1
                    next_waypoint = self.db.select_point_by_visited(visited)
                visited += 1

                v = Vector(start, next_waypoint)
                self.vector_buffer.append((v.vector, v))

                d = Vector(self.current_coordinate, next_waypoint)
                distance = d.magnitude
                start = next_waypoint
        return

    def interrupt_drive_buffer(self):
        self.drive_buffer(done=True)
        self.vector_buffer = []
        self.comms.uplink_rover_status("DRIVE_FAULT")
        return

    def get_current_coordinates(self):
        self.comms.request_current_coordinates()
        self.current_coordinate = self.comms.downlink_coordinates("mps orbiter")
        return

    @classmethod
    def set_destination_coordinates(cls, dest):
        cls.destination_coordinate = dest
        return

    def append_vector_buffer(self, vector):
        self.vector_buffer.append(vector)
        return

    def drive(self, done=False):
        if done is False:
            self.comms.uplink_rover_status("GO_DRIVE")
            print()
            current = self.current_coordinate
            self.db.create_traversed(current)

            # Initialize drive buffer
            self.drive_buffer(initialize=True)

            while self.current_coordinate != self.destination_coordinate:
                self.current_coordinate = self.downlink_coords()
                if self.current_coordinate == (0, 0, 0):
                    done = True
                    break
                self.db.create_traversed(self.current_coordinate)
                self.pass_to_sensor_array()
                time.sleep(.1)
                print("Waiting for Hazard Avoidance;\t", end='')
                #if hazard, clear buffer and rebuffer waypoints
                    # clear buffer
                    # add hazard waypoints
                    #self.drive_buffer()
                self.pass_to_drive_system()
                response = self.drive_system_response()
                while response is None:
                    time.sleep(5)
                    response = self.drive_system_response()
                    if response == "Error":
                        self.drive_buffer(done=True)
                        self.comms.uplink_rover_status("DRIVE_FAULT")
                        return
                    else:
                        pass
                self.drive_buffer()

            if self.current_coordinate == self.destination_coordinate:
                self.comms.uplink_rover_status("SUCCESS")
        self.comms.uplink_rover_status("STOP")
        return

    def pass_to_sensor_array(self):
        vector = self.vector_buffer[0]
        time.sleep(.1)
        print("Sending vector to Sensor Array;\t", end='')
        return

    @staticmethod
    def drive_system_response():
        time.sleep(.3)
        message = "DRIVE_OK"
        print(f"Awaiting Drive System response: {message}: Rover traversed terrain to next waypoint successfully\n")
        return message

    def pass_to_drive_system(self):
        time.sleep(.1)
        vector = self.vector_buffer.pop(0)
        print("Sending vector to Drive System:", vector[1].vector)

    def wait_for_comms_activity(self):
        COMM_CHECK_INTERVAL = 1
        activity = self.comms.activity()
        while activity is False:
            time.sleep(COMM_CHECK_INTERVAL)
            activity = self.comms.activity()
        return

    def downlink_coords(self):
        self.comms.request_current_coordinates()
        self.wait_for_comms_activity()
        point = self.comms.downlink_coordinates("mps orbiter")
        if point is None:
            self.comms.request_current_coordinates()
            self.wait_for_comms_activity()
            point = self.comms.downlink_coordinates("mps orbiter")

        if point == "STOP":
            point = (0, 0, 0)
        return point


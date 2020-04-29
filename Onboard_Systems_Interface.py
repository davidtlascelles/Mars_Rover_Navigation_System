import time


class DriveInterface:

    def __init__(self, database_object, comms_object):
        self.db = database_object
        self.comms = comms_object
        self.destination_coordinate = None
        self.current_coordinate = None

        self.vector_buffer = []

    def drive_buffer(self, done=False):
        # while current != self.destination_coordinate:
        #     v = [0, 0]
        #     first = self.vector_buffer[0][0]
        #     last = self.vector_buffer[len(self.vector_buffer) - 1][0]
        #     if first != last:
        #         v = Vector_Handler.Vector(first, last)
        #
        #     while v.magnitude < 10:
        #         visited += 1
        #
        #         next_point = db.select_point_by_visited(visited)
        #         if next_point == self.destination_coordinate:
        #             done = True
        #             break
        #         while next_point is None:
        #             visited += 1
        #             next_point = db.select_point_by_visited(visited)
        #         self.vector_buffer.append((next_point, Vector_Handler.Vector(current, next_point)))
        #         current = next_point
        #     if done is True:
        #         break
        return

    def __interrupt_drive_buffer(self):
        self.drive_buffer(done=True)
        self.vector_buffer = []
        self.comms.uplink_rover_status("DRIVE_FAULT")
        return

    def get_current_coordinates(self):
        self.comms.get_current_coordinates()
        self.current_coordinate = self.comms.downlink_coordinates("mps orbiter")
        return

    @classmethod
    def set_destination_coordinates(cls, dest):
        cls.destination_coordinate = dest
        return

    def append_vector_buffer(self, vector):
        self.vector_buffer.append(vector)
        return

    def get_sensor_vector(self):
        vector = self.vector_buffer[0]
        print("Send vector to sensors", vector[1])
        return

    def drive(self):
        self.comms.uplink_rover_status("GO_DRIVE")
        self.current_coordinate = self.db.select_point_by_visited(1)
        current = self.current_coordinate
        self.db.create_traversed(current)

        visited = 0

        while self.current_coordinate != self.destination_coordinate:
            self.current_coordinate = self.downlink_coords()
            print(self.current_coordinate)
            self.db.create_traversed(self.current_coordinate)
            print("Pass Vector To Imaging System") #########################################
            print("Add Hazard Avoidance To waypoints") #####################################
            self.drive_buffer()
            print("Pass next vector to drive system")
            print("Recieve drive system response")
            response = None#####################################
            while response is None:
                time.sleep(5)
                response = 0 ################################
                if response == "Error":
                    self.drive_buffer(done=True)
                    self.comms.uplink_rover_status("DRIVE_FAULT")
                    return
                else:
                    pass

        self.comms.uplink_rover_status("SUCCESS")
        return

    def wait_for_comms_activity(self):
        COMM_CHECK_INTERVAL = 1
        activity = self.comms.activity()
        while activity is False:
            time.sleep(COMM_CHECK_INTERVAL)
            activity = self.comms.activity()
        return

    def downlink_coords(self):
        self.comms.get_current_coordinates()
        self.wait_for_comms_activity()
        point = self.comms.downlink_coordinates("mps orbiter")
        if point is None:
            self.comms.get_current_coordinates()
            self.wait_for_comms_activity()
            point = self.comms.downlink_coordinates("mps orbiter")
        return point

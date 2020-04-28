import Communication_Dispatch
import Database
import Vector_Handler
import main


class DriveInterface:

    def __init__(self):
        self.current_coordinate = None
        self.destination_coordinate = main.destination

        self.vector_buffer = [(self.current_coordinate, Vector_Handler.Vector())]

    def drive_buffer(self, done=False):
        db = Database.Database()
        current = self.current_coordinate

        visited = 0
        while current != self.destination_coordinate:
            v = 0
            first = self.vector_buffer[0][0]
            last = self.vector_buffer[len(self.vector_buffer) - 1][0]
            if first != last:
                v = Vector_Handler.Vector(first, last)

            while v.magnitude < 10:
                visited += 1

                next_point = db.select_point_by_visited(visited)
                if next_point == self.destination_coordinate:
                    done = True
                    break
                while next_point is None:
                    visited += 1
                    next_point = db.select_point_by_visited(visited)
                self.vector_buffer.append((next_point, Vector_Handler.Vector(current, next_point)))
                current = next_point
            if done is True:
                break
        return

    def __interrupt_drive_buffer(self):
        comms = Communication_Dispatch.CommunicationDispatch()
        self.drive_buffer(done=True)
        self.vector_buffer = []
        comms.uplink_rover_status("DRIVE_FAULT")
        return

    def get_current_coordinates(self):
        comms = Communication_Dispatch.CommunicationDispatch()
        comms.request_current_coordinates()
        self.current_coordinate = comms.downlink_coordinates("mps orbiter")
        return

    def get_sensor_vector(self):
        vector = self.vector_buffer[0]
        print("Send vector to sensors", vector[1])
        return

    def drive(self):
        db = Database.Database()
        # Get first vector in buffer
        vector = self.vector_buffer.pop(0)

        self.drive_buffer()
        # Send vector to drive system
        print("Send vector to drive system", vector[1])
        # Wait for response
        print("Wait for response")
        response = None
        if response == "Success":
            # Update current coordinates
            self.get_current_coordinates()  ########################################## Mission Sim needs to handle this
            # Trigger imaging interface
            self.get_sensor_vector()
            # Add point to traversed
            db.create_traversed(vector[0])
            # Update buffer
            self.drive_buffer()
        else:
            self.__interrupt_drive_buffer()

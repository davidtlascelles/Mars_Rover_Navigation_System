# import os
# import Pathfinder
# import time
#
#
# class CommunicationDispatch:
#     COMM_CHECK_INTERVAL = 5
#
#     def __init__(self):
#         # Finds current directory
#         self.location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
#
#     def __activity(self):
#         """
#         Listens for activity from Communications System
#         :return: Boolean indicator of activity
#         """
#         file = None
#         try:
#             with open(os.path.join(self.location, 'downlink.txt'), "r") as file:
#                 pass
#         finally:
#             if file is not None:
#                 file.close()
#                 return True
#             return False
#
#     def wait_for_comms_activity(self):
#         activity = self.__activity()
#         while activity is False:
#             time.sleep(self.COMM_CHECK_INTERVAL)
#             activity = self.__activity()
#         return
#
#     def __downlink(self):
#         """
#         Opens downlink packet and verifies it is for the Navigation System
#         :return: Contents of packet as a list of lines
#         """
#         with open(os.path.join(self.location, 'downlink.txt'), "r") as file:
#             message = file.readlines()
#             print(message)
#             file.close()
#             os.remove(os.path.join(self.location, 'downlink.txt'))
#             if message[0].strip() == "navigation":
#                 return message
#             return None
#
#     def downlink_coordinates(self, expected_sender):
#         """
#         Opens downlink packet and verifies it contains coordinates, then verifies the coordinates are
#         for the correct request (current coordinates vs destination coordinates)
#         :param expected_sender: string dictating which sender the packet should come from
#         :return: tuple coordinates
#         """
#         message = self.__downlink()
#         header_message_type = message[1].strip()
#         # Verify packet contains coordinates
#         if header_message_type == 'coordinates':
#             header_sender = message[2].strip()
#             # Verify packet is from correct sender
#             if header_sender == expected_sender:
#                 payload = message[3]
#                 payload = payload.rstrip(')')
#                 payload = payload.lstrip('(')
#                 piece = payload.split(',')
#                 unwrapped_payload = (int(piece[0]), int(piece[1]), float(piece[2]))
#                 # Destination coordinates
#                 if expected_sender == "mission control":
#                     # unwrapped_payload = (749, 574, 1117.56)
#                     self.uplink_rover_status("GO_DEST")
#                     return unwrapped_payload
#                 # Current coordinates
#                 elif expected_sender == "mps orbiter":
#                     # unwrapped_payload = (1328, 823, 1101.89)
#                     self.uplink_rover_status("GO_POSITION")
#                     return unwrapped_payload
#             print(payload)
#             self.uplink_rover_status("WRONG_COORDS")
#         self.uplink_rover_status("NO_COORDS")
#         return None
#
#     def downlink_topography(self):
#         """
#         Opens downlink packet and verifies it contains topographical information
#         :return: Topographical 2D array
#         """
#         message = self.__downlink()
#         message_type = message[1].strip()
#
#         if message_type == 'topography':
#             # sender = message[2].strip()  # Currently unused
#             payload = message[3]
#
#             topography_map = []
#
#             split_line = payload.split("], [")
#             for s_line in split_line:
#                 s_line = s_line.rstrip(']')
#                 s_line = s_line.lstrip('[')
#                 unwrapped = s_line.split(',')
#                 row = []
#                 for z in unwrapped:
#                     row.append(float(z))
#                 topography_map.append(row)
#
#             self.uplink_rover_status("GO_TOPO")
#             return topography_map
#         self.uplink_rover_status("NO_TOPO")
#         return None
#
#     def request_current_coordinates(self):
#         """
#         Sends request to orbiter for current coordinates
#         """
#         self.__uplink("mps orbiter", "Requesting Current Coordinates")
#         return
#
#     def uplink_rover_status(self, code):
#         """
#         Status reporting system for mission control
#         :param code: Status code string
#         """
#         message_dictionary = {
#             "SUCCESS": "Mission Success; Destination reached successfully",
#             "DRIVE_FAULT": "Driving Interrupted; critical failure",
#             "GO_PATH": "Pathfind Success; route established",
#             "NO_PATH": "Pathfind Failure; no route established",
#             "GO_DEST": "Downlink Success; destination coordinates received",
#             "GO_POSITION": "Downlink Success; current coordinates received",
#             "NO_COORDS": "Downlink Failure; no coordinates in packet",
#             "WRONG_COORDS": "Downlink Failure; incorrect coordinates",
#             "GO_TOPO": "Downlink Success; topography downlink received",
#             "NO_TOPO": "Downlink Failure; topography downlink failed ",
#             "GO_PARAMS": "Downlink Success; mission parameters updated"
#         }
#         recipient = "mission control"
#         message = message_dictionary[code]
#         message_tuple = (code, message)
#         self.__uplink(recipient, message_tuple)
#         return
#
#     def get_topography(self, vector):
#         """
#         Uplink a vector to the orbiter to get topographical information around the vector
#         :param vector: vector tuple
#         """
#         recipient = "mps_orbiter"
#         self.__uplink(recipient, vector)
#         return
#
#     def set_parameters(self):
#         message = self.__downlink()
#         header_message_type = message[1].strip()
#         # Verify packet contains coordinates
#         if header_message_type == 'parameters':
#             header_sender = message[2].strip()
#             # Verify packet is from correct sender
#             if header_sender == 'mission control':
#                 payload = message[3].split('=')
#                 parameter = payload[0].strip()
#                 value = float(payload[1])
#                 if parameter == "MAX_DELTA_Z":
#                     self.uplink_rover_status("GO_PARAMS")
#                     Pathfinder.PathFinder.set_MAX_DELTA_Z(value)
#                 elif parameter == "MIN_DISTANCE_FROM_PREV_CHECKPOINT":
#                     self.uplink_rover_status("GO_PARAMS")
#                     Pathfinder.PathFinder.set_MIN_DISTANCE_FROM_PREV_CHECKPOINT(value)
#                 elif parameter == "SAFE_TOPOGRAPHY_THRESHOLD":
#                     self.uplink_rover_status("GO_PARAMS")
#                     Pathfinder.PathFinder.set_SAFE_TOPOGRAPHY_THRESHOLD(value)
#                 return
#         return
#
#     def __uplink(self, recipient, packet):
#         """
#         Interfaces with Communications System to send packets out from the rover
#         :param recipient: String dictating who the message is intended for
#         :param packet: Tuple containing message information
#         """
#         payload = (str(recipient) + "\n", "navigation\n", str(packet))
#
#         print("Sending uplink packet to comms:", payload)
#         with open(os.path.join(self.location, 'uplink.txt'), "w") as file:
#             file.writelines(payload)
#             file.close()
#         return
import os
import Pathfinder


class CommunicationDispatch:

    def __init__(self):
        # Finds current directory
        self.location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    def activity(self):
        """
        Listens for activity from Communications System
        :return: Boolean indicator of activity
        """
        file = None
        try:
            with open(os.path.join(self.location, 'downlink.txt'), "r") as file:
                pass
        finally:
            if file is not None:
                file.close()
                return True
            return False

    def __downlink(self):
        """
        Opens downlink packet and verifies it is for the Navigation System
        :return: Contents of packet as a list of lines
        """
        with open(os.path.join(self.location, 'downlink.txt'), "r") as file:
            message = file.readlines()
            file.close()
            os.remove(os.path.join(self.location, 'downlink.txt'))
            if message[0].strip() == "navigation":
                return message
            return None

    def downlink_coordinates(self, expected_sender):
        """
        Opens downlink packet and verifies it contains coordinates, then verifies the coordinates are
        for the correct request (current coordinates vs destination coordinates)
        :param expected_sender: string dictating which sender the packet should come from
        :return: tuple coordinates
        """
        message = self.__downlink()
        header_message_type = message[1].strip()
        # Verify packet contains coordinates
        if header_message_type == 'coordinates':
            header_sender = message[2].strip()
            # Verify packet is from correct sender
            if header_sender == expected_sender:
                payload = message[3]
                payload = payload.rstrip(')')
                payload = payload.lstrip('(')
                piece = payload.split(',')
                unwrapped_payload = (int(piece[0]), int(piece[1]), float(piece[2]))
                # Destination coordinates
                if expected_sender == "mission control":
                    # unwrapped_payload = (749, 574, 1117.56)
                    self.uplink_rover_status("GO_DEST")
                    return unwrapped_payload
                # Current coordinates
                elif expected_sender == "mps orbiter":
                    # unwrapped_payload = (1328, 823, 1101.89)
                    self.uplink_rover_status("GO_POSITION")
                    return unwrapped_payload
            self.uplink_rover_status("WRONG_COORDS")
        self.uplink_rover_status("NO_COORDS")
        return None

    def downlink_topography(self):
        """
        Opens downlink packet and verifies it contains topographical information
        :return: Topographical 2D array
        """
        message = self.__downlink()
        message_type = message[1].strip()

        if message_type == 'topography':
            # sender = message[2].strip()  # Currently unused
            payload = message[3]

            topography_map = []

            split_line = payload.split("], [")
            for s_line in split_line:
                s_line = s_line.rstrip(']')
                s_line = s_line.lstrip('[')
                unwrapped = s_line.split(',')
                row = []
                for z in unwrapped:
                    row.append(float(z))
                topography_map.append(row)

            self.uplink_rover_status("GO_TOPO")
            return topography_map
        self.uplink_rover_status("NO_TOPO")
        return None

    def get_current_coordinates(self):
        """
        Sends request to orbiter for current coordinates
        """
        self.__uplink("mps orbiter", "Requesting Current Coordinates")
        return

    def uplink_rover_status(self, code):
        """
        Status reporting system for mission control
        :param code: Status code string
        """
        message_dictionary = {
            "SUCCESS": "Mission Success; Destination reached successfully",
            "GO_PATH": "Pathfind Success; route established",
            "NO_PATH": "Pathfind Failure; no route established",
            "GO_DEST": "Downlink Success; destination coordinates received",
            "GO_POSITION": "Downlink Success; current coordinates received",
            "NO_COORDS": "Downlink Failure; no coordinates in packet",
            "WRONG_COORDS": "Downlink Failure; incorrect coordinates",
            "GO_TOPO": "Downlink Success; topography downlink received",
            "NO_TOPO": "Downlink Failure; topography downlink failed ",
            "GO_PARAMS": "Downlink Success; mission parameters updated"
        }
        recipient = "mission control"
        message = message_dictionary[code]
        message_tuple = (code, message)
        self.__uplink(recipient, message_tuple)
        return

    def get_topography(self, vector):
        """
        Uplink a vector to the orbiter to get topographical information around the vector
        :param vector: vector tuple
        """
        recipient = "mps_orbiter"
        self.__uplink(recipient, vector)
        return

    def set_parameters(self):
        message = self.__downlink()
        header_message_type = message[1].strip()
        # Verify packet contains coordinates
        if header_message_type == 'parameters':
            header_sender = message[2].strip()
            # Verify packet is from correct sender
            if header_sender == 'mission control':
                payload = message[3].split('=')
                parameter = payload[0].strip()
                value = float(payload[1])
                if parameter == "MAX_DELTA_Z":
                    self.uplink_rover_status("GO_PARAMS")
                    Pathfinder.PathFinder.set_MAX_DELTA_Z(value)
                elif parameter == "MIN_DISTANCE_FROM_PREV_CHECKPOINT":
                    self.uplink_rover_status("GO_PARAMS")
                    Pathfinder.PathFinder.set_MIN_DISTANCE_FROM_PREV_CHECKPOINT(value)
                elif parameter == "SAFE_TOPOGRAPHY_THRESHOLD":
                    self.uplink_rover_status("GO_PARAMS")
                    Pathfinder.PathFinder.set_SAFE_TOPOGRAPHY_THRESHOLD(value)
                return
        return

    @staticmethod
    def __uplink(recipient, packet):
        """
        Interfaces with Communications System to send packets out from the rover
        :param recipient: String dictating who the message is intended for
        :param packet: Tuple containing message information
        """
        payload = {
            "recipient": recipient,
            "sender": "navigation",
            "payload": packet
        }
        print("Sending uplink packet to comms:", payload)
        return
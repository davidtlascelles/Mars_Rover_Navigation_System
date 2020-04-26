import os


class CommunicationDispatch:

    def __init__(self):
        # Finds current directory
        self.location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    def activity(self):
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
        with open(os.path.join(self.location, 'downlink.txt'), "r") as file:
            message = file.readlines()
            file.close()
            os.remove(os.path.join(self.location, 'downlink.txt'))
            if message[0].strip() == "navigation":
                return message
            return None

    def downlink_coordinates(self, sender):
        message = self.__downlink()
        header_message_type = message[1].strip()
        if header_message_type == 'coordinates':
            header_sender = message[2].strip()
            if header_sender == sender:
                payload = message[3]
                payload = payload.rstrip(')')
                payload = payload.lstrip('(')
                piece = payload.split(',')
                unwrapped_payload = (int(piece[0]), int(piece[1]), float(piece[2]))
                if sender == "mission control":
                    # unwrapped_payload = (749, 574, 1117.56) # destination
                    return unwrapped_payload
                elif sender == "mps orbiter":
                    # unwrapped_payload = (1328, 823, 1101.89) # rover_position
                    return unwrapped_payload
            return None

    def downlink_topography(self):
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

            return topography_map
        return None

    def request_current_coordinates(self):
        self.__uplink("mps orbiter", "Requesting Current Coordinates")
        return

    def uplink_rover_status(self, code):
        message_dictionary = {
            "NOPATH": "Pathfind Failure; no route established",
            "SUCCESS": "Destination reached successfully"
        }
        recipient = "mission control"
        message = message_dictionary[code]
        message_tuple = (code, message)
        self.__uplink(recipient, message_tuple)
        pass

    def uplink_vector(self, vector):
        recipient = "mps_orbiter"
        self.__uplink(recipient, vector)
        return

    @staticmethod
    def __uplink(recipient, packet):
        payload = {
            "recipient": recipient,
            "sender": "navigation",
            "payload": packet
        }
        print("Sending uplink packet to comms:", payload)

import random
import Database
import Onboard_Systems_Interface


#                     E  0   NE  1    N  2    NW  3    W   4    SW   5    S   6   SE   7
transforms = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]

db = Database.Database()

size = db.get_table_size("traversed")

current_coordinates = Onboard_Systems_Interface.current_coordinates

if size == 0:

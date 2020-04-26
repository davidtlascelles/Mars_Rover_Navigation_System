import Vector_Handler
import Pathfinder
import Database

# Establishes a connection to the DB, creates a connection object
Database_object = Database.Database()
Vector_object = Vector_Handler.VectorHandler()
Pathfinder_object = Pathfinder.PathFinder()

# rover_position = (1068, 873, 1101.01) # Pathfind failure
rover_position = (1328, 823, 1101.89)
destination = (749, 574, 1117.56)

# Clears tables from database file for testing new routes
Database_object.delete_all_rows('waypoints')
Database_object.delete_all_rows('checkpoints')

Pathfinder_object.pathfind(Database_object, Vector_object, rover_position, destination)

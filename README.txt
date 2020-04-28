System functions based on lucidchart diagrams

- Pass downrange vector to imaging system after route established (vector to next waypoint)
    ** Program that interfaces with the imaging system to pass a vector

- Pass vectors to drive system
    ** Program that interfaces with the drive system to pass direction vectors as rover's location updates.
    Buffer of upcoming vectors kept in memory

- Inject hazard avoidance waypoints into preliminary route waypoint database
    ** Program that interfaces with the hazard avoidance subsystem to recieve floating point waypoints around obstacles

- Handle pathfind failure
    ** Detect pathfind failure and generate message to send to mission control with pathfind failure information

- Pathfind system probably needs a method to delete/archive waypoints after driving succesfuly through them

- Need some way of determining current location

- Comms system should be able to accept a command from mission control to redefine pathfinding parameters (ie MAX_DELTA_Z)

✔

✔ Uplink status messages
    Program that interfaces with the comms to send status messages from the rover to mission control
    ** Communication_Dispatch has a method for uplinking status messages, but the system currently
    does not generate any message

✔ Receive coordinates
    Program that interfaces with the comms to recieve coordinate points from Mission Control or Orbiting MPS
    Destination Coordinates: 749, 574, 1117.56
    Rover Current Coordinates: 1068, 873, 1101.01
    ** Needs code comments

✔ Receive topographical data
    Program that interfaces with the comms to uplink a vector and downlink topographical data

✔ Generate preliminary route
    Preliminary route working unless pathfind failure occurs

✔ Create vector from current to destination
    Vector handler supports:
     - Creating a vector from two points
     - Finding the magnitude of a vector (2D or 3D)
     - Finding the cardinal direction of a vector

✔ Handle backtracking

✔ Trigger backtracking if route not established

✔ Cache safe checkpoint waypoint

- OPTIONAL
    Improve pathfinding algorithm in pathfind failure conditions. Maybe solve path in pieces to prevent
    reaching recursion depth limit if stuck in problematic area. Current plan for this failure is to
    uplink pathfind failure error.



System functions based on lucidchart diagrams

IMAGING INTERFACE
- Pass downrange vector to imaging system after route established (vector to next waypoint)
    ** Program that interfaces with the imaging system to pass a vector

- Get hazard avoidance waypoints response, inject it into preliminary route waypoint database


DRIVE INTERFACE
- Drive interface needs to generate vectors to pass to Drive System
    Buffer of upcoming vectors kept in memory. Buffer capacity should be based on distance, not number of vectors.
    When last waypoint is reached, stop generating vectors.

- Drive interface loop:
    While drive vector buffer is not empty, keep passing vectors
        Drive System response: Success:
            Update current coordinates
            Trigger imaging interface
            Add traversed waypoint to database
            Update buffer with next vector
        Drive System response: Failure:
            Dump Buffer
            Comms message



✔ Uplink status messages
    Program that interfaces with the comms to send status messages from the rover to mission control

✔ Receive coordinates
    Program that interfaces with the comms to recieve coordinate points from Mission Control or Orbiting MPS
    Destination Coordinates: 749, 574, 1117.56
    Rover Current Coordinates: 1068, 873, 1101.01

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
    reaching recursion depth limit if stuck in problematic area. Current solution for this failure is to
    uplink pathfind failure error.



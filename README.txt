System functions based on lucidchart diagrams

- Receive coordinates
    ** Program that interfaces with the comms to recieve coordinate points from Mission Control or Orbiting MPS
    Destination Coordinates: 749, 574, 1117.56
    Rover Current Coordinates: 1068, 873, 1101.01

- Receive topographical data
    ** Program that interfaces with the comms to uplink a vector and downlink topographical data

- Uplink error messages
    ** Program that interfaces with the comms to send error messages from the rover to mission control

- Pass downrange vector to imaging system after route established (vector to next waypoint)
    ** Program that interfaces with the imaging system to pass a vector

- Inject hazard avoidance waypoints into preliminary route waypoint database
    ** Program that interfaces with the hazard avoidance subsystem to recieve floating point waypoints around obstacles

- Handle backtracking
    ** Program that racalls waypoints and inverts vectors to a safe checkpoint when a safe route is not established

- Create vectors along route from waypoint to waypoint
    ** Program that finds vectors between waypoints in db. Perhaps stores vectors in another table.
    Should be easy after waypoint db is created. Vector system ready

- Pass vectors to drive system
    ** Program that interfaces with the drive system to pass direction vectors as rover's location updates.

✔ Create vector from current to destination
    Vector handler supports:
     - Creating a vector from two points
     - Finding the magnitude of a vector (2D or 3D)
     - Finding the cardinal direction of a vector

* Generate preliminary route (array of waypoint coordinates) from macroscopic topographical data
    Waypoints generate successfuly and are logged into DB unless backtracking event occurs.
    Needs backtracking to handle invalid route
    ** Needs code comments

* Trigger backtracking if route not established
    Currently a print statement in Pathfinder.py -> travel_direction function
    ** Needs code comments

* Cache safe checkpoint waypoint
    DB functional, need to write logic for when to save a checkpoint
    ** Has decent code comments, could improve



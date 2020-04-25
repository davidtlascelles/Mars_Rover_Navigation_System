System functions based on lucidchart diagrams

- Receive destination coordinates
    749, 574, 1117.56

- Receive current coordinates
    1413, 638, 1097.26

✔ Create vector from current to destination
    Vector handler supports:
     - Creating a vector from two points
     - Finding the magnitude of a vector (2D or 3D)
     - Finding the cardinal direction of a vector

- Request topographical data around vector from MPS

* Generate preliminary route (array of waypoint coordinates) from macroscopic topographical data
    Waypoints generate successfuly and are logged into DB unless backtracking event occurs.
    Needs backtracking to handle invalid route
    ** Needs code comments

- Pass vector to imaging system if route established

* Trigger backtracking if route not established
    Currently a print statement in Pathfinder.py -> travel_direction function
    ** Needs code comments

* Handle backtracking (reacalling vectors and waypoints, reversing them to last checkpoint waypoint)
    Need to figure out backtracking logic

- Inject hazard avoidance waypoints into preliminary route waypoint array

* Cache safe checkpoint waypoint
    DB functional, need to write logic for when to save a checkpoint
    ** Has decent code comments, could improve

- Create vectors along route
    Should be easy after waypoint db is created. Vector system ready

- Pass vectors to drive system


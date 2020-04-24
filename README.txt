System functions based on lucidchart diagrams

- Receive destination coordinates
    749, 574, 1117.56

- Receive current coordinates
    1413, 638, 1097.26

✔ Create vector from current to destination
    Vector Handler has been created, not tested thorougly. Handles 2D and 3D vectors.
    3D vector direction angle is represented with cylindrical coordinate system angles

- Request topographical data around vector from MPS

* Generate preliminary route (array of waypoint coordinates) from macroscopic topographical data
    I'm working on this now
- Pass vector to imaging system if route established
* Trigger backtracking if route not established
    Also working on this
* Handle backtracking (reacalling vectors and waypoints, reversing them to last checkpoint waypoint)
    Also this

- Inject hazard avoidance waypoints into preliminary route waypoint array

* Cache safe checkpoint waypoint
    Just started trying to figure out an SQLite db for this

- Create vectors along route
    Should be easy after waypoint db is created. Vector system ready

- Pass vectors to drive system


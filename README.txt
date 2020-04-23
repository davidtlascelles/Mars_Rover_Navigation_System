System functions based on lucidchart diagrams

- Receive destination coordinates
- Receive current coordinates
✔ Create vector from current to destination
    Vector Handler has been created, not tested thorougly. Handles 2D and 3D vectors.
    3D vector direction angle is represented with cylindrical coordinate system angles
- Request topographical data around vector from MPS
- Generate preliminary route (array of waypoint coordinates) from macroscopic topographical data
- Pass vector to imaging system if route established
- Trigger backtracking if route not established
- Handle backtracking (reacalling vectors and waypoints, reversing them to last checkpoint waypoint)
- Inject hazard avoidance waypoints into preliminary route waypoint array
- Cache safe checkpoint waypoint
- Create vectors along route
- Pass vectors to drive system

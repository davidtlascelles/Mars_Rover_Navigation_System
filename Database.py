import os
import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def create_waypoint(conn, waypoint):
    """
    Create a new waypoint into the waypoints table
    :param conn:
    :param waypoint:
    :return: waypoint id
    """
    sql = ''' INSERT INTO waypoints(x, y, z, distance, heading)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, waypoint)
    return cur.lastrowid


def create_checkpoint(conn, checkpoint):
    """
    Create a new task
    :param conn:
    :param checkpoint:
    :return:
    """

    sql = ''' INSERT INTO checkpoints(waypoint_x, waypoint_y, safe_options)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, checkpoint)
    return cur.lastrowid


location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
name = "waypoint.db"
database = os.path.join(location, name)

sql_create_waypoints_table = """ CREATE TABLE IF NOT EXISTS waypoints(
                                        x INTEGER,
                                        y INTEGER, 
                                        z REAL,
                                        distance REAL,
                                        heading TEXT,
                                        PRIMARY KEY(x,y)
                                ); """

sql_create_checkpoints_table = """ CREATE TABLE IF NOT EXISTS checkpoints(
                                        checkpoint_id integer PRIMARY KEY, waypoint_x INTEGER,
                                        waypoint_y INTEGER,
                                        safe_options INTEGER,
                                        FOREIGN KEY (waypoint_x, waypoint_y) 
                                            REFERENCES waypoints (x, y)
                                
                                );"""

# create a database connection
conn = create_connection(database)

# create tables
if conn is not None:
    # create waypoints table
    create_table(conn, sql_create_waypoints_table)

    # create checkpoints table
    create_table(conn, sql_create_checkpoints_table)

    #point = (15, 30, 10.5, 600.2, 'NE')
    #waypoint_id = create_waypoint(conn, point)
else:
    print("Error! cannot create the database connection.")

import os
import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database filepath
    :return: Connection object or None
    """
    connection = None
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)

    return connection


def create_table(connection, create_table_sql):
    """ create a table from the create_table_sql statement
    :param connection: Connection object
    :param create_table_sql: a CREATE TABLE statement
    """
    try:
        c = connection.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def delete_all_rows(connection, table):
    """
    Delete all rows in the table defined by the second argument
    :param connection: Connection object
    :param table: String defining table name to delete
    """
    sql = f"DELETE FROM {table}"
    cur = connection.cursor()
    cur.execute(sql)
    connection.commit()


def create_waypoint(connection, waypoint):
    """
    Create a new waypoint in the waypoints table
    :param connection: Connection object
    :param waypoint: Waypoint tuple (x, y, z, distance, heading, visit_count)
    :return: waypoint id
    """
    waypoint_list = list(waypoint)
    key = compound_key(waypoint)
    waypoint_list.insert(0, key)

    keyed_waypoint = tuple(waypoint_list)

    sql = ''' INSERT INTO waypoints(waypoint_id, x, y, z, distance, heading, visit_count)
              VALUES(?,?,?,?,?,?,?) '''
    cur = connection.cursor()
    cur.execute(sql, keyed_waypoint)
    return cur.lastrowid


def delete_point(connection, key, table):
    """
    Delete a waypoint of a specific id
    :param connection: Connection object
    :param key: x, y coordinate pair
    :param table: String defining table name to delete point from
    """
    if table == "waypoints":
        key_name = "waypoint_id"
        key = compound_key(key)
    elif table == "checkpoints":
        key_name = "checkpoint_id"

    sql = f'DELETE FROM {table} WHERE {key_name}=?'
    cur = connection.cursor()
    cur.execute(sql, (key,))
    connection.commit()


def create_checkpoint(connection, checkpoint):
    """
    Create a new checkpoint in the checkpoints table
    :param connection: Connection object
    :param checkpoint: Checkpoint tuple (waypoint_x, waypoint_y, safe_options)
    :return: checkpoint id
    """
    sql = ''' INSERT INTO checkpoints(waypoint_x, waypoint_y, safe_options)
              VALUES(?,?,?) '''
    cur = connection.cursor()
    cur.execute(sql, checkpoint)
    return cur.lastrowid


def select_point_by_key(connection, key, table, return_row = None):
    """
    Query points by key and table
    :param connection: Connection object
    :param key: x, y coordinate pair
    :param table: String defining table name to delete point from
    :return: coordinate tuple
    """
    if table == 'checkpoints':
        collumn = 'checkpoint_id'
    elif table == 'waypoints':
        key = compound_key(key)
        collumn = 'waypoint_id'

    cur = connection.cursor()
    cur.execute(f"SELECT * FROM {table} WHERE {collumn}=?", (key,))

    row = cur.fetchone()
    if row is None:
        return None
    if return_row is None:
        return point_tuple(connection, row)
    return row

def select_point_by_visited(connection, visited):
    cur = connection.cursor()
    cur.execute(f"SELECT * FROM waypoints WHERE visit_count=?", (visited,))
    row = cur.fetchone()
    if row is None:
        return None
    return point_tuple(connection, row)


def get_visited_count(connection, key):
    key = compound_key(key)
    cur = connection.cursor()
    cur.execute(f"SELECT * FROM waypoints WHERE waypoint_id=?", (key,))
    row = cur.fetchone()
    return row[6]


def update_value(connection, key, table, column, value):
    if table == "waypoints":
        key_name = "waypoint_id"
        key = compound_key(key)
    elif table == "checkpoints":
        key_name = "checkpoint_id"

    sql = f'UPDATE {table} SET {column} = {value} WHERE {key_name}=?;'
    cur = connection.cursor()
    cur.execute(sql, (key,))
    connection.commit()


def compound_key(key):
    """
    Creates compound key from x and y coordinates
    :param key: x, y coordinate tuple
    :return: integer concatenated key
    """
    zeros = len(str(key[1]))
    key = key[0] * (10 ** zeros) + key[1]

    return key


def point_tuple(connection, point):
    x = point[1]
    y = point[2]
    key = compound_key((x, y))
    cur = connection.cursor()
    cur.execute(f"SELECT * FROM waypoints WHERE waypoint_id=?", (key,))
    z = cur.fetchone()[3]
    coordinate_point = (x, y, z)
    return coordinate_point


def table_size(connection, table):
    """
    Finds number of rows in table defined by table argument
    :param connection: Connection object
    :param table: String defining table name to find size of
    :return: number of rows in table (Int)
    """
    sql = f''' SELECT COUNT(*) FROM {table}'''
    cur = connection.cursor()
    cur.execute(sql)
    return cur.fetchone()[0]


def create_tables(connection):
    """
    Create tables
    :param connection: Connection object
    """
    sql_create_waypoints_table = """ CREATE TABLE IF NOT EXISTS waypoints(
                                            waypoint_id INTEGER PRIMARY KEY,
                                            x INTEGER,
                                            y INTEGER, 
                                            z REAL,
                                            distance REAL,
                                            heading TEXT,
                                            visit_count INTEGER
                                    ); """

    sql_create_checkpoints_table = """ CREATE TABLE IF NOT EXISTS checkpoints(
                                            checkpoint_id INTEGER PRIMARY KEY, 
                                            waypoint_x INTEGER,
                                            waypoint_y INTEGER,
                                            safe_options INTEGER,
                                            FOREIGN KEY (waypoint_x, waypoint_y) 
                                                REFERENCES waypoints (x, y)

                                    );"""
    # create tables
    if connection is not None:
        # create waypoints table
        create_table(conn, sql_create_waypoints_table)

        # create checkpoints table
        create_table(conn, sql_create_checkpoints_table)
    else:
        print("Error - Cannot create the database connection.")


location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
name = "waypoint.db"
database_filepath = os.path.join(location, name)

# create a database connection
conn = create_connection(database_filepath)

# creates tables if they don't exist
create_tables(database_filepath)

# To add a value to a table, do this:
#    connection = Database.create_connection(database)  // Create a connection object
#
#    with connection:                                   // Use create_waypoint() or create_checkpoint()
#        Database.create_waypoint(connection, db_point) // parameters are defined in the docstrings

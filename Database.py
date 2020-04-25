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
    :param waypoint: Waypoint tuple (x, y, z, distance, heading)
    :return: waypoint id
    """
    sql = ''' INSERT INTO waypoints(x, y, z, distance, heading)
              VALUES(?,?,?,?,?) '''
    cur = connection.cursor()
    cur.execute(sql, waypoint)
    return cur.lastrowid


def delete_point(connection, id, table):
    """
    Delete a waypoint of a specific id
    :param connection: Connection object
    :param id: x, y coordinate pair
    :param table: String defining table name to delete point from
    """
    sql = f'DELETE FROM {table} WHERE id=?'
    cur = connection.cursor()
    cur.execute(sql, (id,))
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


def create_tables(connection):
    """
    Create tables
    :param connection: Connection object
    """
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

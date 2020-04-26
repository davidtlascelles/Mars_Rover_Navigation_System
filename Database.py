import os
import sqlite3
from sqlite3 import Error


class Database:
    location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    name = "waypoint.db"
    filepath = os.path.join(location, name)

    def __init__(self):
        # creates tables if they don't exist
        self.initialize_tables()

    @staticmethod
    def __create_connection():
        """ create a database connection to the SQLite database
            specified by db_file
        :return: Connection object or None
        """
        connection = None
        try:
            connection = sqlite3.connect(Database.filepath)
            return connection
        except Error as e:
            print(e)

        return connection

    @staticmethod
    def __compound_key(key):
        """
        Creates compound key from x and y coordinates
        :param key: x, y coordinate tuple
        :return: integer concatenated key
        """
        zeros = len(str(key[1]))
        key = key[0] * (10 ** zeros) + key[1]

        return key

    def __point_tuple(self, point):
        x = point[1]
        y = point[2]
        key = self.__compound_key((x, y))
        connection = self.__create_connection()
        cur = connection.cursor()
        cur.execute(f"SELECT * FROM waypoints WHERE waypoint_id=?", (key,))
        z = cur.fetchone()[3]
        coordinate_point = (x, y, z)
        return coordinate_point

    def initialize_tables(self):
        """
        Create tables
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
        connection = self.__create_connection()
        # create tables
        if connection is not None:
            # create waypoints table
            self.create_table(sql_create_waypoints_table)

            # create checkpoints table
            self.create_table(sql_create_checkpoints_table)
        else:
            print("Error - Cannot create the database connection.")

    def create_table(self, create_table_sql):
        """ create a table from the create_table_sql statement
        :param create_table_sql: a CREATE TABLE statement
        """
        connection = self.__create_connection()
        try:
            c = connection.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    def create_waypoint(self, waypoint):
        """
        Create a new waypoint in the waypoints table
        :param waypoint: Waypoint tuple (x, y, z, distance, heading, visit_count)
        :return: waypoint id
        """
        connection = self.__create_connection()
        try:
            waypoint_list = list(waypoint)
            key = self.__compound_key(waypoint)
            waypoint_list.insert(0, key)

            keyed_waypoint = tuple(waypoint_list)

            sql = ''' INSERT INTO waypoints(waypoint_id, x, y, z, distance, heading, visit_count)
                      VALUES(?,?,?,?,?,?,?) '''
            cur = connection.cursor()
            cur.execute(sql, keyed_waypoint)
            connection.commit()
            cur.close()
            return
        except sqlite3.Error as e:
            print(e)
        finally:
            connection.close()

    def create_checkpoint(self, checkpoint):
        """
        Create a new checkpoint in the checkpoints table
        :param checkpoint: Checkpoint tuple (waypoint_x, waypoint_y, safe_options)
        """
        connection = self.__create_connection()
        sql = ''' INSERT INTO checkpoints(waypoint_x, waypoint_y, safe_options)
                              VALUES(?,?,?) '''
        try:
            cur = connection.cursor()
            cur.execute(sql, checkpoint)
            connection.commit()
            cur.close()
            return
        except sqlite3.Error as e:
            print(e)
        finally:
            if connection:
                connection.close()

    def select_point_by_key(self, key, table, return_row=None):
        """
        Query points by key and table
        :param key: x, y coordinate pair
        :param table: String defining table name to delete point from
        :param return_row: Returns row instead of tuple
        :return: coordinate tuple
        """
        if table == 'checkpoints':
            column = 'checkpoint_id'
        else:
            table = 'waypoints'
            key = self.__compound_key(key)
            column = 'waypoint_id'

        connection = self.__create_connection()
        cur = connection.cursor()
        cur.execute(f"SELECT * FROM {table} WHERE {column}=?", (key,))

        row = cur.fetchone()
        if row is None:
            return None
        if return_row is None:
            return self.__point_tuple(point=row)
        return row

    def select_point_by_visited(self, visited):
        connection = self.__create_connection()
        cur = connection.cursor()
        cur.execute(f"SELECT * FROM waypoints WHERE visit_count=?", (visited,))
        row = cur.fetchone()
        if row is None:
            return None
        return self.__point_tuple(row)

    def get_visited_count(self, key):
        connection = self.__create_connection()
        key = self.__compound_key(key)
        cur = connection.cursor()
        cur.execute(f"SELECT * FROM waypoints WHERE waypoint_id=?", (key,))
        row = cur.fetchone()
        return row[6]

    def get_table_size(self, table):
        """
        Finds number of rows in table defined by table argument
        :param table: String defining table name to find size of
        :return: number of rows in table (Int)
        """
        sql = f''' SELECT COUNT(*) FROM {table}'''
        connection = self.__create_connection()
        cur = connection.cursor()
        cur.execute(sql)
        return cur.fetchone()[0]

    def update_value(self, key, table, column, value):
        if table == "checkpoints":
            key_name = "checkpoint_id"
        else:
            table = "waypoints"
            key_name = "waypoint_id"
            key = self.__compound_key(key)

        sql = f'UPDATE {table} SET {column} = {value} WHERE {key_name}=?;'
        connection = self.__create_connection()
        cur = connection.cursor()
        cur.execute(sql, (key,))
        connection.commit()

    def delete_all_rows(self, table):
        """
        Delete all rows in the table defined by the second argument
        :param table: String defining table name to delete
        """
        sql = f"DELETE FROM {table}"
        connection = self.__create_connection()
        cur = connection.cursor()
        cur.execute(sql)
        cur.close()
        connection.commit()

    def delete_point(self, key, table):
        """
        Delete a waypoint of a specific id
        :param key: x, y coordinate pair
        :param table: String defining table name to delete point from
        """
        if table == 'checkpoints':
            column = 'checkpoint_id'
        else:
            table = 'waypoints'
            key = self.__compound_key(key)
            column = 'waypoint_id'

        sql = f'DELETE FROM {table} WHERE {column}=?'
        connection = self.__create_connection()
        cur = connection.cursor()
        cur.execute(sql, (key,))
        connection.commit()

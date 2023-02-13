import mysql.connector

class Database:
    """
    A class for establishing a connection to a MySQL database and
    executing queries.
    """
    def __init__(self, host, port, user, password, database):
        """
        Constructor for the Database class.

        Parameters:
        host (str): The hostname or IP address of the MySQL server.
        port (int): The port number to use when connecting to the server.
        user (str): The username to use when connecting to the server.
        password (str): The password to use when connecting to the server.
        database (str): The name of the database to connect to.
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        """
        Establishes a connection to the MySQL server.

        Returns:
        Connection: A connection object that can be used to execute queries.
        """
        self.connection = mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        )
        return self.connection

    def close(self):
        """
        Closes the connection to the MySQL server.
        """
        self.connection.close()

    def commit(self, query, params=None):
        """
        Executes a query and commits the changes to the database.
        If the query contains placeholders for parameters, the `params` argument
        should be provided to supply the values for the placeholders.

        Parameters:
        query (str): The query to execute.
        params (Optional[tuple]): A tuple containing the values for the placeholders in the query.
        """
        self.connection.reconnect()
        cursor = self.connection.cursor(buffered=False)
        cursor.reset()
        cursor.execute(query, params)
        self.connection.commit()
        cursor.close()

    def fetchall(self, query, params = None):
        """
        Executes a query and fetches all the results.
        If the query contains placeholders for parameters, the `params` argument
        should be provided to supply the values for the placeholders.

        Parameters:
        query (str): The query to execute.
        params (Optional[tuple]): A tuple containing the values for the placeholders in the query.

        Returns:
        list: A list of rows returned by the query.
        """
        self.connection.reconnect()
        cursor = self.connection.cursor(buffered=True)
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        return result

    def fetchone(self, query, params = None):
        """
        Executes a query and fetches a single row.
        If the query contains placeholders for parameters, the `params` argument
        should be provided to supply the values for the placeholders.

        Parameters:
        query (str): The query to execute.
        params (Optional[tuple]): A tuple containing the values for the placeholders in the query.

        Returns:
        list: A list the row returned by the query.
        """
        self.connection.reconnect()
        cursor = self.connection.cursor(buffered=True)
        cursor.execute(query, params)
        result = cursor.fetchone()
        cursor.close()
        return result

    def get_columns(self, query, params = None):
        """
        Executes a SELECT query and returns a list of column names.
        If the query contains placeholders for parameters, the `params` argument
        should be provided to supply the values for the placeholders.

        Parameters:
        query (str): The SELECT query to execute.
        params (Optional[tuple]): A tuple containing the values for the placeholders in the query.

        Returns:
        list: A list of column names.
        """
        self.connection.reconnect()
        cursor = self.connection.cursor(buffered=True)
        cursor.reset()
        cursor.execute(query, params)
        column_names = [column[0] for column in cursor.description]
        cursor.close()
        return column_names



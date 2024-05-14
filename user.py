import psycopg2
import logging

logging.basicConfig(level=logging.DEBUG)


class User:
    def __init__(self, userid, username, password):
        self._userid = userid
        self._username = username
        self._password = password

    @property
    def userid(self):
        return int(self._userid)

    @userid.setter
    def userid(self, userid):
        if not userid:
            raise ValueError("User ID is required")
        if len(str(userid)) != 8:
            raise ValueError("User ID must be 8 characters long")
        try:
            userid = int(userid)
        except ValueError:
            raise ValueError("User ID must be an integer")
        self._userid = userid

    @property
    def username(self):
        return str(self._username)

    @username.setter
    def username(self, username):
        if not username:
            raise ValueError("Username is required")
        self._username = username

    @property
    def password(self):
        return str(self._password)

    @password.setter
    def password(self, password):
        if not password:
            raise ValueError("Password is required")
        self._password = password

    def get_user(self):
        return self.username

    def show(self):
        return "\n".join([
            f"User ID: {self.userid}",
            f"Username: {self.username}",
            f"Password: {self.password}"
        ])

    def __str__(self):
        return self.show()

    @staticmethod
    def create_user_table():
        try:
            conn = psycopg2.connect(
                dbname="mortgage_calculator",
                user="postgres",
                password="admin123",
                host="localhost",
                port="5432"
            )
            conn.autocommit = True
            cursor = conn.cursor()

            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        userid SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password VARCHAR(50) NOT NULL
                    )
                """)
        except psycopg2.Error as e:
            logging.error(f"Error creating user table: {e}")
        finally:
            conn.close()

    @staticmethod
    def add_user(username, password):
        try:
            conn = psycopg2.connect(
                dbname="mortgage_calculator",
                user="postgres",
                password="admin123",
                host="localhost",
                port="5432"
            )
            conn.autocommit = True
            cursor = conn.cursor()

            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        except psycopg2.IntegrityError:
            logging.warning("User already exists.")
        except psycopg2.Error as e:
            logging.error(f"Error adding user: {e}")
        finally:
            conn.close()

    @staticmethod
    def authenticate_user(username, password):
        user = None
        try:
            conn = psycopg2.connect(
                dbname="mortgage_calculator",
                user="postgres",
                password="admin123",
                host="localhost",
                port="5432"
            )
            conn.autocommit = True
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
        except psycopg2.Error as e:
            logging.error(f"Error authenticating user: {e}")
        finally:
            conn.close()

        return user


User.create_user_table()
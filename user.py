import psycopg2
import logging

logging.basicConfig(level=logging.DEBUG)
"""
attribute: 
user_id
username
password
"""
"""
methods:
initiate_mortgage(mortgage_details)
update_mortgage
view_mortgage_details(mortgage_id)
view_all_mortgages()
"""


class User:
    def __init__(self, user_id=None, username="", password=""):
        self._user_id = user_id
        self._username = username
        self._password = password

    @property
    def user_id(self):
        return self._user_id

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    def show(self):
        return "\n".join([
            f"User ID: {self.user_id}",
            f"Username: {self.username}",
            f"Password: {self.password}"
        ])

    def __str__(self):
        return self.show()

    # methods for interacting with mortgages
    def initiate_mortgage(self, mortgage_details):
        pass

    def update_mortgage(self, mortgage_id, updated_details):
        pass

    def view_mortgage_details(self, mortgage_id):
        pass

    def view_all_mortgages(self):
        pass

    # static methods for database operations (e.g., create, retrieve, update, delete users)
    @staticmethod
    def connect_to_database():
        conn = psycopg2.connect(
            dbname="mortgage_calculator",
            user="postgres",
            password="admin123",
            host="localhost",
            port="5432"
        )
        return conn

    @staticmethod
    def create_user(username, password):
        conn = User.connect_to_database()
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
        except psycopg2.IntegrityError:
            logging.warning("User already exists.")
        except psycopg2.Error as e:
            logging.error(f"Error adding user: {e}")
        finally:
            if cursor:
                cursor.close()
            conn.close()

    @staticmethod
    def retrieve_user_by_username(username):
        user = None
        conn = User.connect_to_database()
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
        except psycopg2.Error as e:
            logging.error(f"Error retrieving user: {e}")
        finally:
            if cursor:
                cursor.close()
            conn.close()
        return user

    @staticmethod
    def update_user_password(username, new_password):
        conn = User.connect_to_database()
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password = %s WHERE username = %s", (new_password, username))
            conn.commit()
        except psycopg2.Error as e:
            logging.error(f"Error updating user password: {e}")
        finally:
            if cursor:
                cursor.close()
            conn.close()

    @staticmethod
    def delete_user(username):
        conn = User.connect_to_database()
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = %s", (username,))
            conn.commit()
        except psycopg2.Error as e:
            logging.error(f"Error deleting user: {e}")
        finally:
            if cursor:
                cursor.close()
            conn.close()
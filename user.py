import psycopg2
import logging
import re

logging.basicConfig(level=logging.DEBUG)

class UserManager:
    def __init__(self):
        self.conn = self.connect_to_database()

    @staticmethod
    def connect_to_database():
        try:
            conn = psycopg2.connect(
                dbname="mortgage_calculator",
                user="postgres",
                password="admin123",
                host="localhost",
                port="5432"
            )
            return conn
        except psycopg2.OperationalError as e:
            logging.error(f"Error connecting to the database: {e}")
            raise

    @staticmethod
    def validate_password(password):
        if len(password) <= 5:
            return False
        if not re.search("[a-zA-Z]", password):
            return False
        if not re.search("[0-9]", password):
            return False
        if not re.search("[!@#$%^&*(),.?\":{}|<>]", password):
            return False
        return True

    def create_user(self, username, password):
        if not self.validate_password(password):
            logging.error("Password must be more than 5 characters long and include letters, numbers, and symbols.")
            return

        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            self.conn.commit()
        except psycopg2.IntegrityError:
            logging.warning("User already exists.")
        except psycopg2.Error as e:
            logging.error(f"Error adding user: {e}")
        finally:
            if cursor:
                cursor.close()

    def retrieve_user_by_username(self, username):
        user = None
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
        except psycopg2.Error as e:
            logging.error(f"Error retrieving user: {e}")
        finally:
            if cursor:
                cursor.close()
        return user

    def update_user_password(self, username, new_password):
        if not self.validate_password(new_password):
            logging.error("Password must be more than 5 characters long and include letters, numbers, and symbols.")
            return

        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE users SET password = %s WHERE username = %s", (new_password, username))
            self.conn.commit()
        except psycopg2.Error as e:
            logging.error(f"Error updating user password: {e}")
        finally:
            if cursor:
                cursor.close()

    def delete_user(self, username):
        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = %s", (username,))
            self.conn.commit()
        except psycopg2.Error as e:
            logging.error(f"Error deleting user: {e}")
        finally:
            if cursor:
                cursor.close()

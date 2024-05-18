import psycopg2
import logging

logging.basicConfig(level=logging.DEBUG)


def create_database():
    # connect to the default database
    default_conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="admin123",
        host="localhost",
        port="5432"
    )
    default_conn.autocommit = True
    default_cursor = default_conn.cursor()

    # create mortgage_calculator database if it doesn't exist
    default_cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'mortgage_calculator'")
    database_exists = default_cursor.fetchone()

    if not database_exists:
        default_cursor.execute("CREATE DATABASE mortgage_calculator")

    default_conn.close()

    # connect to the mortgage_calculator database
    conn = psycopg2.connect(
        dbname="mortgage_calculator",
        user="postgres",
        password="admin123",
        host="localhost",
        port="5432"
    )
    conn.autocommit = True
    cursor = conn.cursor()

    # create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(50) NOT NULL
        )
    """)

    # create mortgages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mortgages (
            mortgage_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(user_id),
            principal FLOAT NOT NULL,
            interest FLOAT NOT NULL,
            term INTEGER NOT NULL,
            extra_costs FLOAT NOT NULL,
            deposit FLOAT NOT NULL,
            start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # create transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id SERIAL PRIMARY KEY,
            mortgage_id INTEGER REFERENCES mortgages(mortgage_id),
            transaction_type VARCHAR(50) NOT NULL,
            amount FLOAT NOT NULL,
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # create comments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            comment_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(user_id),
            mortgage_id INTEGER REFERENCES mortgages(mortgage_id),
            comment TEXT NOT NULL,
            comment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_database()

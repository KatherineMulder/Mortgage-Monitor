import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    try:
        #  default 'postgres' database
        default_conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="admin123",
            host="localhost",
            port="5432"
        )
        default_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        default_cursor = default_conn.cursor()

        # Check if mortgage_calculator database exists, create if not
        default_cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'mortgage_calculator'")
        database_exists = default_cursor.fetchone()

        if not database_exists:
            print("Creating 'mortgage_calculator' database...")
            default_cursor.execute("CREATE DATABASE mortgage_calculator")
        else:
            print("'mortgage_calculator' database already exists.")

        default_cursor.close()
        default_conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")
        return

    try:
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

        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """)

        #  mortgages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mortgages (
                mortgage_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id),
                mortgage_name VARCHAR(100) NOT NULL,
                principal NUMERIC(15, 2) NOT NULL,
                interest NUMERIC(5, 2) NOT NULL,
                term INTEGER NOT NULL,
                extra_costs NUMERIC(15, 2),
                deposit NUMERIC(15, 2),
                payment_override_enabled BOOLEAN,
                monthly_payment_override NUMERIC(15, 2),
                fortnightly_payment_override NUMERIC(15, 2),
                start_date DATE DEFAULT CURRENT_DATE,
                comments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                principal_increment_value NUMERIC(15, 2),
                number_of_principal_increments INTEGER,
                interest_rate_increment_value NUMERIC(5, 2),
                number_of_interest_rate_increments INTEGER
            )
        """)

        # add missing columns if they do not exist
        alter_queries = [
            "ALTER TABLE mortgages ADD COLUMN IF NOT EXISTS principal_increment_value NUMERIC(15, 2)",
            "ALTER TABLE mortgages ADD COLUMN IF NOT EXISTS number_of_principal_increments INTEGER",
            "ALTER TABLE mortgages ADD COLUMN IF NOT EXISTS interest_rate_increment_value NUMERIC(5, 2)",
            "ALTER TABLE mortgages ADD COLUMN IF NOT EXISTS number_of_interest_rate_increments INTEGER"
        ]

        for query in alter_queries:
            cursor.execute(query)

        # interest_rate_changes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interest_rate_changes (
                id SERIAL PRIMARY KEY,
                mortgage_id INTEGER REFERENCES mortgages(mortgage_id),
                new_interest_rate NUMERIC(5, 2) NOT NULL,
                effective_date DATE NOT NULL
            )
        """)

        # transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                mortgage_id INTEGER REFERENCES mortgages(mortgage_id),
                transaction_date DATE NOT NULL DEFAULT CURRENT_DATE,
                current_principal NUMERIC(15, 2) NOT NULL,
                interest_rate NUMERIC(5, 2) NOT NULL,
                remaining_term_months INTEGER NOT NULL,
                extra_payment NUMERIC(15, 2),
                updated_monthly_payment NUMERIC(15, 2),
                updated_fortnightly_payment NUMERIC(15, 2),
                balloon_payment NUMERIC(15, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # amortization_schedules table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS amortization_schedules (
                id SERIAL PRIMARY KEY,
                mortgage_id INTEGER REFERENCES mortgages(mortgage_id),
                payment_date DATE NOT NULL,
                principal_payment NUMERIC(15, 2) NOT NULL,
                interest_payment NUMERIC(15, 2) NOT NULL,
                remaining_balance NUMERIC(15, 2) NOT NULL
            )
        """)

        #  comments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id SERIAL PRIMARY KEY,
                mortgage_id INTEGER REFERENCES mortgages(mortgage_id),
                user_id INTEGER REFERENCES users(user_id),
                comment TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        cursor.close()
        conn.close()
        print("Database and tables created successfully.")
    except Exception as e:
        print(f"Error setting up database tables: {e}")


def check_database_connection():
    try:
        conn = psycopg2.connect(
            dbname="mortgage_calculator",
            user="postgres",
            password="admin123",
            host="localhost",
            port="5432"
        )
        conn.close()
        return True
    except psycopg2.OperationalError:
        return False


if __name__ == "__main__":
    create_database()

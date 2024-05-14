import psycopg2


def create_database():
    default_conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="admin123",
        host="localhost",
        port="5432"
    )
    default_conn.autocommit = True
    default_cursor = default_conn.cursor()

    default_cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'mortgage_calculator'")
    database_exists = default_cursor.fetchone()

    if not database_exists:
        default_cursor.execute("CREATE DATABASE mortgage_calculator")

    default_conn.close()

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
        CREATE TABLE IF NOT EXISTS mortgages (
            mortgage_id SERIAL PRIMARY KEY,
            mortgage_name VARCHAR(100) NOT NULL,
            principal NUMERIC NOT NULL,
            interest NUMERIC NOT NULL,
            term_years INTEGER NOT NULL,
            deposit NUMERIC,
            extra_costs NUMERIC,
            monthly_interest NUMERIC,
            monthly_repayment NUMERIC,
            monthly_principal_repayment NUMERIC,
            fortnightly_interest NUMERIC,
            fortnightly_repayment NUMERIC,
            fortnightly_principal_repayment NUMERIC
        )
    """)

    conn.commit()
    conn.close()

create_database()

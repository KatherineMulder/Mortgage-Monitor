import psycopg2


def connect_to_database():

    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="admin123",
        host="localhost",
        port="5432"
    )
    return conn


def authenticate_user(username, password):
    conn = connect_to_database()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        return user
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        cursor.close()
        conn.close()

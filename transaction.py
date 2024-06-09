import psycopg2
from datetime import datetime

DATABASE_URI = {
    'dbname': 'mortgage_calculator',
    'user': 'postgres',
    'password': 'admin123',
    'host': 'localhost',
    'port': '5432'
}


def log_transaction(mortgage_id, transaction_type, amount, current_principal, new_interest_rate=None,
                    new_monthly_payment=None, new_fortnightly_payment=None, remaining_term_months=None,
                    extra_payment=None, description=None):
    try:
        conn = psycopg2.connect(**DATABASE_URI)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO transactions (
                mortgage_id, transaction_date, transaction_type, amount, current_principal, 
                new_interest_rate, new_monthly_payment, new_fortnightly_payment, 
                remaining_term_months, extra_payment, description
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            mortgage_id, datetime.utcnow(), transaction_type, amount, current_principal,
            new_interest_rate, new_monthly_payment, new_fortnightly_payment,
            remaining_term_months, extra_payment, description
        ))

        conn.commit()
        cursor.close()
        conn.close()

        print("Transaction logged successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    log_transaction(
        mortgage_id=1,
        transaction_type="Update",
        amount=5000,
        current_principal=700000,
        new_interest_rate=3.5,
        new_monthly_payment=4500,
        new_fortnightly_payment=2200,
        remaining_term_months=180,
        extra_payment=1000,
        description="Updated mortgage details"
    )

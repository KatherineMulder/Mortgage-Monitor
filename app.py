from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
from user import User
from mortgage import Mortgage

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret key"


def connect_to_database():
    conn = psycopg2.connect(
        dbname="mortgage_calculator",
        user="postgres",
        password="admin123",
        host="localhost",
        port="5432"
    )
    conn.autocommit = True
    return conn


@app.route("/", methods=["GET", "POST"])
def root():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            conn = connect_to_database()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            cursor.close()
            conn.close()

            if user:
                if password == user[2]:
                    session['username'] = username
                    return redirect(url_for("index"))
                else:
                    return render_template('login.html', error="Invalid username or password")
            else:
                return redirect(url_for("signup"))

        except Exception as e:
            return f"An error occurred: {str(e)}"

    return render_template('login.html')


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return render_template("signup.html", error="Passwords do not match")

        try:
            if User.retrieve_user_by_username(username):
                return render_template("signup.html", error="Username already exists")

            User.create_user(username, password)
            return redirect(url_for("login"))

        except Exception as e:
            return f"An error occurred: {str(e)}"

    return render_template("signup.html")


@app.route("/index")
def index():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    mortgage_details = []
    error_message = None

    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT mortgage_id, principal, interest, term, extra_costs, deposit 
            FROM mortgages 
            WHERE user_id = (SELECT user_id FROM users WHERE username = %s)
        """, (username,))
        mortgages = cursor.fetchall()

        for mortgage in mortgages:
            mortgage_id, principal, interest, term, extra_costs, deposit = mortgage
            mortgage_obj = Mortgage()
            mortgage_obj.gather_inputs(principal, interest, term, extra_costs, deposit, False, None, None)
            mortgage_obj.calculate_initial_payment_breakdown()
            mortgage_obj.calculate_mortgage_maturity()
            amortization_schedule = mortgage_obj.amortization_table()

            cursor.execute("""
                SELECT comment 
                FROM comments 
                WHERE mortgage_id = %s
                ORDER BY comment_date
            """, (mortgage_id,))
            comments = cursor.fetchall()

            # Add comments to the mortgage object
            for comment, in comments:
                mortgage_obj.add_comment(comment)

            mortgage_detail = mortgage_obj.to_dict()
            mortgage_detail['mortgage_id'] = mortgage_id  # Ensure mortgage_id is included

            # Debugging prints to check the structure
            print(f"Mortgage ID: {mortgage_id}")
            print(f"Initial Payment Breakdown: {mortgage_detail['initial_payment_breakdown']}")
            print(f"Mortgage Maturity: {mortgage_detail['mortgage_maturity']}")
            print(f"Amortization Schedule: {mortgage_detail['amortization_schedule']}")

            mortgage_details.append(mortgage_detail)

        cursor.close()
        conn.close()
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)

    return render_template('index.html', username=username, mortgage_details=mortgage_details, error_message=error_message)

@app.route("/new_mortgage", methods=["GET", "POST"])
def new_mortgage():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    mortgage_name = None
    monthly_interest = None
    monthly_repayment = None
    monthly_principal_repayment = None
    fortnightly_interest = None
    fortnightly_repayment = None
    fortnightly_principal_repayment = None
    principal = 0
    interest = 0
    term = 0
    extra_costs = 0
    deposit = 0
    payment_override_enabled = False
    monthly_payment_override = None
    fortnightly_payment_override = None

    if request.method == 'POST':
        mortgage_name = request.form["mortgage_name"]
        principal = float(request.form["principal"])
        interest = float(request.form["interest"])
        term = int(request.form["term"])
        extra_costs = float(request.form["extra_costs"])
        deposit = float(request.form["deposit"])
        payment_override_enabled = 'payment_override_enabled' in request.form
        monthly_payment_override = float(request.form["monthly_payment_override"]) if payment_override_enabled else None
        fortnightly_payment_override = float(request.form["fortnightly_payment_override"]) if payment_override_enabled else None

        mortgage = Mortgage()
        mortgage.gather_inputs(
            principal=principal,
            interest=interest,
            term=term,
            extra_costs=extra_costs,
            deposit=deposit,
            payment_override_enabled=payment_override_enabled,
            monthly_payment_override=monthly_payment_override,
            fortnightly_payment_override=fortnightly_payment_override
        )
        mortgage.calculate_initial_payment_breakdown()

        initial_payment_breakdown = mortgage.initial_payment_breakdown
        monthly_interest = round(initial_payment_breakdown["initial_interest_monthly"], 2)
        monthly_principal_repayment = round(initial_payment_breakdown["initial_principal_monthly"], 2)
        monthly_repayment = round(initial_payment_breakdown["estimated_repayment_monthly"], 2)
        fortnightly_interest = round(initial_payment_breakdown["initial_interest_fortnightly"], 2)
        fortnightly_principal_repayment = round(initial_payment_breakdown["initial_principal_fortnightly"], 2)
        fortnightly_repayment = round(initial_payment_breakdown["estimated_repayment_fortnightly"], 2)

    return render_template(
        'new_mortgage.html',
        mortgage_name=mortgage_name,
        principal=principal,
        interest=interest,
        term=term,
        extra_costs=extra_costs,
        deposit=deposit,
        payment_override_enabled=payment_override_enabled,
        monthly_payment_override=monthly_payment_override,
        fortnightly_payment_override=fortnightly_payment_override,
        monthly_interest=monthly_interest,
        monthly_principal_repayment=monthly_principal_repayment,
        monthly_repayment=monthly_repayment,
        fortnightly_interest=fortnightly_interest,
        fortnightly_principal_repayment=fortnightly_principal_repayment,
        fortnightly_repayment=fortnightly_repayment
    )


@app.route("/save_mortgage", methods=["POST"])
def save_mortgage():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    mortgage_name = request.form["mortgage_name"]
    principal = float(request.form["principal"])
    interest = float(request.form["interest"])
    term = int(request.form["term"])
    extra_costs = float(request.form["extra_costs"])
    deposit = float(request.form["deposit"])
    payment_override_enabled = 'payment_override_enabled' in request.form
    monthly_payment_override = float(request.form["monthly_payment_override"]) if payment_override_enabled else None
    fortnightly_payment_override = float(request.form["fortnightly_payment_override"]) if payment_override_enabled else None

    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO mortgages (user_id, principal, interest, term, extra_costs, deposit) 
            VALUES ((SELECT user_id FROM users WHERE username = %s), %s, %s, %s, %s, %s)
        """, (username, principal, interest, term, extra_costs, deposit))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("index"))

    except Exception as e:
        return f"An error occurred: {str(e)}"


@app.route("/update_mortgage")
def update_mortgage():
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template("update_mortgage.html")


@app.route("/remove_mortgage")
def remove_mortgage():
    if 'username' not in session:
        return redirect(url_for('login'))

    return render_template("remove_mortgage.html")


@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route("/add_comment", methods=["POST"])
def add_comment():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    mortgage_id = request.form["mortgage_id"]
    comment = request.form["comment"]

    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO comments (user_id, mortgage_id, comment) 
            VALUES ((SELECT user_id FROM users WHERE username = %s), %s, %s)
        """, (username, mortgage_id, comment))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        return f"An error occurred: {str(e)}"

    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)

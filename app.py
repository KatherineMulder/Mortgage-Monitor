from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import psycopg2
from user import UserManager
from mortgage import Mortgage

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret key"

user_manager = UserManager()

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

            if user and password == user[2]:
                session['username'] = username
                return redirect(url_for("index"))
            else:
                return render_template('login.html', error="Invalid username or password")

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

        if not user_manager.validate_password(password):
            return render_template("signup.html", error="Password does not meet the criteria")

        try:
            if user_manager.retrieve_user_by_username(username):
                return render_template("signup.html", error="Username already exists")

            user_manager.create_user(username, password)
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

            for comment, in comments:
                mortgage_obj.add_comment(comment)

            mortgage_detail = {
                'mortgage_id': mortgage_id,
                'initial_principal': mortgage_obj._initial_principal,
                'initial_interest': mortgage_obj._initial_interest,
                'initial_term': mortgage_obj._initial_term,
                'extra_costs': mortgage_obj._extra_costs,
                'deposit': mortgage_obj._deposit,
                'initial_payment_breakdown': mortgage_obj.initial_payment_breakdown,
                'mortgage_maturity': mortgage_obj.mortgage_maturity,
                'amortization_schedule': mortgage_obj.amortization_schedule,
                'comments': mortgage_obj._comments
            }

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

    results = None
    mortgage_name = None
    principal = None
    interest = None
    term = None
    extra_costs = None
    deposit = None
    payment_override_enabled = None
    monthly_payment_override = None
    fortnightly_payment_override = None
    comment = None

    if request.method == 'POST':
        mortgage_name = request.form.get("mortgage_name")
        principal = float(request.form.get("principal"))
        interest = float(request.form.get("interest"))
        term = int(request.form.get("term"))
        extra_costs = float(request.form.get("extra_costs")) if request.form.get("extra_costs") else 0.0
        deposit = float(request.form.get("deposit")) if request.form.get("deposit") else 0.0

        payment_override_enabled = 'payment_override_enabled' in request.form
        monthly_payment_override = float(
            request.form.get("monthly_payment_override")) if payment_override_enabled and request.form.get(
            "monthly_payment_override") else None
        fortnightly_payment_override = float(
            request.form.get("fortnightly_payment_override")) if payment_override_enabled and request.form.get(
            "fortnightly_payment_override") else None
        comment = request.form.get("comment")

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
        mortgage.calculate_mortgage_maturity()

        if comment:
            mortgage.add_comment(comment)


        formatted_results = {
            'initial_payment_breakdown': {key: f"{value:,.2f}" for key, value in mortgage.initial_payment_breakdown.items()},
            'mortgage_maturity': mortgage.mortgage_maturity,
            'comments': mortgage.get_comments()
        }

        results = formatted_results

        if 'recalculate' in request.form:
            return render_template('new_mortgage.html', results=results, mortgage_name=mortgage_name, principal=principal,
                                   interest=interest, term=term, extra_costs=extra_costs, deposit=deposit,
                                   payment_override_enabled=payment_override_enabled,
                                   monthly_payment_override=monthly_payment_override,
                                   fortnightly_payment_override=fortnightly_payment_override, comment=comment)

    return render_template('new_mortgage.html', results=results, mortgage_name=mortgage_name, principal=principal,
                           interest=interest, term=term, extra_costs=extra_costs, deposit=deposit,
                           payment_override_enabled=payment_override_enabled,
                           monthly_payment_override=monthly_payment_override,
                           fortnightly_payment_override=fortnightly_payment_override, comment=comment)



@app.route("/save_mortgage", methods=["POST"])
def save_mortgage():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    mortgage_name = request.form["mortgage_name"]
    principal = float(request.form["principal"])
    interest = float(request.form["interest"])
    term = int(request.form["term"])
    extra_costs = float(request.form["extra_costs"]) if request.form["extra_costs"] else 0.0
    deposit = float(request.form["deposit"]) if request.form["deposit"] else 0.0
    payment_override_enabled = request.form["payment_override_enabled"] == 'True'
    monthly_payment_override = float(request.form["monthly_payment_override"]) if payment_override_enabled and \
                                                                                  request.form[
                                                                                      "monthly_payment_override"] else None
    fortnightly_payment_override = float(request.form["fortnightly_payment_override"]) if payment_override_enabled and \
                                                                                          request.form[
                                                                                              "fortnightly_payment_override"] else None
    comment = request.form["comment"]

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
    mortgage.calculate_mortgage_maturity()

    if comment:
        mortgage.add_comment(comment)

    # Save the mortgage object in your database or file system here

    return redirect(url_for('index'))  # Adjust according to your index page logic


@app.route("/update_mortgage")
def update_mortgage():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('update_mortgage.html')


@app.route("/remove_mortgage")
def remove_mortgage():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('remove_mortgage.html')


@app.route("/update_password", methods=['POST'])
def update_password():
    if 'username' not in session:
        return jsonify({'message': 'Unauthorized'}), 401
    new_password = request.form['new_password']
    if user_manager.validate_password(new_password):
        user_manager.update_user_password(session['username'], new_password)
        return jsonify({'message': 'password updated successfully!'})
    else:
        return jsonify({'message': 'Please must include numbers and symbol .'}), 400


@app.route("/remove_user", methods=['POST'])
def remove_user():
    if 'username' not in session:
        return jsonify({'message': 'unauthorized'}), 401
    user_manager.delete_user(session['username'])
    session.pop('username', None)
    return jsonify({'message': 'user removed successfully.'})


@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)

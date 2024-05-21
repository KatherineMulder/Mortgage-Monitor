from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import psycopg2
from user import UserManager
from mortgage import Mortgage
from graphing import generate_all_mortgage_charts


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
            SELECT mortgage_id, mortgage_name, principal, interest, term, extra_costs, deposit, start_date, 
                   payment_override_enabled, monthly_payment_override, fortnightly_payment_override 
            FROM mortgages 
            WHERE user_id = (SELECT user_id FROM users WHERE username = %s)
        """, (username,))
        mortgages = cursor.fetchall()

        for mortgage in mortgages:
            mortgage_id, mortgage_name, principal, interest, term, extra_costs, deposit, start_date, payment_override_enabled, monthly_payment_override, fortnightly_payment_override = mortgage
            mortgage_obj = Mortgage()
            mortgage_obj.gather_inputs(principal, interest, term, extra_costs, deposit, payment_override_enabled, monthly_payment_override, fortnightly_payment_override)
            mortgage_obj.calculate_initial_payment_breakdown()
            mortgage_obj.calculate_mortgage_maturity()
            amortization_schedule = mortgage_obj.amortization_table()

            cursor.execute("SELECT comment FROM comments WHERE mortgage_id = %s", (mortgage_id,))
            comments = cursor.fetchall()
            comments = [comment[0] for comment in comments]

            mortgage_details.append({
                'mortgage_name': mortgage_name,
                'initial_principal': principal,
                'initial_interest': interest,
                'initial_term': term,
                'extra_costs': extra_costs,
                'deposit': deposit,
                'initial_payment_breakdown': mortgage_obj.get_initial_payment_breakdown(),
                'mortgage_maturity': mortgage_obj.mortgage_maturity,
                'amortization_schedule': amortization_schedule,
                'comments': comments,
                'created_at': start_date
            })
            # generate chart
            charts = generate_all_mortgage_charts(mortgage_details)

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
    finally:
        cursor.close()
        conn.close()

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
        action = request.form.get('action')
        mortgage_name = request.form.get("mortgage_name")
        principal = float(request.form.get("principal"))
        interest = float(request.form.get("interest"))
        term = int(request.form.get("term"))
        extra_costs = float(request.form.get("extra_costs")) if request.form.get("extra_costs") else 0.0
        deposit = float(request.form.get("deposit")) if request.form.get("deposit") else 0.0

        payment_override_enabled = 'payment_override_enabled' in request.form
        monthly_payment_override = float(request.form.get("monthly_payment_override")) if payment_override_enabled and request.form.get("monthly_payment_override") else None
        fortnightly_payment_override = float(request.form.get("fortnightly_payment_override")) if payment_override_enabled and request.form.get("fortnightly_payment_override") else None
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

        initial_payment_breakdown_raw = mortgage.initial_payment_breakdown
        initial_payment_breakdown_formatted = {key: f"{value:,.2f}" for key, value in mortgage.initial_payment_breakdown.items()}

        formatted_results = {
            'initial_payment_breakdown_raw': initial_payment_breakdown_raw,
            'initial_payment_breakdown': initial_payment_breakdown_formatted,
            'mortgage_maturity': mortgage.mortgage_maturity,
            'comments': mortgage.get_comments()
        }

        results = formatted_results

        if action == 'calculate':
            return render_template('new_mortgage.html', results=results, mortgage_name=mortgage_name, principal=principal,
                                   interest=interest, term=term, extra_costs=extra_costs, deposit=deposit,
                                   payment_override_enabled=payment_override_enabled,
                                   monthly_payment_override=monthly_payment_override,
                                   fortnightly_payment_override=fortnightly_payment_override, comment=comment)

        elif action == 'recalculate':
            if payment_override_enabled and monthly_payment_override:
                if monthly_payment_override <= initial_payment_breakdown_raw['estimated_repayment_monthly']:
                    flash("The override amount must be higher than the estimated repayment", 'danger')
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

        elif action == 'save_mortgage':
            if 'username' in session:
                username = session['username']
                conn = connect_to_database()
                cursor = conn.cursor()
                try:
                    cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
                    user_id = cursor.fetchone()[0]

                    cursor.execute("""
                        INSERT INTO mortgages (user_id, mortgage_name, principal, interest, term, extra_costs, deposit, payment_override_enabled, monthly_payment_override, fortnightly_payment_override)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING mortgage_id
                    """, (user_id, mortgage_name, principal, interest, term, extra_costs, deposit, payment_override_enabled,
                          monthly_payment_override, fortnightly_payment_override))

                    mortgage_id = cursor.fetchone()[0]

                    if comment:
                        cursor.execute("""
                            INSERT INTO comments (mortgage_id, user_id, comment)
                            VALUES (%s, %s, %s)
                        """, (mortgage_id, user_id, comment))

                    conn.commit()
                    flash('Mortgage saved successfully!', 'success')
                except Exception as e:
                    conn.rollback()
                    flash(f"An error occurred: {str(e)}", 'danger')
                finally:
                    cursor.close()
                    conn.close()

                return redirect(url_for('index'))

    return render_template('new_mortgage.html', results=results, mortgage_name=mortgage_name, principal=principal,
                           interest=interest, term=term, extra_costs=extra_costs, deposit=deposit,
                           payment_override_enabled=payment_override_enabled,
                           monthly_payment_override=monthly_payment_override,
                           fortnightly_payment_override=fortnightly_payment_override, comment=comment)

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
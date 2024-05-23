from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import psycopg2
from user import UserManager
from mortgage import Mortgage
import logging

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret key"
user_manager = UserManager()

logging.basicConfig(level=logging.DEBUG)


def connect_to_database():
    try:
        conn = psycopg2.connect(
            dbname="mortgage_calculator",
            user="postgres",
            password="admin123",
            host="localhost",
            port="5432"
        )
        conn.autocommit = True
        logging.debug("Database connection established.")
        return conn
    except Exception as e:
        logging.error(f"Failed to connect to the database: {str(e)}")
        raise


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
            logging.error(f"Login error: {str(e)}")
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
            logging.error(f"Signup error: {str(e)}")
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
                'mortgage_id': mortgage_id,
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

    except Exception as e:
        logging.error(f"Error fetching mortgage details: {str(e)}")
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

        formatted_results = {
            'initial_payment_breakdown': {key: f"{value:,.2f}" for key, value in mortgage.initial_payment_breakdown.items()},
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


@app.route("/update_mortgage/<int:mortgage_id>", methods=["GET", "POST"])
def update_mortgage(mortgage_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = None
    cursor = None

    try:
        conn = connect_to_database()
        cursor = conn.cursor()

        if request.method == 'POST':
            logging.debug("Updating mortgage ID: %s", mortgage_id)

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
            balloon_payment = float(request.form.get("balloon_payment")) if request.form.get("balloon_payment") else 0.0
            new_comment = request.form.get("comment")

            logging.debug(
                "Form data: mortgage_name=%s, principal=%s, interest=%s, term=%s, extra_costs=%s, deposit=%s, payment_override_enabled=%s, monthly_payment_override=%s, fortnightly_payment_override=%s, balloon_payment=%s, new_comment=%s",
                mortgage_name, principal, interest, term, extra_costs, deposit, payment_override_enabled,
                monthly_payment_override, fortnightly_payment_override, balloon_payment, new_comment)

            # Fetch current principal for balloon payment calculation
            cursor.execute("SELECT principal FROM mortgages WHERE mortgage_id = %s", (mortgage_id,))
            current_principal = cursor.fetchone()[0]

            # balloon payyment
            if balloon_payment > 0:
                mortgage = Mortgage()
                mortgage.gather_inputs(
                    principal=current_principal,
                    interest=interest,
                    term=term,
                    extra_costs=extra_costs,
                    deposit=deposit,
                    payment_override_enabled=payment_override_enabled,
                    monthly_payment_override=monthly_payment_override,
                    fortnightly_payment_override=fortnightly_payment_override
                )
                mortgage.make_balloon_payment(balloon_payment)
                principal = mortgage._initial_principal
                logging.debug("Balloon payment applied. New principal: %s", principal)


            cursor.execute("""
                UPDATE mortgages
                SET mortgage_name = %s, principal = %s, interest = %s, term = %s, extra_costs = %s, deposit = %s, 
                    payment_override_enabled = %s, monthly_payment_override = %s, fortnightly_payment_override = %s
                WHERE mortgage_id = %s
            """, (mortgage_name, principal, interest, term, extra_costs, deposit, payment_override_enabled,
                  monthly_payment_override, fortnightly_payment_override, mortgage_id))

            # new comment if there is any
            if new_comment:
                cursor.execute("""
                    INSERT INTO comments (mortgage_id, user_id, comment)
                    VALUES (%s, %s, %s)
                """, (mortgage_id, session['user_id'], new_comment))
                logging.debug("New comment added: %s", new_comment)

            conn.commit()
            logging.debug("Mortgage updated successfully.")
            flash('Mortgage updated successfully!', 'success')
            return redirect(url_for('update_mortgage', mortgage_id=mortgage_id))

        else:
            logging.debug("Fetching mortgage details for mortgage ID: %s", mortgage_id)
            cursor.execute("""
                SELECT mortgage_name, principal, interest, term, extra_costs, deposit, payment_override_enabled, 
                       monthly_payment_override, fortnightly_payment_override
                FROM mortgages
                WHERE mortgage_id = %s
            """, (mortgage_id,))
            mortgage = cursor.fetchone()

            if mortgage is None:
                logging.error("Mortgage not found for ID: %s", mortgage_id)
                flash("Mortgage not found!", 'danger')
                return redirect(url_for('index'))

            mortgage_details = {
                'mortgage_name': mortgage[0],
                'principal': mortgage[1],
                'interest': mortgage[2],
                'term': mortgage[3],
                'extra_costs': mortgage[4],
                'deposit': mortgage[5],
                'payment_override_enabled': mortgage[6],
                'monthly_payment_override': mortgage[7],
                'fortnightly_payment_override': mortgage[8]
            }

            # fetch comment
            cursor.execute("SELECT comment FROM comments WHERE mortgage_id = %s", (mortgage_id,))
            comments = cursor.fetchall()
            comments = [comment[0] for comment in comments]

            logging.debug("Fetched mortgage details: %s", mortgage_details)
            logging.debug("Fetched comments: %s", comments)
            return render_template('update_mortgage.html', mortgage=mortgage_details, mortgage_id=mortgage_id,
                                   comments=comments)

    except Exception as e:
        logging.error("An error occurred: %s", str(e))
        flash(f"An error occurred: {str(e)}", 'danger')
        return redirect(url_for('index'))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/remove_mortgage/<int:mortgage_id>", methods=["POST"])
def remove_mortgage(mortgage_id):
    if 'username' not in session:
        flash('You must be logged in to perform this action', 'danger')
        return redirect(url_for('login'))

    conn = connect_to_database()
    try:
        cursor = conn.cursor()

        #  track the deletion process
        logging.debug(f"Attempting to delete mortgage with ID {mortgage_id}")

        cursor.execute("DELETE FROM comments WHERE mortgage_id = %s", (mortgage_id,))
        cursor.execute("DELETE FROM mortgages WHERE mortgage_id = %s", (mortgage_id,))

        conn.commit()
        logging.debug(f"Successfully deleted mortgage with ID {mortgage_id}")

        flash('Mortgage removed successfully!', 'success')
    except Exception as e:
        conn.rollback()
        logging.error(f"Error occurred while deleting mortgage with ID {mortgage_id}: {str(e)}")
        flash(f"An error occurred: {str(e)}", 'danger')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('index'))


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


from flask import (Flask, render_template, request, redirect, url_for, session,
                   jsonify, flash, send_file)
import psycopg2
from user import UserManager
from mortgage import Mortgage
import logging
import pandas as pd
from io import BytesIO
import database
from graphing import create_amortization_charts
from datetime import datetime
from decimal import Decimal

user_manager = UserManager()
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret key"
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
            SELECT mortgage_id, mortgage_name, principal, interest, term, extra_costs, deposit, 
                   payment_override_enabled, monthly_payment_override, fortnightly_payment_override
            FROM mortgages 
            WHERE user_id = (SELECT user_id FROM users WHERE username = %s)
        """, (username,))
        mortgages = cursor.fetchall()

        for mortgage in mortgages:
            mortgage_id, mortgage_name, principal, interest, term, extra_costs, deposit, payment_override_enabled, monthly_payment_override, fortnightly_payment_override = mortgage
            mortgage_obj = Mortgage(mortgage_name, float(interest), term, float(principal), float(deposit),
                                    float(extra_costs))
            mortgage_obj.gather_inputs(float(principal), float(interest), term, float(extra_costs), float(deposit),
                                       payment_override_enabled,
                                       float(monthly_payment_override) if monthly_payment_override else None,
                                       float(fortnightly_payment_override) if fortnightly_payment_override else None)
            mortgage_obj.calculate_initial_payment_breakdown()
            mortgage_obj.calculate_mortgage_maturity()
            amortization_schedule = mortgage_obj.amortization_table()
            graph_html_monthly, graph_html_fortnightly = create_amortization_charts(amortization_schedule)

            cursor.execute("SELECT comment FROM comments WHERE mortgage_id = %s", (mortgage_id,))
            comments = cursor.fetchall()
            comments = [comment[0] for comment in comments]

            cursor.execute("""
                SELECT new_interest_rate, effective_date
                FROM interest_rate_changes
                WHERE mortgage_id = %s
                ORDER BY effective_date DESC
                LIMIT 1
            """, (mortgage_id,))
            interest_rate_change = cursor.fetchone()

            latest_interest_rate = float(interest_rate_change[0]) if interest_rate_change else float(interest)
            latest_effective_date = interest_rate_change[1] if interest_rate_change else datetime.now()

            mortgage_details.append({
                'mortgage_id': mortgage_id,
                'mortgage_name': mortgage_name,
                'initial_principal': float(principal),
                'initial_interest': float(interest),
                'initial_term': term,
                'extra_costs': float(extra_costs),
                'deposit': float(deposit),
                'initial_payment_breakdown': mortgage_obj.get_initial_payment_breakdown(),
                'mortgage_maturity': mortgage_obj.mortgage_maturity,
                'amortization_schedule': amortization_schedule,
                'comments': comments,
                'created_at': datetime.now(),
                'graph_html_monthly': graph_html_monthly,
                'graph_html_fortnightly': graph_html_fortnightly,
                'latest_interest_rate': latest_interest_rate,
                'latest_effective_date': latest_effective_date,
            })

    except Exception as e:
        logging.error(f"Error fetching mortgage details: {str(e)}")
        error_message = f"An error occurred: {str(e)}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('index.html', username=username, mortgage_details=mortgage_details,
                           error_message=error_message)


@app.route("/new_mortgage", methods=["GET", "POST"])
def new_mortgage():
    if 'username' not in session:
        return redirect(url_for('login'))

    results = None
    increment_results = {
        'principal_increment_value': None,
        'number_of_principal_increments': None,
        'interest_rate_increment_value': None,
        'number_of_interest_rate_increments': None
    }

    if request.method == 'POST':
        action = request.form.get('action')
        mortgage_name = request.form.get("mortgage_name", "")
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
        comment = request.form.get("comment", "")

        principal_increment_value = request.form.get("principal_increment_value")
        principal_increment_value = float(
            principal_increment_value) if principal_increment_value and principal_increment_value != 'None' else None
        increment_results['principal_increment_value'] = principal_increment_value

        number_of_principal_increments = request.form.get("number_of_principal_increments")
        number_of_principal_increments = int(
            number_of_principal_increments) if number_of_principal_increments and number_of_principal_increments != 'None' else None
        increment_results['number_of_principal_increments'] = number_of_principal_increments

        interest_rate_increment_value = request.form.get("interest_rate_increment_value")
        interest_rate_increment_value = float(
            interest_rate_increment_value) if interest_rate_increment_value and interest_rate_increment_value != 'None' else None
        increment_results['interest_rate_increment_value'] = interest_rate_increment_value

        number_of_interest_rate_increments = request.form.get("number_of_interest_rate_increments")
        number_of_interest_rate_increments = int(
            number_of_interest_rate_increments) if number_of_interest_rate_increments and number_of_interest_rate_increments != 'None' else None
        increment_results['number_of_interest_rate_increments'] = number_of_interest_rate_increments

        if action == 'calculate' or action == 'override':
            mortgage = Mortgage(
                mortgage_name, interest, term, principal, deposit, extra_costs, comment,
                payment_override_enabled, monthly_payment_override, fortnightly_payment_override
            )
            mortgage.calculate_initial_payment_breakdown()
            mortgage.calculate_mortgage_maturity()

            # Calculate increments and add them to the results
            planning_scenarios = mortgage.generate_planning_scenarios(
                principal_increment_value, number_of_principal_increments,
                interest_rate_increment_value, number_of_interest_rate_increments
            )

            formatted_results = {
                'initial_payment_breakdown': {key: f"{value:,.2f}" for key, value in
                                              mortgage.initial_payment_breakdown.items()},
                'mortgage_maturity': mortgage.mortgage_maturity,
                'comments': mortgage.get_comments(),
                'increment_results': increment_results,  # Include increment results
                'planning_scenarios': planning_scenarios,  # Include planning scenarios
                'interest': interest  # Include interest
            }

            results = formatted_results

            return render_template(
                'new_mortgage.html', results=results, mortgage_name=mortgage_name, principal=principal,
                interest=interest, term=term, extra_costs=extra_costs, deposit=deposit,
                payment_override_enabled=payment_override_enabled, monthly_payment_override=monthly_payment_override,
                fortnightly_payment_override=fortnightly_payment_override, comment=comment,
                principal_increment_value=principal_increment_value,
                number_of_principal_increments=number_of_principal_increments,
                interest_rate_increment_value=interest_rate_increment_value,
                number_of_interest_rate_increments=number_of_interest_rate_increments
            )

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
                    """, (
                        user_id, mortgage_name, principal, interest, term, extra_costs, deposit,
                        payment_override_enabled, monthly_payment_override, fortnightly_payment_override
                    ))

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

    return render_template(
        'new_mortgage.html', results=results
    )


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

            new_interest_rate = Decimal(request.form.get("new_interest_rate"))
            extra_payment = Decimal(request.form.get("extra_payment")) if request.form.get(
                "extra_payment") else Decimal(0.0)
            payment_override_enabled = 'payment_override_enabled' in request.form
            updated_monthly_payment = Decimal(request.form.get("monthly_payment_override")) if request.form.get(
                "monthly_payment_override") else None
            updated_fortnightly_payment = Decimal(request.form.get("fortnightly_payment_override")) if request.form.get(
                "fortnightly_payment_override") else None
            balloon_payment = Decimal(request.form.get("balloon_payment")) if request.form.get(
                "balloon_payment") else Decimal(0.0)
            new_comment = request.form.get("comment")

            logging.debug(
                "Form data: new_interest_rate=%s, extra_payment=%s, payment_override_enabled=%s, updated_monthly_payment=%s, updated_fortnightly_payment=%s, balloon_payment=%s, new_comment=%s",
                new_interest_rate, extra_payment, payment_override_enabled,
                updated_monthly_payment, updated_fortnightly_payment, balloon_payment, new_comment)

            cursor.execute("SELECT principal, interest, term FROM mortgages WHERE mortgage_id = %s", (mortgage_id,))
            result = cursor.fetchone()
            if result:
                principal = Decimal(result[0])
                interest = Decimal(result[1])
                term = int(result[2])

                # Apply balloon payment
                if balloon_payment > 0:
                    mortgage = Mortgage("temp", interest, term, principal, Decimal(0.0), Decimal(0.0))
                    mortgage.make_balloon_payment(balloon_payment)
                    current_principal = mortgage._initial_principal
                    logging.debug("Balloon payment applied. New principal: %s", current_principal)
                else:
                    current_principal = principal

                cursor.execute("""
                    UPDATE mortgages
                    SET principal = %s, interest = %s, payment_override_enabled = %s, monthly_payment_override = %s, 
                    fortnightly_payment_override = %s
                    WHERE mortgage_id = %s
                """, (current_principal, new_interest_rate, payment_override_enabled, updated_monthly_payment,
                      updated_fortnightly_payment, mortgage_id))

                cursor.execute("""
                    INSERT INTO interest_rate_changes (mortgage_id, new_interest_rate, effective_date)
                    VALUES (%s, %s, %s)
                """, (mortgage_id, new_interest_rate, datetime.now()))

                if new_comment:
                    cursor.execute("SELECT user_id FROM users WHERE username = %s", (session['username'],))
                    user_id = cursor.fetchone()[0]
                    cursor.execute("""
                        INSERT INTO comments (mortgage_id, user_id, comment)
                        VALUES (%s, %s, %s)
                    """, (mortgage_id, user_id, new_comment))
                    logging.debug("New comment added: %s", new_comment)

                conn.commit()
                logging.debug("Mortgage updated successfully.")
                flash('Mortgage updated successfully!', 'success')
                return redirect(url_for('index'))
            else:
                logging.error("Mortgage not found for ID: %s", mortgage_id)
                flash("Mortgage not found!", 'danger')
                return redirect(url_for('index'))

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
                'principal': float(mortgage[1]),
                'interest': float(mortgage[2]),
                'term': mortgage[3],
                'extra_costs': float(mortgage[4]),
                'deposit': float(mortgage[5]),
                'payment_override_enabled': mortgage[6],
                'monthly_payment_override': float(mortgage[7]) if mortgage[7] else None,
                'fortnightly_payment_override': float(mortgage[8]) if mortgage[8] else None
            }

            # comments
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
        return redirect(url_for('login'))

    try:
        conn = connect_to_database()
        cursor = conn.cursor()

        # mortgage belongs to the logged-in user
        cursor.execute("""
            SELECT user_id FROM mortgages WHERE mortgage_id = %s
        """, (mortgage_id,))
        mortgage_user_id = cursor.fetchone()

        if mortgage_user_id is None:
            flash('Mortgage not found!', 'danger')
            logging.error(f"Mortgage {mortgage_id} not found")
            return redirect(url_for('index'))

        user_id = session.get('user_id')
        if not user_id:
            cursor.execute("SELECT user_id FROM users WHERE username = %s", (session['username'],))
            user_id = cursor.fetchone()[0]

        if mortgage_user_id[0] != user_id:
            flash('You do not have permission to delete this mortgage!', 'danger')
            logging.error(f"User {user_id} does not have permission to delete mortgage {mortgage_id}")
            return redirect(url_for('index'))

        cursor.execute("DELETE FROM comments WHERE mortgage_id = %s", (mortgage_id,))
        cursor.execute("DELETE FROM interest_rate_changes WHERE mortgage_id = %s", (mortgage_id,))
        cursor.execute("DELETE FROM mortgages WHERE mortgage_id = %s", (mortgage_id,))
        conn.commit()
        flash('Mortgage deleted successfully!', 'success')
        logging.info(f"Mortgage {mortgage_id} deleted successfully")

    except Exception as e:
        conn.rollback()
        flash(f"An error occurred: {str(e)}", 'danger')
        logging.error(f"Error deleting mortgage {mortgage_id}: {str(e)}")
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
        return jsonify({'message': 'Password updated successfully!'})
    else:
        return jsonify({'message': 'Password must include numbers and symbols.'}), 400


@app.route("/remove_user", methods=['POST'])
def remove_user():
    if 'username' not in session:
        return jsonify({'message': 'Unauthorized'}), 401
    user_manager.delete_user(session['username'])
    session.pop('username', None)
    return jsonify({'message': 'User removed successfully.'})


@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


def get_mortgage_details(mortgage_id):
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT mortgage_id, mortgage_name, principal, interest, term, extra_costs, deposit, start_date, 
                   payment_override_enabled, monthly_payment_override, fortnightly_payment_override 
            FROM mortgages 
            WHERE mortgage_id = %s
        """, (mortgage_id,))
        mortgage = cursor.fetchone()

        if mortgage:
            mortgage_id, mortgage_name, principal, interest, term, extra_costs, deposit, start_date, payment_override_enabled, monthly_payment_override, fortnightly_payment_override = mortgage
            mortgage_obj = Mortgage(mortgage_name, float(interest), term, float(principal), float(deposit),
                                    float(extra_costs))
            mortgage_obj.gather_inputs(
                float(principal), float(interest), term, float(extra_costs), float(deposit),
                payment_override_enabled,
                float(monthly_payment_override) if monthly_payment_override else None,
                float(fortnightly_payment_override) if fortnightly_payment_override else None
            )
            mortgage_obj.calculate_initial_payment_breakdown()
            mortgage_obj.calculate_mortgage_maturity()
            amortization_schedule = mortgage_obj.amortization_table()

            cursor.execute("SELECT comment FROM comments WHERE mortgage_id = %s", (mortgage_id,))
            comments = cursor.fetchall()
            comments = [comment[0] for comment in comments]

            mortgage_details = {
                'mortgage_id': mortgage_id,
                'mortgage_name': mortgage_name,
                'principal': principal,
                'interest': interest,
                'term': term,
                'extra_costs': extra_costs,
                'deposit': deposit,
                'initial_payment_breakdown': mortgage_obj.get_initial_payment_breakdown(),
                'mortgage_maturity': mortgage_obj.mortgage_maturity,
                'amortization_schedule': amortization_schedule,
                'comments': comments,
                'created_at': start_date,
                'payment_override_enabled': payment_override_enabled,
                'monthly_payment_override': monthly_payment_override,
                'fortnightly_payment_override': fortnightly_payment_override
            }

            return mortgage_details

    except Exception as e:
        logging.error(f"Error fetching mortgage details: {str(e)}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return None


@app.route('/amortization_schedule/<int:mortgage_id>')
def amortization_schedule(mortgage_id):
    mortgage = get_mortgage_details(mortgage_id)
    if mortgage is None:
        return "Mortgage not found", 404

    return render_template('amortization_schedule.html', mortgage=mortgage)


@app.route('/export_amortization/<int:mortgage_id>')
def export_amortization(mortgage_id):
    try:
        logging.info("Retrieving mortgage details")
        mortgage = get_mortgage_details(mortgage_id)
        if mortgage is None:
            logging.warning(f"Mortgage with ID {mortgage_id} not found")
            return "Mortgage not found", 404

        logging.info("Converting amortization schedule to data frames")
        amortization_schedule = mortgage['amortization_schedule']

        df_monthly = pd.DataFrame(amortization_schedule['monthly'])
        df_fortnightly = pd.DataFrame(amortization_schedule['fortnightly'])

        logging.info("creating excel writer")
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_monthly.to_excel(writer, index=False, sheet_name='Monthly')
            df_fortnightly.to_excel(writer, index=False, sheet_name='Fortnightly')

        logging.info("export successful")
        output.seek(0)

        # send the file
        return send_file(output, as_attachment=True, download_name='amortization_schedule.xlsx',
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    except Exception as e:
        logging.error(f"Error exporting amortization schedule: {str(e)}")
        return "Internal Server Error", 500


@app.route("/view_projections/<int:mortgage_id>")
def view_projections(mortgage_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    conn = None
    cursor = None
    mortgage_details = {}
    error_message = None

    try:
        conn = connect_to_database()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT mortgage_name, principal, interest, term, extra_costs, deposit, 
                   payment_override_enabled, monthly_payment_override, fortnightly_payment_override
            FROM mortgages 
            WHERE mortgage_id = %s AND user_id = (SELECT user_id FROM users WHERE username = %s)
        """, (mortgage_id, username))
        mortgage = cursor.fetchone()

        if mortgage:
            mortgage_name, principal, interest, term, extra_costs, deposit, payment_override_enabled, monthly_payment_override, fortnightly_payment_override = mortgage
            mortgage_obj = Mortgage(mortgage_name, float(interest), term, float(principal), float(deposit),
                                    float(extra_costs))
            mortgage_obj.gather_inputs(float(principal), float(interest), term, float(extra_costs), float(deposit),
                                       payment_override_enabled,
                                       float(monthly_payment_override) if monthly_payment_override else None,
                                       float(fortnightly_payment_override) if fortnightly_payment_override else None)
            scenarios = mortgage_obj.generate_planning_scenarios(
                principal_increment=3000.00,
                principal_increments=7,
                interest_increment=5.0,
                interest_increments=15
            )

            projected_payments_monthly = []
            projected_payments_fortnightly = []

            for i in range(16):
                monthly_row = [f"{5.0 + (5 * i):.2f}%"]
                fortnightly_row = [f"{5.0 + (5 * i):.2f}%"]
                for scenario in scenarios:
                    if i < len(scenario['monthly_payments']):
                        monthly_row.append(f"${scenario['monthly_payments'][i]:,.2f}")
                    if i < len(scenario['fortnightly_payments']):
                        fortnightly_row.append(f"${scenario['fortnightly_payments'][i]:,.2f}")
                projected_payments_monthly.append(monthly_row)
                projected_payments_fortnightly.append(fortnightly_row)

            mortgage_details = {
                'mortgage_id': mortgage_id,
                'mortgage_name': mortgage_name,
                'projected_payments_monthly': projected_payments_monthly,
                'projected_payments_fortnightly': projected_payments_fortnightly
            }

    except Exception as e:
        logging.error(f"Error fetching mortgage details: {str(e)}")
        error_message = f"An error occurred: {str(e)}"
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template('view_projections.html', mortgage_details=mortgage_details, error_message=error_message)


@app.route('/export_projections/<int:mortgage_id>')
def export_projections(mortgage_id):
    try:
        logging.info("Retrieving mortgage details")
        mortgage = get_mortgage_details(mortgage_id)
        if mortgage is None:
            logging.warning(f"Mortgage with ID {mortgage_id} not found")
            return "Mortgage not found", 404

        # check
        required_keys = ['mortgage_name', 'principal', 'interest', 'term', 'extra_costs', 'deposit',
                         'payment_override_enabled', 'monthly_payment_override', 'fortnightly_payment_override']
        for key in required_keys:
            if key not in mortgage:
                logging.error(f"Key '{key}' not found in mortgage details")
                return f"Missing key: {key}", 500

        logging.info("Generating projections")
        mortgage_obj = Mortgage(
            mortgage['mortgage_name'], float(mortgage['interest']), mortgage['term'],
            float(mortgage['principal']), float(mortgage['deposit']), float(mortgage['extra_costs'])
        )
        mortgage_obj.gather_inputs(
            float(mortgage['principal']), float(mortgage['interest']), mortgage['term'], float(mortgage['extra_costs']),
            float(mortgage['deposit']), mortgage['payment_override_enabled'],
            float(mortgage['monthly_payment_override']) if mortgage['monthly_payment_override'] else None,
            float(mortgage['fortnightly_payment_override']) if mortgage['fortnightly_payment_override'] else None
        )
        scenarios = mortgage_obj.generate_planning_scenarios(
            principal_increment=3000.00, principal_increments=7, interest_increment=5.0, interest_increments=8
        )

        interest_rates = [5.0 + 5 * i for i in range(8)]
        projected_payments_monthly = []
        projected_payments_fortnightly = []

        for scenario in scenarios:
            monthly_row = []
            fortnightly_row = []
            for i in range(8):  # Assuming 8 interest increments
                monthly_row.append(f"${scenario['monthly_payments'][i]:,.2f}")
                fortnightly_row.append(f"${scenario['fortnightly_payments'][i]:,.2f}")
            projected_payments_monthly.append(monthly_row)
            projected_payments_fortnightly.append(fortnightly_row)

        # headers
        columns = [f"{rate:.2f}%" for rate in interest_rates]

        df_projected_monthly = pd.DataFrame(projected_payments_monthly, columns=columns)
        df_projected_fortnightly = pd.DataFrame(projected_payments_fortnightly, columns=columns)

        logging.info("Creating Excel writer")
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_projected_monthly.to_excel(writer, index=False, sheet_name='Monthly Projections')
            df_projected_fortnightly.to_excel(writer, index=False, sheet_name='Fortnightly Projections')

        logging.info("Export successful")
        output.seek(0)

        # send the file
        return send_file(output, as_attachment=True, download_name=f'mortgage_{mortgage_id}_projections.xlsx',
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    except Exception as e:
        logging.error(f"Error exporting projections: {str(e)}")
        return "Internal Server Error", 500


if __name__ == "__main__":
    database.create_database()
    app.run(debug=True)

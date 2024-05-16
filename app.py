from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
import plotly.graph_objs as go
from user import User
from auth import authenticate_user


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
                # if the entered password matches the stored password
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
            return redirect(url_for("index"))

        except Exception as e:
            return f"An error occurred: {str(e)}"

    return render_template("signup.html")


@app.route("/index")
def index():


@app.route('/new_mortgage', methods=['GET', 'POST'])
def new_mortgage():
    mortgage_name = None
    monthly_interest = 0
    monthly_repayment = 0
    monthly_principal_repayment = 0
    fortnightly_interest = 0
    fortnightly_repayment = 0
    fortnightly_principal_repayment = 0

    if request.method == 'POST':
        mortgage_name = request.form['mortgage_name']
        principal = float(request.form['initial_principal'])
        interest = float(request.form['initial_interest'])
        term_years = int(request.form['initial_term'])
        deposit = float(request.form.get('deposit', 0))
        extra_costs = float(request.form.get('extra_costs', 0))

        new_mortgage = Mortgage(
            mortgage_id=None,
            mortgage_name=mortgage_name,
            initial_interest=interest,
            initial_term=term_years,
            initial_principal=principal,
            deposit=deposit,
            extra_costs=extra_costs
        )

        monthly_interest = round(new_mortgage.calculate_monthly_interest(), 2)
        monthly_repayment = round(new_mortgage.calculate_monthly_repayment(), 2)
        monthly_principal_repayment = round(new_mortgage.calculate_monthly_principal_repayment(), 2)
        fortnightly_interest = round(new_mortgage.calculate_fortnightly_interest(), 2)
        fortnightly_repayment = round(new_mortgage.calculate_fortnightly_repayment(), 2)
        fortnightly_principal_repayment = round(new_mortgage.calculate_fortnightly_principal_repayment(), 2)

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
            INSERT INTO mortgages (mortgage_name, principal, interest, term_years, deposit, extra_costs,
                                   monthly_interest, monthly_repayment, monthly_principal_repayment,
                                   fortnightly_interest, fortnightly_repayment, fortnightly_principal_repayment)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
                       (mortgage_name, principal, interest, term_years, deposit, extra_costs,
                        monthly_interest, monthly_repayment, monthly_principal_repayment,
                        fortnightly_interest, fortnightly_repayment, fortnightly_principal_repayment))

        conn.close()

        return redirect(url_for('index'))

    return render_template('new_mortgage.html',
                           mortgage_name=mortgage_name,
                           monthly_interest=monthly_interest,
                           monthly_principal_repayment=monthly_principal_repayment,
                           monthly_repayment=monthly_repayment,
                           fortnightly_interest=fortnightly_interest,
                           fortnightly_principal_repayment=fortnightly_principal_repayment,
                           fortnightly_repayment=fortnightly_repayment)


def generate_interest_principal_chart(interests, principals, mortgage_names):
    data = [
        go.Scatter(x=mortgage_names, y=interests, mode='lines+markers', name='Interest'),
        go.Scatter(x=mortgage_names, y=principals, mode='lines+markers', name='Principal')
    ]
    layout = go.Layout(title='Interest and Principal Payments')
    fig = go.Figure(data=data, layout=layout)
    return fig.to_html(full_html=False)


@app.route("/update_mortgage")
def update_mortgage():
    return render_template("update_mortgage.html")


@app.route("/remove_mortgage")
def remove_mortgage():
    return render_template("remove_mortgage.html")


@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)

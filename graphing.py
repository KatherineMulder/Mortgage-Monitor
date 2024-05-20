from dash import Dash, html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px
import flask
import psycopg2

from mortgage import Mortgage

"""
https://dash.plotly.com/interactive-graphing
"""

server = flask.Flask(__name__)

# create the instance
app = Dash(__name__, server=server, routes_pathname_prefix='/dash/')


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


# fetch mortgage data from the database for the logged-in user
def fetch_mortgage_data(username):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT mortgage_id, mortgage_name, principal, interest, term, extra_costs, deposit, start_date, 
               payment_override_enabled, monthly_payment_override, fortnightly_payment_override 
        FROM mortgages 
        WHERE user_id = (SELECT user_id FROM users WHERE username = %s)
    """, (username,))
    mortgages = cursor.fetchall()
    cursor.close()
    conn.close()

    data = []
    for mortgage in mortgages:
        mortgage_id, mortgage_name, principal, interest, term, extra_costs, deposit, start_date, payment_override_enabled, monthly_payment_override, fortnightly_payment_override = mortgage
        mortgage_obj = Mortgage()
        mortgage_obj.gather_inputs(principal, interest, term, extra_costs, deposit, payment_override_enabled,
                                   monthly_payment_override, fortnightly_payment_override)
        mortgage_obj.calculate_initial_payment_breakdown()
        mortgage_obj.calculate_mortgage_maturity()

        data.append({
            'Mortgage Name': mortgage_name,
            'Initial Principal': principal,
            'Initial Interest': interest,
            'Initial Term': term,
            'Total Amount Borrowed': mortgage_obj.get_initial_payment_breakdown()['total_amount_borrowed'],
            'Monthly Estimated Repayment': mortgage_obj.get_initial_payment_breakdown()['estimated_repayment_monthly'],
            'Monthly Total Repayment': mortgage_obj.get_initial_payment_breakdown()['total_repayment_monthly'],
            'Fortnightly Total Repayment': mortgage_obj.get_initial_payment_breakdown()['total_repayment_fortnightly'],
            'Year': start_date.year
        })

    return pd.DataFrame(data)


# fetch the username from the Flask session
@server.before_request
def get_username():
    flask.g.username = flask.session.get('username')


# layout for the Dash app
app.layout = html.Div([
    html.Div([
        dcc.Dropdown(
            id='mortgage-dropdown'
        )
    ], style={'width': '49%', 'display': 'inline-block'}),

    html.Div([
        dcc.Graph(id='mortgage-graph')
    ], style={'width': '100%', 'display': 'inline-block', 'padding': '20px'}),

    html.Div(dcc.Slider(
        id='year-slider'
    ), style={'width': '100%', 'padding': '0px 20px 20px 20px'})
])


# update the dropdown options and slider marks based on the user's data
@app.callback(
    [Output('mortgage-dropdown', 'options'),
     Output('mortgage-dropdown', 'value'),
     Output('year-slider', 'min'),
     Output('year-slider', 'max'),
     Output('year-slider', 'marks'),
     Output('year-slider', 'value')],
    [Input('mortgage-dropdown', 'id')]
)
def update_controls(_):
    if not flask.g.username:
        return [], None, None, None, {}, None

    df = fetch_mortgage_data(flask.g.username)
    options = [{'label': name, 'value': name} for name in df['Mortgage Name'].unique()]
    value = df['Mortgage Name'].iloc[0] if not df.empty else None
    min_year = df['Year'].min() if not df.empty else None
    max_year = df['Year'].max() if not df.empty else None
    marks = {str(year): str(year) for year in df['Year'].unique()} if not df.empty else {}
    slider_value = max_year

    return options, value, min_year, max_year, marks, slider_value


# callback to update the graph based on the selected mortgage and year
@app.callback(
    Output('mortgage-graph', 'figure'),
    [Input('mortgage-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_graph(selected_mortgage, selected_year):
    if not flask.g.username:
        return px.scatter()

    df = fetch_mortgage_data(flask.g.username)
    filtered_df = df[(df['Mortgage Name'] == selected_mortgage) & (df['Year'] == selected_year)]

    fig = px.line(filtered_df, x='Mortgage Name',
                  y=['Initial Principal', 'Total Amount Borrowed', 'Monthly Estimated Repayment'],
                  title=f'Mortgage Details for {selected_mortgage} in {selected_year}')

    return fig


from app import app as flask_app

# Run the server
if __name__ == "__main__":
    flask_app.run(debug=True)

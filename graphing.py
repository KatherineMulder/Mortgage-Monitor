import plotly.express as px
import pandas as pd


def generate_mortgage_chart(mortgage):
    # Create a DataFrame for the chart
    data = {
        'Category': [
            'Monthly Interest',
            'Monthly Principal',
            'Fortnightly Interest',
            'Fortnightly Principal'
        ],
        'Amount': [
            mortgage['initial_payment_breakdown']['initial_interest_monthly'],
            mortgage['initial_payment_breakdown']['initial_principal_monthly'],
            mortgage['initial_payment_breakdown']['initial_interest_fortnightly'],
            mortgage['initial_payment_breakdown']['initial_principal_fortnightly']
        ]
    }
    df = pd.DataFrame(data)

    # Generate the chart using Plotly Express

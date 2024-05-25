import plotly.express as px
import plotly.io as pio
import pandas as pd


def create_amortization_charts(amortization_schedule):
    df_monthly = pd.DataFrame(amortization_schedule["monthly"])
    df_fortnightly = pd.DataFrame(amortization_schedule["fortnightly"])

    #   monthly schedule
    fig_monthly = px.line(df_monthly, x='Period', y=['Interest', 'Principal'],
                          labels={'value': 'Amount', 'variable': 'Type'}, markers=True)

    fig_monthly.update_layout(
        width=1500,
        height=700,
        title_font=dict(size=24),
        xaxis_title_font=dict(size=20),
        yaxis_title_font=dict(size=20),
        legend_font=dict(size=18),
        font=dict(size=16)
    )

    graph_html_monthly = pio.to_html(fig_monthly, full_html=False)

    #  fortnightly schedule
    fig_fortnightly = px.line(df_fortnightly, x='Period', y=['Interest', 'Principal'],
                              labels={'value': 'Amount', 'variable': 'Type'}, markers=True)

    fig_fortnightly.update_layout(
        width=1500,
        height=700,
        title_font=dict(size=24),
        xaxis_title_font=dict(size=20),
        yaxis_title_font=dict(size=20),
        legend_font=dict(size=18),
        font=dict(size=16)
    )

    graph_html_fortnightly = pio.to_html(fig_fortnightly, full_html=False)

    return graph_html_monthly, graph_html_fortnightly

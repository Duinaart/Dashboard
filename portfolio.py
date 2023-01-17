import dash
from dash import dash_table

import dash_bootstrap_components as dbc
from dash import dcc
from dash import html

import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from euronext import nav_item
from euronext import dropdown

from df_and_graphs import final_portfolio
from df_and_graphs import table_df

pd.options.display.width = 0  # Make sure all columns of df fit

colors = ['#14213d', '#fb8b24', '#2a9134', '#d00000']
########################################################################################################################
""" Data wrangling for datatable"""
df = table_df

df['Acquisition Date'] = pd.to_datetime(df['Acquisition Date']).dt.date
df = df.rename(
    columns={'Acquisition Date': 'Acquisition', 'Pct of portfolio': '% Portfolio', 'Ticker Adj Close': 'Adj Close',
             'Share Value': 'Total Value (€)', 'SP Return': 'S&P Return', 'Cost Basis': 'Cost Basis (€)',})

df['T R filtering'] = df['Ticker Return'] * 100
df['SP R filtering'] = df['S&P Return'] * 100
df['S YTD filtering'] = df['Share YTD'] * 100
df['% oH filtering'] = df['% off High'] * 100

format_mapping = {
    'Cost Basis (€)':'{:,.2f}',
    'Total Value (€)':'{:,.2f}',
    '% Portfolio': "{:.2%}",
    'Share YTD': "{:.2%}",
    '% off High': "{:.2%}",
    'Ticker Return': "{:.2%}",
    'S&P Return': "{:.2%}",
}
for key, value in format_mapping.items():
    df[key] = df[key].apply(value.format)
df = df.round(2)


#######################################################################################################################
nav_item = nav_item

dropdown = dropdown

# Navigation Bar layout
navbar = dbc.Navbar(
    dbc.Container(  # A container keeps the content of the rows and columns into one single blob that can be moved
        [
            # Use row and col to control vertical alignment of logo
            dbc.Row(
                [dbc.Col((html.Img(
                    src='https://prismic-io.s3.amazonaws.com/plotly-marketing-website/bd1f702a-b623-48ab-a459-3ee92a7499b4_logo-plotly.svg',
                    height='30px')), width='auto'),
                    dbc.Col((dbc.NavbarBrand('Finance Dashboard')), width='auto')],
                align='center',
                className="g-0"
            ),
            dbc.Row(dbc.Col(dbc.NavbarToggler(id='navbar-toggler4'))),
            dbc.Row(dbc.Col(dbc.Collapse(
                dbc.Nav(
                    dbc.Col(
                        [nav_item,
                         dropdown,
                         ], width='auto'), className='ml-auto', navbar=True,
                ),
                id='navbar-collapse4',
                navbar=True,
            ), ))
        ],
    ),
    className='mb-5', )
#######################################################################################################################
'''Calculate Portfolio metrics'''
# portfolio_beta = (final_portfolio['Beta'] * final_portfolio['Pct of portfolio']).cumsum().tail(1).values[0].round(4)


''' Create Visualizations '''


#* Compare individual positions return to hypothetical investment in S&P YTD
def update_graph_1():
    fig1 = go.Figure()

    fig1.add_trace(go.Bar(
        x=final_portfolio['Ticker'][:10],
        y=final_portfolio['Share YTD'][:10],
        name='Ticker YTD',
    ))

    fig1.add_trace(go.Scatter(
        x=final_portfolio['Ticker'][:10],
        y=final_portfolio['SP 500 YTD'][:10],
        name='S&P 500 YTD',
    ))

    fig1.layout.update(
        title='YTD Return VS S&P 500 YTD',
        title_x=0.5,
        barmode='group',
        yaxis=dict(title='Returns', tickformat='.2%'),
        xaxis=dict(title='Ticker'),
        legend=dict(x=.8, y=1),
        colorway=colors,
        template='simple_white',
        hovermode='x unified',
    )

    return fig1


#* Current Share Price Versus Closing High since purchased
def update_graph_2():
    fig2 = go.Figure()

    fig2.add_trace(go.Bar(
        x=final_portfolio['Ticker'][:10],
        y=final_portfolio['% off High'],
        name='% off High'
    ))

    fig2.layout.update(
        title='Adj Close % off High',
        title_x=0.5,
        barmode='group',
        yaxis=dict(title='% Below Adj Close High', tickformat='.2%'),
        xaxis=dict(title='Ticker'),
        legend=dict(x=.8, y=1),
        colorway=colors,
        template='simple_white',
        hovermode='x unified',
    )
    return fig2


#* Total Return comparison chart
def update_graph_3():
    fig3 = go.Figure()

    fig3.add_trace(go.Bar(
        x=final_portfolio['Ticker'][:10],
        y=final_portfolio['Ticker Return'][:10],
        name='Ticker Total Return'
    ))
    fig3.add_trace(go.Scatter(
        x=final_portfolio['Ticker'][:10],
        y=final_portfolio['SP Return'],
        name='SP 500 Total Return'
    ))

    fig3.layout.update(
        title='Total Return VS S&P 500',
        title_x=0.5,
        barmode='group',
        yaxis=dict(title='Returns', tickformat='.2%'),
        xaxis=dict(title='Ticker', tickformat='.2%'),
        legend=dict(x=.8, y=1),
        colorway=colors,
        template='simple_white',
        hovermode='x unified',
    )
    return fig3


#* Cumulative Return over time chart
def update_graph_4():
    fig4 = go.Figure()

    fig4.add_trace(go.Bar(
        x=final_portfolio['Ticker'][:10],
        y=final_portfolio['Stock Gain'][:10],
        name='Ticker Total Return ($)'
    ))
    fig4.add_trace(go.Bar(
        x=final_portfolio['Ticker'][:10],
        y=final_portfolio['SP 500 Gain'][:10],
        name='SP 500 Total Return ($)'
    ))
    fig4.add_trace(go.Scatter(
        x=final_portfolio['Ticker'][:10],
        y=final_portfolio['Ticker Return'][:10],
        name='Ticker Total Return (%)',
        yaxis='y2'
    ))

    fig4.layout.update(
        title='Stock Gain/Loss VS S&P 500',
        title_x=0.5,
        barmode='group',
        yaxis=dict(title='Gain/(Loss) (€)'),
        yaxis2=dict(title='Ticker Return', overlaying='y', side='right', tickformat='.2%'),
        xaxis=dict(title='Ticker'),
        legend=dict(x=0, y=1,),
        colorway=colors,
        template='simple_white',
        hovermode='x unified',
    )
    return fig4


#* Get cumulative returns and investment chart
def update_graph_5():
    fig5 = go.Figure()

    fig5.add_trace(go.Bar(
        x=final_portfolio['Ticker'],
        y=final_portfolio['Cum Investment'],
        # mode='lines+markers',
        name='Cum investment'
    ))
    fig5.add_trace(go.Bar(
        x=final_portfolio['Ticker'],
        y=final_portfolio['Cum SP Return'],
        # mode='lines+markers',
        name='Cum SP500 Returns'
    ))
    fig5.add_trace(go.Bar(
        x=final_portfolio['Ticker'],
        y=final_portfolio['Cum Ticker Return'],
        # mode='lines+markers',
        name='Cum Ticker Returns',
    ))
    fig5.add_trace(go.Scatter(
        x=final_portfolio['Ticker'],
        y=final_portfolio['Cum Ticker Return'],
        # mode='lines+markers',
        name='Cum ROI Mult',
        yaxis='y2'
    ))


    fig5.layout.update(
        title='Total Cumulative Investments and Returns Over Time',
        title_x=0.5,
        barmode='group',
        yaxis=dict(title='Returns'),
        xaxis=dict(title='Ticker'),
        legend=dict(x=0, y=1),
        yaxis2=dict(title='Cum ROI Mult', overlaying='y', side='right'),
        colorway=colors,
        template='simple_white',
        hovermode = 'x unified',

    )
    return fig5
###################################################################################################################
body3 = html.Div(
    dbc.Container(
    [
        dbc.Row(dbc.Col(dcc.Store(id='memory-output3'))),
        dbc.Row(dbc.Col(navbar)),
        dbc.Row(dbc.Col(html.H2('Portfolio Dashboard', style={'text-align': 'center'}))),
        dbc.Row(dbc.Col(html.Br())),
        dbc.Row(dbc.Col(
            dash_table.DataTable(
                id='datatable',
                data=df.to_dict('records'),
                columns=[{"name": i, "id": i} for i in df.loc[:-4]],
                fixed_columns={'headers': True, 'data': 1},
                sort_action='native',
                style_cell={
                    # all three widths are needed
                    'minWidth': '160px', 'width': '160px', 'maxWidth': '160px',
                    'overflow': 'hidden', 'font_family': 'nunito sans'
                },
                style_cell_conditional= [{'if': {'column_id': 'T R filtering'},'display': 'None'},
                                         {'if': {'column_id': 'SP R filtering'},'display': 'None'},
                                         {'if': {'column_id': 'S YTD filtering'},'display': 'None'},
                                         {'if': {'column_id': '% oH filtering'},'display': 'None'}],
                style_table={'minWidth': '100%', },
                style_header=
                {'textAlign': 'left',
                 'backgroundColor': '#dae2e2',
                 'fontWeight': 'bold'
                 },
                style_data={'textAlign': 'left'},
                style_data_conditional=
                #* Background color of cells
                [{'if': {'column_id': c, 'row_index': 'even'}, 'backgroundColor': '#b0dbc1'} for c in ['Ticker']]
                + [{'if': {'column_id': c, 'row_index': 'odd'}, 'backgroundColor': '#75c093'} for c in ['Ticker']]
                + [{'if': {'column_id': c, 'row_index': 'even'}, 'backgroundColor': '#fef9e7'} for c in ['Acquisition', 'Quantity', 'Unit Cost', 'Cost Basis (€)', '% Portfolio']]
                + [{'if': {'column_id': c, 'row_index': 'odd'}, 'backgroundColor': '#FCF3CF'} for c in ['Acquisition', 'Quantity', 'Unit Cost', 'Cost Basis (€)', '% Portfolio']]
                + [{'if': {'column_id': c, 'row_index': 'even'}, 'backgroundColor': '#EBF5FB'} for c in ['Adj Close', 'Ticker Return', 'S&P Return', 'Total Value (€)', 'Share YTD']]
                + [{'if': {'column_id': c, 'row_index': 'odd'}, 'backgroundColor': '#D6EAF8'} for c in ['Adj Close', 'Ticker Return', 'S&P Return', 'Total Value (€)', 'Share YTD']]
                + [{'if': {'column_id': c, 'row_index': 'even'}, 'backgroundColor': '#fcf2f2'} for c in ['% off High', 'Volatility', 'Beta']]
                + [{'if': {'column_id': c, 'row_index': 'odd'}, 'backgroundColor': '#fae5e5'} for c in ['% off High', 'Volatility', 'Beta']]
                #* Data color of cells
                + [{'if': {'filter_query': '{T R filtering} > {SP R filtering}','column_id': 'Ticker Return'}, 'color': 'darkgreen'}]
                + [{'if': {'filter_query': '{T R filtering} < {SP R filtering}', 'column_id': 'Ticker Return'}, 'color': 'crimson'}]
                + [{'if': {'filter_query': '{S YTD filtering} > 0', 'column_id': 'Share YTD'}, 'color': 'darkgreen'}]
                + [{'if': {'filter_query': '{S YTD filtering} < 0', 'column_id': 'Share YTD'}, 'color': 'crimson'}]

                ,
                style_as_list_view=True,
                css=[{'selector': '.dash-cell div.dash-cell-value',
                      'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'}],
            ))),
        dbc.Col(dbc.Row(html.Br())),
        # dbc.Col(dbc.Row(html.P('The Portfolio Beta is {}'.format(portfolio_beta)))),
        dbc.Row(
            [
            dbc.Col(dbc.Card(dcc.Graph(id='total-return', figure=update_graph_3()))),
            dbc.Col(dbc.Card(dcc.Graph(id='YTD-return', figure=update_graph_1()))),
            # dbc.Col(dbc.Card(dcc.Graph(id='%-off-high', figure=update_graph_2())))
            ]
        ),
        dbc.Row(
            [
            dbc.Col(dbc.Card(dcc.Graph(id='total-gains', figure=update_graph_4()))),
            dbc.Col(dbc.Card(dcc.Graph(id='total-investments', figure=update_graph_5())))
            ]
        ),
    ]
    )
)


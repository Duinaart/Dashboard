import dash
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from datetime import datetime as dt
from datetime import date

from euronext import nav_item
from euronext import dropdown

import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import requests
from bs4 import BeautifulSoup as bs
import yahoo_fin.stock_info as si

# Light theme: LUX, dark theme: DARKLY (enable darktheme in navbar)
app = dash.Dash(external_stylesheets=[dbc.themes.LUX])
##############################################################

###############################################################
# Make a navigation bar (dropdown items)
## Make a reusable navitem for different dashboards
nav_item = nav_item

## Make a Reusable dropdown for different dashboards
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
                no_gutters=True,
            ),
            dbc.Row(dbc.Col(dbc.NavbarToggler(id='navbar-toggler3'))),
            dbc.Row(dbc.Col(dbc.Collapse(
                dbc.Nav(
                    dbc.Col(
                        [nav_item,
                         dropdown,
                         ], width='auto'), className='ml-auto', navbar=True,
                ),
                id='navbar-collapse3',
                navbar=True,
            ), ))
        ],
    ),
    className='mb-5', )

###################################################################################################################


###############################################################################################################
body2 = html.Div(
    dbc.Container(
        [
            dbc.Row(dbc.Col(dcc.Store(id='memory-output2'))),
            dbc.Row(dbc.Col(navbar)),
            dbc.Row(dbc.Col(html.H3('Financial Dashboard for S&P 500', style={'text-align': 'center'}))),
            # dbc.Row(dbc.Col(html.Br())),
            dbc.Row(
                [
                    dbc.Col(html.Div(
                        dbc.Input(id="inputsp", value='AAPL', debounce=True, ))),
                    dbc.Col(html.Div(id='output2sp', style={'text-align': 'center'})),
                    dbc.Col(html.Div(id='outputsp', style={'text-align': 'center'})),
                ]
            ),
            html.Div(dcc.DatePickerRange(
                id='my-date-picker-range',  # ID to be used for callback
                calendar_orientation='horizontal',  # vertical or horizontal
                day_size=39,  # size of calendar image. Default is 39
                with_portal=False,  # if True calendar will open in a full screen overlay portal
                first_day_of_week=1,  # Display of calendar when open (0 = Sunday)
                reopen_calendar_on_clear=True,
                is_RTL=False,  # True or False for direction of calendar
                clearable=True,  # whether or not the user can clear the dropdown
                number_of_months_shown=1,  # number of months shown when calendar is open
                min_date_allowed=dt(2013, 1, 1),  # minimum date allowed on the DatePickerRange component
                max_date_allowed=date.today(),  # maximum date allowed on the DatePickerRange component
                initial_visible_month=dt(2013, 1, 1),  # the month initially presented when the user opens the calendar
                start_date=dt(2020, 1, 1).date(),
                end_date=date.today(),
                # start_date_placeholder_text="Start Period",
                # end_date_placeholder_text="End Period",
                display_format='MMM Do, YYYY',  # how selected dates are displayed in the DatePickerRange component.
                month_format='MMMM, YYYY',  # how calendar headers are displayed when the calendar is opened.
                minimum_nights=2,  # minimum number of days between start and end date

                # persistence=True,
                # persisted_props=['start_date'],
                # persistence_type='session',  # session, local, or memory. Default is 'local'


                updatemode='singledate',  # singledate or bothdates. Determines when callback is triggered

            )),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id='linegraph-container-sp', figure={}), width=9),
                    dbc.Col(html.Div(id='table'), width='auto')
                ], form=True, align='center')
            # dbc.Row(dbc.Col(html.Div(id='table')))

        ]
)
)
#######################################################################################################################
def register_callbacks_sp500(app):
    @app.callback(Output('output2sp', 'children'), [Input('inputsp', 'value')])
    def full_company_name_sp(value):
        if value is not None:
            r = requests.get('https://finance.yahoo.com/quote/{}/'.format(value))
            webpage = bs(r.content, features='lxml')
            title = str(webpage.find('title'))
            title = title[7:]
            split_title = title.split('(')
            full_name = split_title[0]
            return full_name
        else:
            return ''


    @app.callback(Output('outputsp', 'children'), [Input('inputsp', 'value')])
    def get_latest_close_sp(value):
        if value is not None:
            dataset = si.get_data(value, index_as_date=True, interval='1d')
            df = pd.DataFrame(dataset)
            df = df[::-1]
            latest_close = round(df.loc[df.index[0], 'adjclose'], 2)
            return 'The latest close is: ' + str(latest_close)


    @app.callback(
        Output('linegraph-container-sp', 'figure'),
        [Input('inputsp', 'value'),
         Input('my-date-picker-range', 'start_date'),
         Input('my-date-picker-range', 'end_date')
         ])
    def update_graph(value, start_date, end_date):
        data = si.get_data(value, index_as_date=True, interval='1d')
        df = pd.DataFrame(data)

        dff = df.loc[start_date:end_date]

        fig2 = make_subplots(rows=2, cols=1, shared_xaxes=True, )

        # Make the subplots (way to have hover on both subplots simultaneously is not added yet)
        fig2.add_trace(go.Scatter(x=dff.index, y=dff['close'],
                                  hovertemplate='Price: € %{y}' + '<extra></extra>',
                                  mode='lines', line=dict(color='#14213d')), row=1, col=1)
        fig2.add_trace(go.Bar(x=dff.index, y=dff['volume'],
                              hovertemplate='Volume: %{y}' +
                                            '<extra></extra>', marker=dict(color='#fb8b24')), row=2, col=1)

        # Add the layout to the subplots
        fig2.layout.update(
            title='Stock price evolution',
            showlegend=False,
            template='simple_white',
            title_x=0.5,
            xaxis_showgrid=False,
            yaxis_showgrid=False,
            hovermode='x unified',  # Displays date on the x-axis in full
        )

        # Add labels to subplots
        fig2['layout']['yaxis']['title'] = 'Price'
        fig2['layout']['yaxis2']['title'] = 'Volume'

        return fig2

    @app.callback(
        Output('table', 'children'),
        [Input('inputsp', 'value')])
    def get_yahoo_data(value):
        dff = si.get_stats(value)
        dff = dff.iloc[:9]
        dff['Attribute'][:2] = dff['Attribute'][:2].str[:-2]
        dff['Attribute'][3:5] = dff['Attribute'][3:5].str[:-2]
        dff['Attribute'][7:] = dff['Attribute'][7:].str[:-2]
        # df.set_index('Attribute', inplace=True)
        return [dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in dff.columns],
            data=dff.to_dict('records'),
            style_data={'textAlign': 'left'},
            style_cell={'font_family': 'nunito sans'},
            style_as_list_view=True,
            style_header={'display': 'none'},
        )]
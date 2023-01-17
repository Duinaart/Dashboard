from dash import dcc
import dash_bootstrap_components as dbc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import yahoo_fin.stock_info as si

import requests
import pandas as pd
from datetime import datetime as dt
from datetime import date

##############################################################
# Make a navigation bar (dropdown items)
# Make a reusable navitem for different dashboards
nav_item = dbc.NavItem(
    dbc.Row(
        [dbc.NavLink('Euronext Stock Exchange', href='https://live.euronext.com/nl'),
         dbc.NavLink('Yahoo finance', href='https://finance.yahoo.com/')
         ],
        align='center',
    ),

)

# Make a Reusable dropdown for different dashboards
dropdown = dbc.Col(
    dbc.DropdownMenu(
        children=[
            dbc.DropdownMenuItem('Dash Documentation', href='https://dash.plotly.com/'),
            dbc.DropdownMenuItem('Bootstrap Documentation',
                                 href='https://dash-bootstrap-components.opensource.faculty.ai/docs/'),
            dbc.DropdownMenuItem('Quandl Documentation', href='https://docs.quandl.com/'),
            dbc.DropdownMenuItem(divider=True),
            dbc.DropdownMenuItem('Youtube tutorial',
                                 href='https://www.youtube.com/watch?v=P-XYio7G_Dg&ab_channel=PipInstallPython')
        ],
        nav=True,  # needs to be set to true if it is inside navigation bar to get consistent styling
        in_navbar=True,  # say that it needs to be in navigation bar
        label='Useful Links',
        right=True,
    ),
    width='auto'
)

# Navigation Bar layout
navbar = dbc.Navbar(
    dbc.Container(  # A container keeps the content of the rows and columns into one single blob that can be moved
        [
            # Use row and col to control vertical alignment of logo
            dbc.Row(
                [dbc.Col((html.Img(
                    src='https://prismic-io.s3.amazonaws.com/plotly-marketing-website/'
                        'bd1f702a-b623-48ab-a459-3ee92a7499b4_logo-plotly.svg',
                    height='30px')), width='auto'),
                 dbc.Col((dbc.NavbarBrand('Finance Dashboard')), width='auto')],
                align='center',
                className="g-0"
            ),
            dbc.Row(dbc.Col(dbc.NavbarToggler(id='navbar-toggler2'))),
            dbc.Row(dbc.Col(dbc.Collapse(
                dbc.Nav(
                    dbc.Col(
                        [nav_item,
                         dropdown,
                         ], width='auto'), className='ml-auto', navbar=True,
                ),
                id='navbar-collapse2',
                navbar=True,
            ), ))
        ],
    ),
    # color='dark',
    # dark=True,
    className='mb-5', )

###################################################################################################################


body1 = html.Div([
    dbc.Container(
        [
            dbc.Row(dbc.Col(dcc.Store(id='memory-output'))),
            dbc.Row(dbc.Col(navbar)),
            dbc.Row(
                dbc.Col(html.H3('Financial Dashboard for Euronext Stock Exchange', style={'text-align': 'center'}))),
            # dbc.Row(dbc.Col(html.Br())),
            dbc.Row(
                [
                    dbc.Col(html.Div(dbc.Input(id="input", value='ABI', debounce=True))),
                    dbc.Col(html.Div(id='output', style={'text-align': 'center'})),
                    dbc.Col(html.Div(id='output2', style={'text-align': 'center'})),
                    dbc.Col(html.Div(id='output3', style={'text-align': 'center'})),

                ]
            ),
            html.Div(dcc.DatePickerRange(
                id='my-date-picker-range2',  # ID to be used for callback
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
                    dbc.Col(dcc.Graph(id='linegraph-container-enx', figure={})),

                ]
            ),
            # dbc.Row([dbc.Col(html.Div(id='intermediate-value', style={'display': 'none'}))])
        ],
    ),
])
#######################################################################################################################
'''Create function with callbacks in it - dashboard will import this function'''


def register_callbacks_euronext(app):
    #* Write callback with memory to only take 1 API call and reuse it for the other calbacks
    @app.callback(Output('memory-output', 'data'), [Input('input', 'value')])
    def store_json_data(value):
        if value is not None:
            response = requests.get(
                'https://www.quandl.com/api/v3/datasets/EURONEXT/{}.json?api_key=1eCS2saTbHTFds2LjKkX'.format(value))
            data = response.json()
            return data

    @app.callback(Output('output', 'children'), [Input('memory-output', 'data')])
    def get_company_name(data):
        company_name = data['dataset']['name']
        return company_name

    @app.callback(Output('output2', 'children'), [Input('memory-output', 'data')])
    def get_latest_close(data):
        latest_close = data['dataset']['data'][0][4]
        return 'The latest close is: ' + str(latest_close)

    @app.callback(Output('output3', 'children'), [Input('memory-output', 'data')])
    def get_market(data):
        dataset = data['dataset']['description']
        split_dataset = dataset.split("<br>")
        market = split_dataset[2]
        return market

    @app.callback(
        Output('linegraph-container-enx', 'figure'),
        [Input('memory-output', 'data'),
         Input('my-date-picker-range2', 'start_date'),
         Input('my-date-picker-range2', 'end_date')
         ])
    def update_graph(data, start_date, end_date):
        dataset = data['dataset']['data']
        df = pd.DataFrame(dataset, columns=['date', 'open', 'high', 'low', 'close', 'volume', 'turnover'])
        df = df[::-1]
        df.set_index('date', inplace=True)
        dff = df.loc[start_date:end_date]

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True)

        # Make the subplots (way to have hover on both subplots simultaneously is not added yet)
        fig.add_trace(go.Scatter(x=dff.index, y=dff['close'],
                                 hovertemplate='Price: € %{y}' +
                                               '<extra></extra>',
                                 mode='lines', line=dict(color='#14213d')), row=1, col=1)
        fig.add_trace(go.Bar(x=dff.index, y=dff['volume'],
                             hovertemplate='Volume: %{y}' +
                                           '<extra></extra>', marker=dict(color='#fb8b24')), row=2, col=1)

        # Add the layout to the subplots
        fig.layout.update(
            title='Stock price evolution',
            showlegend=False,
            template='simple_white',
            title_x=0.5,
            xaxis_showgrid=False,
            yaxis_showgrid=False,
            hovermode='x unified',  # Displays date on the x-axis in full
        )

        # Add labels to subplots
        fig['layout']['yaxis']['title'] = 'Price'
        fig['layout']['yaxis2']['title'] = 'Volume'
        return fig





import dash
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from euronext import nav_item
from euronext import dropdown


import re

import pandas as pd
from bs4 import BeautifulSoup as bs
# * Get data from the FinViz Website and transform it into readable html
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

###################################################################################################################
CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH', '/usr/bin/chromedriver')
GOOGLE_CHROME_BIN = os.environ.get('GOOGLE_CHROME_BIN', '/usr/bin/google-chrome-stable')

url = 'https://finviz.com/futures.ashx'
# options = webdriver.ChromeOptions()
# options.binary_location = GOOGLE_CHROME_BIN
# options.add_argument("--headless")
# options.add_argument("--window-size=1920,1080")
# options.add_argument('--disable-gpu')
# options.add_argument('--no-sandbox')
# options.add_argument("--disable-extensions")
# options.add_argument('disable-infobars')

driver = webdriver.Firefox(executable_path='/usr/bin/geckodriver')
driver.set_window_size(1200, 600)
driver.get(url)
driver.maximize_window()

w1 = WebDriverWait(driver, 30)
w1.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div/div[1]/div/div[2]/div[1]/a[1]')))

soup = bs(driver.page_source, 'html')
driver.close()
divs = soup.find_all('div', {'class': 'tile_content'})
# div = divs[0].contents

# * Get useful data from all cards
m = []
# get all small divs inside mother div
for j in range(len(divs)):
    div = divs[j].contents
    n = []
    # every card contains multiple divs, get them all out and sort some stuff
    for i in range(len(div)):
        n.append(div[i].text)
    n.pop(2)
    n[2] = re.search('\(([^)]+)', n[2]).group(1)
    m.append(n)

# * Convert list of lists into pandas Dataframe
df = pd.DataFrame(m)
market_overview = df.copy()

market_overview.columns = ['Index', 'Price', '% Change']
# print(df)

indices = ['Euro Stoxx 50', 'S&P 500', 'Nasdaq 100', 'DJIA', 'Russell 2000', 'Nikkei 225']
risk = ['VIX', '2 Year Note', '5 Year Note', '10 Year Note', '30 Year Bond']

indices_df = market_overview[market_overview['Index'].isin(indices)]
indices_df['Indices Change Filtering'] = indices_df['% Change'].str.replace('%','')
indices_df['Indices Change Filtering'] = pd.to_numeric(indices_df['Indices Change Filtering'])
print(indices_df)

risk_df = market_overview[market_overview['Index'].isin(risk)]
risk_df['Risk Change Filtering'] = risk_df['% Change'].str.replace('%','')
risk_df['Risk Change Filtering'] = pd.to_numeric(risk_df['Risk Change Filtering'])



app = dash.Dash(external_stylesheets=[dbc.themes.LUX])
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
                    dbc.Col((dbc.NavbarBrand("Financial Dashboard")), width='auto')],
                align='center',
                no_gutters=True,
            ),
            dbc.Row(dbc.Col(dbc.NavbarToggler(id='navbar-toggler'))),
            dbc.Row(dbc.Col(dbc.Collapse(
                dbc.Nav(
                    dbc.Col(
                        [nav_item,
                         dropdown,
                         ], width='auto'), className='ml-auto', navbar=True,
                ),
                id='navbar-collapse',
                navbar=True,
            ), ))
        ],
    ),
    className='mb-5', )
###################################################################################################################
body4 = html.Div(
    dbc.Container(
        [
            dbc.Row(dbc.Col(navbar)),
            dbc.Row(dbc.Col(html.H2('Market Overview', style={'text-align': 'center'}))),
            dbc.Row(dbc.Col(html.Br())),
            dbc.Row(
                [
                    dbc.Col(
                        dash_table.DataTable(
                            id='indices',
                            data=indices_df.to_dict('records'),
                            columns=[{"name": i, "id": i} for i in indices_df.iloc[:, 0:3]],
                            # fixed_columns={'headers': True, 'data': 1},
                            sort_action='native',
                            style_header={
                                'backgroundColor': '#e9ecef',
                                'fontWeight': 'bold'
                            },
                            style_cell={'font_family': 'nunito sans', 'padding':'5px'},
                            style_as_list_view=True,
                            style_data_conditional=
                            #* Data color of cells
                            [{'if': {'filter_query': ' {Indices Change Filtering} < -1',
                                     'column_id': '% Change'}, 'color': '#6a040f'}] +
                            [{'if': {'filter_query': '{Indices Change Filtering} < 0 && {Indices Change Filtering} < -1',
                                     'column_id': '% Change'}, 'color': '#dc2f02'}] +
                            [{'if': {'filter_query': ' {Indices Change Filtering} > 0 && {Indices Change Filtering} < 1',
                                     'column_id': '% Change'}, 'color': '#52b788'}] +
                            [{'if': {'filter_query': ' {Indices Change Filtering} > 1',
                                     'column_id': '% Change'}, 'color': '#283618'}]

                        )
                    ),
                    dbc.Col(
                        dash_table.DataTable(
                            id='risk',
                            data=risk_df.to_dict('records'),
                            columns=[{"name": i, "id": i} for i in risk_df.iloc[:, 0:3]],
                            # fixed_columns={'headers': True, 'data': 1},
                            sort_action='native',
                            style_header={
                                'backgroundColor': '#e9ecef',
                                'fontWeight': 'bold'
                            },
                            style_cell={'font_family': 'nunito sans', 'padding': '5px'},
                            style_as_list_view=True,
                            style_data_conditional=
                            # * Data color of cells
                            [{'if': {'filter_query': '{Risk Change Filtering} < -1',
                                     'column_id': '% Change'}, 'color': '#6a040f'}] +
                            [{'if': {
                                'filter_query': '{Risk Change Filtering} < 0 && {Risk Change Filtering} > -1',
                                'column_id': '% Change'}, 'color': '#dc2f02'}] +
                            [{'if': {
                                'filter_query': ' {Risk Change Filtering} > 0 && {Risk Change Filtering} < 1',
                                'column_id': '% Change'}, 'color': '#52b788'}] +
                            [{'if': {'filter_query': '{Risk Change Filtering} > 1',
                                     'column_id': '% Change'}, 'color': '#283618'}]
                        )
                    ),

                ],
            ),
            dbc.Row(dbc.Col(html.Br())),
            dbc.Row(dbc.Col(html.Br())),
            dbc.Row(dbc.Col(html.Br())),
            dbc.Row(dbc.Col(html.Br())),
            dbc.Row(dbc.Col(html.P(dcc.Markdown('Data: _https://finviz.com/futures.ashx_')))),
        ]
    ))


from chart_studio.tools import set_credentials_file
import pandas as pd
import requests
import plotly.graph_objects as go
import chart_studio.plotly as py
from chart_studio.tools import set_credentials_file

# iex_api_key = 'sk_a5cd6e406de64bc493e2fbc08187b3e0'
# iex_base_url = 'https://cloud.iexapis.com/stable/stock/'
#
# plotly_api_key = 'Bx9U1oX59X6aly5iULP5'
# plotly_username = 'Duinaart'
#
# # Plotly chart studio verification
# set_credentials_file(
#     username=plotly_username,
#     api_key=plotly_api_key
# )
#
# """Fetch stock data from API"""
# params = {'token': iex_api_key, 'includeToday': 'true'}
# url = f'{iex_base_url}/AMZN/chart/1m'
# req = requests.get(url, params=params)
# data = req.content
#
# """Parse JSON as Pandas DataFrame."""
# stock_df = pd.read_json(data)
# stock_df = stock_df.loc[stock_df['date'].dt.dayofweek < 5]
# stock_df.set_index(keys=stock_df['date'], inplace=True)
# stock = stock_df.to_csv('stock.csv')

stock_df = pd.read_csv('stock.csv')
fig = go.Figure(data=[
    go.Candlestick(
        x=stock_df['date'],
        open=stock_df['open'],
        high=stock_df['high'],
        low=stock_df['low'],
        close=stock_df['close'],
        )],
)

# fig.update_layout(xaxis_rangeslider_visible=False)
fig.show()
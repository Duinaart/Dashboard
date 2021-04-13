import dash
import dash_bootstrap_components as dbc


from euronext import body1
from sp500 import body2
from portfolio import body3
# from market_overview import body4

from app import app
server = app.server

from euronext import register_callbacks_euronext
from sp500 import register_callbacks_sp500

tabs = dbc.Tabs(
    [
        # dbc.Tab(body4, label='Market'),
        dbc.Tab(body1, label='Euronext'),
        dbc.Tab(body2, label='S&P 500'),
        dbc.Tab(body3, label='Portfolio'),
    ]
)

app.layout = dbc.Container(tabs)

#########################################################################################################
if __name__ == '__main__':
    app.run_server(debug=True, port=8060)

import dash
import dash_bootstrap_components as dbc

from euronext import register_callbacks_euronext
from sp500 import register_callbacks_sp500
from euronext import body1
from sp500 import body2
from portfolio import body3
# Light theme: LUX, dark theme: DARKLY (enable darktheme in navbar)
app = dash.Dash(external_stylesheets=[dbc.themes.LUX])
server = app.server
app.config['suppress_callback_exceptions'] = True


tabs = dbc.Tabs(
    [
        # dbc.Tab(body4, label='Market'),
        dbc.Tab(body1, label='Euronext'),
        dbc.Tab(body2, label='S&P 500'),
        dbc.Tab(body3, label='Portfolio'),
    ]
)

app.layout = dbc.Container(tabs)
#######################################################################################################################
'''CALLBACKS EURONEXT TAB'''

register_callbacks_euronext(app)

#########################################################################################################
'''CALLBACKS SP500 tabs'''

register_callbacks_sp500(app)
#########################################################################################################
if __name__ == '__main__':
    app.run_server(debug=True, port=8060)



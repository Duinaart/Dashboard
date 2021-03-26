import dash
import dash_bootstrap_components as dbc

from euronext import register_callbacks_euronext
from sp500 import register_callbacks_sp500

# Light theme: LUX, dark theme: DARKLY (enable darktheme in navbar)
app = dash.Dash(external_stylesheets=[dbc.themes.LUX])

app.config['suppress_callback_exceptions'] = True

#######################################################################################################################
'''CALLBACKS EURONEXT TAB'''

register_callbacks_euronext(app)

#########################################################################################################
'''CALLBACKS SP500 tabs'''

register_callbacks_sp500(app)




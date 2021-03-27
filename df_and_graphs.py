import pandas as pd
import numpy as np

import yfinance as yf
import plotly.graph_objs as go
import datetime
pd.options.display.width = 0  # Make sure all columns of df fit

'''
TO DO 
    - dividends are not accounted for 
    - portfolio beta
    - maximum drawdown
    - ratio's: Treynor (Portfolio return - market return)/Beta, Sharpe and Jensen 
'''

'''Get Data and create dates necessary'''

#* Import sample worksheet with acquisition dates and initial cost basis
portfolio_df = pd.read_excel('Sample stocks acquisition dates_costs.xlsx')
# print(portfolio_df.dtypes)

#* Create date ranges for S&P and for portfolio's tickers
start_sp = datetime.date(2013, 1, 1)
end_sp = datetime.date.today() - datetime.timedelta(days=1)

end_of_last_year = datetime.date(2020, 12, 31)

# These are separate for if we would want different range
stocks_start = datetime.date(2013, 1, 1)
stocks_end = datetime.date.today() - datetime.timedelta(days=1)

#* Get SP500 data for complete timeframe
sp500_data = yf.download(tickers='^GSPC', start=start_sp, end=end_sp)
sp500 = pd.DataFrame(sp500_data)
# print(sp500)
sp500_adj_close = sp500[['Adj Close']].reset_index()
sp500_adj_close.astype('datetime64[D]')
# print(sp500_adj_close)

# Get adjusted close for end of year to get YTD performance (make it dt.date for stupid comparison reason)
sp500_adj_close_start = sp500_adj_close[sp500_adj_close['Date'].dt.date == end_of_last_year]

#* Generate dynamic list of tickers to pull from yf api based on imported excel file
tickers = portfolio_df['Ticker'].unique()


#* Get stock data for all tickers
def get(tickers, startdate, enddate):
    def data(ticker):
        return yf.download(ticker, start=startdate, end=enddate)

    datas = map(data, tickers)
    return pd.concat(datas, keys=tickers, names=['Ticker', 'Date'])


all_data = get(tickers, stocks_start, stocks_end)
adj_close = all_data[['Adj Close']].reset_index()
# print(adj_close)

#* Get variable enddate to make sure there is valid date (weekends, closed exchanges,...)
def get_latest_close_date():
    earlierday1 = (stocks_end - datetime.timedelta(days=1))
    earlierday2 = (stocks_end - datetime.timedelta(days=2))
    earlierday3 = (stocks_end - datetime.timedelta(days=3))
    earlierday4 = (stocks_end - datetime.timedelta(days=4))
    if stocks_end == adj_close["Date"].iloc[-1]:
        return stocks_end
    elif earlierday1 == adj_close["Date"].iloc[-1]:
        return earlierday1
    elif earlierday2 == adj_close["Date"].iloc[-1]:
        return earlierday2
    elif earlierday3 == adj_close["Date"].iloc[-1]:
        return earlierday3
    elif earlierday4 == adj_close["Date"].iloc[-1]:
        return earlierday4


end_date = get_latest_close_date()
# print(end_date)

# Get ticker close from the end of last year and the latest close price
adj_close_start = adj_close[adj_close['Date'].dt.date == end_of_last_year]
adj_close_latest = adj_close[adj_close['Date'].dt.date == end_date]
# print(adj_close_latest)

#* Change Unit Cost to non-hardcoded values to account for stock splits
# Do this by merging portfolio df with adj_close df
changed_cost = pd.merge(portfolio_df, adj_close, how='left',
                        left_on=['Ticker', 'Acquisition Date'], right_on=['Ticker', 'Date'])
changed_cost.drop(['Unit Cost', 'Date', 'Cost Basis'], axis=1, inplace=True)
changed_cost = changed_cost.rename(columns={'Adj Close': 'Unit Cost'})
changed_cost['Cost Basis'] = changed_cost['Quantity'] * changed_cost['Unit Cost']
changed_cost = changed_cost[['Acquisition Date', 'Ticker', 'Quantity', 'Unit Cost', 'Cost Basis', 'Start of Year']]

# Reset the index to be the tickers
adj_close_latest.set_index('Ticker', inplace=True)
changed_cost.set_index('Ticker', inplace=True)


volatility_sp500 = sp500_adj_close['Adj Close'].pct_change()
volatility_sp500.dropna(axis=0, inplace=True)


#* Calculate the volatility of the individual tickers
def get_standard_deviation():
    d = []
    for ticker in tickers:
        singled_tickers = (adj_close[adj_close['Ticker'] == ticker])
        volatility = singled_tickers['Adj Close'].pct_change().std() * (252 ** 0.5)
        d.append({'Ticker': ticker, 'Volatility': volatility})
    d = pd.DataFrame(d)
    return d


annualized_volatility = get_standard_deviation()
# print(annualized_volatility)

#* Calculate Sharpe Ratio
#! Sharpe = daily_return.mean/daily_return.std
def calculate_sharpe():
    s = []
    return s


sharpe = calculate_sharpe()

#* Calculate Beta of portfolio
# def calculate_beta():
#     b = []
#     for ticker in tickers:
#         singled_ticker = adj_close[adj_close['Ticker'] == ticker]
#         singled_ticker.reset_index(drop=True, inplace=True)
#         pct_change_ticker = singled_ticker['Adj Close'].pct_change()
#         pct_change_ticker.dropna(axis=0, inplace=True)
#         rows = pct_change_ticker.shape[0]
#         pct_change_sp500 = volatility_sp500.iloc[-rows:]
#         x = pct_change_sp500
#         y = pct_change_ticker
#         slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
#         beta_function = slope
#         b.append({'Ticker': ticker, 'Beta': beta_function})
#     b = pd.DataFrame(b)
#     return b
#
#
# beta = calculate_beta()


#######################################################################################################################
''' Create the master Dataframe '''

#* Merge portfolio with adj close df , join by indexes
# merge(left_df, right_df, index=True means that they share index
merged_portfolio = pd.merge(changed_cost, adj_close_latest, left_index=True, right_index=True)
merged_portfolio['Ticker Return'] = merged_portfolio['Adj Close'] / merged_portfolio['Unit Cost'] - 1
merged_portfolio.reset_index(inplace=True)  # reset index to get tickers back as separate column

#* Merge new df with sp500 adjusted closes to get S&P closing price on each position purchase date
#* to allow to track S&P performance over same timeframe as stock
merged_portfolio_sp = pd.merge(merged_portfolio, sp500_adj_close,
                               left_on='Acquisition Date', right_on='Date')
# Delete additional date column and rename columns to: latest date, ticker adj close, sp initial close
del merged_portfolio_sp['Date_y']
merged_portfolio_sp.rename(columns={'Date_x': 'Latest Date', 'Adj Close_x': 'Ticker Adj Close',
                                    'Adj Close_y': 'SP 500 Initial Close'}, inplace=True)

#* Add the equivalent SP 500 purchase at purchase date of stock
merged_portfolio_sp['Equiv SP Shares'] = merged_portfolio_sp['Cost Basis'] / merged_portfolio_sp['SP 500 Initial Close']
merged_portfolio_sp['Latest Date'] = merged_portfolio_sp['Latest Date'].astype('datetime64[D]')

#* Join Dataframe with SP500 latest close
# left_on and right_on is when the two dataframes have different names for joining column
merged_portfolio_sp_latest = pd.merge(merged_portfolio_sp, sp500_adj_close,
                                      left_on='Latest Date', right_on='Date')
# Delete and rename column
del merged_portfolio_sp_latest['Date']
merged_portfolio_sp_latest.rename(columns={'Adj Close': 'SP 500 Latest Close'}, inplace=True)

#* Calculate SP Return over holding period of each position (Absolute return) and compare with ticker return
merged_portfolio_sp_latest['SP Return'] = merged_portfolio_sp_latest['SP 500 Latest Close'] / \
                                          merged_portfolio_sp_latest['SP 500 Initial Close'] - 1
merged_portfolio_sp_latest['Abs return compare'] = merged_portfolio_sp_latest['Ticker Return'] - \
                                                   merged_portfolio_sp_latest['SP Return']

#* Calculate Ticker Share Value , SP 500 Value, Abs Value compare (over/underperformance)
merged_portfolio_sp_latest['Share Value'] = merged_portfolio_sp_latest['Quantity'] * \
                                            merged_portfolio_sp_latest['Ticker Adj Close']
merged_portfolio_sp_latest['SP 500 Value'] = merged_portfolio_sp_latest['Equiv SP Shares'] * \
                                             merged_portfolio_sp_latest['SP 500 Latest Close']
merged_portfolio_sp_latest['Abs Value Compare'] = merged_portfolio_sp_latest['Share Value'] - \
                                                  merged_portfolio_sp_latest['SP 500 Value']

#* Calculate stock gain/loss and sp5OO gain/loss
merged_portfolio_sp_latest['Stock Gain'] = merged_portfolio_sp_latest['Share Value'] - merged_portfolio_sp_latest[
    'Cost Basis']
merged_portfolio_sp_latest['SP 500 Gain'] = merged_portfolio_sp_latest['SP 500 Value'] - merged_portfolio_sp_latest[
    'Cost Basis']

#* Get YTD performance of each position relative to SP500
# Merge overall dataframe with adj close start of year df to get ytd tracking (automatic outer join)
merged_portfolio_sp_latest_YTD = pd.merge(merged_portfolio_sp_latest, adj_close_start, on='Ticker')
del merged_portfolio_sp_latest_YTD['Date']
merged_portfolio_sp_latest_YTD.rename(columns={'Adj Close': 'Ticker Start Year'}, inplace=True)
# print(merged_portfolio_sp_latest_YTD)

#* Join SP500 start of year with current df to get YTD for SP500
merged_portfolio_sp_latest_YTD_sp = pd.merge(merged_portfolio_sp_latest_YTD, sp500_adj_close_start,
                                             left_on='Start of Year', right_on='Date')
del merged_portfolio_sp_latest_YTD_sp['Date']
merged_portfolio_sp_latest_YTD_sp.rename(columns={'Adj Close': 'SP Start Year'}, inplace=True)

#* YTD Return for SP to run comparisons
merged_portfolio_sp_latest_YTD_sp['Share YTD'] = merged_portfolio_sp_latest_YTD_sp['Ticker Adj Close'] / \
                                                 merged_portfolio_sp_latest_YTD_sp['Ticker Start Year'] - 1
merged_portfolio_sp_latest_YTD_sp['SP 500 YTD'] = merged_portfolio_sp_latest_YTD_sp['SP 500 Latest Close'] / \
                                                  merged_portfolio_sp_latest_YTD_sp['SP Start Year'] - 1
#* Sort Dataframe and calculate cumulative portfolio value
portfolio = merged_portfolio_sp_latest_YTD_sp.sort_values(by='Ticker', ascending=True)
portfolio['Cum Investment'] = portfolio['Cost Basis'].cumsum()
portfolio['Cum Ticker Return'] = portfolio['Share Value'].cumsum()
portfolio['Cum SP Return'] = portfolio['SP 500 Value'].cumsum()
portfolio['Cum Ticker ROI'] = portfolio['Cum Ticker Return'] / portfolio['Cum Investment']
# print(portfolio)

#######################################################################################################################
''' See how the positions are doing in comparison with the highest close: useful for trailing stops'''

#* Factor in that some positions were acquired more recently than others, join adj_close df with portfolio_df
portfolio_df.reset_index(inplace=True)
adj_close_acq_date = pd.merge(adj_close, portfolio_df, on='Ticker')

del adj_close_acq_date['Quantity']
del adj_close_acq_date['Unit Cost']
del adj_close_acq_date['Cost Basis']
del adj_close_acq_date['Start of Year']

adj_close_acq_date.sort_values(by=['Ticker', 'Acquisition Date', 'Date'], ascending=[True, True, True], inplace=True)

#* Get timedelta to look at highest close which occurred after acquisition date
adj_close_acq_date['Date Delta'] = adj_close_acq_date['Date'].subtract(adj_close_acq_date['Acquisition Date'])
adj_close_acq_date['Date Delta'] = adj_close_acq_date[['Date Delta']].apply(pd.to_numeric)  # strings to numeric

adj_close_acq_date_modified = adj_close_acq_date[adj_close_acq_date['Date Delta'] >= 0]

#* Pivot table will index on ticker and acquisition date and find max adj close
adj_close_pivot = adj_close_acq_date_modified.pivot_table(index=['Ticker', 'Acquisition Date'],
                                                          values='Adj Close', aggfunc=np.max)
adj_close_pivot.reset_index(inplace=True)

adj_close_pivot_merged = pd.merge(adj_close_pivot, adj_close, on=['Ticker', 'Adj Close'])
# print(adj_close_pivot_merged)

#* Merge adj close pivot table with adj_close table to grab date of adj close high
final_portfolio = pd.merge(portfolio, adj_close_pivot, on=['Ticker', 'Acquisition Date'])
final_portfolio.rename(columns={'Adj Close': 'Highest Adj Close', 'Date': 'Highest Adj Close Date'}, inplace=True)
final_portfolio['% off High'] = final_portfolio['Ticker Adj Close'] / final_portfolio['Highest Adj Close'] - 1

#* Add the standard deviation to the final_portfolio dataframe
final_portfolio = pd.merge(final_portfolio, annualized_volatility, on='Ticker')
final_portfolio = pd.merge(final_portfolio, beta, on='Ticker')
final_portfolio['Pct of portfolio'] = final_portfolio['Share Value'] / final_portfolio['Cum Ticker Return'].tail(1).values[0]
# print(final_portfolio)

#* If multiple positions for same ticker with different acquisition date
# final_portfolio['Counts'] = final_portfolio.index
# final_portfolio['Ticker #'] = final_portfolio['Ticker'].map(str) + ' ' + final_portfolio['Counts'].map(str)
# print(final_portfolio)

''' Export final portfolio for dashboard purposes'''
selection = ['Ticker', 'Acquisition Date', 'Quantity', 'Unit Cost', 'Cost Basis', 'Pct of portfolio',
                                       'Ticker Adj Close', 'Ticker Return', 'SP Return', 'Share Value', 'Share YTD',
                                       '% off High', 'Volatility', 'Beta']
# table_df = final_portfolio.loc[:, selection]
# table_df.to_csv('Dashboard_columns.csv', index=False)

######################################################################################################################
'''Calculate Portfolio performance and risk measures'''
#* Calculate beta of portfolio
# portfolio_beta = (final_portfolio['Beta'] * final_portfolio['Pct of portfolio']).cumsum().tail(1).values[0]
# # print(portfolio_beta)


#* Calculate the Sharpe Ratio of portfolio


# # Calculate Value At Risk:
#     # Calculate periodic returns of stocks in portfolio
# g = []
# for ticker in tickers:
#     singled_ticker = adj_close[adj_close['Ticker'] == ticker]
#     singled_ticker.reset_index(drop=True, inplace=True)
#     pct_change_ticker = singled_ticker['Adj Close'].pct_change()
#     pct_change_ticker.dropna(axis=0, inplace=True)
#     g.append(pct_change_ticker)
# g = pd.DataFrame(g)
# g = g.transpose()
# print(g)



    # Create covariance matrix based on Returns

    # Calculate portfolio mean and the standard deviation
    # Calculate inverse of normal distribution (PPF) with specified confidence interval, stdev and mean
    # Estimate VAR for portfolio by substracting the initial investment for calculation in step 4



#######################################################################################################################
''' Create Visualizations '''

#* Compare individual positions return to hypothetical investment in S&P YTD
trace1 = go.Bar(
    x=final_portfolio['Ticker'][:10],
    y=final_portfolio['Share YTD'][:10],
    name='Ticker YTD',
)

trace2 = go.Scatter(
    x=final_portfolio['Ticker'][:10],
    y=final_portfolio['SP 500 YTD'][:10],
    name='S&P 500 YTD',
)

data = [trace1, trace2]

layout = go.Layout(title='YTD Return VS S&P 500 YTD',
                   title_x=0.5,
                   barmode='group',
                   yaxis=dict(title='Returns', tickformat='.2%'),
                   xaxis=dict(title='Ticker'),
                   legend=dict(x=.8, y=1),
                   template='simple_white',
                   )
fig1 = go.Figure(data=data, layout=layout)
# fig1.show()


#* Current Share Price Versus Closing High since purchased
trace1 = go.Bar(
    x=final_portfolio['Ticker'][:10],
    y=final_portfolio['% off High'],
    name='% off High'
)

data = [trace1]

layout = go.Layout(title='Adj Close % off High',
                   title_x=0.5,
                   barmode='group',
                   yaxis=dict(title='% Below Adj Close High', tickformat='.2%'),
                   xaxis=dict(title='Ticker'),
                   legend=dict(x=.8, y=1),
                   template='simple_white',
                   )
fig2 = go.Figure(data=data, layout=layout)
# fig2.show()

#* Total Return comparison chart
trace1 = go.Bar(
    x=final_portfolio['Ticker'][:10],
    y=final_portfolio['Ticker Return'][:10],
    name='Ticker Total Return'
)
trace2 = go.Scatter(
    x=final_portfolio['Ticker'][:10],
    y=final_portfolio['SP Return'],
    name='SP 500 Total Return'
)
data = [trace1, trace2]
layout = go.Layout(title='Total Return VS S&P 500',
                   title_x=0.5,
                   barmode='group',
                   yaxis=dict(title='Returns', tickformat='.2%'),
                   xaxis=dict(title='Ticker', tickformat='.2%'),
                   legend=dict(x=.8, y=1),
                   template='simple_white'
                   )
fig3 = go.Figure(data=data, layout=layout)
# fig3.show()

#* Cumulative Return over time chart
trace1 = go.Bar(
    x=final_portfolio['Ticker'][:10],
    y=final_portfolio['Stock Gain'][:10],
    name='Ticker Total Return ($)'
)
trace2 = go.Bar(
    x=final_portfolio['Ticker'][:10],
    y=final_portfolio['SP 500 Gain'][:10],
    name='SP 500 Total Return ($)'
)
trace3 = go.Scatter(
    x=final_portfolio['Ticker'][:10],
    y=final_portfolio['Ticker Return'][:10],
    name='Ticker Total Return (%)',
    yaxis='y2'
)
data = [trace1, trace2, trace3]
layout = go.Layout(title='Stock Gain/Loss VS S&P 500',
                   title_x=0.5,
                   barmode='group',
                   yaxis=dict(title='Gain/(Loss) (€)'),
                   yaxis2=dict(title='Ticker Return', overlaying='y', side='right', tickformat='.2%'),
                   xaxis=dict(title='Ticker'),
                   legend=dict(x=.75, y=1),
                   template='simple_white'
                   )
fig4 = go.Figure(data=data, layout=layout)
# fig4.show()

#* Get cumulative returns chart
trace1 = go.Bar(
    x=final_portfolio['Ticker'],
    y=final_portfolio['Cum Investment'],
    # mode='lines+markers',
    name='Cum investment'
)
trace2 = go.Bar(
    x=final_portfolio['Ticker'],
    y=final_portfolio['Cum SP Return'],
    # mode='lines+markers',
    name='Cum SP500 Returns'
)
trace3 = go.Bar(
    x=final_portfolio['Ticker'],
    y=final_portfolio['Cum Ticker Return'],
    # mode='lines+markers',
    name='Cum Ticker Returns',
)
trace4 = go.Scatter(
    x=final_portfolio['Ticker'],
    y=final_portfolio['Cum Ticker Return'],
    # mode='lines+markers',
    name='Cum ROI Mult',
    yaxis='y2'
)

data = [trace1, trace2, trace3, trace4]

layout = go.Layout(title='Total Cumulative Investments and Returns Over Time',
                   title_x=0.5,
                   barmode='group',
                   yaxis=dict(title='Returns'),
                   xaxis=dict(title='Ticker'),
                   legend=dict(x=.4, y=1),
                   yaxis2=dict(title='Cum ROI Mult', overlaying='y', side='right'),
                   template='simple_white'
                   )
fig5 = go.Figure(data=data, layout=layout)
# fig5.show()

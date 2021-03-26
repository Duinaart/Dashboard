#* http://theautomatic.net/yahoo_fin-documentation/#updates

import yahoo_fin.stock_info as si
df = si.get_stats('TSLA')
df = df.iloc[:9]
df['Attribute'][:2] = df['Attribute'][:2].str[:-2]
df['Attribute'][3:5] = df['Attribute'][3:5].str[:-2]
df['Attribute'][7:] = df['Attribute'][7:].str[:-2]
df.set_index('Attribute', inplace=True)
print(df)

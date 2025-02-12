from sys import argv
import sqlite3
import pandas as pd 
import exchange_calendars as xcals
from openbb import obb 

obb.user.preferences.output_type = 'dataframe'

def get_asset_data(symbol, start_date=None, end_date=None):
    data = obb.equity.price.historical(
        symbol,
        start_date=start_date,
        end_date=end_date,
        provider='yfinance'
    )
    data.reset_index(inplace=True)
    data['symbol'] = symbol
    return data

def save_asset_data(symbol, conn, start_date=None, end_date=None):
    data = get_asset_data(symbol, start_date, end_date)
    data.to_sql(
        'stock_data',
        conn,
        if_exists='replace',
        index=False
    )

def save_last_trading_sess(symbol, conn, today):
    data = get_asset_data(symbol, today, today)
    data.to_sql(
        'stock_data',
        conn,
        if_exists='append',
        index=False
    )

if __name__ == '__main__':
    conn = sqlite3.connect('market_data.sqlite')
    if argv[1] == 'bulk':
        symbol = argv[2]
        end_date = argv[4]
        start_date = argv[3]
        save_asset_data(symbol, conn, start_date=None, end_date=None)
        print(f'{symbol} saved between {start_date} and {end_date}')
    elif argv[1] == 'last':
        symbol = argv[2]
        calendars = argv[3]
        cals = xcals.get_calendar(calendars)
        today = pd.Timestamp.today().date()
        print(today)
        if cals.is_session(today):
            save_last_trading_sess(symbol, conn, today)
            print(f'{symbol} saved ')
        else:
            print(f'{today} is not a trading day. Doing Nothing!!!')
    else:
        print('enter bulk or last')

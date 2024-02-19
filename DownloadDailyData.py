import yfinance as yf
import pandas as pd
from datetime import datetime, date, timedelta
import os


def listEmptyFiles():
    res = []
    directory = r"/Volumes/easystore/ProjectGRT/data/"
    for filename in os.listdir(directory):
        if filename.endswith(".csv") and not os.stat(os.path.join(directory,filename)).st_size:
            res.append(filename.split('_')[0])
    return res
# stock_list = listEmptyFiles()

def download_daily(start_date, today):
    directory = r"/Volumes/easystore/ProjectGRT"

    # latest_date = pd.read_csv(os.path.join(directory,"Current_Status.csv"))
    # today = date.today()
    # start_date = datetime.fromisoformat(latest_date["Latest Date"][0])  + timedelta(days=1)

    # if start_date.date() >= today: return
    nasdaq = pd.read_csv(os.path.join(directory,"nasdaq.csv"))
    nyse = pd.read_csv(os.path.join(directory,"nyse.csv"))

    stock_list = nasdaq["Symbol"].to_list() + [ticker.strip().replace("/","-") for ticker in nyse["Symbol"] if '^' not in ticker]

    index = 0
    for i,ticker in enumerate(stock_list[index:],index):
        try:
            ticker = str(ticker)
            stock = yf.Ticker(ticker)
            data = stock.history(start=start_date.strftime(r"%Y-%m-%d"),end=today.strftime(r"%Y-%m-%d"))
            time = data.index[-1].strftime(r"%Y-%m-%d")
            filename = ticker + "_" + data.index[0].strftime(r"%Y-%m-%d") + "_" + data.index[-1].strftime(r"%Y-%m-%d")+".csv"
            print(i,filename)
            data.to_csv(os.path.join(directory,"data",filename))
        except:
            pass
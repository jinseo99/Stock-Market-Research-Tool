import yfinance as yf
import pandas as pd
from datetime import datetime
import os
# nasdaq = pd.read_csv("nasdaq.csv")
# nyse = pd.read_csv("nyse.csv")

# stock_list = nasdaq["Symbol"].to_list() + [ticker.strip().replace("/","-") for ticker in nyse["Symbol"] if '^' not in ticker]

def listEmptyFiles():
    res = []
    directory = r"/Volumes/easystore/data/"
    for filename in os.listdir(directory):
        if filename.endswith(".csv") and not os.stat(os.path.join(directory,filename)).st_size:
            res.append(filename.split('_')[0])
    return res
stock_list = listEmptyFiles()

directory = r"/Volumes/easystore/data/"
index = 0
for i,ticker in enumerate(stock_list[index:],index):
    try:
        ticker = str(ticker)
        stock = yf.Ticker(ticker)
        data = stock.history(start="2019-02-08",end="2024-02-08")
        time = data.index[-1].strftime(r"%Y-%m-%d")
        filename = ticker + "_" + data.index[0].strftime(r"%Y-%m-%d") + "_" + data.index[-1].strftime(r"%Y-%m-%d")+".csv"
        path = directory+filename
        print(i,path)
        data.to_csv(path)
    except:
        pass


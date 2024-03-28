import yfinance as yf
import pandas as pd
from datetime import datetime, date, timedelta
import os
import calendar
from collections import defaultdict
import csv 

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
    stock_map = loadTickerData()
    # latest_date = pd.read_csv(os.path.join(directory,"Current_Status.csv"))
    # today = date.today()
    # start_date = datetime.fromisoformat(latest_date["Latest Date"][0])  + timedelta(days=1)

    # if start_date.date() >= today: return
    # nasdaq = pd.read_csv(os.path.join(directory,"nasdaq.csv"))
    # nyse = pd.read_csv(os.path.join(directory,"nyse.csv"))

    # stock_list = nasdaq["Symbol"].to_list() + [ticker.strip().replace("/","-") for ticker in nyse["Symbol"] if '^' not in ticker]

    for i,ticker in enumerate(stock_map):
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(start=start_date.strftime(r"%Y-%m-%d"),end=today.strftime(r"%Y-%m-%d"))
            # time = data.index[-1].strftime(r"%Y-%m-%d")
            filename = ticker + "_" + data.index[0].strftime(r"%Y-%m-%d") + "_" + data.index[-1].strftime(r"%Y-%m-%d")+".csv"
            print(i,filename)
            data.to_csv(os.path.join(directory,"data",filename))
        except:
            pass

def download_daily_single(ticker, year, month):
    directory = r"/Volumes/easystore/ProjectGRT"
    _, last_day = calendar.monthrange(year, month)
    last_day_date = date(year,month,last_day)+timedelta(days=1)
    stock = yf.Ticker(ticker)
    data = stock.history(start=f"{year}-{month:02}-01", end=last_day_date.strftime(r"%Y-%m-%d"))
    filename = f"{ticker}_{year}-{month:02}_Daily.csv"
    data.to_csv(os.path.join(directory,"StockData","Daily",filename))

def loadTickerData():
    directory = r"/Volumes/easystore/ProjectGRT"

    stock_map = defaultdict(str)
    with open(os.path.join(directory,"nasdaq.csv")) as csv_file: 
        reader = csv.reader(csv_file) 
        
        for row in reader: 
            ticker, name = row[0], row[1] 
            if "Warrant" not in name:
                stock_map[ticker] = name

    with open(os.path.join(directory,"nyse.csv")) as csv_file: 
        reader = csv.reader(csv_file) 
        
        for row in reader: 
            ticker, name = row[0], row[1]
            ticker.strip().replace("/","-")
            if '^' not in ticker:
                stock_map[ticker] = name
    return stock_map

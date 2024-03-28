import pandas as pd
from collections import defaultdict
from datetime import datetime, timedelta, date
import os
import json
def calculateFromScratch():
    f = open('project_variables.json')
    data = json.load(f)
    store_path =data["project-path"]

    stock_ranking = defaultdict(list)
    stock_count = defaultdict(int)
    directory = store_path + "screener/"

    file_count = 1
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            print(file_count, filename)
            df = pd.read_csv(directory+filename)
            for index, row in df.iterrows():
                rank = index+1
                if stock_ranking[row["Ticker"]]: stock_ranking[row["Ticker"]][0] += rank  
                else: stock_ranking[row["Ticker"]].append(rank)
                stock_count[row["Ticker"]] += 1
            file_count+=1

    for ticker in stock_ranking:
        stock_ranking[ticker].append(stock_ranking[ticker][0] / stock_count[ticker])
        stock_ranking[ticker].append(stock_count[ticker])
            
    df = pd.DataFrame.from_dict(stock_ranking, orient="index",columns=["Total Rank","Avg Rank","Total Count"])
    df.index.name = "Ticker"
    df = df.sort_values(by=['Avg Rank'])
    print(df)
    df.to_csv(f"{store_path}AverageVolumeRanking.csv")

def calculateFromPrev(start_date, today):
    f = open('project_variables.json')
    data = json.load(f)
    store_path =data["project-path"]

    directory = store_path
    # latest_date = pd.read_csv(os.path.join(directory,"Current_Status.csv"))
    # today = date.today()
    # start_date = datetime.fromisoformat(latest_date["Latest Date"][0])  + timedelta(days=1)
    # if start_date.date() >= today: return
    average_ranking = pd.read_csv(os.path.join(directory,"AverageVolumeRanking.csv"),index_col=0)
    daterange = pd.date_range(start_date, today)
    for cur_date in daterange:
        filename = "Most-Volume_" + cur_date.strftime(r"%Y-%m-%d") +".csv"
        path = os.path.join(directory,"screener",filename)
        if os.path.exists(path):
            print(path)
            df = pd.read_csv(path)
            for index, row in df.iterrows():
                rank = index+1
                average_ranking.loc[average_ranking["Ticker"] == row["Ticker"], "Total Rank"] += rank  
                average_ranking.loc[average_ranking["Ticker"] == row["Ticker"], "Total Count"] += 1
    average_ranking.to_csv(os.path.join(directory,"AverageVolumeRanking.csv"))
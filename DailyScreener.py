import pandas as pd
import os
from datetime import datetime, date, timedelta
import csv

# df = pd.read_csv('data.csv')
def create_screener(start_date, today):
    directory = r"/Volumes/easystore/ProjectGRT"

    # latest_date = pd.read_csv(os.path.join(directory,"Current_Status.csv"))
    # today = date.today()
    # start_date = datetime.fromisoformat(latest_date["Latest Date"][0])  + timedelta(days=1)

    # if start_date.date() >= today: return
    path_set = set()
    date_list = pd.date_range(start=start_date.strftime(r"%Y-%m-%d"),end=today.strftime(r"%Y-%m-%d"))
    for i, cur_date in enumerate(date_list):
        # df = pd.DataFrame(columns=["Ticker","Change","Volume"])
        print(i, cur_date.date())
        result_list = []
        for filename in os.listdir(os.path.join(directory,"data")):
            if filename.endswith(".csv"):
                path = os.path.join(directory, "data", filename)
                path_set.add(path)
                stock = pd.read_csv(path)
                stock['Date'] = pd.to_datetime(stock['Date'])
                row = stock.loc[stock["Date"]==cur_date]
                if not row.empty and not row.isnull().values.any():
                    row = row.iloc[0]
                    change = 100*(row["Close"]-row["Open"])/row["Open"]
                    result_list.append([filename.split("_")[0],change,int(row["Volume"])])
                # os.replace(path, os.path.join(directory,"data","Archive",filename))
        if not result_list: continue
        result_list.sort(key=lambda x: x[2], reverse=True)
        csv_name = "Most-Volume_"+ cur_date.strftime(r"%Y-%m-%d")+".csv"
        with open(os.path.join(directory,"screener",csv_name), 'w') as f: 
            write = csv.writer(f)
            write.writerow(["Ticker","% Change", "Volume"])
            write.writerows(result_list)
    for visited_path in path_set:
        os.replace(visited_path, os.path.join(directory,"data","Archive",filename))

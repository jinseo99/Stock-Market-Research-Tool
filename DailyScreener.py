import pandas as pd
import os
from datetime import datetime
import csv

# df = pd.read_csv('data.csv')

directory = r"/Volumes/easystore/data/"
save_directory = r"/Volumes/easystore/screener/"
date_list = pd.date_range(start="2019-02-08", end='2024-02-07')
for i, date in enumerate(date_list):
    # df = pd.DataFrame(columns=["Ticker","Change","Volume"])
    print(i, date.date())
    result_list = []
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            path = os.path.join(directory, filename)
            stock = pd.read_csv(path)
            stock['Date'] = pd.to_datetime(stock['Date'])
            row = stock.loc[stock["Date"]==date]
            if not row.empty and not row.isnull().values.any():
                row = row.iloc[0]
                change = 100*(row["Close"]-row["Open"])/row["Open"]
                result_list.append([filename.split("_")[0],change,int(row["Volume"])])
    if not result_list: continue
    result_list.sort(key=lambda x: x[2], reverse=True)
    csv_name = "Most-Volume_"+ date.strftime(r"%Y-%m-%d")+".csv"
    csv_path = save_directory+csv_name
    with open(csv_path, 'w') as f: 
        write = csv.writer(f)
        write.writerow(["Ticker","% Change", "Volume"])
        write.writerows(result_list)
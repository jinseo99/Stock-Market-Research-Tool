import pandas as pd
from collections import defaultdict
import os

stock_ranking = defaultdict(int)
stock_count = defaultdict(int)
directory = r"/Volumes/easystore/screener/"

file_count = 1
for filename in os.listdir(directory):
    if filename.endswith(".csv"):
        print(file_count, filename)
        df = pd.read_csv(directory+filename)
        for index, row in df.iterrows():
            rank = index+1
            stock_ranking[row["Ticker"]] += rank
            stock_count[row["Ticker"]] += 1
        file_count+=1

for ticker in stock_ranking:
    stock_ranking[ticker] /= stock_count[ticker]
        
df = pd.DataFrame.from_dict(stock_ranking, orient="index",columns=["Average Rank"])
df.index.name = "Ticker"
df = df.sort_values(by=['Average Rank'])
print(df)
df.to_csv(r"/Volumes/easystore/AverageVolumeRanking.csv")

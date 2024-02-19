import csv
import pandas as pd
import requests
from datetime import datetime, date
import plotly.graph_objects as go
from pathlib import Path
import time
import sys

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
# JNE5BTFVV3SIZI0L
def download(ticker, selected_date):
    # ticker = sys.argv[1].upper()
    # selected_date = sys.argv[2]
    print(ticker, selected_date)

    CSV_URL = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={}&interval=1min&month={}&datatype=csv&outputsize=full&apikey=JNE5BTFVV3SIZI0L'.format(ticker, selected_date)
    print(CSV_URL)
    success = True
    for i in range(3): 
        if i == 2:
            success = False
            break
        req = requests.get(CSV_URL)
        try:
            req.raise_for_status()
            print("Request successful!")
            break
        except requests.exceptions.RequestException as e:
            print("An error occurred:", e)
            time.sleep(60)
        
    url_content = req.content

    path = r'/Volumes/easystore/ProjectGRT/StockData/'+ ticker + '_' + selected_date+ '.csv'
    print(path)
    file_path = Path(path)
    csv_file = open(file_path, 'wb')
    csv_file.write(url_content)
    csv_file.close()
    return success

import csv
import pandas as pd
import requests
from datetime import datetime, date
import plotly.graph_objects as go
from pathlib import Path
import time
import sys
import json

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
def download(ticker, selected_date):

    f = open('project_variables.json')
    data = json.load(f)
    api, store_path = data["api-key"], data["stock-data-path"]
    # ticker = sys.argv[1].upper()
    # selected_date = sys.argv[2]
    print(ticker, selected_date)

    CSV_URL = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={}&interval=1min&month={}&datatype=csv&outputsize=full&apikey={}'.format(ticker, selected_date, api)
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

    path = store_path + ticker + '_' + selected_date+ '.csv'
    print(path)
    file_path = Path(path)
    csv_file = open(file_path, 'wb')
    csv_file.write(url_content)
    csv_file.close()
    return success

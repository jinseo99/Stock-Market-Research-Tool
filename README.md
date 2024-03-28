# About the Project

Stock Market Research Tool for analyzing stock prices using historic data with indicators such as Volume, RSI and MACD. 
Leveraged Alphavantage for downloading historic stock data for 1-min chart and leveraged yfinance for downloading daily stock data.

# How to Run

project_variables.json file in root directory with the following format:
```
{
    "stock-data-path":"/[root]/StockData/",
    "project-path":"/[root]/",
    "api-key":"[alphavantage api key]"
}
```
clone the respository and run the MainDash.py

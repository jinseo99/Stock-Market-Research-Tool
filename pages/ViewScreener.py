import dash
from dash import Dash, dash_table, html, dcc, callback, ctx
from dash.dependencies import Output, Input, State
import pandas as pd
from datetime import date, timedelta, datetime
from os import listdir
from bisect import bisect_left
from GoogleNews import GoogleNews
import time
from DownloadDailyData import download_daily
from DailyScreener import create_screener
from AverageRanking import calculateFromPrev
import os 
import json

dash.register_page(__name__)
f = open('project_variables.json')
data = json.load(f)
store_path =data["project-path"]

cur_date = None
CSV_DIR = "{store_path}/screener/"
def loadScreenerData():
    csv_files = listdir(CSV_DIR)
    csv_list = []
    for csv_file in csv_files:
        if csv_file.endswith(".csv"):
            items = csv_file.split('_')
            selected_date = items[1]
            year, month, day = int(selected_date[:4]), int(selected_date[5:7]), int(selected_date[8:10])
            csv_list.append((year,month,day))
    return csv_list

screener_list = loadScreenerData()
screener_list.sort()
average_ranking = pd.read_csv("{store_path}AverageVolumeRanking.csv", usecols=["Ticker","Avg Rank"])
average_ranking["Avg Rank"] = average_ranking["Avg Rank"].round(2)

layout = html.Div([
    html.Div([
        html.Div(
            dcc.DatePickerSingle(
                id='my-date-picker-single',
                min_date_allowed=date(screener_list[0][0], screener_list[0][1], screener_list[0][2]),
                max_date_allowed=date(screener_list[-1][0], screener_list[-1][1], screener_list[-1][2]),
                initial_visible_month=date(screener_list[-1][0], screener_list[-1][1], screener_list[-1][2]),
                # date=date(screener_list[-1][0], screener_list[-1][1], screener_list[-1][2]),
                # style={}
        ), style = {"padding-right":"10px"}),
        html.Div(html.Button('<', id='prev-button', style={"height":"2em"}),style={"padding-top":"10px"}),
        html.Div(html.Button('>', id='next-button', style={"height":"2em"}),style={"padding-top":"10px"}),
        html.Div(html.Button("Refresh Data", id ="refresh-data-button", style={"font-size":"1.1em"}), style={"margin":"10px"}),
        html.Div(dcc.Loading(id="refresh-loading",children=html.Div(id="refresh-loading-output"),), style={"padding-top":"15px"})
        ], style={"display":"flex","margin-top":"10px","margin-left":"5%"}
    ),
    html.Div(
        id='output-container-date-picker-single',
        style={"margin-top":"10px","margin-left":"5%"}    
    ),
    html.Div([
        html.Div(dash_table.DataTable(
            id="screener-datatable",   
            # data=df.to_dict('records'), 
            # columns =[{"name": i, "id": i} for i in df.columns],
            style_table={ "font-size":"1.2em"},
            sort_action='native',
            page_current=0,
            page_size=25,
            filter_action='native',
            filter_options = {"case":"insensitive"},
            style_cell_conditional=[
                {'if': {'column_id': 'Volume'},
                'width': '30%'},
            ]
        ),style={"width":"40%","margin":r"2% 5%"}),
        html.Div([
            html.A(id="news-link"),
        ]),

    ], style = {"display":"flex"}),

    dcc.Store(id='cached-data',storage_type="session"),

])

@callback(
    Output("refresh-loading-output","children"),
    Output("my-date-picker-single", "max_date_allowed"),
    Input("refresh-data-button","n_clicks")
)
def refreshData(button):
    global average_ranking, screener_list
    if button:
        directory = r"/Volumes/easystore/ProjectGRT"
        path = os.path.join(directory,"Current_Status.csv")
        latest_date = pd.read_csv(path)
        today = date.today()
        start_date = datetime.fromisoformat(latest_date["Latest Date"][0])  + timedelta(days=1)
        if start_date.date() > today: return "Latest Data already Retrieved", date(screener_list[-1][0], screener_list[-1][1], screener_list[-1][2])
        download_daily(start_date, today+timedelta(days=1))
        create_screener(start_date, today)
        calculateFromPrev(start_date, today)
        latest_date.loc[0,"Latest Date"] = today.strftime(r"%Y-%m-%d")
        latest_date.to_csv(path, index=False)
        average_ranking = pd.read_csv(r"/Volumes/easystore/ProjectGRT/AverageVolumeRanking.csv", usecols=["Ticker","Avg Rank"])
        average_ranking["Avg Rank"] = average_ranking["Avg Rank"].round(2)
        screener_list = loadScreenerData()
        screener_list.sort()
        return "Latest Data Updated", date(screener_list[-1][0], screener_list[-1][1], screener_list[-1][2])
    return "", date(screener_list[-1][0], screener_list[-1][1], screener_list[-1][2])

@callback(
    Output('output-container-date-picker-single', 'children'),
    Output('screener-datatable', 'data'),
    Output('screener-datatable', 'columns'),
    Output("screener-datatable", "selected_cells"),
    Output("screener-datatable", "active_cell"),
    Output("cached-data","data"),
    Output('my-date-picker-single', 'date'),

    # Output("my-date-picker-single","initial_visible_month"),
    Input("cached-data","data"),
    Input('my-date-picker-single', 'date'),

)
def populateTable(cached_data, picker_date):
    # print("DEBUG CACHED",cached_data)
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    # print("DEBUG",cached_data, picker_date, ctx.triggered)
    selected_date = None
    if not cached_data and not picker_date or not input_id:
        selected_date = date.fromisoformat(cached_data["date"]) if cached_data else date(screener_list[-1][0], screener_list[-1][1], screener_list[-1][2])
    else:
        selected_date = date.fromisoformat(cached_data["date"]) if input_id == "cached-data" else date.fromisoformat(picker_date)
    
    year,month,day = selected_date.year,selected_date.month,selected_date.day
    index = bisect_left(screener_list, (year,month,day))
    if index == len(screener_list): year,month,day = screener_list[-1]
    elif screener_list[index] != (year,month,day): year,month,day = screener_list[index]

    path = CSV_DIR+"Most-Volume_{}-{:02d}-{:02d}.csv".format(year,month,day)
    df = pd.read_csv(path)
    df.insert(loc=0, column='Rank', value=range(1,len(df)+1))
    df["% Change"] = df["% Change"].round(2)
    df = df.merge(average_ranking, how="outer", left_on=["Ticker"], right_on=["Ticker"])
    df["id"] = df["Rank"]
    return f"Showing {year}-{month:02}-{day:02}",df.to_dict('records'), [{"name": i, "id": i} for i in df.columns if i != "id"],[], None, {"date":selected_date}, date(year,month,day)


@callback(
    Output("cached-data","data", allow_duplicate=True),
    Input("prev-button","n_clicks"),
    Input("next-button","n_clicks"),
    State("cached-data","data"),
    prevent_initial_call = True
)
def addOrSubtractDay(prev_button, next_button, cached_data):
    selected_date = date.fromisoformat(cached_data["date"]) if cached_data else date(screener_list[-1][0], screener_list[-1][1], screener_list[-1][2])
    if "prev-button" == ctx.triggered_id:
        selected_date -= timedelta(days=1)
        year,month,day = selected_date.year,selected_date.month,selected_date.day
        index = bisect_left(screener_list, (year,month,day))
        if not index: year,month,day = screener_list[0]
        elif screener_list[index] != (year,month,day): year,month,day = screener_list[index-1]
    else:
        selected_date += timedelta(days=1)
        year,month,day = selected_date.year,selected_date.month,selected_date.day
        index = bisect_left(screener_list, (year,month,day))
        if index == len(screener_list): year,month,day = screener_list[-1]
        elif screener_list[index] != (year,month,day): year,month,day = screener_list[index]
    # print("DEBUG ADDORSUB",year,month,day)
    cur_date = date(year,month,day)
    return {"date":cur_date}

@callback(
    Output("news-link","href"),
    Output("news-link","children"),
    # Output("news-page","src"),
    Input("screener-datatable","active_cell"),
    # State('screener-datatable', 'derived_virtual_row_ids'),
    # State('screener-datatable', 'selected_row_ids'),
    State('my-date-picker-single', 'date'),
    State("screener-datatable","data")
)
def cellSelected(cell, selected_date, data):
    # print(cell)

    if cell and cell["column_id"] == "Ticker":
        selected_date = date.fromisoformat(selected_date).strftime(r"%m/%d/%Y")
        ticker = data[cell["row_id"]-1][cell["column_id"]]
        url = f"https://www.google.com/search?q={ticker}&lr=lang_en&biw=1920&bih=976&source=lnt&&tbs=lr:lang_1en,cdr:1,cd_min:{selected_date},cd_max:{selected_date},sbd:1&tbm=nws"
        # src=r"/Users/jinlee/Desktop/Codes/Python Codes/stock_data_scraper/Chromium.app"
        return url, f"{ticker} {selected_date}"
    return "", ""
import csv
import time
import pandas as pd
from datetime import datetime, date
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from pathlib import Path
import sys
import dash
from dash import Dash, html, dcc, dash_table, ctx, no_update, callback, clientside_callback
from dash.dependencies import Output, Input, State
from os import listdir
import os
from collections import defaultdict
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import dash_daq as daq
from HistoricalStockData_Single import download
from numerize import numerize
from DownloadDailyData import download_daily_single, loadTickerData
from Indicators import createRSI, createMACD

dash.register_page(__name__)

def loadStockData():
    CSV_DIR = r"/Volumes/easystore/ProjectGRT/StockData/"
    csv_files = listdir(CSV_DIR)
    csv_map = defaultdict(lambda: defaultdict(list))
    for csv_file in csv_files:
        if csv_file.endswith(".csv"):
            items = csv_file.split('_')
            ticker, selected_date = items[0], items[1]
            year, month = int(selected_date[:4]), int(selected_date[5:7])
            csv_map[ticker][year].append(month)
    return csv_map

csv_map = loadStockData()
stock_map = loadTickerData()
# print(csv_map)
# ticker = sys.argv[1].upper()
# selected_date = sys.argv[2]
# print(ticker, selected_date)

# ticker, selected_date = 'AAPL', "2023-02"
# CSV_PATH = "/Users/jinlee/Desktop/Codes/Python Codes/stock_data_scraper/StockData/{}_{}.csv".format(ticker,selected_date)

# df['timestamp']= pd.to_datetime(df['timestamp'])

HOLIDAYS_2020 = ["2020-01-01","2020-01-20","2020-02-17","2020-04-10","2020-05-25","2020-07-03","2020-09-07","2020-11-26","2020-12-25"] 
HOLIDAYS_2021 = ["2021-01-01","2021-01-18","2021-02-15","2021-04-02","2021-05-31","2021-07-05","2021-09-06","2021-11-25","2021-12-24"]
HOLIDAYS_2022 = ["2022-01-17","2022-02-21","2022-04-15","2022-05-30","2022-07-04","2022-09-05","2022-11-24","2022-12-26"]
HOLIDAYS_2023 = ["2023-01-02","2023-01-16","2023-02-20","2023-04-07","2023-05-29","2023-06-19","2023-07-04","2023-09-04","2023-09-23","2023-12-25"]
HOLIDAYS_2024 = ["2024-01-01","2024-01-15","2024-02-19","2024-03-29","2024-05-29","2024-06-19","2024-07-04","2024-09-02","2024-11-28","2024-12-25"]
ALL_HOLIDAYS = HOLIDAYS_2020+HOLIDAYS_2021+HOLIDAYS_2022+HOLIDAYS_2023+HOLIDAYS_2024
df = fig = None

def createFig(CSV_PATH,ticker):
    global df
    df = pd.read_csv(CSV_PATH)
    df = df[::-1]
    df.columns.values[0] = "timestamp"
    df["timestamp"] = pd.to_datetime(df["timestamp"])


    df.insert(0,'time','')
    df["time"] = df['timestamp'].dt.strftime(r'%m-%d %-I:%M %p')

    df["id"] = df["timestamp"].copy()
    df.set_index('id', inplace=True, drop=False)

    # fig = px.line(df, x = "timestamp", y = 'close', custom_data=["open","high","low","volume"], title=ticker, render_mode="svg",height=800)
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[.55,.15,.15,.15], subplot_titles=[f"{ticker} <a href='https://www.google.com/search?q={stock_map[ticker]}'>({stock_map[ticker]}) </a>",""])
    fig.append_trace(go.Scatter(x=df['timestamp'], y=df['close']), row=1,col=1)
    # fig.append_trace(go.Candlestick(x=df['timestamp'], open=df["open"], high=df["high"],low=df["low"],close=df['close']), row=1,col=1)

    fig.append_trace(go.Scatter(x=df['timestamp'], y=df['volume'], line={"color":"orange"}), row=2,col=1)
    
    df_rsi = createRSI(df)
    df_macd_macd, df_macd_signal = createMACD(df)
    df["macd"] = df_macd_macd

    # print("DEBUG", df_rsi.loc[0])
    fig.append_trace(go.Scatter(x=df['timestamp'], y=df_rsi, line={"color":"purple"}), row=3,col=1)
    fig.add_hline(y=80, line_dash="dot", row=3, col=1, line={"color":"green"}, annotation_text="80", annotation_position="right", annotation_font={"color":"green"})
    fig.add_hline(y=20, line_dash="dot", row=3, col=1, line={"color":"red"}, annotation_text="20", annotation_position="right", annotation_font={"color":"red"})

    fig.append_trace(go.Scatter(x=df['timestamp'], y=df_macd_macd, line={"color":"purple"}), row=4,col=1)
    fig.append_trace(go.Scatter(x=df['timestamp'], y=df_macd_signal, line={"color":"orange"}), row=4,col=1)


    fig.update_xaxes(
        showspikes=True,
        rangeslider_visible=False,
        rangebreaks=[
            # dict(bounds=[6, 1], pattern='day of week'),
            dict(values=[]),
            dict(bounds=["sat", "mon"]),
            dict(bounds=[20, 4], pattern="hour")
        ],
    )
    fig.update_yaxes(showspikes=True, fixedrange=True,side="right")
    fig.update_layout(
        showlegend=False,
        hovermode="x",
        height=800
    )
    # fig.update_traces(hoverinfo="none", hovertemplate=None)
    fig.update_traces(hoverinfo="none")

    return fig
# fig = createFig(CSV_PATH,ticker)

# fig.show(config=config)
# app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

layout = html.Div([
    html.Div([
        html.Div([
            dcc.Graph(
                id='fig',
                config={'scrollZoom': True},
                # figure=fig,
                clear_on_unhover=True
            ),
            html.Div([
                html.Div(dcc.Dropdown(
                    id="ticker-dynamic-dropdown",
                    options=sorted([k for k in csv_map]),
                    # value="AAPL"
                ), 
                style = {"width":"200px"}), 
                html.Div(dcc.Dropdown(id="year-dynamic-dropdown", ),style = {"width":"100px"}),
                html.Div(dcc.Dropdown(id="month-dynamic-dropdown"), style = {"width":"100px"}),
                html.Div(daq.BooleanSwitch(id="extended-hours-switch",label="Extended Hours", on=True), style = {"margin-left":"10px"}),
                html.Div(daq.BooleanSwitch(id="remove-holidays-switch",label="Remove Holidays", on=False), style = {"margin-left":"10px"}),
                html.Div(html.Button("Reload Data", id="reload-button"), style = {"margin-left":"10px"}, )
            ],style={"display":"flex", "margin-left":"5%"}),
            html.Div([
                html.Div(dcc.Input(id="ticker-input", type="text", placeholder="ticker", debounce=True,), style = {}),
                html.Div(dcc.Input(id="date-input", type="text", placeholder="yyyy-MM", debounce=True), style = {}),
                html.Div(html.Button('Download', id='download-button'), style = {}),
                html.Div(dcc.Loading(id="output-loading"),style = {"margin-left":"10px"})
            ],style={"display":"flex","margin-left":"5%", "margin-top":"1%"}),
        ], style={"width":"80%"}),
        html.Div([
            dash_table.DataTable(
                id="fig-table",
                page_size= 25,
                filter_action='native',
                filter_options = {"case":"insensitive"},
            ),
            html.Div(html.A(id="news-link-visualize",), style={"margin-top":"10px"}),
        ], style={"width":"17%"}),
        # html.Div(id="table-test-output")
    ], style= {"display":"flex"}),
    dcc.Tooltip(id="graph-tooltip"),
    dcc.Store(id='cached-visual-data',storage_type="session"),
])

@callback(
    Output("news-link-visualize","href"),
    Output("news-link-visualize","children"),
    Input("fig-table","active_cell"),
    State("fig-table","data"),
    State("ticker-dynamic-dropdown", "value"),
    State("year-dynamic-dropdown","value"),
)
def cellSelected(cell, data, ticker, year):
    if cell and cell["column_id"] == "Date":
        selected = data[cell["row"]][cell["column_id"]].split('-')
        month, day = int(selected[0]), int(selected[1])
        selected_date = date(year,month,day).strftime(r"%m/%d/%Y")
        url = f"https://www.google.com/search?q={ticker}&lr=lang_en&biw=1920&bih=976&source=lnt&&tbs=lr:lang_1en,cdr:1,cd_min:{selected_date},cd_max:{selected_date},sbd:1&tbm=nws"
        return url, f"{ticker} {selected_date}"
    return "", ""

@callback(
    Output("output-loading", "children",allow_duplicate=True),
    Output("ticker-dynamic-dropdown","options",allow_duplicate=True),
    Output("year-dynamic-dropdown","options", allow_duplicate=True),
    Output("month-dynamic-dropdown","options", allow_duplicate=True),
    Input("reload-button","n_clicks"),
    State("ticker-dynamic-dropdown","value"),
    State("year-dynamic-dropdown","value"),
    prevent_initial_call = True
)
def readloadClicked(button,ticker,year):
    # print("DEBUG",button,ticker,year)
    global csv_map
    if button:
        csv_map = loadStockData()
    return ("Reloaded Data",
            sorted([k for k in csv_map]), 
            sorted([k for k in csv_map[ticker]]) if ticker else [], 
            sorted([k for k in csv_map[ticker][year]]) if year else [])


@callback(
    Output("output-loading", "children"),
    Input("download-button","n_clicks"),
    State("ticker-input","value"),
    State("date-input","value"),
)
def downloadClicked(button,ticker,date):
    if button:
        if ticker and date:
            ticker= ticker.upper()
            msg = "Failed to Download {} {}!".format(ticker,date)
            sdate = date.split("-")
            download_daily_single(ticker,int(sdate[0]), int(sdate[1]))
            if download(ticker,date): msg = "Successfully Downloaded {} {}.".format(ticker,date)
            return msg
        else:
            return "Specify ticker and date!"
    return ""

@callback(
    Output("fig", "figure", allow_duplicate=True),
    Input('remove-holidays-switch', 'on'),
    State("fig","figure"),
    prevent_initial_call=True
)
def updateHoliday(on,fig):
    # print("DEBUG Holiday")
    # print(fig["layout"].keys())

    if on: 
        for key in fig["layout"]:
            if "xaxis" in key:
                fig["layout"][key]["rangebreaks"][0]["values"] = ALL_HOLIDAYS
    else: 
        for key in fig["layout"]:
            if "xaxis" in key:
                fig["layout"][key]["rangebreaks"][0]["values"] = []
    return fig


@callback(
    Output("fig", 'figure',allow_duplicate=True),
    Input('extended-hours-switch', 'on'),
    State("fig","figure"),
    prevent_initial_call=True
)
def updateExtended(on,fig):
    # print("DEBUG Extended")
    if on: 
        for key in fig["layout"]:
            if "xaxis" in key:
                fig["layout"][key]["rangebreaks"][-1]["bounds"] = [20,4]
    else: 
        for key in fig["layout"]:
            if "xaxis" in key:
                fig["layout"][key]["rangebreaks"][-1]["bounds"] = [16,9.5]
    return fig

@callback(
    Output("fig", "figure"),
    Output("cached-visual-data","data"),
    Output("ticker-dynamic-dropdown","value"),
    Output("year-dynamic-dropdown","value"),
    Output("month-dynamic-dropdown","value"),

    Output("year-dynamic-dropdown","options"),
    Output("month-dynamic-dropdown","options"),

    Output('fig-table', 'data'),
    Output('fig-table', 'columns'),

    Input("cached-visual-data","data"),
    Input("ticker-dynamic-dropdown","value"),
    Input("year-dynamic-dropdown","value"),
    Input("month-dynamic-dropdown","value"),
    State("year-dynamic-dropdown","options"),
    State("month-dynamic-dropdown","options"),

    State('remove-holidays-switch', 'on'),
    State('extended-hours-switch', 'on'),

    # prevent_initial_call=True,
)
def populateFigure(data, ticker, year, month,year_options, month_options, holiday_on, extended_on):
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    # print("DEBUG POPULATE",data, ticker, year,month, ctx.triggered[0])
    if not data and not (ticker or year or month) or not input_id:
        ticker, year, month = (data["ticker"], data["year"], data["month"]) if data else ("AAPL", 2023, 2)
        year_options = sorted([k for k in csv_map[ticker]])
        month_options = sorted([k for k in csv_map[ticker][year]]) 

    else:
        if input_id == "cached-visual-data":
            ticker, year, month = data["ticker"], data["year"], data["month"]

        if input_id == "ticker-dynamic-dropdown":
            year_options = sorted([k for k in csv_map[ticker]])
            year = year_options[0]
        if input_id == "year-dynamic-dropdown" or input_id == "ticker-dynamic-dropdown":
            month_options = sorted([k for k in csv_map[ticker][year]]) 
            month = month_options[0]

    CSV_PATH = "/Volumes/easystore/ProjectGRT/StockData/{}_{:d}-{:02d}.csv".format(ticker,year,month)
    fig = createFig(CSV_PATH,ticker)
    fig = updateHoliday(holiday_on, fig)
    fig = updateExtended(extended_on, fig)
    Daily_Directory = "/Volumes/easystore/ProjectGRT/StockData/Daily"
    Daily_file_name = f"{ticker}_{year}-{month:02}_Daily.csv"
    Daily_Path = os.path.join(Daily_Directory,Daily_file_name)
    if not os.path.isfile(Daily_Path): download_daily_single(ticker, year, month)
    daily_df = pd.read_csv(Daily_Path)
    daily_df.insert(1,'% Change','')
    daily_df["% Change"] = daily_df.apply(lambda x: (100*(x["Close"]-x["Open"])/x["Open"]), axis=1)
    daily_df["Date"] = pd.to_datetime(daily_df["Date"])
    daily_df['Date'] = daily_df['Date'].dt.strftime(r'%m-%d')
    daily_df = daily_df.round(2)
    return fig, {"ticker":ticker, "year":year, "month":month}, ticker, year, month, year_options, month_options, daily_df.to_dict('records'), [{"name": i, "id": i} for i in daily_df.columns if i in ["Date", "Open","Close","% Change","Volume"]]


@callback(
    Output("graph-tooltip", "show"),
    Output("graph-tooltip", "bbox"),
    Output("graph-tooltip", "children"),
    Input("fig", "hoverData"),
    State("fig","figure")
)
def calculatePercentChange(data,fig):
    # print(data)
    if not data: return False, no_update, no_update


    pt = data["points"][0]
    # print(pt)
    x, y = pt["bbox"]["x0"]-160, pt["bbox"]["y0"]-180
    selected_date = datetime.strptime(pt["x"], r"%Y-%m-%d %H:%M")

    mask = (df['timestamp'] >= (fig["layout"]["xaxis"]["range"][0] if fig["layout"]["xaxis"]["range"] else "00:00:00"))
    df_range = df.loc[mask]
    dff = df_range[df_range.timestamp == selected_date]
    # print(dff)
    initial_price = float(df_range[df_range.timestamp == df_range.timestamp.min()]["close"])
    final_price = float(dff["close"])
    change = 100*((final_price-initial_price)/initial_price)

    # print(x, selected_date, pt["bbox"])
    bbox = {"x0":0,"x1":100,"y0":0,"y1":450}

    y_label = ''
    if not pt["curveNumber"]:
        y_label = f"{final_price:.2f}"
    elif pt["curveNumber"] == 1:
        y_label = f"{numerize.numerize(int(dff['volume']))}"
    elif pt["curveNumber"] == 2:
        y_label = f"{pt['y']:.2f}"
    else:
        y_label = f"{pt['y']:.4f}"
    children = [
        html.Div([
            html.Table([
                html.Tr([
                    html.Td("Volume",style={"color":"grey"}),
                    html.Td("{}".format(numerize.numerize(int(dff["volume"])),2), style={"text-align":"right"}),
                ]),
                html.Tr([
                    html.Td("Open",style={"color":"grey"}),
                    html.Td("{:.2f}".format(float(dff["open"])), style={"text-align":"right"}),
                ]),
                html.Tr([
                    html.Td("High",style={"color":"grey"}),
                    html.Td("{:.2f}".format(float(dff["high"])), style={"text-align":"right"}),
                ]),
                html.Tr([
                    html.Td("Low",style={"color":"grey"}),
                    html.Td("{:.2f}".format(float(dff["low"])), style={"text-align":"right"}),
                ]),
                html.Tr([
                    html.Td("Close",style={"color":"grey"}),
                    html.Td("{:.2f}".format(final_price), style={"text-align":"right"}),
                ]),
                html.Tr([
                    html.Td("% Change",style={"color":"grey"}),
                    html.Td("{:.2f}%".format(change), style={"text-align":"right"}),
                ])

            ])
        ], ),
        html.Div([
            html.P(
                children=f"{selected_date.strftime(r'%m-%d %-I:%M %p')}",
                style={
                    "padding":"5px",
                    "border-radius":"5%",
                    "background":"black",
                    "color":"white"
                }
            )
            
        ], style={
            "position":"fixed",
            "top":"580px",
            "left":f"{x}px"
        }),
        html.Div([
            html.P(
                children=y_label,
                style={
                    "padding":"5px",
                    "border-radius":"5%",
                    "background":"black",
                    "color":"white"
                }
            )
            
        ], style={
            "position":"fixed",
            "top":f"{y}px",
            "left":"69.5vw"
        })

    ]

    return True, bbox, children

@callback(
    Output("fig", "figure",allow_duplicate=True),
    Input("fig", "relayoutData"),
    State("fig","figure"),
    State("cached-visual-data","data"),
    prevent_initial_call = True,
)
def scaleYaxis(rng,fig,data):
    # print("DEBUG SCALEYAXIS:",rng)  
    # print(df, fig["data"][0]["x"])
    if not fig: 
        # print("DEBUG FIG NOT FOUND",data)
        ticker, year, month = (data["ticker"], data["year"], data["month"]) if data else ('AAPL', 2023, 2)
        CSV_PATH = "/Volumes/easystore/ProjectGRT/StockData/{}_{:d}-{:02d}.csv".format(ticker,year,month)
        fig = createFig(CSV_PATH,ticker)
    if rng and "xaxis.autorange" in rng:
        # print("AUTORANGE INITIATE")
        fig['layout']['xaxis']['autorange'] = rng["xaxis.autorange"]
        fig['layout']['yaxis']['autorange'] = rng["xaxis.autorange"]
        fig['layout']['xaxis2']['autorange'] = rng["xaxis2.autorange"]
        fig['layout']['yaxis2']['autorange'] = rng["xaxis2.autorange"]
        fig['layout']['xaxis4']['autorange'] = rng["xaxis4.autorange"]
        fig['layout']['yaxis4']['autorange'] = rng["xaxis4.autorange"]

    elif rng and ("xaxis.range[0]" in rng or "xaxis.range" in rng):
        # print("MANUAL INITIATE")
        fig['layout']['xaxis']['autorange'] = False
        fig['layout']['yaxis']['autorange'] = False
        fig['layout']['xaxis2']['autorange'] = False
        fig['layout']['yaxis2']['autorange'] = False

        fig['layout']['xaxis4']['autorange'] = False
        fig['layout']['yaxis4']['autorange'] = False

        start_time = rng['xaxis.range'][0] if "xaxis.range" in rng else rng['xaxis.range[0]']
        end_time = rng["xaxis.range"][1] if "xaxis.range" in rng else rng['xaxis.range[1]']
        start_time = datetime.fromisoformat(start_time.split('.')[0])
        end_time = datetime.fromisoformat(end_time.split('.')[0])
        # print(start_time, end_time)
    
        try:
            mask = (df['timestamp'] >= start_time) & (df['timestamp'] <= end_time)
            df_range = df.loc[mask]
            ymin, ymax = df_range["close"].min(), df_range["close"].max()
            ymin2, ymax2 = df_range["volume"].min(), df_range["volume"].max()
            ymin4, ymax4 = df_range["macd"].min(), df_range["macd"].max()

            offset = (ymax-ymin)*0.1
            offset2 = (ymax2-ymin2)*0.1
            offset4 = (ymax4-ymin4)*0.1

            # print(ymin,ymax,offset)
            fig['layout']['yaxis']['range'] = [ymin-offset,ymax+offset]
            fig['layout']['yaxis2']['range'] = [ymin2-offset2,ymax2+offset2]
            fig['layout']['yaxis4']['range'] = [ymin4-offset4,ymax4+offset4]

        except KeyError:
            pass
        finally:
            fig['layout']['xaxis']['range'] = fig['layout']['xaxis2']['range'] = fig['layout']['xaxis4']['range'] = [max(min(df["timestamp"]),start_time),min(max(df["timestamp"]),end_time)]
    return fig



# if __name__ == "__main__":
#     app.run(debug=True)
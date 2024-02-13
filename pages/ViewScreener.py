import dash
from dash import Dash, dash_table, html, dcc, callback, ctx
from dash.dependencies import Output, Input, State
import pandas as pd
from datetime import date, timedelta
from os import listdir
from bisect import bisect_left

dash.register_page(__name__)
cur_date = None
CSV_DIR = "/Volumes/easystore/screener/"
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

layout = html.Div([
    html.Div([html.Div([
        html.Div(
            dcc.DatePickerSingle(
                id='my-date-picker-single',
                min_date_allowed=date(screener_list[0][0], screener_list[0][1], screener_list[0][2]),
                max_date_allowed=date(screener_list[-1][0], screener_list[-1][1], screener_list[-1][2]),
                initial_visible_month=date(screener_list[-1][0], screener_list[-1][1], screener_list[-1][2]),
                # date=date(screener_list[-1][0], screener_list[-1][1], screener_list[-1][2]),
                # style={}
        ), style = {"display":"table-cell","padding-right":"10px"}),
        html.Div(html.Button('<', id='prev-button'),style = {"display":"table-cell"}),
        html.Div(html.Button('>', id='next-button'),style = {"display":"table-cell"}),
        ], style={"display":"table-row"})
    ], style={"display":"table", "margin-top":"50px", "margin-left":"5%",}),
    html.Div(
        id='output-container-date-picker-single',
        style={"margin-top":"10px","margin-left":"5%"}    
    ),

    dash_table.DataTable(
        id="screener-datatable",   
        # data=df.to_dict('records'), 
        # columns =[{"name": i, "id": i} for i in df.columns],
        style_table={'maxWidth': '40%',"margin-top":"10px","margin-left":"5%"},
        sort_action='native',
        style_cell_conditional=[
            {'if': {'column_id': 'Ticker'},
            'width': '20%'},
            {'if': {'column_id': '% Change'},
            'width': '50%'},
        ]
    ),
    dcc.Store(id='cached-data',storage_type="session"),

])

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
    print("DEBUG",cached_data, picker_date, ctx.triggered)
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

    return f"Showing {year}-{month:02}-{day:02}",df.to_dict('records'), [{"name": i, "id": i} for i in df.columns],[], None, {"date":selected_date}, date(year,month,day)


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
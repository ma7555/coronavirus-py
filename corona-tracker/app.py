import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import time
import threading
from bs4 import BeautifulSoup
import requests

baseURLJH = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/"

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

colors = {
        'background': '#111111',
        'text': 'rgb(119,189,217)'
        }

tickFont = {'size': 15, 
            'color': colors['text'], 
            'family': 'sans-serif'
            }


cols_int =['CumConfirmed', 'CumDeaths', 'CumRecovered']

def loadDataJH(fileName, columnName):

    data = pd.read_csv(baseURLJH + fileName) \
             .melt(id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'], var_name='date', value_name=columnName)
    
    data['Province/State'] = data['Province/State'].fillna('<all>')
    data.fillna(0, inplace=True)

    data[columnName] = data[columnName].astype(np.int64)
    
    data['date'] = data['date'].astype('datetime64[ns]')
    return data


def loadData_ulklc():
    data = pd.read_csv('https://raw.githubusercontent.com/ulklc/covid19-timeseries/master/countryReport/raw/rawReport.csv')

    data['day'] = data['day'].astype('datetime64[ns]')

    data.rename(columns={'countryName': 'Country/Region', 
                            'lat': 'Lat', 'lon': 'Long', 
                            'confirmed': 'CumConfirmed', 
                            'death':'CumDeaths', 
                            'recovered':'CumRecovered', 
                            'day': 'date'}, 
                            inplace=True)

    data['Province/State'] = '<all>'

    data.drop(['region', 'countryCode'], axis=1, inplace=True)
    data = data[['Province/State', 'Country/Region', 'Lat', 'Long', 'date', 'CumConfirmed', 'CumDeaths', 'CumRecovered']]

    return data



allData = loadData_ulklc()
countries = allData['Country/Region'].unique()
countries.sort()

confirmed_eg, recovers_eg, deaths_eg = 0, 0, 0

RELOAD_INTERVAL = 1 * 3600 # reload interval in seconds



def refresh_data_every():
    while True:
        refresh_data()
        time.sleep(RELOAD_INTERVAL)

def refresh_data():
    global allData, countries, confirmed_eg, recovers_eg, deaths_eg
    ### some expensive computation function to update dataframe
    # allData = loadDataJH("time_series_covid19_confirmed_global.csv", "CumConfirmed") \
    #         .merge(loadDataJH("time_series_covid19_deaths_global.csv", "CumDeaths")) \
    #         .merge(loadDataJH("time_series_19-covid-Recovered.csv", "CumRecovered"))
    allData = loadData_ulklc()
    countries = allData['Country/Region'].unique()
    countries.sort()

    print('DATA UPDATED!!')

thread = threading.Thread(target=refresh_data_every, daemon=True)
thread.start()

app = dash.Dash(__name__)
app.title = 'EG - Coronavirus COVID-19 Tracker'

app.layout = html.Div(className='body',
                style={
                    'family':"sans-serif" ,
                    'backgroundColor': colors['background'],
                    'position':'absolute',
                    'width':'100%',
                    'height':'100%',
                    'top':'0px',
                    'left':'0px',
                    'z-index':'1000'
                    },
                children=[
                html.H1('Egypt Coronavirus (COVID-19) Tracker', 
                        style={
                            'textAlign': 'center',
                            'margin-top': '3rem',
                            'color': colors['text']
                        }),
                html.Div(className="row", 
                        style={'margin-left': '2rem'},
                        children=[
                    html.Div(className="three columns", children=[
                        html.H5('Country', 
                                    style={
                                            'textAlign': 'left',
                                            'color': colors['text']
                                        }
                                ),
                        dcc.Dropdown(
                            id='country',
                            options=[{'label':c, 'value':c} for c in countries],
                            value='Egypt',
                            disabled=False
                        )
                    ]),
                    html.Div(className="three columns", children=[
                        html.H5('Governorate/State', 
                                    style={
                                            'textAlign': 'left',
                                            'color': colors['text']
                                            }),
                        dcc.Dropdown(
                            id='state'
                        )
                    ]),
                    html.Div(className="three columns", children=[
                        html.H5('Selected Metrics', 
                                    style={
                                            'textAlign': 'left',
                                            'color': colors['text']
                                            }),
                        dcc.Checklist(
                            id='metrics',
                            options=[{'label':m, 'value':m} for m in ['Confirmed', 'Deaths', 'Recovered', 'Active']],
                            value=['Confirmed', 'Deaths', 'Active'], 
                                    style={
                                            'textAlign': 'left',
                                            'color': colors['text']
                                            }
                            )
                        ])
                    ]),
                html.Div(className="row", children=[
                    html.Div(className="three columns", children=[
                        html.Div(
                            [html.H2(id="confirmed_text"), html.H4("Confirmed", 
                                                                    style={
                                                                            'textAlign': 'left',
                                                                            'color': colors['background']
                                                                        }
                                                                    )
                                                                ],
                                     id="confirmed",
                                     className="mini_container",
                                    )
                                ]
                            ),
                        html.Div(className="three columns", children=[
                            html.Div(
                                [html.H2(id='deaths_text'), 
                                 html.H4("Deaths", 
                                            style={
                                                    'textAlign': 'left',
                                                    'color': colors['background']
                                                }
                                            )
                                        ],
                                    id="deaths",
                                    className="mini_container",
                                    )
                                ]
                            ),
                        html.Div(className="three columns", children=[
                            html.Div(
                                [html.H2(id="recovered_text"), 
                                 html.H4("Recovered", 
                                            style={
                                                    'textAlign': 'left',
                                                    'color': colors['background']
                                                }
                                            )
                                        ],
                                    id="recovered",
                                    className="mini_container",
                                    )
                                ]
                            ),
                        html.Div(className="three columns", children=[
                                html.Div(
                                    [html.H2(id="active_text"), 
                                    html.H4("Active", 
                                                style={
                                                        'textAlign': 'left',
                                                        'color': colors['background']
                                                    }
                                                )
                                            ],
                                    id="active",
                                    className="mini_container",
                                ),
                            ],
                        )
                    ]),

                html.Div(className="row", children=[

                    html.Div(className="three columns", children=[
                        html.Div(
                            [html.H2(id='expected_cases_by_tomorrow_text', children='NA'), 
                             html.H5("Expected Cases by Tomorrow", 
                                            style={
                                                    'textAlign': 'left',
                                                    'color': colors['background']
                                                }
                                            )
                                        ],
                                    id="expected_cases_by_tomorrow",
                                    className="mini_container",
                                    )
                                ]
                            ),

                    html.Div(className="three columns", children=[
                        html.Div(
                            [html.H2(id="cases_increase_text"), 
                             html.H5("Cases Increase From Yesterday", 
                                                                    style={
                                                                            'textAlign': 'left',
                                                                            'color': colors['background']
                                                                        }
                                                                    )
                                                                ],
                                     id="cases_increase",
                                     className="mini_container",
                                    )
                                ]
                            ),
                    html.Div(className="three columns", children=[
                        html.Div(
                            [html.H2(id="mortality_rate_infection_text"), 
                             html.H5("Mortality Rate / Infection Case", 
                                                                    style={
                                                                            'textAlign': 'left',
                                                                            'color': colors['background']
                                                                        }
                                                                    )
                                                                ],
                                     id="mortality_rate_infections",
                                     className="mini_container",
                                    )
                                ]
                            ),
                        html.Div(className="three columns", children=[
                            html.Div(
                                [html.H2(id='mortality_rate_closed_text'), 
                                 html.H5("Mortality Rate / Closed Case", 
                                            style={
                                                    'textAlign': 'left',
                                                    'color': colors['background']
                                                }
                                            )
                                        ],
                                    id="mortality_rate_closed",
                                    className="mini_container",
                                    )
                                ]
                            )
                        ],
                    )
                    ,
                    
                dcc.Loading(dcc.Graph(
                        id="plot_cum_metrics",
                        config={ 'displayModeBar': False }
                    )),
                dcc.Loading(dcc.Graph(
                        id="plot_new_metrics",
                        config={ 'displayModeBar': False }
                    ))
                        
                # html.Div([
                #     html.Div([
                #         #html.H3('New Metrics'),
                #         dcc.Graph(
                #     id="plot_cum_metrics",
                #     config={ 'displayModeBar': False }
                # )
                #     ], className="six columns"),

                #     html.Div([
                #         #html.H3('Cum Metrics'),
                #         dcc.Graph(
                #     id="plot_new_metrics",
                #     config={ 'displayModeBar': False }
                # )
                #     ], className="six columns"),
                # ], className="row")
                ,
                html.Div(className="row", children=[
                    dcc.Markdown(className='three columns', 
                                children=['''
                                > Data by Johns Hopkins University Center for Systems Science and Engineering (JHU CSSE)

                                > [Github](https://github.com/CSSEGISandData/COVID-19)
                                '''],
                                style={ 'width': '100%',
                                        'textAlign': 'left',
                                        'background-color': colors['background'],
                                        'color': colors['text'],
                                        'font-size': 13
                                        }
                                    )
                    ]
                ),
            html.Div(id='intermediate', style={'display': 'none'}),
            dcc.Interval(id='interval-component', interval=1*1000) # in milliseconds
            ]
        )

def fix_data_errors(data):
    # fix erros where cum value of today less than yesterday
    df_fix_err = data.select_dtypes(include='int64').diff() < 0
    for col in df_fix_err.columns:
        error_ixs = df_fix_err.index[df_fix_err[col] == True]
        data.loc[error_ixs, col] = np.nan
        data[col] = data[col].fillna(method='ffill').astype(np.int64)

    return data

@app.callback(
    Output('intermediate', 'children'),
    [Input('country', 'value'), Input('state', 'value')])
def nonreactive_data(country, state):
    data = allData.loc[allData['Country/Region'] == country].copy()

    data = data.iloc[-14:, :]
    
    data = fix_data_errors(data)

    data['CumActive'] = data['CumConfirmed'] - data['CumDeaths'] - data['CumRecovered']

    if state == '<all>':
        data = data.drop('Province/State', axis=1).groupby("date").sum().reset_index()
    else:
        data = data.loc[data['Province/State'] == state]
    newCases = data.select_dtypes(include='int64').diff().fillna(0)

    newCases.columns = [column.replace('Cum', 'New') for column in newCases.columns]
    data = data.join(newCases)
    #data['dateStr'] = data['date'].dt.strftime('%b %d, %Y')
    data['dateStr'] = data.date.dt.strftime('%d %b %y')
    data['DiffYesterday'] = ((data.NewConfirmed.shift(periods=-1) / data.CumConfirmed)*100).round(1)
    data['MortalityRateInfection'] = ((data.CumDeaths / data.CumConfirmed)*100).round(1)
    data['MortalityRateClosed'] = ((data.CumDeaths / (data.CumDeaths + data.CumRecovered))*100).round(1)
    data = data.loc[~(data[['CumConfirmed', 'CumDeaths', 'CumRecovered', 'NewConfirmed', 'NewDeaths']]==0).all(axis=1)]
    return data.to_json()

@app.callback(
    [Output('state', 'options'), Output('state', 'value')],
    [Input('country', 'value')]
)
def update_states(country):
    states = list(allData.loc[allData['Country/Region'] == country]['Province/State'].unique())
    states.insert(0, '<all>')
    states.sort()
    state_options = [{'label':s, 'value':s} for s in states]
    state_value = state_options[0]['value']
    return state_options, state_value

def barchart(data, metrics, prefix="", yaxisTitle=""):
    figure = go.Figure(
                        data=[
                                go.Bar( 
                                    name=metric, x=data.date, y=data[prefix + metric],
                                    marker_line_color='rgb(0,0,0)', marker_line_width=1,
                                    marker_color={ 'Deaths':'rgb(200,30,30)', 
                                                   'Recovered':'rgb(30,200,30)', 
                                                   'Confirmed': colors['text'], 
                                                   'Active': 'rgb(245,140,10)'}[metric]
                                ) for metric in metrics
                            ],
                        layout= {
                                'plot_bgcolor': colors['background'],
                                'paper_bgcolor': colors['background'],
                                'font': {
                                    'color': colors['text']
                                        },
                                'xaxis':dict(showticklabels=True, fixedrange=True),
                                'yaxis':dict(showticklabels=True, fixedrange=True)
                                }
                        )
    figure.update_layout( 
              barmode='group', legend=dict(x=.05, y=0.95, font={'size':15}, bgcolor='rgba(240,240,240,0.2)'), 
              plot_bgcolor=colors['background'], font=tickFont) \
          .update_xaxes( 
              title="", tickangle=-45, type='category', showgrid=False, gridcolor='#DDDDDD', 
              tickfont=tickFont, ticktext=data.dateStr, tickvals=data.date) \
          .update_yaxes(
              title=yaxisTitle, showgrid=True, gridcolor='#DDDDDD')
    return figure

def scatterchart(data, metrics, prefix="", yaxisTitle=""):
    figure = go.Figure(data=[
                            go.Scatter( 
                                name=metric, x=data.date, y=data[prefix + metric],
                                mode='lines+markers',
                                marker_line_color='rgb(0,0,0)', marker_size=12,
                                marker_color={ 'Deaths':'rgb(200,30,30)', 
                                               'Recovered':'rgb(30,200,30)', 
                                               'Confirmed': colors['text'], 
                                               'Active': 'rgb(245,140,10)'}[metric]
                            ) for metric in metrics
                        ],
                        layout= {
                                'plot_bgcolor': colors['background'],
                                'paper_bgcolor': colors['background'],
                                'font': {
                                    'color': colors['text']
                                    },
                                'xaxis':dict(showticklabels=True, fixedrange=True),
                                'yaxis':dict(showticklabels=True, fixedrange=True)
                                }
                            )
    figure.update_layout( 
              legend=dict(x=.05, y=0.95, font={'size':15}, bgcolor='rgba(240,240,240,0.2)'), 
              plot_bgcolor=colors['background'], font=tickFont) \
          .update_xaxes( 
              title="", tickangle=-45, type='category', showgrid=False, gridcolor='#DDDDDD', 
              tickfont=tickFont, ticktext=data.dateStr, tickvals=data.date) \
          .update_yaxes(
              title=yaxisTitle, showgrid=True, gridcolor='#DDDDDD')
    return figure


@app.callback(
    Output('plot_new_metrics', 'figure'), 
    [Input('intermediate', 'children'), Input('metrics', 'value')]
)
def update_plot_new_metrics(cleaned_data, metrics):
    data = pd.read_json(cleaned_data)
    metrics_ = [metric for metric in metrics if metric != 'Active']
    return barchart(data, metrics_, prefix="New", yaxisTitle="New Cases per Day")

@app.callback(
    Output('plot_cum_metrics', 'figure'), 
    [Input('intermediate', 'children'), Input('metrics', 'value')]
)
def update_plot_cum_metrics(cleaned_data, metrics):
    data = pd.read_json(cleaned_data)
    return scatterchart(data, metrics, prefix="Cum", yaxisTitle="Cumulated Cases")

@app.callback(
    [
        Output('confirmed_text', 'children'),
        Output('deaths_text', 'children'),
        Output('recovered_text', 'children'),
        Output('active_text', 'children'),
        Output('mortality_rate_infection_text', 'children'),
        Output('mortality_rate_closed_text', 'children'),
        Output('cases_increase_text', 'children'),
    ],
    [Input('intermediate', 'children'), Input('country', 'value')]
)
def update_text(cleaned_data, country):
    data = pd.read_json(cleaned_data)
    try:
        new_cases = data['NewConfirmed'].iat[-1]
        if new_cases > 0:
            new_cases = str('+') + str(new_cases)
        else:
            new_cases = str(new_cases)
            
        stats = data[['CumConfirmed', 'CumDeaths', 'CumRecovered', 'CumActive', 'MortalityRateInfection', 'MortalityRateClosed']].iloc[-1].tolist() + \
                [new_cases + ' (' + str(data['DiffYesterday'].iat[-2]) + '%)']

        # if country == 'Egypt':
        #     stats[0] = max(stats[0], confirmed_eg) 
        #     stats[1] = max(stats[1], deaths_eg) 
        #     stats[2] = max(stats[2], recovers_eg) 

        for stat in range(-3, -1):
            stats[stat] = str(stats[stat]) + '%'
            
    except:
        stats = [0, 0, 0, 0, 0, 0, 0]
    return stats

if __name__ == '__main__':
    app.run_server(port=8080, debug=True, threaded=True, processes=1)
    
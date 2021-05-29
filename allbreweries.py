# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table

import plotly.express as px

import pandas as pd

import os
ROOT_DIR = os.getcwd()
DATA_DIR = os.path.join(ROOT_DIR,'data')
BBS_DIR = os.path.join(DATA_DIR,'breweriesByState')


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "brewxplorer"

allBreweries = pd.read_excel(os.path.join(BBS_DIR,'cleaned.xlsx'))

allBreweries.dropna(inplace=True)

counts_dict = allBreweries['breweryCity'].value_counts().to_dict()

allBreweries['breweryCounts'] = allBreweries.apply(lambda x: counts_dict[x.breweryCity], axis=1)

list_of_states = list(allBreweries['breweryState'].unique())
list_of_states.sort()
list_of_states = ['all'] + list_of_states


app.layout = html.Div(
    children=[
    html.H1('Breweries in the United States',
            style={'text-align': 'center'
                  }
           ),
        
    html.Div(
        children=[
            html.H6('Select a State'),
            dcc.Dropdown(
                id='state-selector',
                options=[{'label': i, 'value': i} for i in list_of_states],
                value='all'
                )]
        ,
        style={'width': '48%', 'float': 'left'}
    ),
        
    html.Div(
        children=[
            html.H6('Search a brewery'),
            dcc.Dropdown(
                id='brewery-finder',
                options=[{'label': i, 'value': i} for i in allBreweries['breweryName'].unique()],
                )
        ],
        style={'width': '48%', 'float': 'right'}
    ),
        
    html.Div(
        children=[
            html.H6('Select a City'),
            dcc.Dropdown(
                id='city-selector',
                value='all'
                )],
        style={'width': '48%', 'float': 'bottom'}
    ),
    
    html.Div(
        children=[
            html.H6(
                    id='brewery-location',
                    children='')
        ],
        style={'width': '48%', 'float': 'right'}
    ),
    
    html.Br(),
        
    html.Div(
        dcc.Graph(id='US_breweries-graph'),
        style={'width': '48%', 'float': 'left'}
    ),
        
    html.Div(
    dash_table.DataTable(id='table',
                         columns=[{"name": i, "id": i} for i in allBreweries.columns[0:3]],
                        page_size=10
                        ), 
    
    style={'width': '48%', 'float': 'right'}),
    
    html.Div(
        children=html.H4(
            id='summary-data',
            children='There are x breweries in the united states'),
        style={'width': '48%', 'float': 'bottom'}
    )
])

@app.callback(
    Output('brewery-location', 'children'),
    Input('brewery-finder','value')
)
def brewery_finder(selected_brewery):
    df = allBreweries[allBreweries['breweryName']== selected_brewery]
    return 'Brewery location: ' + df.breweryCity + ', ' + df.breweryState
    

@app.callback(
    Output('city-selector', 'options'),
    Input('state-selector', 'value')
)
def update_city_options(selected_state):
    df = allBreweries[allBreweries['breweryState']==selected_state]
    cities_in_state = list(df['breweryCity'].unique())
    cities_in_state.sort()
    cities_in_state = ['all'] + cities_in_state
    return [{'label': i, 'value': i} for i in cities_in_state]


@app.callback(
    Output('US_breweries-graph', 'figure'),
    Output('table', 'data'),
    Output('summary-data', 'children'),
    Input('state-selector', 'value'),
    Input('city-selector', 'value')
)
def update_plot(selected_state, selected_city):
    if selected_state=='all':
        # All of the US
        df = allBreweries.copy()
        fig = px.scatter_mapbox(df, lat="lat", lon="lon", 
                                hover_name="breweryCity", 
                                hover_data=["breweryState","breweryCounts"],
                                color_discrete_sequence=["fuchsia"], 
                                size="breweryCounts", 
                                opacity=0.1, zoom=3, height=300)
       
        variable_text = 'the United States'
            
    else:
        # Particular state selected
        if selected_city=='all':
            #all cities in a particular state
            df = allBreweries[allBreweries['breweryState']==selected_state].copy()
            df.sort_values(by=['breweryCity'], inplace=True)
            fig = px.scatter_mapbox(df, lat="lat", lon="lon", hover_name="breweryCity",
                                    hover_data=["breweryState","breweryCounts"],
                                    color_discrete_sequence=["fuchsia"], 
                                    size="breweryCounts", 
                                    opacity=0.5, zoom=5, height=300)
           
            variable_text = 'the state of ' + selected_state
        else:
            #particular city in a particular state
            df = allBreweries[(allBreweries['breweryState']==selected_state) & 
                                  (allBreweries['breweryCity']==selected_city)].copy()
                
            fig = px.scatter_mapbox(df, lat="lat", lon="lon",
                                    hover_name="breweryCity", 
                                    hover_data=["breweryState","breweryCounts"],
                                    color_discrete_sequence=["fuchsia"], 
#                                     marker = {'size': 20, 'symbol': ["beer"]},
                                    size="breweryCounts", 
                                    zoom=5, height=300)
            variable_text = selected_city + ', ' + selected_state
        
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":5,"t":5,"l":0,"b":0})
    
    data = df[df.columns[0:3]].sort_values(by=['breweryState']).to_dict('records')
    
    num = df.shape[0]

    if num>1:
        common_text = 'We found ' + str(num) + ' breweries in '
    else:
        common_text = 'We found ' + str(num) + ' brewery in '
        
    summary_text = common_text + variable_text

    return fig, data, summary_text


    

if __name__ == '__main__':
    app.run_server(debug=True)


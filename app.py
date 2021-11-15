# Import required libraries
import pickle
import copy
import datetime as dt
import math

import pandas as pd
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html

# Multi-dropdown options
from controls import COUNTIES, WELL_STATUSES, WELL_TYPES, WELL_COLORS

external_scripts = [
    {
        'src':'https://kit.fontawesome.com/04fd9b612c.js',
        'crossorigin': 'anonymous'
    }
]

app = dash.Dash(__name__,
                external_scripts=external_scripts)

# Create controls
county_options = [{'label': str(COUNTIES[county]), 'value':str(county)} for county in COUNTIES]
well_status_options = [{'label': str(WELL_STATUSES[well_status]), 'value':str(well_status)} for well_status in WELL_STATUSES]
well_type_options = [{'label': str(WELL_TYPES[well_type]), 'value':str(well_type)} for well_type in WELL_TYPES]

# Load data
df = pd.read_csv('data/wellspublic.csv')
# Parse datetime
df['Date_Well_Completed'] = pd.to_datetime(df['Date_Well_Completed'])
# Save df by a filter
df = df[df['Date_Well_Completed'] > dt.datetime(1960, 1, 1)]
# Select only 3 columns of df
trim = df[['API_WellNo', 'Well_Type', 'Well_Name']]
# Select index of trim
trim.index = trim['API_WellNo']
#
dataset = trim.to_dict(orient='index')

points = pickle.load(open("data/points.pkl", "rb"))

# Create global chart template
mapbox_access_token = 'pk.eyJ1IjoiamFja2x1byIsImEiOiJjajNlcnh3MzEwMHZtMzNueGw3NWw5ZXF5In0.fk8k06T96Ml9CLGgKmk81w'

# Map graph layout
layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(
        l=30,
        r=30,
        b=20,
        t=40
    ),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation='h'),
    title='Satellite Overview',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(
            lon=-78.05,
            lat=42.54
        ),
        zoom=7,
    )
)

# Create app layout
app.layout = html.Div(
    [
        dcc.Store(id='aggregate_data'),
        # Header
        html.Div(
            [
                # SPS Logo.
                html.Img(
                    src='https://www.spsolutions.com.mx/assets/img/SPS_logo.png',
                    className='two columns',
                    style={"width":100,"height":100}
                ),
                # Dashboard Title.
                html.Div(
                    [
                        html.H1('New York Oil and Gas Production Overview')
                    ],
                    className='eight columns'
                ),
                # Buttom contact us
                html.A(
                    html.Button("Contact Us", id='learnmore'),
                    href="https://www.spsolutions.com.mx/",
                    className="two columns"
                )
            ],
            id='header',
            className='row'
        ),
        html.Div(
            [
                # Controls
                html.Div(
                    [
                        # Title Rangeslider
                        html.P(
                            'Filter by construction date (or select range in histogram):',
                            className='control_label'
                        ),
                        html.Br(),
                        # Range Slider
                        dcc.RangeSlider(
                            id='year_slider',
                            min=1960,
                            max=2017,
                            marks={
                                1960: '1960',
                                1970: '1970',
                                1980: '1980',
                                1990: '1990',
                                2000: '2000',
                                2010: '2010',
                                2017: '2017'
                            },
                            value=[1990,2010],
                            className="dcc_control"
                        ),
                        html.Br(),
                        # Title of filters
                        html.P(
                            'Filter by well status:',
                            className='control_label'
                        ),
                        # Radio Items for filters
                        dcc.RadioItems(
                            id='well_status_selector',
                            options=[
                                {'label':'All ','value':'all'},
                                {'label':'Active only ','value':'active'},
                                {'label':'Customize ','value':'custom'}
                            ],
                            value='active',
                            labelStyle={'display':'inline-block'},
                            className="dcc_control"
                        ),
                        # All options of filters
                        dcc.Dropdown(
                            id='well_statuses',
                            options=well_status_options,
                            multi=True,
                            value=list(WELL_STATUSES.keys()),
                            className='dcc_control'
                        ),
                        # Lock camera
                        dcc.Checklist(
                            id='lock_selector',
                            options=[
                                {'label':'Lock camera','value':'locked'}
                            ],
                            value=[],
                            className="dcc_control"
                        ),
                        # Title filter by well
                        html.P(
                            'Filter by well type:',
                            className="control_label"
                        ),
                        # Radio items of well type
                        dcc.RadioItems(
                            id='well_type_selector',
                            options=[
                                {'label':'All ','value':'all'},
                                {'label':'Productive only ','value':'productive'},
                                {'label':'Customize ','value':'custom'}
                            ],
                            value='productive',
                            labelStyle={'display':'inline-block'},
                            className='dcc_control'
                        ),
                        # Options of well type
                        dcc.Dropdown(
                            id='well_types',
                            options=well_type_options,
                            multi=True,
                            value=list(WELL_TYPES.keys()),
                            className='dcc_control'
                        ),
                    ],
                    className="pretty_container four columns"
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                # Number of wells card
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.P("No. of Wells"),
                                                html.P(
                                                    id='well_text',
                                                    className='info_text'
                                                )
                                            ]
                                        ),
                                        html.Div(
                                            [
                                                html.I(className="fas fa-gopuram item")
                                            ],className='icon_item'
                                        )
                                    ],
                                    id='wells',
                                    className='pretty_container box'
                                ),
                                # Fluids cards
                                html.Div(
                                    [
                                        # Gas card
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.P('Gas'),
                                                        html.P(
                                                            id='gasText',
                                                            className='info_text'
                                                        )
                                                    ]
                                                ),
                                                html.Div(
                                                    [
                                                        html.I(className="fas fa-burn item")
                                                    ],className='icon_item'
                                                ),
                                            ],
                                            id='gas',
                                            className='pretty_container box'
                                        ),
                                        # Oil card
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.P('Oil'),
                                                        html.P(
                                                            id='oilText',
                                                            className='info_text'
                                                        )
                                                    ],className='text_box'
                                                ),
                                                html.Div(
                                                    [
                                                        html.I(className="fas fa-gas-pump item")
                                                    ],className='icon_item'
                                                ),
                                            ],
                                            id='oil',
                                            className='pretty_container box',
                                        ),
                                        # Water card
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.P('Water'),
                                                        html.P(
                                                            id='waterText',
                                                            className='info_text'
                                                        )
                                                    ],className='text_box'
                                                ),
                                                html.Div(
                                                    [
                                                        html.I(className="fas fa-tint item")
                                                    ],className='icon_item'
                                                ),
                                            ],
                                            id='water',
                                            className='pretty_container box'
                                        )
                                    ],
                                    id='tripleContainer'
                                )
                            ],
                            id='infoContainer',
                            className='row'
                        ),
                        # Completed wells/Year graph
                        html.Div(
                            [
                                dcc.Graph(
                                    id='count_graph'
                                )
                            ],
                            id='countGraphContainer',
                            className='pretty_container'
                        )
                    ],
                    id='rightCol',
                    className='eight columns'
                )
            ],
            className='row'
        ),
        html.Div(
            [
                # Mapbox graph
                html.Div(
                    [
                        dcc.Graph(id='main_graph')
                    ],
                    className='pretty_container eight columns'
                ),
                # Well graph
                html.Div(
                    [
                        dcc.Graph(id='individual_graph')
                    ],
                    className='pretty_container four columns'
                )
            ],
            className='row'
        ),
        html.Div(
            [
                # Production summary graph
                html.Div(
                    [
                        dcc.Graph(id='pie_graph')
                    ],
                    className='pretty_container seven columns'
                ),
                # Aggregate graph
                html.Div(
                    [
                        dcc.Graph(id='aggregate_graph')
                    ],
                    className='pretty_container five columns'
                )
            ],
            className='row'
        )
    ],
    id='mainContainer',
    style={
        "display":'flex',
        'flex-direction':'column'
    }
)

# Helper functions
def human_format(num):
    magnitude = int(math.log(num, 1000))
    mantissa = str(int(num / (1000**magnitude)))
    return mantissa + ['', 'K', 'M', 'G', 'T', 'P'][magnitude]

def filter_dataframe(df, well_statuses, well_types, year_slider):
    dff = df[df['Well_Status'].isin(well_statuses)
            & df['Well_Type'].isin(well_types)
            & (df['Date_Well_Completed'] > dt.datetime(year_slider[0], 1, 1))
            & (df['Date_Well_Completed'] < dt.datetime(year_slider[1], 1, 1))]
    return dff

def fetch_individual(api):
    try:
        points[api]
    except:
        return None, None, None, None

    index = list(range(min(points[api].keys()), max(points[api].keys()) + 1))
    gas = []
    oil = []
    water = []

    for year in index:
        try:
            gas.append(points[api][year]['Gas Produced, MCF'])
        except:
            gas.append(0)
        try:
            oil.append(points[api][year]['Oil Produced, bbl'])
        except:
            oil.append(0)
        try:
            water.append(points[api][year]['Water Produced, bbl'])
        except:
            water.append(0)
    return index, gas, oil, water

def fetch_aggregate(selected, year_slider):

    index = list(range(max(year_slider[0],1985),2016))
    gas = []
    oil = []
    water = []

    for year in index:
        count_gas = 0
        count_oil = 0
        count_water = 0
        for api in selected:
            try:
                count_gas += points[api][year]['Gas Produced, MCF']
            except:
                pass
            try:
                count_oil += points[api][year]['Oil Produced, bbl']
            except:
                pass
            try:
                count_water += points[api][year]['Water Produced, bbl']
            except:
                pass
        gas.append(count_gas)
        oil.append(count_oil)
        water.append(count_water)
    
    return index, gas, oil, water

# Create callbacks

@app.callback(Output('aggregate_data', 'data'),
            [Input('well_statuses', 'value'),
            Input('well_types', 'value'),
            Input('year_slider', 'value')])
def update_production_text(well_statuses, well_types, year_slider):
    dff = filter_dataframe(df, well_statuses, well_types, year_slider)
    selected = dff['API_WellNo'].values
    index, gas, oil, water = fetch_aggregate(selected, year_slider)
    return [human_format(sum(gas)), human_format(sum(oil)), human_format(sum(water))]

# Well Status radio button selector

@app.callback(Output('well_statuses', 'value'),
            [Input('well_status_selector', 'value')])
def display_status(selector):
    if selector == 'all':
        return list(WELL_STATUSES.keys())
    elif selector == 'active':
        return ['AC']
    else:
        return []

# Well Type radio button selector

@app.callback(Output('well_types', 'value'),
            [Input('well_type_selector', 'value')])
def display_type(selector):
    if selector == 'all':
        return list(WELL_TYPES.keys())
    elif selector == 'productive':
        return ['GD','GE','GW','IG','IW','OD','OE','OW']
    else:
        return []

# Slider count graph

@app.callback(Output('year_slider', 'value'),
            [Input('count_graph', 'selectedData')])
def update_year_slider(count_graph_selected):
    if count_graph_selected is None:
        return [1990,2010]
    else:
        nums = []
        for point in count_graph_selected['points']:
            nums.append(int(point['pointNumber']))
        return [min(nums) + 1960, max(nums)+1961]

# Selectors well text

@app.callback(Output('well_text', 'children'),
            [Input('well_statuses', 'value'),
            Input('well_types', 'value'),
            Input('year_slider', 'value')])
def update_well_text(well_statuses, well_types, year_slider):
    dff = filter_dataframe(df, well_statuses, well_types, year_slider)
    return dff.shape[0]

@app.callback(Output('gasText','children'),
            [Input('aggregate_data','data')])
def update_gas_text(data):
    return data[0] + " mcf"

@app.callback(Output('oilText','children'),
            [Input('aggregate_data','data')])
def update_oil_text(data):
    return data[1] + " bbl"

@app.callback(Output('waterText','children'),
            [Input('aggregate_data','data')])
def update_water_text(data):
    return data[2] + " bbl"

# Mapbox graph
@app.callback(Output('main_graph', 'figure'),
            [Input('well_statuses', 'value'),
            Input('well_types', 'value'),
            Input('year_slider', 'value')],
            [State('lock_selector', 'values'),
            State('main_graph', 'relayoutData')])
def make_main_figure(well_statuses, well_types, year_slider,
                    selector, main_graph_layout):

    dff = filter_dataframe(df, well_statuses, well_types, year_slider)

    traces = []
    for well_type, dfff in dff.groupby('Well_Type'):
        trace = dict(
            type='scattermapbox',
            lon=dfff['Surface_Longitude'],
            lat=dfff['Surface_latitude'],
            text=dfff['Well_Name'],
            customdata=dfff['API_WellNo'],
            name=WELL_TYPES[well_type],
            marker=dict(
                size=4,
                opacity=0.6,
            )
        )
        traces.append(trace)

    if (main_graph_layout is not None and 'locked' in selector):

        lon = float(main_graph_layout['mapbox']['center']['lon'])
        lat = float(main_graph_layout['mapbox']['center']['lat'])
        zoom = float(main_graph_layout['mapbox']['zoom'])
        layout['mapbox']['center']['lon'] = lon
        layout['mapbox']['center']['lat'] = lat
        layout['mapbox']['zoom'] = zoom
    else:
        lon = -78.05
        lat = 42.54
        zoom = 7

    figure = dict(data=traces, layout=layout)
    return figure

# Well name graph
@app.callback(Output('individual_graph', 'figure'),
            [Input('main_graph', 'hoverData')])
def make_individual_figure(main_graph_hover):

    layout_individual = copy.deepcopy(layout)

    if main_graph_hover is None:
        main_graph_hover = {'points': [{'curveNumber': 4,
                                        'pointNumber': 569,
                                        'customdata': 31101173130000}]}

    chosen = [point['customdata'] for point in main_graph_hover['points']]
    index, gas, oil, water = fetch_individual(chosen[0])

    if index is None:
        annotation = dict(
            text='No data available',
            x=0.5,
            y=0.5,
            align="center",
            showarrow=False,
            xref="paper",
            yref="paper"
        )
        layout_individual['annotations'] = [annotation]
        data = []
    else:
        data = [
            dict(
                type='scatter',
                mode='lines+markers',
                name='Gas Produced (mcf)',
                x=index,
                y=gas,
                line=dict(
                    shape="spline",
                    smoothing=2,
                    width=1,
                    color='#fac1b7'
                ),
                marker=dict(symbol='diamond-open')
            ),
            dict(
                type='scatter',
                mode='lines+markers',
                name='Oil Produced (bbl)',
                x=index,
                y=oil,
                line=dict(
                    shape="spline",
                    smoothing=2,
                    width=1,
                    color='#a9bb95'
                ),
                marker=dict(symbol='diamond-open')
            ),
            dict(
                type='scatter',
                mode='lines+markers',
                name='Water Produced (bbl)',
                x=index,
                y=water,
                line=dict(
                    shape="spline",
                    smoothing=2,
                    width=1,
                    color='#92d8d8'
                ),
                marker=dict(symbol='diamond-open')
            )
        ]
        layout_individual['title'] = dataset[chosen[0]]['Well_Name']

    figure = dict(data=data, layout=layout_individual)
    return figure

# Aggregate" Well tupe graph
@app.callback(Output('aggregate_graph', 'figure'),
            [Input('well_statuses', 'value'),
            Input('well_types', 'value'),
            Input('year_slider', 'value'),
            Input('main_graph', 'hoverData')])
def make_aggregate_figure(well_statuses, well_types, year_slider,
                        main_graph_hover):

    layout_aggregate = copy.deepcopy(layout)

    if main_graph_hover is None:
        main_graph_hover = {'points': [{'curveNumber': 4, 'pointNumber': 569,
                                        'customdata': 31101173130000}]}

    chosen = [point['customdata'] for point in main_graph_hover['points']]
    well_type = dataset[chosen[0]]['Well_Type']
    dff = filter_dataframe(df, well_statuses, well_types, year_slider)

    selected = dff[dff['Well_Type'] == well_type]['API_WellNo'].values
    index, gas, oil, water = fetch_aggregate(selected, year_slider)

    data = [
        dict(
            type='scatter',
            mode='lines',
            name='Gas Produced (mcf)',
            x=index,
            y=gas,
            line=dict(
                shape="spline",
                smoothing="2",
                color='#F9ADA0'
            )
        ),
        dict(
            type='scatter',
            mode='lines',
            name='Oil Produced (bbl)',
            x=index,
            y=oil,
            line=dict(
                shape="spline",
                smoothing="2",
                color='#849E68'
            )
        ),
        dict(
            type='scatter',
            mode='lines',
            name='Water Produced (bbl)',
            x=index,
            y=water,
            line=dict(
                shape="spline",
                smoothing="2",
                color='#59C3C3'
            )
        )
    ]
    layout_aggregate['title'] = 'Aggregate: ' + WELL_TYPES[well_type]

    figure = dict(data=data, layout=layout_aggregate)
    return figure


# Production Summary graph
@app.callback(Output('pie_graph', 'figure'),
            [Input('well_statuses', 'value'),
            Input('well_types', 'value'),
            Input('year_slider', 'value')])
def make_pie_figure(well_statuses, well_types, year_slider):

    layout_pie = copy.deepcopy(layout)

    dff = filter_dataframe(df, well_statuses, well_types, year_slider)

    selected = dff['API_WellNo'].values
    index, gas, oil, water = fetch_aggregate(selected, year_slider)

    aggregate = dff.groupby(['Well_Type']).count()

    data = [
        dict(
            type='pie',
            labels=['Gas', 'Oil', 'Water'],
            values=[sum(gas), sum(oil), sum(water)],
            name='Production Breakdown',
            text=['Total Gas Produced (mcf)', 'Total Oil Produced (bbl)',
                'Total Water Produced (bbl)'],
            hoverinfo="text+value+percent",
            textinfo="label+percent+name",
            hole=0.5,
            marker=dict(
                colors=['#fac1b7', '#a9bb95', '#92d8d8']
            ),
            domain={"x": [0, .45], 'y':[0.2, 0.8]},
        ),
        dict(
            type='pie',
            labels=[WELL_TYPES[i] for i in aggregate.index],
            values=aggregate['API_WellNo'],
            name='Well Type Breakdown',
            hoverinfo="label+text+value+percent",
            textinfo="label+percent+name",
            hole=0.5,
            marker=dict(
                colors=[WELL_COLORS[i] for i in aggregate.index]
            ),
            domain={"x": [0.55, 1], 'y':[0.2, 0.8]},
        )
    ]
    layout_pie['title'] = 'Production Summary: {} to {}'.format(
        year_slider[0], year_slider[1])
    layout_pie['font'] = dict(color='#777777')
    layout_pie['legend'] = dict(
        font=dict(color='#CCCCCC', size='10'),
        orientation='h',
        bgcolor='rgba(0,0,0,0)'
    )

    figure = dict(data=data, layout=layout_pie)
    return figure


# Completed Wells/Year graph
@app.callback(Output('count_graph', 'figure'),
            [Input('well_statuses', 'value'),
            Input('well_types', 'value'),
            Input('year_slider', 'value')])
def make_count_figure(well_statuses, well_types, year_slider):

    layout_count = copy.deepcopy(layout)

    dff = filter_dataframe(df, well_statuses, well_types, [1960, 2017])
    g = dff[['API_WellNo', 'Date_Well_Completed']]
    g.index = g['Date_Well_Completed']
    g = g.resample('A').count()

    colors = []
    for i in range(1960, 2018):
        if i >= int(year_slider[0]) and i < int(year_slider[1]):
            colors.append('rgb(10, 134, 134)')
        else:
            colors.append('rgba(10, 134, 134,0.2)')

    data = [
        dict(
            type='scatter',
            mode='markers',
            x=g.index,
            y=g['API_WellNo'] / 2,
            name='All Wells',
            opacity=0,
            hoverinfo='skip'
        ),
        dict(
            type='bar',
            x=g.index,
            y=g['API_WellNo'],
            name='All Wells',
            marker=dict(
                color=colors
            ),
        ),
    ]

    layout_count['title'] = 'Completed Wells/Year'
    layout_count['dragmode'] = 'select'
    layout_count['showlegend'] = False
    layout_count['autosize'] = True

    figure = dict(data=data, layout=layout_count)
    return figure


# Main
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
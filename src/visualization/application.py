import os
import pathlib
import re
import plotly.express as px
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State
import cufflinks as cf
from src.models.predict_model import Predict
from src.models.averaging_model import AvgModel

# Initialize app

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)
server = app.server

# Load data

APP_PATH = str(pathlib.Path(__file__).parent.resolve())

# with open(os.path.join(
#             config("PYTHONPATH"),
#             "./data/raw/shapefile_toronto/Neighbourhood_Crime_Rates_Boundary_File_clean.json"), 
#         "r") as f:
#     counties = json.load(f)
# df = pd.read_csv(os.path.join(
#             config("PYTHONPATH"),
#             "./data/processed/crime_data.csv"))

with open("./viz_data/Neighbourhood_Crime_Rates_Boundary_File_clean.json", "r") as f:
    counties = json.load(f)
df = pd.read_csv("./viz_data/crime_data.csv")

YEARS = [2014, 2015, 2016, 2017, 2018, 2019]
CRIME_OPTIONS = [
    "Assault",
    "Robbery"
]
PREMISES = [
    "Outside"
]
DAYS_OF_WEEK = [
    "Monday", "Tuesday", "Wednesday", "Thursday", 
    "Friday", "Saturday", "Sunday"
]
HOURS_OF_DAY = list(range(25))

model = AvgModel()
predicter = Predict(df, model)
predicter.filter_df(
            premises=["Outdoor"], 
            crimes=["Assualt"], 
            max_year=2019, 
            min_year=2014, 
            min_hour=0,
            max_hour=24,
            days_of_week=DAYS_OF_WEEK
)
preds = predicter.predict_cases_per_sq_km_per_nbhd_per_hour()
assert preds.shape[0] == len(counties["features"])

# App layout

app.layout = html.Div(
    id="root",
    children=[
                html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("deloitte_logo_transparent_back.png"),
                            id="plotly-image",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "Crime Rates in Toronto",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "Estimating the number of crimes per hour occurring by neighbourhood", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
                html.Div(
                    [
                        html.A(
                            html.Button("Learn More", id="learn-more-button"),
                            href="https://plot.ly/dash/pricing/",
                        )
                    ],
                    className="one-third column",
                    id="button",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(
            id="app-container",
            children=[
                html.Div(
                    id="left-column",
                    children=[
                        html.Div(
                            id="slider-container",
                            children=[
                                html.P(
                                    id="slider-text",
                                    children="Drag the slider to change the year:",
                                ),
                                dcc.RangeSlider(
                                    id="years-slider",
                                    min=min(YEARS),
                                    max=max(YEARS),
                                    value=[min(YEARS), max(YEARS)],
                                    marks={
                                        str(year): {
                                            "label": str(year),
                                            "style": {"color": "#7fafdf"},
                                        }
                                        for year in YEARS
                                    },
                                ),
                            ],
                        ),
                        html.Div(
                            id="hour-of-day-slider-container",
                            children=[
                                html.P(
                                    id="hours-slider-text",
                                    children="Drag the slider to change the hour of day:",
                                ),
                                dcc.RangeSlider(
                                    id="hours-slider",
                                    min=min(HOURS_OF_DAY),
                                    max=max(HOURS_OF_DAY),
                                    value=[min(HOURS_OF_DAY), max(HOURS_OF_DAY)],
                                    marks={
                                        str(hour): {
                                            "label": str(hour),
                                            "style": {"color": "#7fafdf"},
                                        }
                                        for hour in HOURS_OF_DAY
                                    },
                                ),
                            ],
                        ),
                        html.Div(
                            id="day-of-week-slider-container",
                            children=[
                                html.P(
                                    id="day-slider-text",
                                    children="Drag the slider to change the day of week:",
                                ),
                                dcc.RangeSlider(
                                    id="day-slider",
                                    min=0,
                                    max=len(DAYS_OF_WEEK)-1,
                                    value=[0, len(DAYS_OF_WEEK)],
                                    marks={
                                        i : {
                                            "label": DAYS_OF_WEEK[i],
                                            "style": {"color": "#7fafdf"},
                                        }
                                        for i in range(len(DAYS_OF_WEEK))
                                    },
                                ),
                            ],
                        ),
                        html.Div(
                            id="heatmap-container",
                            children=[
                                html.P(
                                    f"Heatmap of estimated probability of {CRIME_OPTIONS[0]}\
                            occuring in a given square foot of each neihbourhood in year {min(YEARS)}",
                                    id="heatmap-title",
                                ),
                                dcc.Graph(
                                    id="county-choropleth",
                                    figure=(
                                        px.choropleth(preds, 
                                            geojson=counties, 
                                            color="expected_crimes_per_hour_per_sq_km",
                                            locations="nbhd_id", 
                                            featureidkey="properties.clean_nbdh_id",
                                            hover_data=["neighbourhood"],
                                            color_continuous_scale="Viridis",
                                            scope="north america",
                                        )
                                        .update_geos(showcountries=False, showcoastlines=False, showland=False, showlakes=False, fitbounds="locations")
                                        .update_layout(margin={"r":0,"t":0,"l":0,"b":0})
                                    )
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)


@app.callback(
    Output("county-choropleth", "figure"),
    [
        Input("years-slider", "value"), 
        Input("hours-slider", "value"),
        Input("day-slider", "value")
    ],
    [State("county-choropleth", "figure")],
)
def display_map(years, hours, days, figure):
    model = AvgModel()
    predicter = Predict(df, model)
    predicter.filter_df(
                premises=["Outdoor"],
                crimes=["Assualt"], 
                max_year=years[1], 
                min_year=years[0], 
                min_hour=hours[0],
                max_hour=hours[1],
                days_of_week=DAYS_OF_WEEK[days[0]:days[1]]
    )
    preds = predicter.predict_cases_per_sq_km_per_nbhd_per_hour()
    assert preds.shape[0] == len(counties["features"])
    fig=(
        px.choropleth(preds, 
            geojson=counties, 
            color="expected_crimes_per_hour_per_sq_km",
            locations="nbhd_id", 
            featureidkey="properties.clean_nbdh_id",
            hover_data=["neighbourhood"],
            color_continuous_scale="Viridis",
            scope="north america",
        )
        .update_geos(showcountries=False, showcoastlines=False, showland=False, showlakes=False, fitbounds="locations")
        .update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    )
    return fig


@app.callback(
    Output("heatmap-title", "children"), 
    [
        Input("years-slider", "value"), 
        # Input("crime-dropdown", "value")
    ])
def update_map_title(year):#, crime):
    # TODO: get the crime droppddown
    crime="Assaualt"
    return f"Heatmap of estimated number of {crime}s per hour\
            occuring in a given square km of each neihbourhood"


if __name__ == "__main__":
    app.run_server(debug=True, port=8052)
    # app.run_server()

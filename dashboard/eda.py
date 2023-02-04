'''
Import libraries
'''
from flask import Flask, request, render_template, redirect, url_for, jsonify
import pandas as pd
import numpy as np
import plotly.express as px
from urllib.request import urlopen
import json

'''
Function: Get counties geoJSON for plotly express
Parameters: None
Returns: dictionary for counties geoJSON
'''
def get_counties_geojson():
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties_geojson = json.load(response)
        return counties_geojson

'''
Function: Get county-state dictionary
Parameters: mbd dataframe
Returns: county-state dictionary
'''
def get_county_state_dict(df):
    unique_state_county = df.groupby(['county', 'state']).size().reset_index()
    counties = list(unique_state_county['county'])
    states = list(unique_state_county['state'])
    state_county_dict = {}
    for i in range(len(states)):
        if(states[i] not in state_county_dict.keys()):
            state_county_dict[states[i]] = []
        state_county_dict[states[i]].append(counties[i])
    state_county_dict['All states'] = ['All counties']
    return state_county_dict

'''
Function: Get states and counties lists
Parameters: mbd dataframe
Returns: county-state lists
'''
def get_state_county_lists(df):
    state_county_dict = get_county_state_dict(df)
    states = list(state_county_dict.keys())
    states = sorted(states)
    states[2] = 'Alaska'
    states[1] = 'Alabama'
    states[0] = 'All States'
    default_counties = ['All counties']
    return states, default_counties

'''
Function: Get years and months lists
Parameters: mbd dataframe
Returns: years-months lists
'''
def get_years_months_lists(df):
    months_df = df.drop_duplicates(subset=['first_day_of_month'])
    months_list = list(months_df['first_day_of_month'])
    months = [months_list[i] for i in range(len(months_list)-1, 0, -1)]

    years = ['2021', '2020', '2019', '2018', '2017']

    return months, years

'''
Get metrics for landing page
Parameters: mbd dataframe
Returns: metrics
'''
def get_landing_page_metrics(df):
    num_states = df.state.unique().size - 1
    num_counties = df.county.unique().size
    country_level_microbusiness = df.groupby(["first_day_of_month"]).active.sum().reset_index() 
    num_active_microbusinesses = list(country_level_microbusiness['active'])[-1]
    return num_states, num_counties, num_active_microbusinesses

'''
Create default microbusiness density line plot for landing page
Parameters: mbd dataframe
Returns: plotly line plot 
'''
def get_default_mbd_plot(df):
    country_level_microbusiness = df.groupby(["first_day_of_month"]).active.sum().reset_index()
    plot_1 = px.line(country_level_microbusiness, x = "first_day_of_month", y = "active", 
                    labels={
                                    "first_day_of_month": "Month",
                                    "active": "Active Microbusinesses"
                                },
                    title='Change in number of microbusiness across USA'
                )
    return plot_1

'''
Create default microbusiness density choropleth for landing page
Parameters: mbd dataframe
Returns: plotly choropleth plot 
'''
def get_mbd_choropleth(df):

    counties_geojson = get_counties_geojson()

    density_df = df.drop_duplicates(subset=['state', 'county'], keep = 'last')
    months_df = df.drop_duplicates(subset=['first_day_of_month'])
    months_list = list(months_df['first_day_of_month'])
    months = [months_list[i] for i in range(len(months_list)-1, 0, -1)]

    plot_2 = px.choropleth(density_df, geojson = counties_geojson, locations='cfips', color='microbusiness_density',
                           color_continuous_scale="Viridis",
                           range_color=(0, 12),
                           scope="usa",
                           hover_name='county',
                           labels={'microbusiness_density':'Microbusiness Density'},
                           title='Microbusiness Density across the USA'
                          )
    plot_2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return plot_2

'''
Create default broadband pct choropleth for landing page
Parameters: mbd dataframe, census dataframe
Returns: plotly choropleth plot 
'''
def get_pct_broadband_plot(df, census_df):

    counties_geojson = get_counties_geojson()

    braodband_df = census_df[['pct_bb_2021', 'cfips']]
    braodband_df = pd.merge(braodband_df, df, how="inner", on=["cfips"])
    braodband_df = braodband_df.drop_duplicates('cfips')
    broadband_plot = px.choropleth(braodband_df, geojson = counties_geojson, locations='cfips', color='pct_bb_2021',
                           color_continuous_scale="Viridis",
                           scope="usa",
                           hover_name='county',
                           labels={'pct_bb_2021':'% Broadband'},
                           title='Percentage of households with access to broadband across the USA'
                          )

    return broadband_plot

'''
Create default college pct choropleth for landing page
Parameters: mbd dataframe, census dataframe
Returns: plotly choropleth plot 
'''
def get_pct_college_plot(df, census_df):

    counties_geojson = get_counties_geojson()

    college_df = census_df[['pct_college_2021', 'cfips']]
    college_df = pd.merge(college_df, df, how="inner", on=["cfips"])
    college_df = college_df.drop_duplicates('cfips')
    college_plot = px.choropleth(college_df, geojson = counties_geojson, locations='cfips', color='pct_college_2021',
                           color_continuous_scale="Viridis",
                           scope="usa",
                           hover_name='county',
                           labels={'pct_college_2021':'% College'},
                           title='Percentage of population over the age of 25 with a college degree'
                          )

    return college_plot

'''
Create default workforce pct choropleth for landing page
Parameters: mbd dataframe, census dataframe
Returns: plotly choropleth plot 
'''
def get_pct_workforce_plot(df, census_df):

    counties_geojson = get_counties_geojson()

    workforce_df = census_df[['pct_it_workers_2021', 'cfips']]
    workforce_df = pd.merge(workforce_df, df, how="inner", on=["cfips"])
    workforce_df = workforce_df.drop_duplicates('cfips')
    workforce_plot = px.choropleth(workforce_df, geojson = counties_geojson, locations='cfips', color='pct_it_workers_2021',
                           color_continuous_scale="Viridis",
                           scope="usa",
                           hover_name='county',
                           labels={'pct_it_workers_2021':'% Workforce'},
                           title='The percentage of workforce in IT industry across the USA'
                          )

    return workforce_plot

'''
Create default houhehold median income choropleth for landing page
Parameters: mbd dataframe, census dataframe
Returns: plotly choropleth plot 
'''
def get_hh_median_income_plot(df, census_df):

    counties_geojson = get_counties_geojson()

    hh_income_df = census_df[['median_hh_inc_2021', 'cfips']]
    hh_income_df = pd.merge(hh_income_df, df, how="inner", on=["cfips"])
    hh_income_df = hh_income_df.drop_duplicates('cfips')
    hh_income_plot = px.choropleth(hh_income_df, geojson = counties_geojson, locations='cfips', color='median_hh_inc_2021',
                           color_continuous_scale="Viridis",
                           scope="usa",
                           hover_name='county',
                           labels={'median_hh_inc_2021':'HH income'},
                           title='Median household income across the USA'
                          )

    return hh_income_plot

'''
Update mbd county list upon user input
Parameters: selected_state, selected_month, mbd dtaframe and census dataframe
Returns: plotly line plot and counties list for selected atate
'''
def get_updated_county_list(selected_state, df, census_df):
    counties_geojson = get_counties_geojson()

    # Get values for the counties dropdown
    state_county_dict = get_county_state_dict(df)
    counties_list = sorted(state_county_dict[selected_state])
    counties_list.insert(0, 'All counties')

    # Get data at state level
    state_plot_data = df.groupby(["state", "first_day_of_month"]).active.sum().reset_index() 
    state_plot_data = state_plot_data.loc[state_plot_data['state'] == selected_state]

    # Get metrics for 'Change in number of microbusinesses' part of the dashboard at State level
    fig = px.line(state_plot_data, x = "first_day_of_month", y = "active", 
                    labels={
                                    "first_day_of_month": "Month",
                                    "active": "Active Microbusinesses"
                                },
                    title='Change in number of microbusiness across ' + selected_state
                )

    return fig, counties_list

'''
Update mbd line plot upon user input
Parameters: selected_state, selected_month, mbd dtaframe and census dataframe
Returns: plotly line plot 
'''
def get_updated_mbd_line_plot(selected_state, selected_county, df, census_df):
    counties_geojson = get_counties_geojson()

    state_plot_data = df.groupby(["state", "county", "first_day_of_month"]).active.sum().reset_index() 
    state_plot_data = state_plot_data.loc[state_plot_data['state'] == selected_state]
    county_plot_data = state_plot_data.loc[state_plot_data['county'] == selected_county]

    if(selected_county == 'All counties'):
        plot_data = state_plot_data.groupby(["state", "first_day_of_month"]).active.sum().reset_index() 
    else:
        plot_data = county_plot_data

    print(plot_data)

    # Get metrics for 'Change in number of microbusinesses' part of the dashboard at State level
    fig = px.line(plot_data, x = "first_day_of_month", y = "active", 
                    labels={
                                    "first_day_of_month": "Month",
                                    "active": "Active Microbusinesses"
                                },
                    title='Change in number of microbusiness across ' + selected_county + '(' + selected_state + ')'
                )

    return fig

'''
Update mbd choropleths upon user input
Parameters: selected_state, selected_month, mbd dtaframe and census dataframe
Returns: plotly choropleth plot 
'''
def get_updated_mbd_choropleth(selected_state, selected_month, df, census_df):
    counties_geojson = get_counties_geojson()

    if(selected_state == 'All States'):
        density_df = df.loc[df['first_day_of_month'] == selected_month]
    else:
        density_df = df.loc[df['first_day_of_month'] == selected_month]
        density_df = density_df.loc[df['state'] == selected_state]
    # print(density_df)

    # Get target state and respective county geojson
    target_state = [list(density_df['cfips'])[0][:2]]    
    print(target_state)
    counties_geojson_state = counties_geojson.copy()
    counties_geojson_state['features'] = [f for f in counties_geojson['features'] if f['properties']['STATE'] in target_state]

    # Get plot
    fig = px.choropleth(density_df, geojson = counties_geojson, locations='cfips', color='microbusiness_density',
                           color_continuous_scale="Viridis",
                           range_color=(0, 12),
                           scope="usa",
                           hover_name='county',
                           labels={'unemp':'Microbusiness Density'},
                           title='Microbusiness Density across ' + selected_state + ' on ' + selected_month
                          )
    # fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return fig

'''
Update metrics choropleths upon user input
Parameters: selected_state, selected_year, mbd dtaframe and census dataframe
Returns: plotly choropleth plot 
'''
def get_updated_metrics_choropleths(selected_state, selected_year, df, census_df):
    counties_geojson = get_counties_geojson()

    # Get data at country level

    broadband_column = 'pct_bb_' + selected_year
    college_column = 'pct_college_' + selected_year
    workforce_column = 'pct_it_workers_' + selected_year
    hh_income_column = 'median_hh_inc_' + selected_year

    broadband_df = census_df[[broadband_column, 'cfips']]
    broadband_df = pd.merge(broadband_df, df, how="inner", on=["cfips"])
    broadband_df = broadband_df.drop_duplicates('cfips')
    if(selected_state != 'All States'):
        broadband_df = broadband_df.loc[broadband_df['state'] == selected_state]

    college_df = census_df[[college_column, 'cfips']]
    college_df = pd.merge(college_df, df, how="inner", on=["cfips"])
    college_df = college_df.drop_duplicates('cfips')
    if(selected_state != 'All States'):
        college_df = college_df.loc[college_df['state'] == selected_state]

    workforce_df = census_df[[workforce_column, 'cfips']]
    workforce_df = pd.merge(workforce_df, df, how="inner", on=["cfips"])
    workforce_df = workforce_df.drop_duplicates('cfips')
    if(selected_state != 'All States'):
        workforce_df = workforce_df.loc[workforce_df['state'] == selected_state]

    hh_income_df = census_df[[hh_income_column, 'cfips']]
    hh_income_df = pd.merge(hh_income_df, df, how="inner", on=["cfips"])
    hh_income_df = hh_income_df.drop_duplicates('cfips')
    if(selected_state != 'All States'):
        hh_income_df = hh_income_df.loc[hh_income_df['state'] == selected_state]

    # Broadband pct
    broadband_plot = px.choropleth(broadband_df, geojson = counties_geojson, locations='cfips', color=broadband_column,
                           color_continuous_scale="Viridis",
                           scope="usa",
                           hover_name='county',
                           labels={broadband_column:'% Broadband'},
                           title='Percentage of households with access to broadband across ' + selected_state
                          )
    # broadband_plot.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    # College pct
    college_plot = px.choropleth(college_df, geojson = counties_geojson, locations='cfips', color=college_column,
                           color_continuous_scale="Viridis",
                           scope="usa",
                           hover_name='county',
                           labels={college_column:'% College'},
                           title='Percentage of population over the age of 25 with a college degree across ' + selected_state
                          )
    # college_plot.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    # Workforce pct
    workforce_plot = px.choropleth(workforce_df, geojson = counties_geojson, locations='cfips', color=workforce_column,
                           color_continuous_scale="Viridis",
                           scope="usa",
                           hover_name='county',
                           labels={workforce_column:'% Workforce'},
                           title='The percentage of workforce in IT industry across ' + selected_state
                          )
    # workforce_plot.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    # Median Income
    hh_income_plot = px.choropleth(hh_income_df, geojson = counties_geojson, locations='cfips', color=hh_income_column,
                           color_continuous_scale="Viridis",
                           scope="usa",
                           hover_name='county',
                           labels={hh_income_column:'HH income'},
                           title='Median household income across ' + selected_year
                          )
    # hh_income_plot.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return broadband_plot, college_plot, workforce_plot, hh_income_plot

'''
Get statistics line plots for landing page
Parameters: mbd dtaframe and census dataframe
Returns: plotly line plots
'''
def get_statistics_line_plots(df, census_df):

    master_df = pd.merge(census_df, df, how="inner", on=["cfips"])
    master_df = master_df.drop_duplicates('cfips')

    years = ['2017', '2018', '2019', '2020', '2021']

    broadband_df = master_df.filter(regex='pct_bb')
    # workforce_df = master_df.filter(regex='pct_it')
    # college_df = master_df.filter(regex='pct_college')
    # hh_income_df = master_df.filter(regex='median_hh')

    broadband_stats = broadband_df.describe()
    # workforce_stats = workforce_df.describe()
    # college_stats = college_df.describe()
    # hh_income_stats = hh_income_df.describe()

    broadband_means = [i for i in broadband_stats.loc['mean']]
    # workforce_means = [i for i in workforce_stats.loc['mean']]
    # college_means = [i for i in college_stats.loc['mean']]
    # hh_income_means = [i for i in hh_income_stats.loc['mean']]

    broadband_plot = px.line(x = years, y = broadband_means, 
                    title='Change in pct of <br> broadband connection <br> across the USA'
                )
    broadband_plot.update_layout(xaxis_title = 'Year', yaxis_title = 'Pct of houses with broadband connection')

    # workforce_plot = px.line(x = years, y = workforce_means, 
    #                 title='Change in pct of <br> IT workforce <br> across the USA'
    #             )
    # workforce_plot.update_layout(xaxis_title = 'Year', yaxis_title = 'Pct of IT workforce')

    # college_plot = px.line(x = years, y = college_means, 
    #                 title='Change in pct of <br> people with college degree <br> across the USA'
    #             )
    # college_plot.update_layout(xaxis_title = 'Year', yaxis_title = 'Pct of people with college degree')

    # hh_income_plot = px.line(x = years, y = hh_income_means, 
    #                 title='Change in <br> median household income <br> across the USA'
    #             )
    # hh_income_plot.update_layout(xaxis_title = 'Year', yaxis_title = 'Median household income')

    # return broadband_plot, workforce_plot, college_plot, hh_income_plot
    return broadband_plot

def get_updated_stats_county_list(selected_state, selected_type, df, census_df):
    counties_geojson = get_counties_geojson()

    # Get values for the counties dropdown
    state_county_dict = get_county_state_dict(df)
    counties_list = sorted(state_county_dict[selected_state])
    counties_list.insert(0, 'All counties')

    master_df = pd.merge(census_df, df, how="inner", on=["cfips"])
    master_df = master_df.drop_duplicates('cfips')
    master_df = master_df[master_df['state'] == selected_state]

    years = ['2017', '2018', '2019', '2020', '2021']

    broadband_df = master_df.filter(regex='pct_bb')
    workforce_df = master_df.filter(regex='pct_it')
    college_df = master_df.filter(regex='pct_college')
    hh_income_df = master_df.filter(regex='median_hh')

    broadband_stats = broadband_df.describe()
    workforce_stats = workforce_df.describe()
    college_stats = college_df.describe()
    hh_income_stats = hh_income_df.describe()

    broadband_means = [i for i in broadband_stats.loc['mean']]
    workforce_means = [i for i in workforce_stats.loc['mean']]
    college_means = [i for i in college_stats.loc['mean']]
    hh_income_means = [i for i in hh_income_stats.loc['mean']]

    broadband_plot = px.line(x = years, y = broadband_means, 
                    title='Change in pct of <br> broadband connection <br> across ' + selected_state
                )
    broadband_plot.update_layout(xaxis_title = 'Year', yaxis_title = 'Pct of houses with broadband connection')

    workforce_plot = px.line(x = years, y = workforce_means, 
                    title='Change in pct of <br> IT workforce <br> across ' + selected_state
                )
    workforce_plot.update_layout(xaxis_title = 'Year', yaxis_title = 'Pct of IT workforce')

    college_plot = px.line(x = years, y = college_means, 
                    title='Change in pct of <br> people with college degree <br> across ' + selected_state
                )
    college_plot.update_layout(xaxis_title = 'Year', yaxis_title = 'Pct of people with college degree')

    hh_income_plot = px.line(x = years, y = hh_income_means, 
                    title='Change in <br> median household income <br> across ' + selected_state
                )
    hh_income_plot.update_layout(xaxis_title = 'Year', yaxis_title = 'Median household income')

    if('band' in selected_type):
        return broadband_plot, counties_list
    elif('income' in selected_type):
        return hh_income_plot, counties_list
    elif('college' in selected_type):
        return college_plot, counties_list
    else:
        return workforce_plot, counties_list

'''
Update mbd line plot upon user input
Parameters: selected_state, selected_month, mbd dtaframe and census dataframe
Returns: plotly line plot 
'''
def get_updated_stats_line_plot(selected_state, selected_county, selected_type, df, census_df):
    counties_geojson = get_counties_geojson()

    # Get values for the counties dropdown
    state_county_dict = get_county_state_dict(df)
    counties_list = sorted(state_county_dict[selected_state])
    counties_list.insert(0, 'All counties')

    master_df = pd.merge(census_df, df, how="inner", on=["cfips"])
    master_df = master_df.drop_duplicates('cfips')
    master_df = master_df[master_df['state'] == selected_state]
    if(selected_county != 'All counties'):
        master_df = master_df[master_df['county'] == selected_county]

    years = ['2017', '2018', '2019', '2020', '2021']

    broadband_df = master_df.filter(regex='pct_bb')
    workforce_df = master_df.filter(regex='pct_it')
    college_df = master_df.filter(regex='pct_college')
    hh_income_df = master_df.filter(regex='median_hh')

    broadband_stats = broadband_df.describe()
    workforce_stats = workforce_df.describe()
    college_stats = college_df.describe()
    hh_income_stats = hh_income_df.describe()

    broadband_means = [i for i in broadband_stats.loc['mean']]
    workforce_means = [i for i in workforce_stats.loc['mean']]
    college_means = [i for i in college_stats.loc['mean']]
    hh_income_means = [i for i in hh_income_stats.loc['mean']]

    broadband_plot = px.line(x = years, y = broadband_means, 
                    title='Change in pct of <br> broadband connection <br> across ' + selected_county + '(' + selected_state + ')'
                )
    broadband_plot.update_layout(xaxis_title = 'Year', yaxis_title = 'Pct of houses with broadband connection')

    workforce_plot = px.line(x = years, y = workforce_means, 
                    title='Change in pct of <br> IT workforce <br> across ' + selected_county + '(' + selected_state + ')'
                )
    workforce_plot.update_layout(xaxis_title = 'Year', yaxis_title = 'Pct of IT workforce')

    college_plot = px.line(x = years, y = college_means, 
                    title='Change in pct of <br> people with college degree <br> across ' + selected_county + '(' + selected_state + ')'
                )
    college_plot.update_layout(xaxis_title = 'Year', yaxis_title = 'Pct of people with college degree')

    hh_income_plot = px.line(x = years, y = hh_income_means, 
                    title='Change in <br> median household income <br> across ' + selected_county + '(' + selected_state + ')'
                )
    hh_income_plot.update_layout(xaxis_title = 'Year', yaxis_title = 'Median household income')

    if('band' in selected_type):
        return broadband_plot
    elif('income' in selected_type):
        return hh_income_plot
    elif('college' in selected_type):
        return college_plot
    else:
        return workforce_plot

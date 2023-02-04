'''
Import libraries
'''
from flask import Flask, request, render_template, redirect, url_for, jsonify
import pandas as pd
import numpy as np
import plotly.express as px
from urllib.request import urlopen
import json
import eda

'''
Initialize Flask Application
'''
app = Flask(__name__)

'''
Function: Read mbd and census data
Parameters: None
Returns: mbd dataframe, census dataframe
'''
def read_data():
    df = pd.read_csv('data/train.csv')
    df['cfips'] = df['cfips'].apply(lambda x: '{0:0>5}'.format(x))

    census_df = pd.read_csv('data/census_starter.csv')
    census_df['cfips'] = census_df['cfips'].apply(lambda x: '{0:0>5}'.format(x))

    return df, census_df

'''
Index page
'''
@app.route('/', methods=['GET', 'POST'])
def index():

    # Read data into a dataframe
    df, census_df = read_data()
    state_county_dict = eda.get_county_state_dict(df)

    # Get metrics for dashboard
    num_states, num_counties, num_active_microbusinesses = eda.get_landing_page_metrics(df)

    # Get list of states and counties
    states, default_counties = eda.get_state_county_lists(df)

    # Get plot for 'Change in number of microbusinesses' part of the dashboard
    plot_1 = eda.get_default_mbd_plot(df)

    # Plot 2 - MBD Choropeth map
    plot_2 = eda.get_mbd_choropleth(df)

    # Get lists of months and years
    months, years = eda.get_years_months_lists(df)

    # Broadband pct plot
    broadband_plot = eda.get_pct_broadband_plot(df, census_df)

    # College pct plot
    college_plot = eda.get_pct_college_plot(df, census_df)

    # Workforce pct plot
    workforce_plot = eda.get_pct_workforce_plot(df, census_df)

    # Median Income plot
    hh_income_plot = eda.get_hh_median_income_plot(df, census_df)

    broadband_line_plot = eda.get_statistics_line_plots(df, census_df)
    stats_types = ['Pct broadband', 'Pct college degree', 'Pct IT workforce', 'Median household income']

    return render_template('index.html', num_states = num_states, num_counties = num_counties,
    num_microbusinesses = num_active_microbusinesses, default_plot=plot_1.to_html(full_html=False),
    states = states, default_counties = default_counties, state_county_dict = state_county_dict,
    density_plot=plot_2.to_html(full_html=False), months = months, years = years,
    broadband_plot = broadband_plot.to_html(full_html=False),
    college_plot = college_plot.to_html(full_html=False),
    workforce_plot = workforce_plot.to_html(full_html=False),
    hh_income_plot = hh_income_plot.to_html(full_html=False),
    broadband_line_plot = broadband_line_plot.to_html(full_html=False),
    # college_line_plot = college_line_plot.to_html(full_html=False),
    # workforce_line_plot = workforce_line_plot.to_html(full_html=False),
    # hh_income_line_plot = hh_income_line_plot.to_html(full_html=False),
    stats_types = stats_types
    )

'''
Update county dropdown and plot for MBD line plot
'''
@app.route('/update_county_dropdown')
def update_county_dropdown():

    # The value of the first dropdown (selected by the user)
    selected_state = request.args.get('selected_state', type=str)

    df, census_df = read_data()

    fig, counties_list = eda.get_updated_county_list(selected_state, df, census_df)

    # Create the value sin the dropdown as a html string
    html_string_selected = ''
    for entry in counties_list:
        html_string_selected += '<option value="{}">{}</option>'.format(entry, entry)

    return jsonify(html_string_selected = html_string_selected, state_plot = fig.to_html(full_html=False))

'''
Update plot for MBD line plot
'''
@app.route('/update_plot')
def update_plot():

    # The value of the first dropdown (selected by the user)
    selected_state = request.args.get('selected_state', type=str)

    # The value of the second dropdown (selected by the user)
    selected_county = request.args.get('selected_county', type=str)

    df, census_df = read_data()
    
    fig = eda.get_updated_mbd_line_plot(selected_state, selected_county, df, census_df)

    return jsonify(county_plot = fig.to_html(full_html=False))

'''
Update MBD choropleth
'''
@app.route('/update_density_plot')
def update_density_plot():

    # The value of the state dropdown (selected by the user)
    selected_state = request.args.get('selected_state', type=str)

    # The value of the month dropdown (selected by the user)
    selected_month = request.args.get('selected_month', type=str)

    df, census_df = read_data()    
    fig = eda.get_updated_mbd_choropleth(selected_state, selected_month, df, census_df)

    return jsonify(density_plot = fig.to_html(full_html=False))

'''
Update other metrics choropleth
'''
@app.route('/update_metrics_plots')
def update_metrics_plots():

    # The value of the state dropdown (selected by the user)
    selected_state = request.args.get('selected_state', type=str)

    # The value of the month dropdown (selected by the user)
    selected_year = request.args.get('selected_year', type=str)

    df, census_df = read_data()
    broadband_plot, college_plot, workforce_plot, hh_income_plot = eda.get_updated_metrics_choropleths(selected_state, selected_year, df, census_df)
    
    return jsonify(broadband_plot = broadband_plot.to_html(full_html=False),
    college_plot = college_plot.to_html(full_html=False),
    workforce_plot = workforce_plot.to_html(full_html=False),
    income_plot = hh_income_plot.to_html(full_html=False))

'''
Update county dropdown and plot for stats line plots
'''
@app.route('/update_stats_county_dropdown')
def update_stats_county_dropdown():

    # The value of the first dropdown (selected by the user)
    selected_state = request.args.get('selected_state', type=str)

    # The value of the third dropdown (selected by the user)
    selected_type = request.args.get('selected_type', type=str)

    df, census_df = read_data()

    fig, counties_list = eda.get_updated_stats_county_list(selected_state, selected_type, df, census_df)

    # Create the value sin the dropdown as a html string
    html_string_selected = ''
    for entry in counties_list:
        html_string_selected += '<option value="{}">{}</option>'.format(entry, entry)

    return jsonify(html_string_selected = html_string_selected, 
    plot = fig.to_html(full_html=False))

'''
Update plots for stats line plots
'''
@app.route('/update_stats_plot')
def update_stats_plot():

    # The value of the first dropdown (selected by the user)
    selected_state = request.args.get('selected_state', type=str)

    # The value of the second dropdown (selected by the user)
    selected_county = request.args.get('selected_county', type=str)

    # The value of the third dropdown (selected by the user)
    selected_type = request.args.get('selected_type', type=str)

    df, census_df = read_data()
    
    fig= eda.get_updated_stats_line_plot(selected_state, selected_county, selected_type, df, census_df)

    return jsonify(plot = fig.to_html(full_html=False))

'''
Update plots for stats line plots
'''
@app.route('/update_stats_plot_type')
def update_stats_plot_type():

    # The value of the first dropdown (selected by the user)
    selected_state = request.args.get('selected_state', type=str)

    # The value of the second dropdown (selected by the user)
    selected_county = request.args.get('selected_county', type=str)

    # The value of the third dropdown (selected by the user)
    selected_type = request.args.get('selected_type', type=str)

    df, census_df = read_data()
    
    fig = eda.get_updated_stats_line_plot(selected_state, selected_county, selected_type, df, census_df)

    return jsonify(plot = fig.to_html(full_html=False))

if __name__ == '__main__':
    app.run(debug = True)
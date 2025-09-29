# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                html.Br(),
                                dcc.Dropdown(id='site-dropdown', options=[
                                    {'label' : ls, 'value' : ls} for ls in spacex_df['Launch Site'].unique()
                                ] + [
                                    {'label' : 'All Sites', 'value' : 'All Sites'}
                                ], value='All Sites', placeholder='Select a Launch Site', searchable=True),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider', min=0, max=10_000, step=1_000, value=(min_payload, max_payload)),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value'),
)
def update_pie(launch_site):
    if launch_site != 'All Sites':
        df_filtered = spacex_df[spacex_df['Launch Site'] == launch_site]
        df_filtered = df_filtered['class'].value_counts().reset_index()
        index_to_name = {1 : 'Success', 0 : 'Failure'}
        # df_filtered = df_filtered.sort_values(by='class', ascending=True, ignore_index=True)
        values = df_filtered['count']
        names = df_filtered['class'].map(lambda x : index_to_name[x])
        title = f"Launch Success for {launch_site}"
    else:
        df_grouped = spacex_df.groupby('Launch Site', as_index = False)['class'].sum()
        values = df_grouped['class']
        names = df_grouped['Launch Site']
        title = f"Total Launch Success by Site"
    
    figure = px.pie(
        values=values,
        names=names,
        title=title,  
    )
    return figure

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('site-dropdown', 'value'),
        Input('payload-slider', 'value')
    ]
)
def update_scatter(launch_site, payload):
    df_filtered = spacex_df
    if launch_site != 'All Sites':
        df_filtered = df_filtered[(df_filtered['Launch Site'] == launch_site) & df_filtered['Payload Mass (kg)'].between(*payload)]
        title=f'Launch Outcome vs. Payload Mass for {launch_site}'
    else:
        title='Launch Outcome vs. Payload Mass per Booster Version'
    
    x=df_filtered['Payload Mass (kg)']
    y=df_filtered['class']
    color=df_filtered['Booster Version Category']
    
    figure = px.scatter(
        x=x,
        y=y,
        color=color,
        title=title
    )
    figure.update_layout(
        xaxis_title='Payload Mass (kg)',
        yaxis_title='Outcome',
        legend_title_text='Booster Version',
        xaxis_range=[-100, 10_000],
        yaxis_range=[-0.1,1.1],
    )
    figure.update_yaxes(
        tickvals=[0,1],
        ticktext=['Failure', 'Success']
    )
    return figure

# Run the app
if __name__ == '__main__':
    app.run()

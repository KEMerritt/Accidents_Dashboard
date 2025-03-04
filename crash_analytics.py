import pandas as pd
from dash import Dash, dcc, html
import os
import kaggle
import subprocess
from kaggle.api.kaggle_api_extended import KaggleApi
import plotly.express as px
from dash.dependencies import Input, Output
import matplotlib.pyplot as plt
import matplotlib
import plotly.graph_objects as go



df = pd.read_csv("US_Accidents_March23.csv", usecols=["State", "Severity", "Start_Time", "Temperature(F)"])
df['Temperature'] = df['Temperature(F)']
df[['Year', 'Month', 'Day']] = df['Start_Time'].str.split('-', expand=True)

app = Dash(__name__)
app.layout = html.Div([
	
	html.H1("US Accidents Dashboard", style = {"textAlight": "center"}),
	dcc.Dropdown(
		id = "state-dropdown",
		options = [{"label":state, "value": state} for state in df["State"].unique()],
		value = ["FL"],
		multi = True,
		style = {"width":"50%"}
	),
	dcc.Dropdown(
		id = 'year-dropdown',
		options =[{'label':year, 'value': year} for year in df['Year'].unique()],
		value = [2020,2021],
		multi = True,
		style = {"width":"50%"}
	),
	dcc.Dropdown(
		id = 'month-slider',
		options = [{'label':month, 'value':month} for month in df['Month'].unique()],
	
		value = ["11","12"],
		multi = True,
		style = {"width":"50%"}
		
	),
	dcc.RangeSlider(
		id = 'temperature-range-slider',
		min = df['Temperature'].min(),
		max = df['Temperature'].max(),
		step = 1,
		marks = {i: f"{i}°F" for i in range(-50,100, 15)},
		value = [int(df['Temperature'].min()), int(df['Temperature'].max())]
		),
	html.Div([
		dcc.Graph(id = 'accident-temperature-plot'),
		dcc.Graph(id = 'accident-heatmap-chart'),
		], style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '10px'}),
	html.Div([
		dcc.Graph(id = "severity-chart"),
		#]),
	#html.Div([
		dcc.Graph(id = "monthly-trend"),
		],style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '10px'})

	])
@app.callback(
	Output("severity-chart","figure"),
	Input("state-dropdown","value")
	)
def update_severity_chart(selected_states):
    #print(f"State Selected:{selected_state}")

    #filtered_df = df[df["State"] == selected_state]
    filtered_df = df[df['State'].isin(selected_states)]
    #filtered_df = filtered_df.sample(n=10000, random_state=42)
    #filtered_df["Severity"] = pd.to_numeric(filtered_df["Severity"], errors='coerce')
    #filtered_df["Severity"] = pd.to_numeric(filtered_df["Severity"], errors ='coerce')

    #filtered_df["Severity"] = pd.to_numeric(filtered_df["Severity"], errors = 'coerce')

    #print(filtered_df["Severity"].dtypes)

    if filtered_df.empty:
        return go.Figure()

    fig = go.Figure()

    # fig.add_trace(go.Histogram(x=filtered_df["Severity"], name = "Severity"))
    # fig.update_layout(
    #     title = f"Accident Severity Distribution in {selected_state}",
    #     xaxis = dict(title="Severity"),
    #     yaxis = dict(title = "Count"),
    #     showlegend = True)

    for year in sorted(filtered_df["Year"].unique()):
        year_data = filtered_df[filtered_df["Year"] == year]
        #print(f"Year:{year}, Severity values: {year_data.unique()}")
        #print(f"Year:{year}, Number of data points: {len(year_data)}")
        severe = year_data["Severity"].tolist()
        fig.add_trace(go.Histogram(
            x=severe,
            name=str(year),
            opacity=0.75, 
            xbins=dict(start=1, end=5, size=1)
        ))

    fig.update_layout(
        title=f"Accident Severity Distribution in {selected_states}",
        xaxis=dict(title="Severity"),
        yaxis=dict(title="Count"),
        barmode="stack",
        showlegend=True
    )
    # fig.add_trace(go.Histogram(

    # 	x = [1,2,2,3,3,3,3,4,4,4],
    # 	opacity = 0.75,
    # 	xbins = dict(start = 1, end =5, size =1)
    # ))
    #fig.show()
    
    
    #fig = px.histogram(filtered_df, x="Severity", title=f"Accident Severity Distribution in {selected_state}")
    return fig


@app.callback(
    Output("monthly-trend", "figure"),
    Input("state-dropdown", "value")
)
def update_monthly_trend(selected_states):
    #filtered_df = df[df["State"] == selected_state]
    filtered_df = df[df['State'].isin(selected_states)]
    

    #monthly_data = filtered_df.groupby("Month").size().reset_index(name="Accidents")
    #monthly_data = filtered_df.groupby("Month").size().reset_index(name="Accidents")
    monthly_data = filtered_df.groupby(['Year', 'Month']).size().reset_index(name="Accidents")
     # Ensure Month is treated as categorical to maintain order
    #print(monthly_data)
    #print(monthly_data.columns.tolist())
    #print(monthly_data['Accidents'])
    monthly_data["Month"] = pd.Categorical(
    	monthly_data["Month"], 
        categories=[f"{i:02d}" for i in range(1, 13)],  # Generates "01", "02", ..., "12"
        ordered=True
    )

  
    #monthly_data = monthly_data.sort_values("Month")
    monthly_data = monthly_data.sort_values(['Month'])
   
    # Extract lists for plotting
    #months = monthly_data["Month"].tolist()
    #accidents = monthly_data["Accidents"].tolist()
    fig = go.Figure()
    #fig.add_trace(go.Scatter(x=months, y=accidents, mode='lines', name='Monthly Accident Trend'))
    for year in monthly_data['Year'].unique():
    	year_data = monthly_data[monthly_data['Year']==year]
    	months = year_data['Month'].tolist()
    	accidents = year_data['Accidents'].tolist()
    	fig.add_trace(go.Scatter(
    		x = months,
    		y = accidents,
    		mode = 'lines',
    		name = str(year)))
    fig.update_layout(
    	title = f"Monthly Accident Trend for {selected_states}",
    	xaxis = dict(title='Month'),
    	yaxis = dict(title = 'Accidents'),
    	showlegend = True)

 

 
    return fig
@app.callback(
    Output('accident-temperature-plot', 'figure'),
    [
        Input('state-dropdown', 'value'),
        Input('year-dropdown', 'value'),
        Input('month-slider', 'value'),
        Input('temperature-range-slider', 'value')
    ]
)
def update_temperature_plot(selected_states, selected_years, selected_months, temperature_range):
    # Filter the dataframe based on the inputs
    filtered_df = df[
        (df['State'].isin(selected_states)) &
        (df['Year'].isin(selected_years)) &
        (df['Month'].isin(selected_months)) &
        (df['Temperature'] >= temperature_range[0]) &
        (df['Temperature'] <= temperature_range[1])
    ]
    temp_data = filtered_df.groupby('Temperature').size().reset_index(name="Accidents")

    temp_data = temp_data.sort_values(['Temperature'])
    fig = go.Figure()

    #for state in selected_states:
	#state_data = temp_data[temp_data['State'] == state]
    temps = temp_data['Temperature'].tolist()
	#temps = temp_data["Temperature"].tolist()
	#print(temps)

    accidents = temp_data['Accidents'].tolist()
    fig.add_trace(go.Scatter(
    	x = temps,
    	y = accidents,
    	mode = 'lines',
    	))
    fig.update_layout(
    	title = f"Accident Trend by Temperature {selected_states}",
    	xaxis = dict(title = "Temperature"),
    	yaxis = dict(title = "Accidents"),
    	showlegend = False)



    return fig

@app.callback(
    Output("accident-heatmap-chart", "figure"),
    Input('state-dropdown','value')
    
)
def update_accident_heatmap(selected_states):
    #sample_df = df.sample(n=10000, random_state = 123)
    accident_counts = df.groupby(['State','Month']).size().reset_index(name = 'Accidents')
    heatmap_data = accident_counts.pivot(index='State', columns='Month', values='Accidents').fillna(0)
    tempz = heatmap_data.values.tolist()
    tempx = heatmap_data.columns.tolist()
    tempy = heatmap_data.index.tolist()
    fig = go.Figure(data = go.Heatmap(
        z = tempz,
        x = tempx,
        y = tempy,
        colorscale = 'Viridis',
        colorbar = dict(title="Number of Accidents")
		))
    fig.update_layout(
        title = f"Heatmap of Accidents by State and Month",
        xaxis_title = "Month",
        yaxis_title = "State",
        xaxis = dict(tickmode='array',tickvals = list(range(1,13)),ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
        yaxis=dict(tickmode='array', tickvals=heatmap_data.index),
        showlegend = False
    )
    #fig.show()

    return fig

if __name__ == "__main__":
    app.run_server(debug=True)




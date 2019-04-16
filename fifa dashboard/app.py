import plotly
from plotly.graph_objs import *
import plotly.plotly as py
from plotly import tools
from datetime import datetime as dt
import numpy as np
import plotly.figure_factory as ff
import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from plotly import tools

app = dash.Dash(hot_reload = True)
hist_color = "#D91E36"

data = pd.read_csv("../data.csv", index_col=0)

data.columns = data.columns.str.lower().str.replace(" ", "_")

bad_cols = ["club_logo", "photo", "flag", "loaned_from"]

data = data.drop(bad_cols, axis = 1)
data = data.query("position != 'GK'")
gk_cols = [i for i in data.columns if "gk" in i]

data = data.drop(gk_cols, axis = 1)
data = data.set_index("id")

top5 = np.load("../top_5_clubs.pkl")
data = data[data.club.isin(top5)].copy()
attribute_cols = data.columns[48:-1].tolist()
features = data[attribute_cols].copy()
features.dropna(inplace=True)

features["passing"] = (features.shortpassing + features.longpassing)/2.

features["tackling"] = (features.standingtackle + features.slidingtackle)/2.
features.drop(["standingtackle", "slidingtackle", "shortpassing", "longpassing"], axis = 1, inplace=True)

cols = ["finishing", "passing", "dribbling", "curve", "ballcontrol", "tackling", "balance", "marking", "agility"]
X = features[cols].copy()

name_id_dict = data.name.to_dict()
hazard_id = 183277
salah_id = 209331

grid = []
n = [1,2,3]
for i in n:
	for e in n:
		grid.append([i, e])

a = data.name

data.loc[a.duplicated(), "name"] = a[a.duplicated()] + ", " + data.loc[a.duplicated(), "club"]

options = []
for i in data.name.unique():
	d = {"label":i, "value":i}
	options.append(d)

part2 = html.Div(children = [html.Div(children = "Player vs Histograms"),
html.Label('Select Players'),
	html.Div(children = [dcc.Dropdown(id = "drop2", options=options, value = [],multi=False)], 
	style = {"width": "48%"}),
			dcc.Graph(id = "graph2")])


app.layout = html.Div(children=[
	html.H1(children='Fifa Dashboard'),

	html.Div(children='''
		Explore the Fifa Dataset
	'''),
	html.Label('Select Player(s)'),
	html.Div(children = [dcc.Dropdown(id = "drop", options=options, value = [],multi=True)], 
		style = {"width": "48%"}),
	
	dcc.Graph(
		id='graph',
		figure={
			'data': [
				{'r': [0, 0, 0], '"theta': ["", "", ""], 'type': 'scatterpolar', 'name': 'Placeholder'}
			],
			'layout': {
				'polar': {'radialaxis': {"range":[0, 100], 'visible':True}}}
			}
		), part2])
	
	
		
@app.callback(
	Output('graph', 'figure'),
	[Input('drop', 'value')])
def update_polar(players):
	traces = []	
	if len(players) < 1:
		return {'data': [{'r': [0, 0, 0], '"theta': ["", "", ""], 'type': 'scatterpolar', 'name': 'Placeholder'}],
					'layout': {'polar': {'radialaxis': {"range":[0, 100], 'visible':True}}}}
	for i in players:
		indy = data[data.name == i].index[0]
		z = X.loc[indy].tolist()
		z = z + [z[0]]
		trace = Scatterpolar(r = z, theta = cols + [cols[0]], fill = "toself", name = i, opacity = .7)
		traces.append(trace)
	lay = Layout(polar = dict(radialaxis = dict(visible = True, range = [0, 100])), showlegend = True)	
	return {"data": traces, "layout": lay}
	
	
@app.callback(
	Output('graph2', 'figure'),
	[Input('drop2', 'value')])
def update_hist(player):
	
	indy = data[data.name == player].index[0]
	z = X.loc[indy]
	fig = tools.make_subplots(rows=3, cols=3, subplot_titles=cols);
	for i in range(len(cols)):
		c = cols[i]
		
		vc = X[c].value_counts().reindex(np.arange(X[c].min()- 1, X[c].max() + 1))
		
		trace = Bar(x = vc.index, y = vc.values, name = player, marker = dict(color = hist_color))
		
		
		fig.append_trace(trace,grid[i][0], grid[i][1])
		
		sd = Scatter(x =[z[c], z[c]], y = [0, vc.max()] , 
						marker = dict(color = "black"), mode = "lines", name = player)
		fig.append_trace(sd,grid[i][0], grid[i][1])
	fig["layout"].update(showlegend = False, height=750, width=750,
								title='FIFA Histograms')	
	return 	fig
if __name__ == '__main__':
	app.run_server()
	

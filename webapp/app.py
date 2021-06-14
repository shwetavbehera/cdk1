import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import plotly.graph_objects as go

import plotly.express as px

from webapp.database import s_monatsmittel, stations, s_jahresmittel, years, heatmap_values, \
    heatmap_station_labels, heatmap_year_labels, altitude

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
GRAPH_TEMPLATE = 'plotly_white'

@app.callback(
    Output('station_yearly_monthly_mean', 'figure'),
    Input('station1', 'value'))  # Otherwise no output :(
def station_yearly_monthly_mean(value):
    fig = px.imshow(heatmap_values,
                    labels=dict(x='Station', y='Jahre', color='Schneehöhe'),
                    x=heatmap_station_labels,
                    y=heatmap_year_labels,
                    height=600,
                    aspect='auto',
                    color_continuous_scale='deep',
                    title='Schneehöhe - durchschnitlisches Monatsmittel',
                    template=GRAPH_TEMPLATE
                    )

    fig.update_yaxes(type='category')

    return fig


@app.callback(
    Output('station_yearly_comparison', 'figure'),
    Input('station1', 'value'),
    Input('year1', 'value'),
    Input('year2', 'value'))
def station_yearly_comparison(station, year1, year2):
    year1 = int(year1)
    year2 = int(year2)

    data = s_monatsmittel[s_monatsmittel['Ort'] == station]
    data = data[data['Jahre'].isin([year1, year2])].groupby(['Ort', 'Jahre', 'Monate']).agg({
        'Schneehöhe Monatsmittel': 'mean'
    }).reset_index()

    data_1 = data[data['Jahre'] == year1]
    data_2 = data[data['Jahre'] == year2]

    fig = go.Figure(
        data=[
            go.Bar(name=f'{year1}', x=data_1['Monate'], y=data_1['Schneehöhe Monatsmittel'], yaxis='y',
                   offsetgroup=1),
            go.Bar(name=f'{year2}', x=data_2['Monate'], y=data_2['Schneehöhe Monatsmittel'], yaxis='y2',
                   offsetgroup=2)
        ],
        layout={
            'xaxis': {'title': 'Monate'},
            'yaxis': {'title': f'{year1}'},
            'yaxis2': {'title': f'{year2}', 'overlaying': 'y', 'side': 'right'},
            'title': {'text': f'Schneehöhe Monatsmittel für Jahre {year1} und {year2}'}
        }
    )

    fig.update_xaxes(tickvals=list(range(1, 13)))
    fig.update_layout(template=GRAPH_TEMPLATE)

    return fig


@app.callback(
    Output('station_monthly_comparison', 'figure'),
    Input('station1', 'value'),
    Input('station2', 'value'))
def station_monthly_comparison(station1, station2):
    data = s_monatsmittel[s_monatsmittel['Ort'].isin([station1, station2])].groupby(['Ort', 'Monate']).agg({
        'Schneehöhe Monatsmittel': 'mean'
    }).reset_index()

    fig = px.bar(data,
                 x='Monate', y='Schneehöhe Monatsmittel',
                 barmode='group', color='Ort',
                 title=f'Schneehöhe Monatsmittel über den gesamten Zeitraum',
                 template=GRAPH_TEMPLATE)

    for i in range(2):
        station_name = fig.data[i].name
        station_height = altitude[station_name]
        fig.data[i].name = f"{station_name}, {station_height}m"

    fig.update_xaxes(tickvals=list(range(1, 13)))

    return fig


@app.callback(
    Output('station_monthly_mean', 'figure'),
    Input('station1', 'value'))
def station_monthly_mean(station):
    fig = px.scatter(s_monatsmittel[s_monatsmittel['Ort'] == station],
                     x='Jahre', y='Schneehöhe Monatsmittel', color='Monate', trendline='lowess',
                     title='Schneehöhe Monatsmittel 1959-2020',
                     template=GRAPH_TEMPLATE,
                     color_continuous_scale='viridis')

    fig.update_layout(transition_duration=500)

    return fig


@app.callback(
    Output('yearly_mean_snow', 'figure'),
    Input('station1', 'value'))
def station_yearly_mean(station):
    altitude = list(s_jahresmittel[s_jahresmittel['Ort'] == station]['Höhe'])[0]
    fig = px.scatter(s_jahresmittel[s_jahresmittel['Ort'] == station],
                     x='Jahre', y='Schneehöhe Jahresmittel', trendline='lowess',
                     title=f'Schneehöhe Jahresmittel in {station}, {altitude} m',
                     template=GRAPH_TEMPLATE)

    return fig


app.layout = html.Div(children=[
    html.Div([
        html.Div([
            html.Div([
                html.Img(src=app.get_asset_url('header.jpeg'),
                         style={'margin-bottom': '30px'}),
            ], style={'text-align': 'center'}),
            html.Div([
                html.H1('Klimawandel in der Berge'),
            ], style={'text-align': 'center'}),
            dcc.Markdown('''
            Laut der Beherbergungsstatistik des Kantons, die idyllischen Berge Graubündens sorgen 
            für mehr als 5 millionen Übernachtungen pro Jahr. aber auch die märchenhaften 
            Schneehänge dieses Kantons können sich dem Klimawandel und den unvermeidlichen 
            Veränderungen nicht entziehen. Die Klimaänderung zeigt sich nicht nur im signifikanten 
            Temperaturanstieg, es gibt viele weitere Klimaindikatoren, welche die Klimaänderungen verdeutlichen. 
            In der Bergwelt ist dies natürlich die Menge des Schnees. Unten kann man die Veränderungen der 
            Schneemenge in den bergigen Gebieten des Kantons Graubünden beobachten.
             
            '''),

            html.Div([
                html.Img(src=app.get_asset_url('middle.jpeg'),
                         style={'margin-bottom': '30px'}),
            ], style={'text-align': 'center'}),

            dcc.Markdown('''

            Die Situation ist ernst. Schweizer Meteorologen berichten, dass nicht nur die Gesamtmenge 
            des gefallenen Schnees abgenommen hat, sondern auch die Anzahl der Tage mit Neuschnee 
            um 20-60% zurückgegangen ist, je nach Höhenlage der Station. Es ist durchaus zu erwarten, 
            dass in einigen Jahren viele Skigebiete zu Winterwandergebieten werden. Wie sich der fehlende 
            Schnee auf die Vegetation und Fauna auswirkt, ist noch nicht klar. Sollte der fehlende 
            Schnee nicht durch mehr Regen kompensiert werden, könnte es passieren, dass man statt durch 
            eine Bergwiese durch ein wüstenhaftes Terrain wandert. Zum Glück sind wir noch nicht so weit, 
            aber die Klimabedingungen ändern sich und unten kann man selbst beobachten, wie stark.

            ''',
                         style={'margin-bottom': '30px'}),

            dcc.Graph(id='station_yearly_monthly_mean',
                      style={'margin-bottom': '30px'}),

            dcc.Markdown('''

            Die obige Grafik zeigt die Stationen nach ihrer Höhe geordnet, von den niedrigsten Stationen
            auf der linken Seite bis zu den am höchsten gelegenen Stationen auf der rechten Seite. Während
            die tiefer gelegenen Stationen durchgängig niedrige mittlere Schneemengen aufweisen, zeigen
            die höher gelegenen Stationen einen interessanten Trend mit abnehmender Schneehöhe.
            Überraschenderweise hat das Jahr 2020 dieses Muster durchbrochen, so dass es ein klares
            in vivo Experiment ist, dass nicht alles verloren ist, wenn wir es nur schaffen, unseren
            Kohlenstoff-Fußabdruck zu senken.

            ''',
                         style={'margin-bottom': '30px'}),
            html.Div([
                html.Div([
                    html.Label('Die erste Station auswählen'),
                    dcc.Dropdown(
                        id='station1',
                        options=stations,
                        value='St. Moritz'
                    )
                ]),
            ], style={'width': '300px'}),

            html.Div([
                dcc.Graph(id='yearly_mean_snow'),
                dcc.Graph(id='station_monthly_mean'),

            ], style={'columnCount': 2}),

            html.Div([

                html.Div([
                    html.Div([
                        html.Label('Das erste Jahr auswählen'),
                        dcc.Dropdown(
                            id='year1',
                            options=years,
                            value='1968'
                        ),
                        html.Label('Das zweite Jahr auswählen'),
                        dcc.Dropdown(
                            id='year2',
                            options=years,
                            value='2012'
                        ),
                    ], style={'width': '100%', 'height': '140px'}),
                    dcc.Graph(id='station_yearly_comparison'),
                ]),
                html.Div([
                    html.Div([
                        html.Label('Die zweite Station auswählen'),
                        dcc.Dropdown(
                            id='station2',
                            options=stations,
                            value='St. Antönien'
                        ),

                    ], style={'width': '100%', 'height': '140px'}),
                    dcc.Graph(id='station_monthly_comparison'),
                ]),

            ], style={'columnCount': 2}),

        ], style={'width': '1100px',
                  'display': 'inline-block',
                  'text-align': 'left'})
    ], style={'text-align': 'center'})
])

if __name__ == '__main__':
    app.run_server(debug=False)

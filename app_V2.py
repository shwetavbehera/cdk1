import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import plotly.graph_objects as go

import plotly.express as px

import pandas as pd

from webapp.database import s_monatsmittel, stations, s_jahresmittel, years, all_data_df

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


@app.callback(
    Output('station_yearly_monthly_mean', 'figure'),
    Input('station_yearly_comparison-station', 'value')) # Otherwise no output :(
def station_yearly_monthly_mean(value):
    yearly_data = all_data_df. \
        groupby(['Station', 'Jahre']). \
        agg(values=('Schneehöhe Monatsmittel', 'mean'), Höhe=('Höhe', 'first')). \
        astype(float).reset_index()

    stations = pd.DataFrame(yearly_data['Station'].unique(), columns=['Station'])
    stations = stations.merge(pd.DataFrame(range(yearly_data['Jahre'].min(),
                                                 yearly_data['Jahre'].max() + 1), columns=['Jahre']), how='cross')

    heatmap_data = pd.merge(stations, yearly_data, how='left', on=['Station', 'Jahre']) \
        .sort_values(by=['Jahre', 'Höhe'], ascending=[False, True]).reset_index()

    year_labels = heatmap_data['Jahre'].unique()
    station_labels = heatmap_data['Station'].unique()
    values = heatmap_data['values'].to_numpy().reshape((len(year_labels), len(station_labels)))

    fig = px.imshow(values,
                    labels=dict(x='Station', y='Jahre', color='Schneehöhe'),
                    x=station_labels,
                    y=year_labels,
                    height=600,
                    aspect='auto',
                    color_continuous_scale='deep',
                    title='Schneehöhe - durchschnitlisches Monatsmittel'
                    )
    fig.update_yaxes(type='category')

    return fig


@app.callback(
    Output('station_yearly_comparison', 'figure'),
    Input('station_yearly_comparison-station', 'value'),
    Input('station_yearly_comparison-year1', 'value'),
    Input('station_yearly_comparison-year2', 'value'))
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
            'yaxis': {'title': f'{year1}'},
            'yaxis2': {'title': f'{year2}', 'overlaying': 'y', 'side': 'right'},
            'title': {'text': f'Schneehöhe Monatsmittel für Jahre {year1} und {year2}'}
        }
    )

    fig.update_xaxes(tickvals=list(range(1, 13)))

    return fig


@app.callback(
    Output('station_monthly_comparison', 'figure'),
    Input('station_monthly_comparison-station1', 'value'),
    Input('station_monthly_comparison-station2', 'value'))
def station_monthly_comparison(station1, station2):
    data = s_monatsmittel[s_monatsmittel['Ort'].isin([station1, station2])].groupby(['Ort', 'Monate']).agg({
        'Schneehöhe Monatsmittel': 'mean'
    }).reset_index()

    fig = px.bar(data,
                 x='Monate', y='Schneehöhe Monatsmittel',
                 barmode='group', color='Ort',
                 title=f'Schneehöhe Monatsmittel über den gesamten Zeitraum für {station1} and {station2}')

    fig.update_xaxes(tickvals=list(range(1, 13)))

    return fig


@app.callback(
    Output('station_monthly_mean', 'figure'),
    Input('station_monthly_mean_dropdown', 'value'))
def station_monthly_mean(station):
    fig = px.scatter(s_monatsmittel[s_monatsmittel['Ort'] == station],
                     x='Jahre', y='Schneehöhe Monatsmittel', color='Monate', trendline='lowess',
                     title='Schneehöhe Monatsmittel 1959-2020')

    fig.update_layout(transition_duration=500)

    return fig


@app.callback(
    Output('yearly_mean_snow', 'figure'),
    Input('yearly_mean_snow-station', 'value'))
def station_yearly_mean(station):
    altitude = list(s_jahresmittel[s_jahresmittel['Ort'] == station]['Höhe'])[0]
    fig = px.scatter(s_jahresmittel[s_jahresmittel['Ort'] == station],
                     x='Jahre', y='Schneehöhe Jahresmittel', trendline='lowess',
                     title=f'Schneehöhe Jahresmittel in {station}, {altitude} m')

    return fig


app.layout = html.Div(children=[
    html.Div([
        html.Div([
            html.Img(src=app.get_asset_url('header.jpeg'),
                     style={'margin-bottom': '30px'}),

            dcc.Markdown('''
            # Das Verschwinden des Schnee

            **Was wäre der Schweizer Winter ohne Schnee? Viele schweizer Einwohner geniessen den jährlichen Schnee. 
            Ob durch Sport oder allgemeine Tourismus, die Wirtschaft der Schweiz profitiert von dem Zufluss 
            von Touristen in den Bergen. Wirft man ein Blick in die Vergangenheit, sieht die heutige Situation aber 
            duster aus. Mit dem zunehmenden Effekt vom globalen Klimawandel in den letzten 50 Jahren ist die 
            Zukunft der Schneesport-gebiete gefährdet.**
            
            Laut der Beherbergungsstatistik des Kantons, die idyllischen Berge Graubündens sorgen 
            für mehr als 5 millionen Übernachtungen pro Jahr. aber auch die märchenhaften 
            Schneehänge dieses Kantons können sich dem Klimawandel und den unvermeidlichen 
            Veränderungen nicht entziehen. Die Klimaänderung zeigt sich nicht nur im substantiellen 
            Temperaturanstieg, es gibt viele weitere Indikatoren, welche die Klimaänderungen verdeutlichen. 
            In der Bergwelt ist dies natürlich die Menge des Schnees. Unten kann man die Veränderungen der 
            Schneemenge in den bergigen Gebieten des Kantons Graubünden beobachten.
             
            '''),

            html.Img(src=app.get_asset_url('middle.jpeg'),
                     style={'margin-top': '30px',
                            'margin-bottom': '30px'}),

            dcc.Markdown('''

            Die Situation ist ernst. Schweizer Meteorologen berichten, dass nicht nur die Gesamtmenge 
            des gefallenen Schnees abgenommen hat, sondern auch die Anzahl der Tage mit Neuschnee 
            um 20-60% zurückgegangen ist, je nach Höhenlage der Station. Es ist durchaus zu erwarten, 
            dass in einigen Jahren viele Skigebiete zu Winterwandergebieten werden. Wie sich der fehlende 
            Schnee auf die Vegetation und Fauna auswirkt, ist noch nicht klar. Sollte der fehlende 
            Schnee nicht durch mehr Regen kompensiert werden, könnte es passieren, dass man statt durch 
            eine Bergwiese durch ein wüstenhaftes Terrain wandert. Zum Glück sind wir noch nicht so weit, 
            aber die Klimabedingungen ändern sich und unten kann man selbst beobachten, wie stark.
            Das Wetter und das Klima der Schweiz wird seit mehr als 100 Jahren auf mehrere Stationen gemessen 
            und von MeteoSchweiz zur Verfügung gestellt.

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

            ## Scuol unter die Lupe

            Über 1300 liegend, bietet Scuol Ski-, Snowboardtouren, Wanderwege, Langlaufen und vieles mehr. 
            Bis heute ist es ein sehr aktiver Schneesport Bereich, der aber gegenüber der Effekte der Zeit 
            nicht immun ist. Über die letzten 70 Jahren, seit Beobachtungen über diese Station aufgenommen 
            wurden, hat sich die Schneehöhe deutlich verändert. Seit 1943 bis 2020 hat sich die Schneehöhe 
            durchschnittlich um 6 cm verringert, das sind 30% der ursprünglichen Messung.

            ''',
            style={'margin-bottom': '30px'}),

            html.Img(src=app.get_asset_url('scuol1.jpeg'),
                     style={'margin-top': '30px',
                            'margin-bottom': '30px'}),



            dcc.Markdown('''
            
            Nun stellt sich die frage, wie sich die Schneesport Saison sich verändert als Folge von Klimawandel. 
            Wenn man das Verhalten der Schneehöhe innerhalb von einem Jahr in den letzten 50 Jahren betrachtet, 
            sieht man die Veränderung des Intervals, wann Schnee vorhanden ist. Die Messwerte zeigen, dass 
            die Saison in 2020 einige Monate später vorkommt als in 1970. Zudem gibt es auch weniger Monate mit 
            hoher Schneehöhe. Das hat zur Folge, dass heute Schneesport Saisons kürzer sind. Mit allen 
            Schneesportler und Schneesportlerinnen und neue Interessierte jedes Jahr, wird es schwieriger 
            dieses Volumen zu befriedigen, wenn die Saisons jedes Jahr kürzer werden.
            
            ''',
            style={'margin-bottom': '30px'}),
            
            html.Img(src=app.get_asset_url('scuol2.jpeg'),
                     style={'margin-top': '30px',
                            'margin-bottom': '30px'}),
            
            dcc.Markdown('''

            ## Die Zukunft
            Anhand der vergangenen Änderung des Klimas ist es deutlich vorherzusagen, dass die Situation weiterhin 
            ein Problem für den alltäglichen Schweizer darstellen wird. Mit der weiteren Abnahme der Schneehöhe, 
            werden Schneesportler und Schneesportlerinnen voraussichtlich in den kommenden Jahrzehnten immer höher 
            gehen müssen um ihr Bedürfnis zu erfüllen – bis schlussendlich kein Schnee mehr vorhanden ist auch in den 
            höchsten Gebiete.

            Deshalb ist für die Einwohnern der Schweiz Aufmerksamkeit gefragt. Klimawandel ist ein Thema, das immer 
            wieder erscheint – in Zeitungen, Fernseher oder Blogs – aber von vielen schnell vergessen geht. Aber wenn 
            heute nichts gemacht wird, können wir vergessen mit unsere Kindern und Enkeln die Erfahrungen zu sammeln, 
            die wir glücklicherweise bereits gesammelt haben. Hier sind persönliche Massnahmen zu finden, die ergriffen 
            werden können, um seinen kleinen aber wichtigen Beitrag zu leisten.

            ''',
            style={'margin-bottom': '30px'}),

            html.Div([

                html.Label('Die erste Station auswählen'),
                dcc.Dropdown(
                    id='station_yearly_comparison-station',
                    options=stations,
                    value='St. Moritz'
                ),
                html.Label('Das erste Jahr auswählen'),
                dcc.Dropdown(
                    id='station_yearly_comparison-year1',
                    options=years,
                    value='1968'
                ),
                html.Label('Das zweite Jahr auswählen'),
                dcc.Dropdown(
                    id='station_yearly_comparison-year2',
                    options=years,
                    value='2012'
                )
            ], style={'width': '200px'}),
            dcc.Graph(id='station_yearly_comparison',
                      style={'margin-bottom': '30px'}),

            html.Div([
                html.Label('Die erste Station auswählen'),
                dcc.Dropdown(
                    id='station_monthly_comparison-station1',
                    options=stations,
                    value='St. Moritz'
                ),
                html.Label('Die zweite Station auswählen'),
                dcc.Dropdown(
                    id='station_monthly_comparison-station2',
                    options=stations,
                    value='Maloja'
                ),
            ], style={'width': '200px'}),
            dcc.Graph(id='station_monthly_comparison',
                      style={'margin-bottom': '30px'}),

            html.Label('Station Auswahl'),
            dcc.Dropdown(
                id='station_monthly_mean_dropdown',
                options=stations,
                value='St. Moritz',
                style={'width': '200px'}
            ),
            dcc.Graph(id='station_monthly_mean'),

            html.Label('Station Auswahl'),
            dcc.Dropdown(
                id='yearly_mean_snow-station',
                options=stations,
                value='St. Moritz',
                style={'width': '200px'}
            ),
            dcc.Graph(id='yearly_mean_snow'),

        ], style={'width': '800px',
                  'display': 'inline-block',
                  'text-align': 'left'})
    ], style={'text-align': 'center'})
])

if __name__ == '__main__':
    app.run_server(debug=False)

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import plotly.graph_objects as go

import plotly.express as px

from database import s_monatsmittel, stations, s_jahresmittel, years, heatmap_values, \
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
                html.Img(src=app.get_asset_url('oberengadin.jpg'),
                         style={'margin-bottom': '30px'}),
            ], style={'text-align': 'center'}),
            html.Div([
                html.H1('Klimawandel in der Berge'),
            ], style={'text-align': 'center'}),
            dcc.Markdown('''
            Was wäre der Schweizer Winter ohne Schnee? Viele Schweizer Einwohner geniessen den jährlichen Schnee. 
            Ob durch Sport oder allgemeine Tourismus, die Wirtschaft der Schweiz profitiert von dem Zufluss 
            von Touristen in den Bergen. Wirft man ein Blick in die Vergangenheit, sieht die heutige Situation aber 
            duster aus. Mit dem zunehmenden Effekt vom globalen Klimawandel in den letzten 50 Jahren ist die 
            Zukunft der Schneesport-gebiete gefährdet.**
            
            Laut der Beherbergungsstatistik des Kantons, die idyllischen Berge Graubündens sorgen 
            für mehr als 5 Millionen Übernachtungen pro Jahr. aber auch die märchenhaften 
            Schneehänge dieses Kantons können sich dem Klimawandel und den unvermeidlichen 
            Veränderungen nicht entziehen. Die Klimaänderung zeigt sich nicht nur im substantiellen 
            Temperaturanstieg, es gibt viele weitere Indikatoren, welche die Klimaänderungen verdeutlichen. 
            In der Bergwelt ist dies natürlich die Menge des Schnees. Unten kann man die Veränderungen der 
            Schneemenge in den bergigen Gebieten des Kantons Graubünden beobachten.
            
            Die Situation ist ernst. Schweizer Meteorologen berichten, dass nicht nur die Gesamtmenge 
            des gefallenen Schnees abgenommen hat, sondern auch die Anzahl der Tage mit Neuschnee 
            um 20-60% zurückgegangen ist, je nach Höhenlage der Station. Es ist durchaus zu erwarten, 
            dass in einigen Jahren viele Skigebiete zu Winterwandergebieten werden. Wie sich der fehlende 
            Schnee auf die Vegetation und Fauna auswirkt, ist noch nicht klar. Sollte der fehlende 
            Schnee nicht durch mehr Regen kompensiert werden, könnte es passieren, dass man statt durch 
            eine Bergwiese durch ein wüstenhaftes Terrain wandert. Zum Glück sind wir noch nicht so weit, 
            aber die Klimabedingungen ändern sich und unten kann man selbst beobachten, wie stark.
            Das Wetter und das Klima der Schweiz werden seit mehr als 100 Jahren auf mehrere Stationen gemessen 
            und von MeteoSchweiz zur Verfügung gestellt.
            

            ''',
                         style={'margin-bottom': '30px'}),

            dcc.Graph(id='station_yearly_monthly_mean',
                      style={'margin-bottom': '30px'}),

            dcc.Markdown('''
            Die obige Grafik zeigt die Stationen nach ihrer Höhe geordnet, von den niedrigsten Stationen
            auf der linken Seite bis zu den an den höchsten gelegenen Stationen auf der rechten Seite. Während
            die tiefen gelegenen Stationen durchgängig niedrige mittlere Schneemengen aufweisen, zeigen
            die höher gelegenen Stationen einen interessanten Trend mit abnehmender Schneehöhe.
            Überraschenderweise hat das Jahr 2020 dieses Muster durchbrochen, so dass es ein klares
            in vivo Experiment ist, dass nicht alles verloren ist, wenn wir es nur schaffen, unseren
            Kohlenstoff-Fußabdruck zu senken.
            
           
            ## Scuol unter die Lupe

            Über 1300 liegend, bietet Scuol Ski-, Snowboardtouren, Wanderwege, Langlaufen und vieles mehr. 
            Bis heute ist es ein sehr aktiver Schneesport Bereich, der aber gegenüber den Effekten der Zeit 
            nicht immun ist. Über die letzten 70 Jahren, seit Beobachtungen über diese Station aufgenommen 
            wurden, hat sich die Schneehöhe deutlich verändert. Seit 1943 bis 2020 hat sich die Schneehöhe 
            durchschnittlich um 6 cm verringert, das sind 30% der ursprünglichen Messung.
            
            Nun stellt sich die frage, wie sich die Schneesport Saison sich verändert als Folge von Klimawandel. 
            Wenn man das Verhalten der Schneehöhe innerhalb von einem Jahr in den letzten 50 Jahren betrachtet, 
            sieht man die Veränderung des Intervals, wann Schnee vorhanden ist. Die Messwerte zeigen, dass 
            die Saison in 2020 einige Monate später vorkommt als in 1970. Zudem gibt es auch weniger Monate mit 
            hoher Schneehöhe. Das hat zur Folge, dass heute Schneesport Saisons kürzer sind. Mit allen 
            Schneesportler und Schneesportlerinnen und neue Interessierte jedes Jahr, wird es schwieriger 
            dieses Volumen zu befriedigen, wenn die Saisons jedes Jahr kürzer werden.
            
            
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
            
            
            ## Quellen
            
            Idaweb              - https://gate.meteoswiss.ch/idaweb/login.do;idaweb=wTw69Rl6Z2sfPbw4HcX-ix91CleZTANWW4FUq89B0BLpXEEjgrTi!1808625866
            SRF Statistik       - https://www.srf.ch/news/schweiz/alles-faehrt-ski-aber-nicht-die-eigenen
            Scuol               - https://www.engadin.com/en/node/2443
            Wintersportsaison   - https://www.nzz.ch/wissenschaft/klima/klimawandel-immer-kuerzere-wintersportsaison-ld.146197?reduced=true
            Zukunft Schneesport - https://www.republik.ch/2019/02/06/wo-koennen-wir-im-jahr-2060-noch-ski-fahren
            Massnahmen          - https://www.planat.ch/de/wissen/klimawandel/massnahmen-kw



            ''',
                         style={'margin-bottom': '30px'}),
            html.Div([
                html.Div([
                    html.Label('Station Auswahl:'),
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
                        html.Label('Das 1. Jahr auswählen:'),
                        dcc.Dropdown(
                            id='year1',
                            options=years,
                            value='1968'
                        ),
                        html.Label('Das 2. Jahr auswählen:'),
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
                        html.Label('Die 2. Station auswählen:'),
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

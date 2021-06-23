import pandas as pd
from monthly_download.py import *

# TODO: Replace reading from the Pickle file with SQL
all_data_df = get_data()

s_monatsmittel = all_data_df[~all_data_df["Schneehöhe Monatsmittel"].isna()]
winter_months = [10, 11, 12, 1, 2, 3, 4, 5]
s_monatsmittel = s_monatsmittel[s_monatsmittel["Monate"].isin(winter_months)]

s_jahresmittel = all_data_df[~all_data_df['Schneehöhe Jahresmittel'].isna()]

max_mean_snow_data = all_data_df.groupby(['Ort', 'Jahre', 'Monate']).agg(
    max_mean_snow=('Schneehöhe Monatsmittel', 'max')) \
    .sort_values(by='max_mean_snow', ascending=False).reset_index() \
    .groupby(['Ort', 'Jahre']).first().reset_index()

monatsmittel_ort = set(s_monatsmittel['Ort'].unique())
jahresmittel_ort = set(s_jahresmittel['Ort'].unique())
common_stations = list(monatsmittel_ort.intersection(jahresmittel_ort))
stations = [{'label': x, 'value': x} for x in common_stations]

years = [{'label': x, 'value': x} for x in list(range(all_data_df["Jahre"].min(), all_data_df["Jahre"].max()))]

altitude_df = all_data_df[['Ort', 'Station', 'Höhe']].groupby(['Ort', 'Station', 'Höhe']).first().reset_index()
altitude = {x[1][0]: x[1][2] for x in altitude_df.iterrows()}

# Heatmap visualization
heatmap_yearly_data = all_data_df. \
    groupby(['Station', 'Jahre']). \
    agg(values=('Schneehöhe Monatsmittel', 'mean'), Höhe=('Höhe', 'first')). \
    astype(float).reset_index()

heatmap_stations = pd.DataFrame(heatmap_yearly_data['Station'].unique(), columns=['Station'])
heatmap_stations = heatmap_stations.merge(pd.DataFrame(range(heatmap_yearly_data['Jahre'].min(),
                                                             heatmap_yearly_data['Jahre'].max() + 1),
                                                       columns=['Jahre']),
                                          how='cross')

heatmap_data = pd.merge(heatmap_stations, heatmap_yearly_data, how='left', on=['Station', 'Jahre']) \
    .sort_values(by=['Jahre', 'Höhe'], ascending=[False, True]).reset_index()

heatmap_year_labels = heatmap_data['Jahre'].unique()
heatmap_station_labels = heatmap_data['Station'].unique()
heatmap_values = heatmap_data['values'].to_numpy().reshape((len(heatmap_year_labels), len(heatmap_station_labels)))

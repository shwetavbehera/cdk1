import pandas as pd

all_data_df = pd.read_pickle("../all_data.pkl")

s_monatsmittel = all_data_df[~all_data_df["Schneehöhe Monatsmittel"].isna()]
winter_months = [10, 11, 12, 1, 2, 3, 4, 5]
s_monatsmittel = s_monatsmittel[s_monatsmittel["Monate"].isin(winter_months)]

s_jahresmittel = all_data_df[~all_data_df['Schneehöhe Jahresmittel'].isna()]

stations = [{'label': x, 'value': x} for x in list(s_monatsmittel['Ort'].unique())]
years = [{'label': x, 'value': x} for x in list(range(1965, 2021))]


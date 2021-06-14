# Finds all the pathnames matching a specified pattern - glob module
from glob import glob
# Read and write strings as files - StringIO - needed because 'files' are separated by empty lines
from io import StringIO
import pandas as pd

data_types = {
    'time': 'str',
    'hto000y0': 'Int32',
    'hto000m0': 'Int32'
}

columns = {
    'stn': 'Station',
    'hto000y0': 'Schneehöhe Jahresmittel',
    'hto000m0': 'Schneehöhe Monatsmittel'
}

station_heights = {
    'STZ': 1895,
    'SLF7MZ': 1850,
    'SMO': 1800,
    'SMZ': 1825,
    'MOZ': 1850,
    'PON': 1787,
    'POA': 1780,
    'WSLCLB': 1866,
    'WSLCLF': 1760,
    'ZUO': 1750,
    'MMZOZ': 1662,
    'SLF7ZU': 1710,
    'ZOZ': 1850,
    'SLF7MA': 1810,
    'ARS': 1900,
    'ARD': 1840,
    'ARO': 1878,
    'TSG': 2040,
    'MAN': 2800,
    'VAB': 1568,
    'VBA': 2560,
    'LEH': 1400,
    'LEZ': 1500,
    'SLF5PL': 1630,
    'SIV': 2470,
    'SVH': 2380,
    'SLF5SE': 1420,
    'SED': 1429,
    'SLF5OB': 1420,
    'VEL': 1245,
    'MMSVG': 1168,
    'SVG': 1172,
    'SCU': 1304,
    'SCL': 1240,
    'SLF7SU': 1285,
    'BIV': 1856,
    'GRU': 650,
    'GUS': 590,
    'SDO': 1460,
    'SPG': 1460,
    'BOGRSP': 1473,
    'SPL': 1504,
    'TST': 1273,
    'LAT': 1408,
    'STM': 1390,
    'SMM': 1386,
    'VAS': 1250,
    'SLF5VA': 1260,
    'VLS': 1242,
    'SLFVL2': 2070,
    'SLFVLS': 3121,
    'AVB': 1993,
    'SBD': 1625,
    'BOGRSB': 1631,
    'BEO': 2073,
    'SBV': 1620,
    'SAN': 1456
}

station_location = {
    'STZ': 'St. Moritz',
    'SLF7MZ': 'St. Moritz',
    'SMO': 'St. Moritz',
    'SMZ': 'St. Moritz',
    'MOZ': 'St. Moritz',
    'PON': 'Pontresina',
    'POA': 'Pontresina',
    'WSLCLB': 'Celerina Bestand',
    'WSLCLF': 'Celerina Bestand',
    'ZUO': 'Zuoz',
    'MMZOZ': 'Zuoz',
    'SLF7ZU': 'Zuoz',
    'ZOZ': 'Zuoz',
    'SLF7MA': 'Maloja',
    'ARS': 'Arosa',
    'ARD': 'Arosa',
    'ARO': 'Arosa',
    'TSG': 'Arosa',
    'MAN': 'Arosa',
    'VAB': 'Valbella',
    'VBA': 'Valbella',
    'LEH': 'Lenzerheide',
    'LEZ': 'Lenzerheide',
    'SLF5PL': 'Laax',
    'SIV': 'Silvretta',
    'SVH': 'Silvretta',
    'SLF5SE': 'Sedrun',
    'SED': 'Sedrun',
    'SLF5OB': 'Obersaxen',
    'VEL': 'Vella',
    'MMSVG': 'Savognin',
    'SVG': 'Savognin',
    'SCU': 'Scuol',
    'SCL': 'Scuol',
    'SLF7SU': 'Scuol',
    'BIV': 'Bivio',
    'GRU': 'Grüsch',
    'GUS': 'Grüsch',
    'SDO': 'Splügen',
    'SPG': 'Splügen',
    'BOGRSP': 'Splügen',
    'SPL': 'Splügen',
    'TST': 'Tschiertschen',
    'LAT': 'Bergün / Latsch',
    'STM': 'Val Müstair',
    'SMM': 'Val Müstair',
    'VAS': 'Vals',
    'SLF5VA': 'Vals',
    'VLS': 'Vals',
    'SLFVL2': 'Vals',
    'SLFVLS': 'Vals',
    'AVB': 'Avers',
    'SBD': 'San Bernardino',
    'BOGRSB': 'San Bernardino',
    'BEO': 'San Bernardino',
    'SBV': 'San Bernardino',
    'SAN': 'St. Antönien'
}


# Here I changed the pattern to match the extracted file names.
def import_files(pattern='*_data.txt'):
    all_data_df = pd.DataFrame()

    # filename - names of all files in a specific folder matching the conditions described in glob()
    for filename in glob(pattern):
        # Open all files, one by one.
        with open(filename) as input_file:
            # Read all lines in one file, from 3. line on (to avoid empty lines).
            # We get an array & read from 3. line on.
            file_data = input_file.readlines()[2:]

        while file_data:
            # Copy all lines until you reach the first empty line into a string variable 'table' (csv-like).
            table = "".join(file_data[0:file_data.index("\n")])
            # Delete all copied lines + the empty line.
            file_data = file_data[file_data.index("\n") + 1:]

            # Load the 'tables' into a pandas dataframe, thus creating the df.
            file_df = pd.read_table(StringIO(table), sep=';', na_values='-', dtype=data_types)
            # Unite all temp dataframes into one main dataframe.
            all_data_df = pd.concat([all_data_df, file_df])

    # Extract year/month from date string.
    all_data_df['Jahre'] = all_data_df['time'].apply(lambda x: x[0:4])
    all_data_df['Jahre'] = all_data_df['Jahre'].astype('int32')
    all_data_df['Monate'] = all_data_df['time'].apply(lambda x: x[4:6])
    all_data_df['Monate'] = all_data_df['Monate'].replace('', None).astype('float').astype('Int32')

    columns_order = ['stn', 'Höhe', 'Ort', 'Jahre', 'Monate', 'hto000m0']

    # Schneehöhe Jahresmittel is not present until the end of the year
    if 'hto000y0' in all_data_df.columns:
        columns_order.append('hto000y0')

    all_data_df['Höhe'] = all_data_df['stn'].apply(lambda x: station_heights[x]).astype('int32')
    all_data_df['Ort'] = all_data_df['stn'].apply(lambda x: station_location[x])

    all_data_df = all_data_df.drop('time', axis=1)
    all_data_df = all_data_df[columns_order]

    all_data_df = all_data_df.rename(columns=columns)

    return all_data_df

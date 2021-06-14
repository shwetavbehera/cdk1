import os
from glob import glob

import pandas

from scrape import scrape_data
from wrangle import import_files

email = "katarina.fatur%40students.fhnw.ch"
password = "7CDB6F8990"

download_dates = [
    # ('01.01.1940', '31.12.1949'),
    # ('01.01.1950', '31.12.1959'),
    ('01.01.1960', '31.12.1969'),
    # ('01.01.1970', '31.12.1979'),
    # ('01.01.1980', '31.12.1989'),
    # ('01.01.1990', '31.12.1999'),
    # ('01.01.2000', '31.12.2009'),
    # ('01.01.2010', '31.12.2019'),
    # ('01.01.2020', '31.12.2020'),
]

all_data_df = pandas.DataFrame()

for dates in download_dates:
    print("Downloading", dates)
    try:
        scrape_data(email, password, dates[0], dates[1])
    except:
        print("Failed at", dates)

all_data_df = import_files()

all_data_df.to_pickle("all_data.pkl")

for file_name in glob('*_data.txt'):
    os.remove(file_name)

for file_name in glob('*_legend.txt'):
    os.remove(file_name)

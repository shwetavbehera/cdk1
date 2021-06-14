import os
import psycopg2
import pandas.io.sql as psql
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from datetime import date
from datawrangler import import_files
from datacrawler import scrape_data



def get_new_data ():

    # connect to db
    con = psycopg2.connect(
        user = "ivqhdeed",
        password = "71wPDwbYLp1dFIZjtH3Q0Els36doVsx6",
        host="dumbo.db.elephantsql.com",
        database = "ivqhdeed"    
    )
    
    # cursor
    cur = con.cursor()
    
    # get last date that we updated the database
    last_dates = psql.read_sql('SELECT * FROM public."Dates"', con)
    last_date = last_dates['Dates'].iloc[-1]
    today = date.today()
    
    # get the raw data from last date of crawling until now
    scrape_data(email, password, last_date, today)
    
    # get the txt file with the data
    cwd = os.getcwd()
    regex = re.compile('(.*data.txt$)')
    for root, dirs, files in os.walk(cwd):
        for file in files:
            if regex.match(file):
            data_file = file
            os.remove(file)
            
    # wrangle the data to fit into the database           
    df_new_data_raw = import_files(str(data_file))
    
    cur.execute("insert into Klimadaten")
    
    # execute query to get whole dataframe
    full_data_df = psql.read_sql('SELECT * FROM public."Klimadaten"', con)
    
    
    con.close()
    
    
    
    return full_data_df
import os
import psycopg2
import pandas.io.sql as psql
import pandas
import re
import requests
from bs4 import BeautifulSoup


def get_new_data (date):

    # connect to db
    con = psycopg2.connect(
        user = "ivqhdeed",
        password = "71wPDwbYLp1dFIZjtH3Q0Els36doVsx6",
        host="dumbo.db.elephantsql.com",
        database = "ivqhdeed"    
    )

    # execute query
    dataframe = psql.read_sql('SELECT * FROM public."Klimadaten"', con)
    lasttime = psql.read_sql('SELECT * FROM public."Dates"', con)
    
    payload = {
    'user': 'katarina.fatur@students.fhnw.ch',
    'inUserPass': '7CDB6F8990'
    }

    # Use 'with' to ensure the session context is closed after use.
    with requests.Session() as s:
        p = s.post('https://gate.meteoswiss.ch/idaweb/login.do', data=payload)
        # print the html returned or something more intelligent to see if it's a successful login page.

        # An authorised request.
        r = s.get('https://gate.meteoswiss.ch/idaweb/system/ordersList.do')
        soup = BeautifulSoup(str(r), "lxml")
        print(r)

        con.close()
    
    
    
    return new_dataframe

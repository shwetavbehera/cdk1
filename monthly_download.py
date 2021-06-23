import os
import psycopg2
import pandas.io.sql as psql
import re
from datetime import date
from datetime import datetime
import sys
from scrape import scrape_data
from wrangle import import_files

# Credentials for database connection
param_dic = {
    "host"      : "dumbo.db.elephantsql.com",
    "database"  : "ivqhdeed",
    "user"      : "ivqhdeed",
    "password"  : "71wPDwbYLp1dFIZjtH3Q0Els36doVsx6"
}

def connect(params_dic):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params_dic)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        sys.exit(1) 
    return conn

# Dunction to inserting single row of data into the DB
def single_insert(conn, insert_req):
    """ Execute a single INSERT request """
    cursor = conn.cursor()
    try:
        cursor.execute(insert_req)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    cursor.close()
    
    
def update_db(conn):
    # get last date that we updated the database
    last_dates = psql.read_sql('SELECT * FROM public."Dates"', conn)
    last_date = last_dates['Dates'].iloc[-1].strftime('%d.%m.%Y')

    # Login to the Idaweb portal and scraping the data from last updated date until now
    email = "katarina.fatur%40students.fhnw.ch"
    password = "7CDB6F8990"
    start_date = last_date
    end_date = date.today().strftime('%d.%m.%Y')
    scrape_data(email, password, start_date, end_date)

    # get the txt file with the data, save the data and delete the txt file
    cwd = os.getcwd()
    regex = re.compile('(.*data.txt$)')
    for root, dirs, files in os.walk(cwd):
        for file in files:
            if regex.match(file):
                new_data = import_files()
                
    if 'Schneehöhe Jahresmittel' in new_data.columns:
        new_data['Schneehöhe Jahresmittel'] = new_data['Schneehöhe Jahresmittel'].astype(float)
        new_data['Schneehöhe Monatsmittel'] = new_data['Schneehöhe Monatsmittel'].astype(float)
        for i in range(len(new_data)):
            query = """INSERT into "Test"(staion, hoehe, ort, jahre, monate, jahressumme, monatssumme) values('%s', '%s','%s','%s','%s','%s','%s');""" % (new_data['Station'].iloc[i], new_data['Höhe'].iloc[i], new_data['Ort'].iloc[i], new_data['Jahre'].iloc[i], new_data['Monate'].iloc[i], new_data['Schneehöhe Jahresmittel'].iloc[i], new_data['Schneehöhe Monatsmittel'].iloc[i])
            single_insert(conn, query)
    else:
        new_data['Schneehöhe Monatsmittel'] = new_data['Schneehöhe Monatsmittel'].astype(float)
        for i in range(len(new_data)):
            query = """INSERT into "Test"(staion, hoehe, ort, jahre, monate, monatssumme) values('%s', '%s','%s','%s','%s','%s');""" % (new_data['Station'].iloc[i], new_data['Höhe'].iloc[i], new_data['Ort'].iloc[i], new_data['Jahre'].iloc[i], new_data['Monate'].iloc[i], new_data['Schneehöhe Monatsmittel'].iloc[i])

            
def get_data():
    # Connecting to the database
    conn = connect(param_dic)
    
    # Update the database if it is the first day of the month
    today = datetime.now()
    if today.day == 1:
        update_db(conn)
    # execute query to get whole dataframe
    full_data_df = psql.read_sql('SELECT * FROM public."Test"', conn)
    
    # Rename columns to make it usable for further use
    full_data_df = full_data_df.rename(columns={'staion': 'Station', 
                                                'hoehe': 'Höhe', 
                                                'ort': 'Ort', 
                                                'jahre': 'Jahre', 
                                                'monate': 'Monate', 
                                                'jahressumme': 'Schneehöhe Monatsmittel', 
                                                'monatssumme': 'Schneehöhe Jahresmittel'})
    
    # Convert floats to Integer
    full_data_df['Höhe'] = full_data_df['Höhe'].astype('Int64')
    full_data_df['Jahre'] = full_data_df['Jahre'].astype('Int64')
    full_data_df['Monate'] = full_data_df['Monate'].astype('Int64')
    full_data_df['Schneehöhe Monatsmittel'] = full_data_df['Schneehöhe Monatsmittel'].astype('Int64')
    full_data_df['Schneehöhe Jahresmittel'] = full_data_df['Schneehöhe Jahresmittel'].astype('Int64')
    

    # Close the connection
    conn.close()
    return full_data_df
